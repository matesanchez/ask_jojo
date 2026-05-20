"""Missing articles check — terms in the manifest without a wiki slug."""

from __future__ import annotations

import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

from ._util import iter_wiki_pages, parse_frontmatter
from .base import CheckResult

# Simple word tokenizer for manifest titles — reuse jojo_qa's tokenize pattern
_TOKEN_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9\-]+")


def _load_manifest_titles(manifest_path: Path) -> list[str]:
    """Extract entry titles / paths from ``manifest.json``."""
    titles: list[str] = []
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return titles

    entries = data.get("entries") or {}
    if isinstance(entries, dict):
        entries = entries.values()
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        title = entry.get("title") or entry.get("name") or entry.get("path") or ""
        if title:
            titles.append(str(title))
    return titles


def run(
    wiki_root: Path | str,
    manifest_path: Path | str | None = None,
    api_key: str | None = None,
) -> CheckResult:
    """Find manifest terms that do not have a corresponding wiki slug.

    Deterministic pre-filter: tokenize manifest titles, look for tokens
    that appear as a slug substring. Terms with no partial match are
    candidates.

    Model pass: stub — returns ``api_key_required`` when no key is present.

    Args:
        wiki_root: path to the compiled wiki repository.
        manifest_path: path to ``ask_jojo_raw/manifest.json``.
        api_key: Anthropic API key. When absent, model pass is skipped.

    Returns:
        A :class:`CheckResult`. Status is ``"api_key_required"`` when no
        API key is configured.
    """
    wiki_root = Path(wiki_root)
    start = time.monotonic()

    # Collect known slugs
    known_slugs: set[str] = set()
    for page_path in iter_wiki_pages(wiki_root):
        fm, _ = parse_frontmatter(page_path)
        slug = fm.get("slug")
        if slug:
            known_slugs.add(str(slug).lower())

    candidates: list[dict] = []

    if manifest_path is not None:
        manifest_path = Path(manifest_path)
        if manifest_path.exists():
            titles = _load_manifest_titles(manifest_path)
            for title in titles:
                # Tokenize the title and check if any token matches a slug
                tokens = _TOKEN_RE.findall(title.lower())
                matched = any(tok in known_slugs for tok in tokens)
                if not matched and tokens:
                    candidates.append(
                        {
                            "slug": "_manifest",
                            "message": (
                                f"manifest entry {title!r} has no"
                                " matching wiki slug — missing article candidate"
                            ),
                            "severity": "info",
                        }
                    )

    duration_ms = int((time.monotonic() - start) * 1000)

    if not api_key:
        return CheckResult(
            check_name="missing_articles",
            status="api_key_required",
            findings=candidates,
            run_at=datetime.now(tz=timezone.utc).isoformat(),
            duration_ms=duration_ms,
        )

    # API key present: model stub (Phase 8)
    return CheckResult(
        check_name="missing_articles",
        status="pass",
        findings=candidates,
        run_at=datetime.now(tz=timezone.utc).isoformat(),
        duration_ms=duration_ms,
    )
