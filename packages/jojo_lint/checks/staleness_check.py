"""Staleness check — pages not reviewed in over 90 days."""

from __future__ import annotations

import time
from datetime import date, datetime, timezone
from pathlib import Path

from ._util import iter_wiki_pages, parse_frontmatter
from .base import CheckResult

_STALE_REVIEWED_DAYS = 90


def run(
    wiki_root: Path | str,
    manifest_path: Path | str | None = None,
    api_key: str | None = None,
) -> CheckResult:
    """Find pages whose ``last_reviewed`` date is more than 90 days old.

    Deterministic pre-filter: always finds stale-reviewed pages and
    returns them as ``severity: "warn"`` candidates.

    Model pass: stub — returns ``api_key_required`` when no key is present.
    Model check is not yet implemented (Phase 8 stub).

    Args:
        wiki_root: path to the compiled wiki repository.
        manifest_path: unused today; reserved for the model pass.
        api_key: Anthropic API key. When absent, model pass is skipped.

    Returns:
        A :class:`CheckResult`. Status is ``"api_key_required"`` when no
        API key is configured.
    """
    wiki_root = Path(wiki_root)
    start = time.monotonic()
    today = date.today()

    candidates: list[dict] = []

    for page_path in iter_wiki_pages(wiki_root):
        fm, _ = parse_frontmatter(page_path)

        last_reviewed_raw = fm.get("last_reviewed")
        if not last_reviewed_raw:
            continue

        try:
            if isinstance(last_reviewed_raw, date):
                last_reviewed = last_reviewed_raw
            else:
                last_reviewed = date.fromisoformat(str(last_reviewed_raw))
        except (ValueError, TypeError):
            continue

        age_days = (today - last_reviewed).days
        if age_days > _STALE_REVIEWED_DAYS:
            slug = str(fm.get("slug") or page_path.relative_to(wiki_root).as_posix())
            candidates.append(
                {
                    "slug": slug,
                    "message": f"last_reviewed {age_days} days ago — staleness candidate",
                    "severity": "warn",
                }
            )

    duration_ms = int((time.monotonic() - start) * 1000)

    if not api_key:
        return CheckResult(
            check_name="staleness",
            status="api_key_required",
            findings=candidates,
            run_at=datetime.now(tz=timezone.utc).isoformat(),
            duration_ms=duration_ms,
        )

    # API key present: model stub (Phase 8)
    return CheckResult(
        check_name="staleness",
        status="pass",
        findings=candidates,
        run_at=datetime.now(tz=timezone.utc).isoformat(),
        duration_ms=duration_ms,
    )
