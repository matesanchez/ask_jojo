"""qmd activation — threshold-gated escalation to BM25/vector retrieval.

PLAN.md Section 6 Phase 4 step 5 specifies an "escalation deferred"
pattern: ``qmd`` (Karpathy's local BM25 + vector index over markdown)
is *installed* in Phase 4 but *dormant* until measured retrieval
quality crosses a threshold. This module is the threshold check.

Three triggers (any one of the three flips the activation switch):

1. **Index size**: ``_index.md`` exceeds 200 pages (the canonical
   Karpathy threshold for index-first navigation falling apart).
2. **Latency**: p95 ``/api/qa/query`` latency exceeds 8 s on the
   benchmark harness (p95 < 8 s is the Phase 4 exit criterion;
   crossing it is a forcing function).
3. **Miss rate**: more than 15 percent of recent Q&A sessions fall
   through to ``raw_fallback`` for "no candidates" or "partial
   coverage" reasons over the last 14 days.

When any trigger fires, ``should_activate`` returns ``True`` and
``activate()`` flips ``config.qmd_active`` to ``True``. The runtime
retrieval path in ``synthesize.build_retrieval_bundle`` checks
``is_active()`` and prepends a ``qmd``-shortlist step before the
``rank_candidates`` substring scoring.

The ``qmd`` package itself is listed in ``pyproject.toml`` under the
optional ``[qa]`` extra. Installing it is a one-line ``pip install
'.[qa]'``; activating it is a config flip. Today's Phase 4 ships with
``qmd`` installed and dormant.

Public API:

- ``ActivationStatus`` — dataclass with the three triggers' current
  values and the resulting ``active`` boolean.
- ``check(...)`` — read state from disk, return ``ActivationStatus``.
- ``should_activate(...)`` — convenience wrapper returning ``bool``.
- ``activate()`` / ``deactivate()`` — flip ``config.qmd_active``.
- ``is_active()`` — read ``config.qmd_active``. Single source of truth
  for the runtime retrieval path.

The actual ``qmd`` integration (BM25 prefilter -> Sonnet shortlist
-> answer) is intentionally not in this file. Adding it is a single
function in ``synthesize.build_retrieval_bundle`` once ``is_active()``
returns ``True``; see the deferred ``_qmd_prefilter`` stub below.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jojo_core import config

from . import index_loader, miss_log

# Activation threshold defaults. Override via ``config.json`` for
# experimentation (e.g. lower the index threshold during a stress test).
DEFAULT_INDEX_PAGE_THRESHOLD = 200
DEFAULT_P95_LATENCY_SEC_THRESHOLD = 8.0
DEFAULT_MISS_RATE_THRESHOLD = 0.15
DEFAULT_MISS_WINDOW_DAYS = 14


@dataclass(frozen=True)
class ActivationStatus:
    """Current state of the activation triggers and the resulting flag.

    Attributes:
        index_pages: current ``_index.md`` page count.
        index_threshold: configured threshold (default 200).
        index_trigger: ``index_pages >= index_threshold``.
        p95_latency_sec: most recent p95 latency, or None if unmeasured.
        p95_threshold: configured threshold (default 8.0).
        p95_trigger: ``p95_latency_sec`` exceeds ``p95_threshold``.
        miss_rate: rolling miss rate over the configured window, or None
            if we don't have enough data yet.
        miss_threshold: configured threshold (default 0.15).
        miss_trigger: ``miss_rate`` exceeds ``miss_threshold``.
        active: True iff any trigger fires *and* ``qmd`` is available.
        qmd_available: whether the ``qmd`` package is importable; if
            False, no trigger can flip ``active`` to True.
        manual_override: True iff the operator set
            ``config.qmd_force_active``.
        reason: short explanation of which trigger(s) fired (or which
            blocked).
    """

    index_pages: int
    index_threshold: int
    index_trigger: bool
    p95_latency_sec: float | None
    p95_threshold: float
    p95_trigger: bool
    miss_rate: float | None
    miss_threshold: float
    miss_trigger: bool
    active: bool
    qmd_available: bool
    manual_override: bool
    reason: str


def _qmd_available() -> bool:
    """Whether the ``qmd`` package is importable in the current env.

    Today this returns False unless ``pip install '.[qa]'`` has been
    run. The check is import-light (no side effects) so calling it on
    every retrieval bundle build is fine.
    """
    try:
        import qmd  # noqa: F401
        return True
    except ImportError:
        return False


def _read_p95_latency() -> float | None:
    """Read the most recent p95 latency from ``config.json``.

    The latency is written by the benchmark harness
    (``scripts/run_benchmark.py``) on every ``--full`` run. Until the
    API key lands, this stays absent and the trigger never fires.
    """
    val = config.get("qa_p95_latency_sec", None)
    if val is None:
        return None
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def _compute_miss_rate(
    window_days: int = DEFAULT_MISS_WINDOW_DAYS,
) -> float | None:
    """Compute the recent miss rate.

    Returns None if there's insufficient data (fewer than 20 sessions
    in the window — too small to extract a reliable rate).
    """
    summary = miss_log.summary(window_days=window_days)
    total_misses = summary.get("total_misses", 0)
    # The miss log records misses; we need a denominator. ``config.json``
    # stores the total session count for the window (written by the
    # benchmark harness or by qa_router.py's session counter).
    total_sessions = int(config.get("qa_session_count", 0) or 0)
    if total_sessions < 20:
        return None
    return total_misses / max(total_sessions, 1)


def check(
    *,
    wiki_root: Path | str,
    index_threshold: int = DEFAULT_INDEX_PAGE_THRESHOLD,
    p95_threshold: float = DEFAULT_P95_LATENCY_SEC_THRESHOLD,
    miss_threshold: float = DEFAULT_MISS_RATE_THRESHOLD,
    miss_window_days: int = DEFAULT_MISS_WINDOW_DAYS,
) -> ActivationStatus:
    """Read state from disk and compute activation status."""
    wiki_root = Path(wiki_root)
    entries = index_loader.load_index(wiki_root)
    index_pages = len(entries)
    index_trigger = index_pages >= index_threshold

    p95 = _read_p95_latency()
    p95_trigger = (p95 is not None) and (p95 > p95_threshold)

    miss_rate = _compute_miss_rate(window_days=miss_window_days)
    miss_trigger = (miss_rate is not None) and (miss_rate > miss_threshold)

    qmd_avail = _qmd_available()
    manual = bool(config.get("qmd_force_active", False))

    triggered = any([index_trigger, p95_trigger, miss_trigger, manual])
    active = triggered and qmd_avail

    reasons: list[str] = []
    if manual:
        reasons.append("manual override (config.qmd_force_active=True)")
    if index_trigger:
        reasons.append(
            f"index_pages={index_pages} >= threshold={index_threshold}"
        )
    if p95_trigger and p95 is not None:
        reasons.append(f"p95_latency={p95:.2f}s > threshold={p95_threshold}s")
    if miss_trigger and miss_rate is not None:
        reasons.append(
            f"miss_rate={miss_rate:.2%} > threshold={miss_threshold:.2%}"
        )
    if triggered and not qmd_avail:
        reasons.append(
            "trigger fired but qmd package not importable; install via "
            "'pip install .[qa]' to activate"
        )
    if not reasons:
        reasons.append("no activation trigger fired (qmd dormant)")

    return ActivationStatus(
        index_pages=index_pages,
        index_threshold=index_threshold,
        index_trigger=index_trigger,
        p95_latency_sec=p95,
        p95_threshold=p95_threshold,
        p95_trigger=p95_trigger,
        miss_rate=miss_rate,
        miss_threshold=miss_threshold,
        miss_trigger=miss_trigger,
        active=active,
        qmd_available=qmd_avail,
        manual_override=manual,
        reason="; ".join(reasons),
    )


def should_activate(*, wiki_root: Path | str) -> bool:
    """Convenience: returns ``check(...).active``."""
    return check(wiki_root=wiki_root).active


# -- runtime activation flag ---------------------------------------------


def is_active() -> bool:
    """Single source of truth for the runtime retrieval path.

    Reads ``config.qmd_active`` (set by ``activate()``). The runtime
    path in ``synthesize.build_retrieval_bundle`` consults this on each
    call; flipping the bit is enough to enable qmd retrieval in
    production without restarting the backend.
    """
    return bool(config.get("qmd_active", False))


def activate() -> None:
    """Flip ``config.qmd_active = True``. Idempotent."""
    config.set("qmd_active", True)


def deactivate() -> None:
    """Flip ``config.qmd_active = False``. Used by tests and rollback."""
    config.set("qmd_active", False)


# -- deferred qmd integration --------------------------------------------


def qmd_prefilter(
    question: str,
    wiki_root: Path,
    *,
    k_shortlist: int = 30,
) -> list[str]:
    """Run the qmd BM25/vector prefilter and return the top-k slugs.

    Stub today. The implementation when this lights up will be roughly:

        index = qmd.load_index(wiki_root / ".qmd")
        hits = index.search(question, k=k_shortlist)
        return [hit.slug for hit in hits]

    The returned slugs feed ``index_loader.rank_candidates`` as the
    candidate pool, replacing the full-index scan for retrieval. The
    rest of the pipeline (synthesis prompt, citations, write-back) is
    unchanged.

    If qmd is not active, callers should fall back to
    ``index_loader.rank_candidates`` over the full index.
    """
    _ = (question, wiki_root, k_shortlist)
    if not is_active():
        return []
    # Stub return: empty list signals "qmd activated but not yet
    # implemented", the runtime path then falls back to the full-index
    # path.
    return []


# -- helper for the Ops tab ----------------------------------------------


def status_summary(*, wiki_root: Path | str) -> dict[str, Any]:
    """Render-friendly summary for /api/ops/status and /api/qa/qmd-status."""
    s = check(wiki_root=wiki_root)
    return {
        "active": s.active,
        "qmd_available": s.qmd_available,
        "manual_override": s.manual_override,
        "triggers": {
            "index": {
                "value": s.index_pages,
                "threshold": s.index_threshold,
                "fired": s.index_trigger,
            },
            "latency": {
                "value": s.p95_latency_sec,
                "threshold": s.p95_threshold,
                "fired": s.p95_trigger,
            },
            "miss_rate": {
                "value": s.miss_rate,
                "threshold": s.miss_threshold,
                "fired": s.miss_trigger,
            },
        },
        "reason": s.reason,
    }
