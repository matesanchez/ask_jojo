"""Raw API router — backs the Raw tab in the JoJo Bot frontend.

The Raw tab is the human audit surface on top of `ask_jojo_raw/`. Every
answer the bot gives in the Wiki tab has to cite a raw file; the Raw tab
is where a curious engineer verifies that the citation is real and
sourced from something they actually have permission to see.

The three endpoints mirror what the UI needs:

- ``GET  /api/raw/tree``          — hierarchical view of the manifest,
                                   grouped by source_type then by path.
- ``GET  /api/raw/file/{id}``     — frontmatter + body of one entry.
- ``GET  /api/raw/manifest``      — quick summary (counts by source, totals).

Implementation notes:

- Source of truth is ``manifest.json``. We deliberately never list the
  filesystem directly — that's the "filesystem walks should never bypass
  the manifest" invariant from PLAN.md §6 Phase 1. If a file is on disk
  but not in the manifest, it's invisible to the Raw tab (and flagged by
  the compile phase).
- The tree endpoint is cheap enough to recompute on each request for
  Phase 1 (a few-hundred-entry manifest loads in <5ms). Caching can
  land when we start seeing multi-thousand-entry manifests.
- We return ``entry_id`` (the stable manifest key) as the node
  identifier, not a filesystem path, so the UI keeps working after
  supersedence chains rename raw files.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException

from jojo_connectors_common import Manifest, split_frontmatter

router = APIRouter()


# -------------------------------------------------------------------- config
def _raw_root() -> Path:
    """Resolve the raw root each call so tests (and the local-mode runtime)
    can relocate it without restarting the process. Reads config.json first
    and falls back to ``$JOJO_RAW_ROOT`` via ``jojo_core.config.get``."""
    from jojo_core import config
    return Path(config.get(config.KEY_RAW_ROOT, "./ask_jojo_raw")).resolve()


def _load_manifest() -> Manifest:
    root = _raw_root()
    return Manifest.load(root / "manifest.json")


# -------------------------------------------------------------------- tree
@dataclass
class _TreeNode:
    """Mutable tree-builder node; converted to dicts before return.

    `kind` is either "dir" or "file". For files, `entry` carries the
    manifest metadata the UI needs to render a leaf row (title, access
    badge, fetched timestamp) without a second round-trip.
    """

    name: str
    kind: str  # "dir" | "file"
    children: dict[str, _TreeNode] = field(default_factory=dict)
    entry: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        if self.kind == "file":
            return {
                "name": self.name,
                "kind": "file",
                "entry": self.entry,
            }
        # Sort dirs before files, then alphabetically — matches VS Code's
        # explorer and what most engineers expect at a glance.
        kids = sorted(
            self.children.values(),
            key=lambda c: (c.kind == "file", c.name.lower()),
        )
        return {
            "name": self.name,
            "kind": "dir",
            "children": [c.to_dict() for c in kids],
        }


def _build_tree(manifest: Manifest) -> list[dict[str, Any]]:
    """Turn a flat manifest into a nested tree keyed by path segments."""
    root_children: dict[str, _TreeNode] = {}

    for entry in manifest.entries.values():
        # Use POSIX segments — the manifest stores repo-relative POSIX paths.
        segments = [s for s in entry.path.replace("\\", "/").split("/") if s]
        if not segments:
            continue
        cursor_children = root_children
        for seg in segments[:-1]:
            node = cursor_children.setdefault(seg, _TreeNode(name=seg, kind="dir"))
            if node.kind != "dir":
                # A file and a dir collided. Shouldn't happen with stable_id,
                # but if someone hand-edited the manifest, surface it instead
                # of silently dropping the entry.
                node = _TreeNode(name=seg, kind="dir")
                cursor_children[seg] = node
            cursor_children = node.children
        leaf_name = segments[-1]
        cursor_children[leaf_name] = _TreeNode(
            name=leaf_name,
            kind="file",
            entry={
                "id": entry.id,
                "path": entry.path,
                "title": entry.title or leaf_name,
                "source_type": entry.source_type,
                "source_url": entry.source_url,
                "access_level": entry.access_level,
                "fetched": entry.fetched,
                "size_bytes": entry.size_bytes,
                "sha256": entry.sha256,
                "supersedes": entry.supersedes,
            },
        )

    top = sorted(
        root_children.values(),
        key=lambda c: (c.kind == "file", c.name.lower()),
    )
    return [c.to_dict() for c in top]


# -------------------------------------------------------------------- endpoints
@router.get("/tree")
def get_tree() -> dict[str, Any]:
    """Return the manifest rendered as a nested dir/file tree.

    Response shape::

        {
          "raw_root": "/abs/path/ask_jojo_raw",
          "total_entries": 142,
          "tree": [
            {"name": "sharepoint", "kind": "dir", "children": [
              {"name": "ProteinScience", "kind": "dir", "children": [
                {"name": "sharepoint_foo.md", "kind": "file", "entry": {...}},
                ...
              ]},
            ]},
            ...
          ]
        }

    The UI expects `children` on dirs and `entry` on files. Empty manifest
    → empty tree; not an error.
    """
    manifest = _load_manifest()
    return {
        "raw_root": str(_raw_root()),
        "total_entries": len(manifest.entries),
        "tree": _build_tree(manifest),
    }


@router.get("/file/{entry_id}")
def get_file(entry_id: str) -> dict[str, Any]:
    """Return the frontmatter + body of one raw entry.

    We split the frontmatter server-side so the UI doesn't ship a YAML
    parser just to render the metadata panel. The body is returned as
    raw markdown — the UI renders it with react-markdown.
    """
    manifest = _load_manifest()
    entry = manifest.get(entry_id)
    if entry is None:
        raise HTTPException(status_code=404, detail=f"entry not found: {entry_id}")

    raw_root = _raw_root()
    file_path = (raw_root / entry.path).resolve()
    # Defense against path traversal from a hand-edited manifest: the resolved
    # file path must live inside the raw root.
    try:
        file_path.relative_to(raw_root)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="entry path escapes raw root") from exc

    if not file_path.exists():
        # The manifest entry exists but the .md file is gone — this is a
        # real inconsistency the user should know about. 410 Gone makes
        # the state legible to the UI.
        raise HTTPException(
            status_code=410,
            detail=f"manifest entry exists but file is missing on disk: {entry.path}",
        )

    text = file_path.read_text(encoding="utf-8")
    frontmatter, body = split_frontmatter(text)

    # Track supersedence chain forward so the UI can nudge users toward
    # the current version without rebuilding this lookup client-side.
    superseded_by = manifest.supersedence.get(entry_id)

    return {
        "entry": {
            "id": entry.id,
            "path": entry.path,
            "title": entry.title,
            "source_type": entry.source_type,
            "source_url": entry.source_url,
            "source_id": entry.source_id,
            "access_level": entry.access_level,
            "fetched": entry.fetched,
            "sha256": entry.sha256,
            "size_bytes": entry.size_bytes,
            "redacted_fields": entry.redacted_fields,
            "supersedes": entry.supersedes,
            "superseded_by": superseded_by,
        },
        "frontmatter": frontmatter,
        "body": body,
    }


@router.get("/manifest")
def get_manifest_summary() -> dict[str, Any]:
    """Return a summary view of the manifest.

    This is the same shape as ``/api/ingest/status`` but rooted at the
    Raw tab so the frontend can keep its API calls colocated with its
    routes. The UI uses it for the header counts ("142 files across 4
    sources") and for the per-source badges in the tree header.
    """
    manifest = _load_manifest()
    by_source: dict[str, int] = {}
    latest_fetched: dict[str, str] = {}
    for entry in manifest.entries.values():
        by_source[entry.source_type] = by_source.get(entry.source_type, 0) + 1
        # ISO-8601 sorts lexicographically, so max() gives us the latest.
        if entry.fetched and entry.fetched > latest_fetched.get(entry.source_type, ""):
            latest_fetched[entry.source_type] = entry.fetched
    return {
        "raw_root": str(_raw_root()),
        "schema_version": "0.1.0",
        "total_entries": len(manifest.entries),
        "by_source": by_source,
        "latest_fetched_by_source": latest_fetched,
        "supersedence_chains": len(manifest.supersedence),
    }
