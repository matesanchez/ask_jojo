"""Stub check — low-confidence pages that have not been updated recently."""

from __future__ import annotations

import time
from datetime import date, datetime, timezone
from pathlib import Path

from ._util import iter_wiki_pages, parse_frontmatter
from .base import CheckResult


def run(wiki_root: Path | str, stale_days: int = 60) -> CheckResult:
    """Find ``confidence: low`` pages whose ``last_updated`` is stale.

    A page is stale when its ``last_updated`` date is more than
    ``stale_days`` days before today's date.

    Args:
        wiki_root: path to the compiled wiki repository.
        stale_days: age threshold in days (default 60).

    Returns:
        A :class:`CheckResult` with severity ``"warn"`` per stale page.
        Status is ``"warn"`` when any stale pages are found, ``"pass"``
        otherwise.
    """
    wiki_root = Path(wiki_root)
    start = time.monotonic()
    today = date.today()

    findings: list[dict] = []

    for page_path in iter_wiki_pages(wiki_root):
        fm, _ = parse_frontmatter(page_path)

        if str(fm.get("confidence", "")).lower() != "low":
            continue

        last_updated_raw = fm.get("last_updated")
        if not last_updated_raw:
            continue

        try:
            # last_updated may be a date object (PyYAML auto-converts) or a string
            if isinstance(last_updated_raw, date):
                last_updated = last_updated_raw
            else:
                last_updated = date.fromisoformat(str(last_updated_raw))
        except (ValueError, TypeError):
            continue

        age_days = (today - last_updated).days
        if age_days > stale_days:
            slug = str(fm.get("slug") or page_path.relative_to(wiki_root).as_posix())
            findings.append(
                {
                    "slug": slug,
                    "message": (
                        f"confidence:low, not updated in {age_days} days"
                    ),
                    "severity": "warn",
                }
            )

    duration_ms = int((time.monotonic() - start) * 1000)
    status = "warn" if findings else "pass"

    return CheckResult(
        check_name="stub",
        status=status,
        findings=findings,
        run_at=datetime.now(tz=timezone.utc).isoformat(),
        duration_ms=duration_ms,
    )
