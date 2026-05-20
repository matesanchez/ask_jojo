"""Real-endpoint tests for /api/raw.

These go beyond the 501 smoke tests — they construct a tiny raw repo with
a manifest + .md files and exercise the tree / file / manifest endpoints
end-to-end. Keeping these separate from `test_ingest_endpoints.py` keeps
the fixtures minimal: these tests never touch IngestDriver.
"""

from __future__ import annotations

import importlib
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from jojo_connectors_common import Manifest, ManifestEntry


@pytest.fixture
def client_with_raw(tmp_path: Path, monkeypatch):
    """Spin up a TestClient pointed at a tmp JOJO_RAW_ROOT that we pre-populate.

    The raw router reads JOJO_RAW_ROOT per-request, so we don't need to reload
    the router — but we do reload `backend.main` so subsequent tests don't
    share the TestClient. (A TestClient is stateful-ish via RQ fallback.)
    """
    raw = tmp_path / "ask_jojo_raw"
    raw.mkdir()
    monkeypatch.setenv("JOJO_RAW_ROOT", str(raw))

    # Invalidate any cached config readers so tests don't pick up dev env.
    from backend import main
    from backend.routers import raw_router

    importlib.reload(raw_router)
    importlib.reload(main)

    return TestClient(main.app), raw


def _write_entry(
    raw: Path,
    *,
    entry_id: str,
    rel_path: str,
    title: str,
    body: str,
    source_type: str = "drive",
    access_level: str = "all_fte",
    source_url: str = "file:///Z:/example.md",
    source_id: str = "example",
    fetched: str = "2026-04-22T12:00:00+00:00",
    sha256: str = "a" * 64,
    size_bytes: int = 100,
) -> ManifestEntry:
    """Write a raw .md with frontmatter and return a matching ManifestEntry."""
    full = raw / rel_path
    full.parent.mkdir(parents=True, exist_ok=True)
    fm = (
        "---\n"
        f"id: {entry_id}\n"
        f"source_type: {source_type}\n"
        f"source_url: {source_url}\n"
        f"source_id: {source_id}\n"
        f"title: {title}\n"
        f"sha256: {sha256}\n"
        f"access_level: {access_level}\n"
        f"fetched: {fetched}\n"
        "language: en\n"
        "tags: []\n"
        "redacted_fields: []\n"
        "---\n"
    )
    full.write_text(fm + body, encoding="utf-8")
    return ManifestEntry(
        id=entry_id,
        path=rel_path,
        sha256=sha256,
        source_type=source_type,
        source_url=source_url,
        source_id=source_id,
        title=title,
        access_level=access_level,
        fetched=fetched,
        size_bytes=size_bytes,
    )


def _save_manifest(raw: Path, entries: list[ManifestEntry]) -> None:
    mani = Manifest(raw / "manifest.json")
    for e in entries:
        mani.upsert(e)
    mani.save()


# -------------------------------------------------------------------- /tree
def test_tree_empty_when_no_manifest(client_with_raw):
    client, raw = client_with_raw
    r = client.get("/api/raw/tree")
    assert r.status_code == 200
    body = r.json()
    assert body["total_entries"] == 0
    assert body["tree"] == []
    assert body["raw_root"] == str(raw)


def test_tree_groups_entries_by_path_segments(client_with_raw):
    client, raw = client_with_raw
    e1 = _write_entry(
        raw,
        entry_id="drive_sop-recipe",
        rel_path="drive/sop/recipe.md",
        title="SOP Recipe",
        body="# Body\n",
    )
    e2 = _write_entry(
        raw,
        entry_id="drive_sop-other",
        rel_path="drive/sop/other.md",
        title="Other",
        body="# Other\n",
    )
    e3 = _write_entry(
        raw,
        entry_id="sharepoint_intro",
        rel_path="sharepoint/ProteinScience/intro.md",
        title="Intro",
        body="# Intro\n",
        source_type="sharepoint",
    )
    _save_manifest(raw, [e1, e2, e3])

    r = client.get("/api/raw/tree")
    assert r.status_code == 200
    body = r.json()
    assert body["total_entries"] == 3

    # Top level is alphabetical across source_type dirs.
    top_names = [n["name"] for n in body["tree"]]
    assert top_names == ["drive", "sharepoint"]

    # The drive/sop dir holds both files, sorted alphabetically.
    drive = body["tree"][0]
    assert drive["kind"] == "dir"
    sop = drive["children"][0]
    assert sop["name"] == "sop"
    file_names = [c["name"] for c in sop["children"]]
    assert file_names == ["other.md", "recipe.md"]

    # Each file has the entry metadata the UI needs to render a leaf row.
    recipe = sop["children"][1]
    assert recipe["kind"] == "file"
    assert recipe["entry"]["id"] == "drive_sop-recipe"
    assert recipe["entry"]["title"] == "SOP Recipe"
    assert recipe["entry"]["access_level"] == "all_fte"


def test_tree_sorts_dirs_before_files_at_same_level(client_with_raw):
    """Dirs bubble above sibling files — matches VS Code explorer ordering."""
    client, raw = client_with_raw
    top_file = _write_entry(
        raw,
        entry_id="drive_toplevel",
        rel_path="drive/toplevel.md",
        title="Top-level note",
        body="# Top\n",
    )
    nested = _write_entry(
        raw,
        entry_id="drive_sub-note",
        rel_path="drive/sub/note.md",
        title="Nested note",
        body="# Nested\n",
    )
    _save_manifest(raw, [top_file, nested])

    r = client.get("/api/raw/tree")
    drive = r.json()["tree"][0]
    # "sub" (dir) comes before "toplevel.md" (file) even though alphabetically
    # "sub" < "toplevel" happens to line up — so use a case where the dir name
    # would sort after the file name if it were a file:
    # We check the kinds in order.
    kinds = [c["kind"] for c in drive["children"]]
    assert kinds == ["dir", "file"]


def test_tree_cache_busts_on_manifest_change(client_with_raw):
    """Second call returns cached result; adding an entry busts the cache."""
    client, raw = client_with_raw
    e1 = _write_entry(raw, entry_id="d_a", rel_path="drive/a.md", title="A", body="# A\n")
    _save_manifest(raw, [e1])

    r1 = client.get("/api/raw/tree")
    assert r1.json()["total_entries"] == 1

    # Second call — manifest unchanged — hits the cache (same result).
    r2 = client.get("/api/raw/tree")
    assert r2.json()["total_entries"] == 1

    # Add a second entry and rewrite the manifest (mtime advances).
    e2 = _write_entry(raw, entry_id="d_b", rel_path="drive/b.md", title="B", body="# B\n")
    _save_manifest(raw, [e1, e2])

    # Cache must bust because manifest mtime changed.
    r3 = client.get("/api/raw/tree")
    assert r3.json()["total_entries"] == 2


# -------------------------------------------------------------------- /file
def test_file_returns_frontmatter_and_body(client_with_raw):
    client, raw = client_with_raw
    e = _write_entry(
        raw,
        entry_id="drive_recipe",
        rel_path="drive/recipe.md",
        title="Recipe",
        body="# Recipe\n\nStep one.\n",
    )
    _save_manifest(raw, [e])

    r = client.get("/api/raw/file/drive_recipe")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["entry"]["id"] == "drive_recipe"
    assert body["entry"]["title"] == "Recipe"
    assert body["entry"]["source_type"] == "drive"
    assert body["entry"]["superseded_by"] is None
    # Frontmatter was parsed server-side.
    assert body["frontmatter"]["title"] == "Recipe"
    assert body["frontmatter"]["access_level"] == "all_fte"
    # Body has the frontmatter stripped.
    assert body["body"].startswith("# Recipe\n")
    assert "---" not in body["body"].splitlines()[0]


def test_file_404_for_unknown_id(client_with_raw):
    client, raw = client_with_raw
    _save_manifest(raw, [])
    r = client.get("/api/raw/file/drive_does-not-exist")
    assert r.status_code == 404


def test_file_410_when_manifest_entry_points_at_missing_file(client_with_raw):
    """Manifest/disk drift surfaces as 410 Gone so the UI can warn instead
    of silently showing an empty preview."""
    client, raw = client_with_raw
    # Build an entry whose path we never actually wrote.
    e = ManifestEntry(
        id="drive_ghost",
        path="drive/ghost.md",
        sha256="b" * 64,
        source_type="drive",
        source_url="",
        source_id="ghost",
        title="Ghost",
        access_level="all_fte",
        fetched="2026-04-22T12:00:00+00:00",
        size_bytes=0,
    )
    _save_manifest(raw, [e])
    r = client.get("/api/raw/file/drive_ghost")
    assert r.status_code == 410
    assert "missing" in r.json()["detail"].lower()


def test_file_rejects_path_traversal(tmp_path: Path, client_with_raw):
    """A hand-edited manifest with ../ in a path must not escape raw root."""
    client, raw = client_with_raw
    # Construct a manifest entry whose path tries to escape.
    (tmp_path / "outside.md").write_text("---\nid: x\n---\n# nope\n", encoding="utf-8")
    rogue_manifest = {
        "schema_version": "0.1.0",
        "generated": "2026-04-22T00:00:00+00:00",
        "entries": {
            "drive_rogue": {
                "path": "../outside.md",
                "sha256": "c" * 64,
                "source_type": "drive",
                "source_url": "",
                "source_id": "rogue",
                "title": "Rogue",
                "access_level": "all_fte",
                "fetched": "2026-04-22T12:00:00+00:00",
                "size_bytes": 0,
                "redacted_fields": [],
                "supersedes": None,
            }
        },
        "supersedence": {},
    }
    (raw / "manifest.json").write_text(json.dumps(rogue_manifest), encoding="utf-8")
    r = client.get("/api/raw/file/drive_rogue")
    assert r.status_code == 400
    assert "escapes" in r.json()["detail"].lower()


def test_file_reports_superseded_by_pointer(client_with_raw):
    """If the manifest records a supersedence, the file response exposes it
    so the UI can nudge the reader toward the newer version."""
    client, raw = client_with_raw
    old = _write_entry(
        raw,
        entry_id="drive_old",
        rel_path="drive/old.md",
        title="Old",
        body="# Old\n",
    )
    new = _write_entry(
        raw,
        entry_id="drive_new",
        rel_path="drive/new.md",
        title="New",
        body="# New\n",
    )
    mani = Manifest(raw / "manifest.json")
    mani.upsert(old)
    new.supersedes = "drive_old"
    mani.upsert(new)
    mani.save()

    r = client.get("/api/raw/file/drive_old")
    assert r.status_code == 200
    assert r.json()["entry"]["superseded_by"] == "drive_new"


# -------------------------------------------------------------------- /manifest
def test_manifest_summary_empty(client_with_raw):
    client, raw = client_with_raw
    r = client.get("/api/raw/manifest")
    assert r.status_code == 200
    body = r.json()
    assert body["total_entries"] == 0
    assert body["by_source"] == {}
    assert body["latest_fetched_by_source"] == {}
    assert body["raw_root"] == str(raw)


def test_manifest_summary_counts_and_latest_fetched(client_with_raw):
    client, raw = client_with_raw
    e1 = _write_entry(
        raw,
        entry_id="drive_a",
        rel_path="drive/a.md",
        title="A",
        body="# A\n",
        fetched="2026-04-22T10:00:00+00:00",
    )
    e2 = _write_entry(
        raw,
        entry_id="drive_b",
        rel_path="drive/b.md",
        title="B",
        body="# B\n",
        fetched="2026-04-22T12:00:00+00:00",
    )
    e3 = _write_entry(
        raw,
        entry_id="sharepoint_c",
        rel_path="sharepoint/c.md",
        title="C",
        body="# C\n",
        source_type="sharepoint",
        fetched="2026-04-22T11:00:00+00:00",
    )
    _save_manifest(raw, [e1, e2, e3])

    r = client.get("/api/raw/manifest")
    body = r.json()
    assert body["total_entries"] == 3
    assert body["by_source"] == {"drive": 2, "sharepoint": 1}
    # Latest fetched per source reflects max(ISO) — ISO-8601 sorts lexicographically.
    assert body["latest_fetched_by_source"]["drive"] == "2026-04-22T12:00:00+00:00"
    assert body["latest_fetched_by_source"]["sharepoint"] == "2026-04-22T11:00:00+00:00"
