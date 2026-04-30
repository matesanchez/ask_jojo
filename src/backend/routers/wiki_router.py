"""Wiki API router — backs the Wiki tab in the JoJo Bot frontend.

Endpoints serve the compiled `ask_jojo_wiki/` directory.  All operations
are read-only file access; no writes land until Phase 3 final pass.

Endpoint map:

- ``GET  /api/wiki/tree``         — full directory tree grouped by type dir.
- ``GET  /api/wiki/page``         — frontmatter + body of one page (?path=).
- ``GET  /api/wiki/backlinks``    — inbound link list (?slug=).
- ``GET  /api/wiki/search``       — substring search (?q=, min 2 chars).
- ``GET  /api/wiki/stats``        — page count, last git commit, schema ver.
- ``POST /api/wiki/edit``         — propose a Claude-written edit (feature-flagged).
- ``PATCH /api/wiki/page``        — write-back stub (Phase 3 final pass).
"""

from __future__ import annotations

import difflib
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from jojo_connectors_common import split_frontmatter
from jojo_core import config

router = APIRouter()

# -------------------------------------------------------------------- config

_SKIP_NAMES: frozenset[str] = frozenset(
    {"_index.md", "_needs_review.md", "README.md", "SCHEMA.md"}
)

_SCHEMA_VER_RE = re.compile(r"\*\*Schema version:\*\*\s*([\w.]+)", re.IGNORECASE)


def _wiki_root() -> Path:
    """Resolve the wiki root per-request so tests can relocate it.

    Checks ``JOJO_WIKI_ROOT`` env var first (matches raw_router's pattern for
    test isolation via monkeypatch), then falls back to ``config.json``, then
    to the sibling ``ask_jojo_wiki/`` directory at the repo root.
    """
    default = str(
        Path(__file__).resolve().parents[4] / "ask_jojo_wiki"
    )
    env_val = os.environ.get("JOJO_WIKI_ROOT")
    if env_val:
        return Path(env_val).resolve()
    return Path(config.get("wiki_root", default)).resolve()


def _guard_path(wiki_root: Path, resolved: Path) -> None:
    """Raise HTTP 400 if ``resolved`` escapes ``wiki_root``."""
    try:
        resolved.relative_to(wiki_root)
    except ValueError as exc:
        raise HTTPException(
            status_code=400, detail="path traversal not allowed"
        ) from exc


def _iter_pages(wiki_root: Path):
    """Yield ``(rel, full_path, frontmatter_dict)`` for every wiki page.

    Skips ``_index.md``, ``_backlinks.json``, ``README.md``, ``SCHEMA.md``,
    ``_needs_review.md``, and any file whose name starts with ``_``.
    """
    for full_path in sorted(wiki_root.rglob("*.md")):
        if full_path.name in _SKIP_NAMES:
            continue
        if full_path.name.startswith("_"):
            continue
        rel = full_path.relative_to(wiki_root)
        try:
            text = full_path.read_text(encoding="utf-8")
        except OSError:
            continue
        fm, _ = split_frontmatter(text)
        yield rel, full_path, fm


# -------------------------------------------------------------------- public helpers
# These are called by ops_router — keep them importable.

def wiki_stats(wiki_root: Path | None = None) -> dict[str, Any]:
    """Compute the stats blob used by GET /api/wiki/stats and GET /api/ops/status."""
    if wiki_root is None:
        wiki_root = _wiki_root()

    total = sum(1 for _ in _iter_pages(wiki_root))

    # Git last-commit info.
    last_sha = ""
    last_msg = ""
    last_date = ""
    try:
        result = subprocess.run(
            ["git", "-C", str(wiki_root), "log", "-1", "--format=%H|%s|%cI"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            parts = result.stdout.strip().split("|", 2)
            last_sha = parts[0] if len(parts) > 0 else ""
            last_msg = parts[1] if len(parts) > 1 else ""
            last_date = parts[2] if len(parts) > 2 else ""
    except Exception:  # noqa: BLE001
        pass

    # Schema version — scan SCHEMA.md for "**Schema version:** x.y.z".
    schema_version = "0.1.0"
    schema_path = wiki_root / "SCHEMA.md"
    if schema_path.exists():
        try:
            text = schema_path.read_text(encoding="utf-8")
            m = _SCHEMA_VER_RE.search(text)
            if m:
                schema_version = m.group(1)
        except OSError:
            pass

    return {
        "total_pages": total,
        "last_commit_sha": last_sha,
        "last_commit_message": last_msg,
        "last_commit_date": last_date,
        "schema_version": schema_version,
        "index_page_count": total,
    }


# -------------------------------------------------------------------- endpoints

@router.get("/tree")
def get_tree() -> dict[str, Any]:
    """Return the wiki directory tree grouped by first-level directory.

    Response shape::

        {
          "tree": [
            {
              "kind": "dir",
              "name": "targets",
              "children": [
                {
                  "kind": "file",
                  "slug": "cbl-b",
                  "title": "CBL-B (Casitas B-lineage Lymphoma B)",
                  "type": "target",
                  "path": "targets/cbl-b.md",
                  "confidence": "high",
                  "last_updated": "2026-04-29"
                }
              ]
            }
          ],
          "total_pages": 138
        }
    """
    wiki_root = _wiki_root()
    dirs: dict[str, list[dict[str, Any]]] = {}
    total = 0
    for rel, _full, fm in _iter_pages(wiki_root):
        total += 1
        parts = rel.parts
        dir_name = parts[0] if len(parts) > 1 else "other"
        node: dict[str, Any] = {
            "kind": "file",
            "slug": fm.get("slug") or rel.stem,
            "title": fm.get("title") or rel.stem,
            "type": fm.get("type", ""),
            "path": str(rel).replace("\\", "/"),
            "confidence": fm.get("confidence", ""),
            "last_updated": str(fm.get("last_updated", "")),
        }
        dirs.setdefault(dir_name, []).append(node)

    tree = []
    for dir_name in sorted(dirs.keys()):
        children = sorted(dirs[dir_name], key=lambda f: (f["title"] or "").lower())
        tree.append({"kind": "dir", "name": dir_name, "children": children})

    return {"tree": tree, "total_pages": total}


@router.get("/page")
def get_page(
    path: str = Query(..., description="Page path (targets/cbl-b.md) or bare slug (targets/cbl-b)"),
) -> dict[str, Any]:
    """Return frontmatter + body of a wiki page.

    Accepts paths with or without the ``.md`` extension.
    Returns 400 on path traversal, 404 when the file is missing.
    """
    wiki_root = _wiki_root()

    # Normalise: ensure .md extension.
    norm = path if path.endswith(".md") else path + ".md"
    candidate = (wiki_root / norm).resolve()
    _guard_path(wiki_root, candidate)

    if not candidate.exists():
        raise HTTPException(status_code=404, detail=f"wiki page not found: {path}")

    text = candidate.read_text(encoding="utf-8")
    fm, body = split_frontmatter(text)
    rel = candidate.relative_to(wiki_root)

    return {
        "path": str(rel).replace("\\", "/"),
        "slug": fm.get("slug") or rel.stem,
        "title": fm.get("title") or rel.stem,
        "type": fm.get("type", ""),
        "confidence": fm.get("confidence", ""),
        "last_updated": str(fm.get("last_updated", "")),
        "last_reviewed": str(fm.get("last_reviewed", "")),
        "schema_version": fm.get("schema_version", ""),
        "corpus": fm.get("corpus", ""),
        "tags": fm.get("tags") or [],
        "aliases": fm.get("aliases") or [],
        "related": fm.get("related") or [],
        "sources": fm.get("sources") or [],
        "body": body,
    }


@router.get("/backlinks")
def get_backlinks(
    slug: str = Query(..., description="Slug to look up inbound links for"),
) -> dict[str, Any]:
    """Return the list of slugs that contain a wikilink pointing at ``slug``.

    Reads ``_backlinks.json`` on each call (file is small; on-call read is
    fine for Phase 3 — cache when needed). Returns an empty list (not 404)
    when the slug has no inbound links.
    """
    wiki_root = _wiki_root()
    backlinks_path = wiki_root / "_backlinks.json"
    linked_from: list[str] = []
    if backlinks_path.exists():
        try:
            data: dict[str, list[str]] = json.loads(
                backlinks_path.read_text(encoding="utf-8")
            )
            linked_from = data.get(slug, [])
        except (OSError, json.JSONDecodeError):
            pass
    return {"slug": slug, "linked_from": linked_from}


@router.get("/search")
def search(
    q: str = Query(..., min_length=2, description="Search query (minimum 2 chars)"),
) -> dict[str, Any]:
    """Substring search over page titles, slugs, and aliases.

    Returns up to 20 results. Case-insensitive.  No fuzzy matching — 138 pages
    is cheap enough for a simple ``q.lower() in field.lower()`` scan.
    """
    if len(q) < 2:
        raise HTTPException(
            status_code=400, detail="search query must be at least 2 characters"
        )

    wiki_root = _wiki_root()
    q_lower = q.lower()
    results = []
    for rel, _full, fm in _iter_pages(wiki_root):
        if len(results) >= 20:
            break
        title: str = fm.get("title") or rel.stem
        slug: str = fm.get("slug") or rel.stem
        aliases: list[str] = fm.get("aliases") or []
        hit = (
            q_lower in title.lower()
            or q_lower in slug.lower()
            or any(q_lower in a.lower() for a in aliases)
        )
        if hit:
            results.append(
                {
                    "slug": slug,
                    "title": title,
                    "type": fm.get("type", ""),
                    "path": str(rel).replace("\\", "/"),
                }
            )
    return {"query": q, "results": results}


@router.get("/stats")
def get_stats() -> dict[str, Any]:
    """Return high-level wiki health info (page count, last commit, schema)."""
    return wiki_stats()


class EditRequest(BaseModel):
    path: str
    instruction: str


@router.post("/edit")
def request_edit(req: EditRequest) -> dict[str, Any]:
    """Propose a Claude-written edit to a wiki page.

    Feature-flagged: if ``anthropic_api_key`` is not configured, returns
    ``{ "status": "api_key_required", ... }`` with HTTP 200 — the UI shows
    a nudge, not a crash.
    """
    api_key: str | None = config.get(config.KEY_ANTHROPIC_API_KEY, None)
    if not api_key:
        return {
            "status": "api_key_required",
            "message": (
                "Configure JOJO_API_KEY (or set anthropic_api_key in config.json) "
                "to enable JoJo-written edits."
            ),
        }

    wiki_root = _wiki_root()
    norm = req.path if req.path.endswith(".md") else req.path + ".md"
    page_path = (wiki_root / norm).resolve()
    _guard_path(wiki_root, page_path)

    if not page_path.exists():
        raise HTTPException(status_code=404, detail=f"wiki page not found: {req.path}")

    original_text = page_path.read_text(encoding="utf-8")
    _fm, original_body = split_frontmatter(original_text)

    try:
        import anthropic  # type: ignore[import]
    except ImportError as exc:
        raise HTTPException(
            status_code=500,
            detail="anthropic package is not installed — run: pip install anthropic",
        ) from exc

    client = anthropic.Anthropic(api_key=api_key)
    prompt = (
        f"You are editing a wiki page for Nurix Therapeutics. "
        f"The current page body (after frontmatter) is:\n\n{original_body}\n\n"
        f"Apply this instruction and return ONLY the revised full body "
        f"(no frontmatter, no commentary):\n\n{req.instruction}"
    )
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    proposed_body: str = message.content[0].text

    diff_lines = list(
        difflib.unified_diff(
            original_body.splitlines(keepends=True),
            proposed_body.splitlines(keepends=True),
            fromfile=f"a/{req.path}",
            tofile=f"b/{req.path}",
        )
    )
    diff_str = "".join(diff_lines)

    return {
        "status": "proposed",
        "path": str(page_path.relative_to(wiki_root)).replace("\\", "/"),
        "diff": diff_str,
        "proposed_body": proposed_body,
    }


@router.patch("/page")
def patch_page(
    path: str = Query(..., description="Path to the wiki page to update"),
) -> None:
    """Write-back for accepted edits. Coming in Phase 3 final pass."""
    _ = path
    raise HTTPException(
        status_code=501,
        detail="Page write-back coming in Phase 3 final pass.",
    )
