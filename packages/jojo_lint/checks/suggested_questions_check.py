"""Suggested questions check — LLM-generated question ideas (stub)."""

from __future__ import annotations

import time
from datetime import datetime, timezone
from pathlib import Path

from .base import CheckResult


def run(wiki_root: Path | str, api_key: str | None = None) -> CheckResult:
    """Generate suggested questions the wiki should be able to answer.

    Model pass: stub — returns ``api_key_required`` when no key is present.
    Model check is not yet implemented (Phase 8 stub).

    Args:
        wiki_root: path to the compiled wiki repository.
        api_key: Anthropic API key. When absent, returns ``api_key_required``.

    Returns:
        A :class:`CheckResult` with status ``"api_key_required"`` when no
        API key is configured; otherwise a stub ``"pass"`` with no findings.
    """
    _ = wiki_root  # unused until Phase 8
    start = time.monotonic()
    duration_ms = int((time.monotonic() - start) * 1000)

    if not api_key:
        return CheckResult(
            check_name="suggested_questions",
            status="api_key_required",
            findings=[],
            run_at=datetime.now(tz=timezone.utc).isoformat(),
            duration_ms=duration_ms,
        )

    # API key present: model stub (Phase 8)
    return CheckResult(
        check_name="suggested_questions",
        status="pass",
        findings=[],
        run_at=datetime.now(tz=timezone.utc).isoformat(),
        duration_ms=duration_ms,
    )
