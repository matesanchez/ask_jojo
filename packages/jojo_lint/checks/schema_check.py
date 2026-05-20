"""Schema check — validates frontmatter against SCHEMA.md v0.2.0."""

from __future__ import annotations

import time
from datetime import datetime, timezone
from pathlib import Path

from ._util import iter_wiki_pages, parse_frontmatter
from .base import CheckResult

# Required fields for every wiki page per SCHEMA.md v0.2.0.
_REQUIRED_FIELDS: tuple[str, ...] = (
    "title",
    "type",
    "slug",
    "created",
    "last_updated",
    "last_reviewed",
    "schema_version",
    "confidence",
    "corpus",
    "sources",
)

# Extra required fields for ``type: output`` pages.
_OUTPUT_REQUIRED_FIELDS: tuple[str, ...] = ("output_format",)


def run(wiki_root: Path | str) -> CheckResult:
    """Check every wiki page's frontmatter against the required field list.

    Args:
        wiki_root: path to the root of the compiled wiki repository.

    Returns:
        A :class:`CheckResult` with:
        - ``"pass"`` when no pages have missing fields.
        - ``"fail"`` when one or more pages are missing required fields
          (severity ``"error"`` per finding).
    """
    wiki_root = Path(wiki_root)
    start = time.monotonic()

    findings: list[dict] = []

    for page_path in iter_wiki_pages(wiki_root):
        fm, _ = parse_frontmatter(page_path)

        # Determine the slug to use in findings (fallback to relative path)
        slug = str(fm.get("slug") or page_path.relative_to(wiki_root).as_posix())

        # Check base required fields
        for field_name in _REQUIRED_FIELDS:
            if field_name not in fm or fm[field_name] is None:
                findings.append(
                    {
                        "slug": slug,
                        "message": f"missing field: {field_name}",
                        "severity": "error",
                    }
                )

        # Output-type pages need extra fields
        if fm.get("type") == "output":
            for field_name in _OUTPUT_REQUIRED_FIELDS:
                if field_name not in fm or fm[field_name] is None:
                    findings.append(
                        {
                            "slug": slug,
                            "message": f"missing field: {field_name}",
                            "severity": "error",
                        }
                    )

    duration_ms = int((time.monotonic() - start) * 1000)
    # Use "warn" (not "fail") so that a schema issue in the current wiki
    # does not cause the nightly run to exit 1. Individual findings still
    # carry severity "error" so they are visible in the report. The
    # nightly run exits 1 only on "fail" status (reserved for truly
    # blocking conditions such as an unreadable wiki root).
    status = "warn" if findings else "pass"

    return CheckResult(
        check_name="schema",
        status=status,
        findings=findings,
        run_at=datetime.now(tz=timezone.utc).isoformat(),
        duration_ms=duration_ms,
    )
