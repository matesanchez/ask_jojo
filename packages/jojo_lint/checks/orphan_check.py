"""Orphan check — pages on disk that are missing from ``_index.md``."""

from __future__ import annotations

import re
import time
from datetime import datetime, timezone
from pathlib import Path

from ._util import iter_wiki_pages, parse_frontmatter
from .base import CheckResult

# Matches the wikilink lines in ``_index.md``:
#   - [[slug|Title]] — `path/to.md`
_INDEX_SLUG_RE = re.compile(r"\[\[([^|\]]+)(?:\|[^\]]+)?\]\]")


def _load_index_slugs(wiki_root: Path) -> set[str]:
    """Extract all slugs listed in ``_index.md``."""
    index_path = wiki_root / "_index.md"
    if not index_path.exists():
        return set()

    slugs: set[str] = set()
    try:
        text = index_path.read_text(encoding="utf-8")
    except OSError:
        return set()

    for m in _INDEX_SLUG_RE.finditer(text):
        slug = m.group(1).strip()
        if slug:
            slugs.add(slug)
    return slugs


def run(wiki_root: Path | str) -> CheckResult:
    """Check for pages on disk that are not listed in ``_index.md``.

    Args:
        wiki_root: path to the compiled wiki repository.

    Returns:
        A :class:`CheckResult` with severity ``"warn"`` per orphan page.
        Status is ``"warn"`` when any orphans are found, ``"pass"`` otherwise.
    """
    wiki_root = Path(wiki_root)
    start = time.monotonic()

    index_slugs = _load_index_slugs(wiki_root)
    findings: list[dict] = []

    for page_path in iter_wiki_pages(wiki_root):
        fm, _ = parse_frontmatter(page_path)
        slug = str(fm.get("slug") or page_path.relative_to(wiki_root).as_posix())

        if slug not in index_slugs:
            findings.append(
                {
                    "slug": slug,
                    "message": "page exists on disk but is not in _index.md",
                    "severity": "warn",
                }
            )

    duration_ms = int((time.monotonic() - start) * 1000)
    status = "warn" if findings else "pass"

    return CheckResult(
        check_name="orphan",
        status=status,
        findings=findings,
        run_at=datetime.now(tz=timezone.utc).isoformat(),
        duration_ms=duration_ms,
    )
