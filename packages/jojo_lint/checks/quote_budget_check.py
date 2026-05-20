"""Quote budget check — blockquote fraction of wiki content."""

from __future__ import annotations

import time
from datetime import datetime, timezone
from pathlib import Path

from ._util import iter_wiki_pages, parse_frontmatter
from .base import CheckResult

_PER_PAGE_THRESHOLD = 0.30  # flag individual pages over this blockquote fraction


def _count_lines(body: str) -> tuple[int, int]:
    """Return ``(total_lines, blockquote_lines)`` for a page body.

    Only counts non-empty lines (ignores blank lines) to avoid inflating
    denominator with whitespace.
    """
    lines = body.splitlines()
    non_empty = [ln for ln in lines if ln.strip()]
    blockquotes = [ln for ln in non_empty if ln.lstrip().startswith(">")]
    return len(non_empty), len(blockquotes)


def run(
    wiki_root: Path | str,
    max_quoted_fraction: float = 0.20,
) -> CheckResult:
    """Check blockquote density across the wiki and per individual page.

    Global check:
      If the fraction of blockquote lines across all pages exceeds
      ``max_quoted_fraction`` (default 0.20), one ``_global`` finding is
      emitted.

    Per-page check:
      Pages where blockquote lines exceed 30 % of their non-frontmatter
      non-empty body lines are also flagged.

    Args:
        wiki_root: path to the compiled wiki repository.
        max_quoted_fraction: global blockquote fraction policy threshold.

    Returns:
        A :class:`CheckResult` with severity ``"warn"`` for any violations.
        Status is ``"warn"`` when violations exist, ``"pass"`` otherwise.
    """
    wiki_root = Path(wiki_root)
    start = time.monotonic()

    findings: list[dict] = []
    total_lines_global = 0
    total_blockquotes_global = 0

    per_page: list[tuple[str, int, int]] = []

    for page_path in iter_wiki_pages(wiki_root):
        fm, body = parse_frontmatter(page_path)
        slug = str(fm.get("slug") or page_path.relative_to(wiki_root).as_posix())

        total_lines, blockquote_lines = _count_lines(body)
        per_page.append((slug, total_lines, blockquote_lines))
        total_lines_global += total_lines
        total_blockquotes_global += blockquote_lines

        # Per-page threshold
        if total_lines > 0:
            page_fraction = blockquote_lines / total_lines
            if page_fraction > _PER_PAGE_THRESHOLD:
                pct = round(page_fraction * 100, 1)
                findings.append(
                    {
                        "slug": slug,
                        "message": (
                            f"blockquote fraction {pct}% exceeds"
                            f" {int(_PER_PAGE_THRESHOLD * 100)}% per-page policy"
                        ),
                        "severity": "warn",
                    }
                )

    # Global threshold
    if total_lines_global > 0:
        global_fraction = total_blockquotes_global / total_lines_global
        if global_fraction > max_quoted_fraction:
            pct = round(global_fraction * 100, 1)
            findings.append(
                {
                    "slug": "_global",
                    "message": (
                        f"quoted fraction {pct}% exceeds"
                        f" {int(max_quoted_fraction * 100)}% policy"
                    ),
                    "severity": "warn",
                }
            )

    duration_ms = int((time.monotonic() - start) * 1000)
    status = "warn" if findings else "pass"

    return CheckResult(
        check_name="quote_budget",
        status=status,
        findings=findings,
        run_at=datetime.now(tz=timezone.utc).isoformat(),
        duration_ms=duration_ms,
    )
