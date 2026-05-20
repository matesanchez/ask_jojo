"""Shared utilities for wiki enumeration and frontmatter parsing."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

# Files to exclude from wiki page enumeration at the wiki root level.
_ROOT_EXCLUDES: frozenset[str] = frozenset(
    {"_index.md", "_backlinks.json", "SCHEMA.md", "README.md", "_log.md"}
)


def iter_wiki_pages(wiki_root: Path) -> list[Path]:
    """Return all ``.md`` page files under ``wiki_root``, excluding meta-files.

    Excludes:
    - Files under hidden directories (any path component starting with ``.``)
    - Files whose names start with ``_``
    - ``README.md`` (any directory)
    - ``SCHEMA.md`` (any directory)
    - Non-``.md`` files (so PNG/PPTX/PDF assets are skipped)

    Returns a sorted list for deterministic ordering.
    """
    results: list[Path] = []
    for p in wiki_root.rglob("*.md"):
        # Skip hidden directories (e.g. .git, .graphify, .github)
        if any(part.startswith(".") for part in p.parts):
            continue
        # Skip files starting with underscore (meta-files like _index.md)
        if p.name.startswith("_"):
            continue
        # Skip README.md and SCHEMA.md anywhere in the tree
        if p.name in ("README.md", "SCHEMA.md"):
            continue
        results.append(p)
    return sorted(results)


def parse_frontmatter(path: Path) -> tuple[dict[str, Any], str]:
    """Parse YAML frontmatter from a wiki page.

    Returns ``(fm_dict, body)`` where:
    - ``fm_dict`` is the parsed YAML (empty dict on parse failure or absent).
    - ``body`` is the text after the closing ``---``.

    Never raises; returns ``({}, full_text)`` on any parse error.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return {}, ""

    if not text.startswith("---"):
        return {}, text

    end = text.find("\n---", 3)
    if end == -1:
        return {}, text

    fm_text = text[4:end]
    body = text[end + 4:]

    try:
        fm = yaml.safe_load(fm_text)
    except yaml.YAMLError:
        fm = {}

    if not isinstance(fm, dict):
        fm = {}

    return fm, body


# Wikilink pattern: [[slug]] or [[slug|label]] or [[slug#anchor]] or [[slug#anchor|label]]
_WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")


def extract_wikilinks(body: str) -> list[str]:
    """Extract the slug portion of all ``[[...]]`` wikilinks in ``body``.

    Handles:
    - ``[[slug]]``
    - ``[[slug|label]]``
    - ``[[slug#anchor|label]]``
    - ``[[slug#anchor]]``

    Returns the slug part only (before ``|`` and before ``#``), stripped.
    Skips empty slugs.
    """
    slugs: list[str] = []
    for m in _WIKILINK_RE.finditer(body):
        inner = m.group(1)
        # Split on pipe first to get the target (before the display label)
        target = inner.split("|", 1)[0]
        # Split on # to drop anchors
        slug = target.split("#", 1)[0].strip()
        if slug:
            slugs.append(slug)
    return slugs
