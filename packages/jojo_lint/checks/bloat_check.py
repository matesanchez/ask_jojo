"""Bloat check — pages exceeding line or byte thresholds."""

from __future__ import annotations

import time
from datetime import datetime, timezone
from pathlib import Path

from ._util import iter_wiki_pages, parse_frontmatter
from .base import CheckResult


def run(
    wiki_root: Path | str,
    max_lines: int = 1000,
    max_bytes: int = 51200,
) -> CheckResult:
    """Find pages that exceed the line or byte size thresholds.

    Args:
        wiki_root: path to the compiled wiki repository.
        max_lines: maximum allowed line count (default 1000).
        max_bytes: maximum allowed file size in bytes (default 50 KB).

    Returns:
        A :class:`CheckResult` with severity ``"warn"`` per oversized page.
        Status is ``"warn"`` when any oversized pages are found, ``"pass"``
        otherwise.
    """
    wiki_root = Path(wiki_root)
    start = time.monotonic()

    findings: list[dict] = []

    for page_path in iter_wiki_pages(wiki_root):
        fm, _ = parse_frontmatter(page_path)
        slug = str(fm.get("slug") or page_path.relative_to(wiki_root).as_posix())

        try:
            content = page_path.read_text(encoding="utf-8")
        except OSError:
            continue

        line_count = content.count("\n") + 1
        byte_count = len(content.encode("utf-8"))

        if line_count > max_lines or byte_count > max_bytes:
            findings.append(
                {
                    "slug": slug,
                    "message": (
                        f"{line_count} lines / {byte_count} bytes"
                        " -- exceeds threshold"
                    ),
                    "severity": "warn",
                }
            )

    duration_ms = int((time.monotonic() - start) * 1000)
    status = "warn" if findings else "pass"

    return CheckResult(
        check_name="bloat",
        status=status,
        findings=findings,
        run_at=datetime.now(tz=timezone.utc).isoformat(),
        duration_ms=duration_ms,
    )
