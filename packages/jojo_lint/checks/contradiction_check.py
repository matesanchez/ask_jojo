"""Contradiction check — LLM-assisted (stub; deterministic pre-filter runs always)."""

from __future__ import annotations

import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from ._util import extract_wikilinks, iter_wiki_pages, parse_frontmatter
from .base import CheckResult


def _find_shared_link_pairs(wiki_root: Path) -> list[dict]:
    """Deterministic pre-filter: find page pairs that share wikilink targets.

    Two pages that both link to the same third page are candidates for
    contradiction checking (they describe overlapping topic space).
    Returns a list of finding dicts with ``severity: "info"``.
    """
    # Map: target_slug -> list of source slugs that link to it
    link_map: dict[str, list[str]] = defaultdict(list)

    for page_path in iter_wiki_pages(wiki_root):
        fm, body = parse_frontmatter(page_path)
        source_slug = str(fm.get("slug") or page_path.relative_to(wiki_root).as_posix())
        for target in set(extract_wikilinks(body)):
            link_map[target].append(source_slug)

    candidates: list[dict] = []
    for target_slug, sources in link_map.items():
        if len(sources) >= 2:
            for i in range(len(sources)):
                for j in range(i + 1, len(sources)):
                    candidates.append(
                        {
                            "slug": sources[i],
                            "message": (
                                f"shares wikilink target [[{target_slug}]]"
                                f" with [[{sources[j]}]] -- contradiction candidate"
                            ),
                            "severity": "info",
                        }
                    )
    return candidates


def run(wiki_root: Path | str, api_key: str | None = None) -> CheckResult:
    """Check for potential contradictions between pages.

    Deterministic pre-filter: always runs and returns shared-link pairs
    as ``severity: "info"`` candidates.

    Model pass: returns ``api_key_required`` when no API key is present.
    Model check is not yet implemented (Phase 8 stub).

    Args:
        wiki_root: path to the compiled wiki repository.
        api_key: Anthropic API key. When absent, model pass is skipped.

    Returns:
        A :class:`CheckResult`. Status is ``"api_key_required"`` when no
        API key is configured; ``"pass"`` (with candidate findings) when
        the pre-filter runs without a key.
    """
    wiki_root = Path(wiki_root)
    start = time.monotonic()

    candidates = _find_shared_link_pairs(wiki_root)

    duration_ms = int((time.monotonic() - start) * 1000)

    if not api_key:
        return CheckResult(
            check_name="contradiction",
            status="api_key_required",
            findings=candidates,
            run_at=datetime.now(tz=timezone.utc).isoformat(),
            duration_ms=duration_ms,
        )

    # API key present: model stub (Phase 8)
    return CheckResult(
        check_name="contradiction",
        status="pass",
        findings=candidates,
        run_at=datetime.now(tz=timezone.utc).isoformat(),
        duration_ms=duration_ms,
    )
