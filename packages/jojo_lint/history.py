"""History — append-only JSONL run log and metrics series."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .checks.base import CheckResult

# Default history directory — overridable via ``JOJO_LINT_HISTORY_DIR`` env var.
# Resolved in cli.py; callers pass it explicitly to every function here so the
# module has no side effects at import time.


def _default_history_dir() -> Path:
    """Return the default history directory path (not created yet)."""
    import os

    env_val = os.environ.get("JOJO_LINT_HISTORY_DIR")
    if env_val:
        return Path(env_val)
    return Path.home() / "AppData" / "Local" / "JojoBot" / "lint-history"


def append_run(
    scope: str,
    results: list[CheckResult],
    history_dir: Path | str | None = None,
) -> Path:
    """Append one run record to ``history_dir/lint-history.jsonl``.

    Each record is a single JSON object on one line::

        {
          "scope": "nightly",
          "run_at": "2026-05-19T02:00:00+00:00",
          "results": [...]   // list of CheckResult.to_dict()
        }

    Args:
        scope: ``"nightly"`` or ``"weekly"``.
        results: list of :class:`CheckResult` from a run.
        history_dir: directory to write ``lint-history.jsonl`` into.
            Defaults to the platform default if ``None``.

    Returns:
        Path to the ``lint-history.jsonl`` file.
    """
    if history_dir is None:
        history_dir = _default_history_dir()
    history_dir = Path(history_dir)
    history_dir.mkdir(parents=True, exist_ok=True)

    log_path = history_dir / "lint-history.jsonl"
    record: dict[str, Any] = {
        "scope": scope,
        "run_at": datetime.now(tz=timezone.utc).isoformat(),
        "results": [r.to_dict() for r in results],
    }
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record) + "\n")
    return log_path


def load_runs(
    scope: str | None = None,
    days: int = 30,
    history_dir: Path | str | None = None,
) -> list[dict[str, Any]]:
    """Read run records from ``lint-history.jsonl``.

    Args:
        scope: filter to ``"nightly"`` or ``"weekly"``. ``None`` returns all.
        days: only return runs from the last ``days`` days.
        history_dir: directory containing ``lint-history.jsonl``.

    Returns:
        List of run dicts, most-recent first. Empty list if no file exists.
    """
    if history_dir is None:
        history_dir = _default_history_dir()
    log_path = Path(history_dir) / "lint-history.jsonl"
    if not log_path.exists():
        return []

    cutoff = datetime.now(tz=timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    # Move back ``days`` days
    from datetime import timedelta

    cutoff = cutoff - timedelta(days=days)

    runs: list[dict[str, Any]] = []
    try:
        text = log_path.read_text(encoding="utf-8")
    except OSError:
        return []

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue

        if scope is not None and record.get("scope") != scope:
            continue

        run_at_str = record.get("run_at", "")
        try:
            run_at = datetime.fromisoformat(run_at_str)
            if run_at.tzinfo is None:
                run_at = run_at.replace(tzinfo=timezone.utc)
        except (ValueError, TypeError):
            run_at = datetime.now(tz=timezone.utc)

        if run_at >= cutoff:
            runs.append(record)

    # Most-recent first
    runs.sort(key=lambda r: r.get("run_at", ""), reverse=True)
    return runs


# Confidence string -> numeric score mapping
_CONFIDENCE_SCORES: dict[str, float] = {
    "critical": 0.0,
    "low": 0.25,
    "medium": 0.75,
    "high": 1.0,
}


def metrics_series(
    days: int = 30,
    history_dir: Path | str | None = None,
) -> list[dict[str, Any]]:
    """Return a 30-day rolling metrics series from run history.

    Each entry in the returned list covers one nightly run and includes:
    - ``run_at``: ISO datetime of the run.
    - ``orphan_count``: number of orphan findings.
    - ``avg_confidence_score``: mean confidence score across all pages that
      appeared as ``stub`` findings (proxy for overall wiki health).
    - ``stale_count``: number of stub/staleness findings.
    - ``wikilink_error_count``: number of broken-wikilink findings.

    Args:
        days: look-back window in days.
        history_dir: directory containing ``lint-history.jsonl``.

    Returns:
        List of metric dicts, oldest first.
    """
    runs = load_runs(scope="nightly", days=days, history_dir=history_dir)

    series: list[dict[str, Any]] = []
    for run in reversed(runs):  # oldest first
        metrics: dict[str, Any] = {
            "run_at": run.get("run_at"),
            "orphan_count": 0,
            "avg_confidence_score": 1.0,
            "stale_count": 0,
            "wikilink_error_count": 0,
        }

        confidence_scores: list[float] = []

        for result in run.get("results", []):
            check_name = result.get("check_name", "")
            findings = result.get("findings", [])

            if check_name == "orphan":
                metrics["orphan_count"] = len(findings)
            elif check_name == "stub":
                metrics["stale_count"] = len(findings)
                # Extract confidence from message if present
                for f in findings:
                    msg = f.get("message", "").lower()
                    for level, score in _CONFIDENCE_SCORES.items():
                        if level in msg:
                            confidence_scores.append(score)
                            break
                    else:
                        confidence_scores.append(_CONFIDENCE_SCORES["low"])
            elif check_name == "wikilink":
                metrics["wikilink_error_count"] = sum(
                    1 for f in findings if f.get("severity") == "error"
                )

        if confidence_scores:
            metrics["avg_confidence_score"] = sum(confidence_scores) / len(confidence_scores)

        series.append(metrics)

    return series
