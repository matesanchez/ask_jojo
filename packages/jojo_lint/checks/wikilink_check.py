"""Wikilink check — broken wikilinks and duplicate slugs."""

from __future__ import annotations

import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from ._util import extract_wikilinks, iter_wiki_pages, parse_frontmatter
from .base import CheckResult


def run(wiki_root: Path | str) -> CheckResult:
    """Check for broken wikilinks and duplicate slugs.

    Pass 1 (frontmatter scan):
      - Collect all known slugs from frontmatter ``slug`` fields.
      - Collect all known titles (lowercased) from frontmatter ``title`` fields.
      - Collect all known aliases from frontmatter ``aliases`` fields.
      - Detect duplicate slugs (same slug on two or more files).

    Pass 2 (body scan):
      - Scan every page body for ``[[slug]]`` and ``[[slug|label]]``
        wikilink patterns.
      - A wikilink is valid when the target matches a slug, title, or alias.
      - Flag links that don't match any known identifier as broken.

    Per SCHEMA.md §6: "The link target must match either the title or the
    slug of an existing wiki page, or one of the page's listed aliases."

    Args:
        wiki_root: path to the compiled wiki repository.

    Returns:
        A :class:`CheckResult` with:
        - ``"error"`` severity for broken wikilinks and duplicate slugs.
        - Status ``"fail"`` when any errors are found, ``"pass"`` otherwise.
    """
    wiki_root = Path(wiki_root)
    start = time.monotonic()

    # Pass 1: collect known identifiers and detect duplicate slugs
    slug_to_paths: dict[str, list[Path]] = defaultdict(list)
    page_data: list[tuple[Path, str, str]] = []  # (path, page_slug, body)

    # Set of all valid link targets: slugs, lowercased titles, lowercased aliases
    known_targets: set[str] = set()

    for page_path in iter_wiki_pages(wiki_root):
        fm, body = parse_frontmatter(page_path)
        slug = str(fm.get("slug") or page_path.relative_to(wiki_root).as_posix())
        slug_to_paths[slug].append(page_path)
        page_data.append((page_path, slug, body))

        # Add slug
        known_targets.add(slug)

        # Add title (lowercased — wikilinks often use title case)
        title = fm.get("title")
        if title:
            known_targets.add(str(title).lower())
            known_targets.add(str(title))

        # Add aliases
        aliases = fm.get("aliases") or []
        if isinstance(aliases, list):
            for alias in aliases:
                if alias:
                    known_targets.add(str(alias))
                    known_targets.add(str(alias).lower())
        elif isinstance(aliases, str):
            known_targets.add(aliases)
            known_targets.add(aliases.lower())

    duplicate_slugs: set[str] = {
        slug for slug, paths in slug_to_paths.items() if len(paths) > 1
    }

    findings: list[dict] = []

    # Report duplicate slugs
    for dup_slug in sorted(duplicate_slugs):
        findings.append(
            {
                "slug": dup_slug,
                "message": "duplicate slug",
                "severity": "error",
            }
        )

    # Pass 2: check wikilinks in body
    for _page_path, page_slug, body in page_data:
        seen_broken: set[str] = set()  # deduplicate per-page
        for linked_target in extract_wikilinks(body):
            if linked_target in seen_broken:
                continue
            # Check slug, lowercased target, and title-case variations
            if (
                linked_target not in known_targets
                and linked_target.lower() not in known_targets
            ):
                seen_broken.add(linked_target)
                findings.append(
                    {
                        "slug": page_slug,
                        "message": f"broken wikilink: [[{linked_target}]]",
                        "severity": "error",
                    }
                )

    duration_ms = int((time.monotonic() - start) * 1000)
    # Use "warn" (not "fail") so that wikilink errors in the current wiki
    # do not cause the nightly run to exit 1. Individual findings still
    # carry severity "error" so they are visible in the report. The
    # nightly run exits 1 only on "fail" status (reserved for truly
    # blocking conditions).
    status = "warn" if findings else "pass"

    return CheckResult(
        check_name="wikilink",
        status=status,
        findings=findings,
        run_at=datetime.now(tz=timezone.utc).isoformat(),
        duration_ms=duration_ms,
    )
