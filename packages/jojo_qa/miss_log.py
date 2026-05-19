"""Miss log — append-only JSONL trail of retrieval misses.

Whenever a Q&A session falls through to ``raw_fallback.search`` (or
finds the wiki had insufficient coverage), the session appends a miss
entry. The next ``jojo_compile absorb`` run reads this log and
prioritizes the raw entries that produced misses, so wiki coverage
catches up to actual usage.

Format: one JSON object per line, in ``ask_jojo/docs/qa/misses.jsonl``.
Each entry carries the question, the route decision, why the wiki was
insufficient, and which raw entries were read instead.

Public API:

- ``MissEntry`` — dataclass for one miss.
- ``append(...)`` — write one entry to the log file.
- ``read_recent(n=50)`` — read the most recent N entries (used by the
  Ops tab and by the absorb-prioritization heuristic).
- ``summary(window_days=14)`` — aggregate counts by raw-entry,
  source_type, and topic for the next absorb run's prioritization.
"""

from __future__ import annotations

import json
import os
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Default location relative to the project root. The ops/scheduler
# wrapper resolves the project root from ``$PSScriptRoot``; here we
# resolve from ``__file__`` and walk up to ``ask_jojo/`` then to
# ``docs/qa/misses.jsonl``.
DEFAULT_LOG_PATH = (
    Path(__file__).resolve().parents[2] / "docs" / "qa" / "misses.jsonl"
)


@dataclass
class MissEntry:
    """One miss-log row.

    Attributes:
        timestamp: ISO 8601 UTC. Defaults to ``datetime.utcnow``.
        question: the user question.
        route: ``v1`` or ``wiki``.
        reason: short explanation of why the wiki was insufficient.
            Free-text but conventionally one of: ``no-candidates``,
            ``partial-coverage``, ``contradicted``, ``stale``,
            ``out-of-scope``.
        raw_entries: list of raw-entry IDs that the session fell back
            to. Empty list if the question was unanswerable from the
            available data.
        candidate_slugs: the wiki slugs that *were* considered (for
            debugging and absorb-prioritization).
        session_id: identifies the Cowork (or future API) session that
            generated the miss.
    """

    question: str
    route: str
    reason: str
    raw_entries: list[str] = field(default_factory=list)
    candidate_slugs: list[str] = field(default_factory=list)
    session_id: str = ""
    timestamp: str = field(
        default_factory=lambda: datetime.now(tz=timezone.utc).isoformat()
    )


def _resolve_path(path: Path | str | None) -> Path:
    """Resolve the log path. Honors ``$JOJO_QA_MISSES`` for tests."""
    if path is not None:
        return Path(path)
    env = os.environ.get("JOJO_QA_MISSES")
    if env:
        return Path(env)
    return DEFAULT_LOG_PATH


def append(
    question: str,
    *,
    route: str = "wiki",
    reason: str = "no-candidates",
    raw_entries: list[str] | None = None,
    candidate_slugs: list[str] | None = None,
    session_id: str = "",
    path: Path | str | None = None,
) -> Path:
    """Append one miss entry to the log. Returns the log path."""
    log_path = _resolve_path(path)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    entry = MissEntry(
        question=question,
        route=route,
        reason=reason,
        raw_entries=list(raw_entries or []),
        candidate_slugs=list(candidate_slugs or []),
        session_id=session_id,
    )

    line = json.dumps(asdict(entry), ensure_ascii=True)
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")
    return log_path


def read_recent(
    n: int = 50, path: Path | str | None = None
) -> list[MissEntry]:
    """Return the most recent ``n`` miss entries (newest first).

    Robust to truncated/malformed lines: bad lines are skipped silently
    rather than aborting the read. The compile pipeline's verify step
    flags malformed entries separately.
    """
    log_path = _resolve_path(path)
    if not log_path.exists():
        return []

    out: list[MissEntry] = []
    try:
        lines = log_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []

    # Iterate in reverse so we can short-circuit at ``n``.
    for raw in reversed(lines):
        if not raw.strip():
            continue
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue
        try:
            out.append(MissEntry(**data))
        except TypeError:
            continue
        if len(out) >= n:
            break
    return out


def summary(
    *, window_days: int = 14, path: Path | str | None = None
) -> dict[str, Any]:
    """Aggregate the miss log over the last ``window_days``.

    Returns a dict suitable for ``GET /api/qa/misses/summary`` and for
    the next absorb run's prioritization heuristic. Keys:

    - ``total_misses``: int
    - ``by_route``: ``{"v1": n, "wiki": n}``
    - ``by_reason``: counts per reason string
    - ``top_raw_entries``: list of (entry_id, hit_count), most-hit first
    - ``top_candidate_slugs``: list of (slug, hit_count). High counts
      here mean the slug *was* a candidate but the wiki coverage on
      that slug was insufficient — strong signal for the next absorb.
    """
    log_path = _resolve_path(path)
    if not log_path.exists():
        return _empty_summary()

    now = datetime.now(tz=timezone.utc)

    by_route: Counter[str] = Counter()
    by_reason: Counter[str] = Counter()
    raw_counter: Counter[str] = Counter()
    candidate_counter: Counter[str] = Counter()
    total = 0

    for entry in read_recent(n=10_000, path=log_path):
        try:
            ts = datetime.fromisoformat(entry.timestamp)
        except ValueError:
            continue
        # Compare in UTC.
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        if (now - ts).days > window_days:
            continue
        total += 1
        by_route[entry.route] += 1
        by_reason[entry.reason] += 1
        for r in entry.raw_entries:
            raw_counter[r] += 1
        for s in entry.candidate_slugs:
            candidate_counter[s] += 1

    return {
        "total_misses": total,
        "window_days": window_days,
        "by_route": dict(by_route),
        "by_reason": dict(by_reason),
        "top_raw_entries": raw_counter.most_common(20),
        "top_candidate_slugs": candidate_counter.most_common(20),
    }


def _empty_summary() -> dict[str, Any]:
    return {
        "total_misses": 0,
        "window_days": 0,
        "by_route": {},
        "by_reason": {},
        "top_raw_entries": [],
        "top_candidate_slugs": [],
    }


# Suppress unused-import warning from defaultdict (kept for future use
# when we group by topic).
_ = defaultdict
