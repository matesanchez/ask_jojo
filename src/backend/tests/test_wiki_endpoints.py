"""Real-endpoint tests for /api/wiki.

Mirrors the pattern in test_raw_endpoints.py: construct a minimal fake wiki
directory with sample pages, a _backlinks.json, and an _index.md, then hit
the endpoints end-to-end through the TestClient.

All cases required by the Phase 3 spec are covered here.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# -------------------------------------------------------------------- helpers

def _write_wiki_page(
    wiki: Path,
    *,
    slug: str,
    title: str,
    page_type: str = "target",
    confidence: str = "high",
    subdir: str = "targets",
    aliases: list[str] | None = None,
    tags: list[str] | None = None,
    sources: list[dict] | None = None,
    body: str = "## Overview\n\nSample body.\n",
) -> Path:
    """Write a wiki page with proper YAML frontmatter."""
    parent = wiki / subdir
    parent.mkdir(parents=True, exist_ok=True)
    page_path = parent / f"{slug}.md"

    aliases_yaml = ""
    if aliases:
        aliases_yaml = "aliases: [" + ", ".join(aliases) + "]\n"

    tags_yaml = ""
    if tags:
        tags_yaml = "tags: [" + ", ".join(tags) + "]\n"

    sources_yaml = ""
    if sources:
        lines = ["sources:\n"]
        for s in sources:
            lines.append(f"  - path: {s.get('path', '')}\n")
            lines.append(f"    hash: {s.get('hash', 'abc123')}\n")
            lines.append(f"    ingested: {s.get('ingested', '2026-04-29')}\n")
        sources_yaml = "".join(lines)

    fm = (
        "---\n"
        f"slug: {slug}\n"
        f"title: {title}\n"
        f"type: {page_type}\n"
        f"confidence: {confidence}\n"
        "last_updated: 2026-04-29\n"
        "last_reviewed: 2026-04-29\n"
        "schema_version: 0.1.0\n"
        "corpus: protein-sciences\n"
        f"{aliases_yaml}"
        f"{tags_yaml}"
        f"{sources_yaml}"
        "---\n"
    )
    page_path.write_text(fm + body, encoding="utf-8")
    return page_path


def _write_backlinks(wiki: Path, data: dict[str, list[str]]) -> None:
    (wiki / "_backlinks.json").write_text(
        json.dumps(data, indent=2), encoding="utf-8"
    )


def _write_index(wiki: Path) -> None:
    (wiki / "_index.md").write_text("# Wiki Index\nTotal pages: 3\n", encoding="utf-8")


# -------------------------------------------------------------------- fixture

@pytest.fixture
def client_with_wiki(tmp_path: Path, monkeypatch):
    """Create a minimal fake wiki and return (TestClient, wiki_root)."""
    wiki = tmp_path / "ask_jojo_wiki"
    wiki.mkdir()

    # Three sample pages.
    _write_wiki_page(
        wiki,
        slug="cbl-b",
        title="CBL-B (Casitas B-lineage Lymphoma B)",
        page_type="target",
        confidence="high",
        subdir="targets",
        aliases=["CBL-B", "Cbl-b"],
        tags=["target", "e3-ligase"],
        sources=[{"path": "raw/onedrive/cbl_b.md", "hash": "abc123"}],
    )
    _write_wiki_page(
        wiki,
        slug="cbl-b-program",
        title="CBL-B Program",
        page_type="program",
        confidence="medium",
        subdir="programs",
    )
    _write_wiki_page(
        wiki,
        slug="del-screening",
        title="DEL Screening",
        page_type="method",
        confidence="low",
        subdir="methods",
    )

    # Backlinks: cbl-b is linked from cbl-b-program and del-screening.
    _write_backlinks(
        wiki,
        {
            "cbl-b": ["cbl-b-program", "del-screening"],
            "del-screening": ["cbl-b"],
        },
    )

    # Index (required by spec fixture; not directly used by API but present in real wiki).
    _write_index(wiki)

    monkeypatch.setenv("JOJO_WIKI_ROOT", str(wiki))

    from backend.main import app

    return TestClient(app), wiki


# -------------------------------------------------------------------- /tree

def test_tree_groups_pages_by_directory(client_with_wiki):
    client, _wiki = client_with_wiki
    r = client.get("/api/wiki/tree")
    assert r.status_code == 200
    body = r.json()
    assert body["total_pages"] == 3
    dir_names = [d["name"] for d in body["tree"]]
    assert "targets" in dir_names
    assert "programs" in dir_names
    assert "methods" in dir_names


def test_tree_directory_contains_correct_children(client_with_wiki):
    client, _wiki = client_with_wiki
    r = client.get("/api/wiki/tree")
    tree = {d["name"]: d for d in r.json()["tree"]}

    targets = tree["targets"]["children"]
    assert len(targets) == 1
    assert targets[0]["slug"] == "cbl-b"
    assert targets[0]["title"] == "CBL-B (Casitas B-lineage Lymphoma B)"
    assert targets[0]["confidence"] == "high"
    assert targets[0]["kind"] == "file"
    assert targets[0]["path"] == "targets/cbl-b.md"


# -------------------------------------------------------------------- /page

def test_page_returns_frontmatter_and_body(client_with_wiki):
    client, _wiki = client_with_wiki
    r = client.get("/api/wiki/page", params={"path": "targets/cbl-b.md"})
    assert r.status_code == 200
    body = r.json()
    assert body["slug"] == "cbl-b"
    assert body["title"] == "CBL-B (Casitas B-lineage Lymphoma B)"
    assert body["type"] == "target"
    assert body["confidence"] == "high"
    assert body["corpus"] == "protein-sciences"
    assert "CBL-B" in body["aliases"]
    assert body["body"].startswith("## Overview")
    # Frontmatter must not bleed into body.
    assert "---" not in body["body"].splitlines()[0]


def test_page_resolves_without_extension(client_with_wiki):
    client, _wiki = client_with_wiki
    r = client.get("/api/wiki/page", params={"path": "targets/cbl-b"})
    assert r.status_code == 200
    assert r.json()["slug"] == "cbl-b"


def test_page_traversal_returns_400(client_with_wiki):
    client, _wiki = client_with_wiki
    r = client.get("/api/wiki/page", params={"path": "../../../etc/passwd"})
    assert r.status_code == 400
    assert "traversal" in r.json()["detail"].lower()


def test_page_nonexistent_returns_404(client_with_wiki):
    client, _wiki = client_with_wiki
    r = client.get("/api/wiki/page", params={"path": "targets/nonexistent.md"})
    assert r.status_code == 404


# -------------------------------------------------------------------- /backlinks

def test_backlinks_returns_linked_from(client_with_wiki):
    client, _wiki = client_with_wiki
    r = client.get("/api/wiki/backlinks", params={"slug": "cbl-b"})
    assert r.status_code == 200
    body = r.json()
    assert body["slug"] == "cbl-b"
    assert set(body["linked_from"]) == {"cbl-b-program", "del-screening"}


def test_backlinks_orphan_returns_empty_list(client_with_wiki):
    """A slug with no inbound links returns [] rather than 404."""
    client, _wiki = client_with_wiki
    r = client.get("/api/wiki/backlinks", params={"slug": "orphan-page"})
    assert r.status_code == 200
    assert r.json()["linked_from"] == []


# -------------------------------------------------------------------- /search

def test_search_matches_title(client_with_wiki):
    client, _wiki = client_with_wiki
    r = client.get("/api/wiki/search", params={"q": "CBL"})
    assert r.status_code == 200
    body = r.json()
    slugs = [item["slug"] for item in body["results"]]
    assert "cbl-b" in slugs


def test_search_matches_alias(client_with_wiki):
    client, _wiki = client_with_wiki
    r = client.get("/api/wiki/search", params={"q": "Cbl-b"})
    assert r.status_code == 200
    slugs = [item["slug"] for item in r.json()["results"]]
    assert "cbl-b" in slugs


def test_search_single_char_returns_400(client_with_wiki):
    client, _wiki = client_with_wiki
    r = client.get("/api/wiki/search", params={"q": "x"})
    assert r.status_code == 422  # FastAPI validation: min_length=2


def test_search_returns_at_most_20_results(tmp_path: Path, monkeypatch):
    """Smoke: more than 20 matching pages still returns <= 20 results."""
    wiki = tmp_path / "big_wiki"
    wiki.mkdir()
    for i in range(25):
        _write_wiki_page(
            wiki,
            slug=f"target-{i}",
            title=f"Target {i}",
            subdir="targets",
        )
    _write_backlinks(wiki, {})
    _write_index(wiki)
    monkeypatch.setenv("JOJO_WIKI_ROOT", str(wiki))
    from backend.main import app
    client = TestClient(app)
    r = client.get("/api/wiki/search", params={"q": "target"})
    assert r.status_code == 200
    assert len(r.json()["results"]) <= 20


# -------------------------------------------------------------------- /stats

def test_stats_returns_required_keys(client_with_wiki):
    client, _wiki = client_with_wiki
    r = client.get("/api/wiki/stats")
    assert r.status_code == 200
    body = r.json()
    assert "total_pages" in body
    assert "last_commit_sha" in body
    assert body["total_pages"] == 3


def test_stats_git_failure_still_returns_200(client_with_wiki):
    """Even when the wiki dir is not a git repo, /stats returns 200."""
    client, _wiki = client_with_wiki
    # The tmp wiki isn't a git repo, so git log will fail.
    r = client.get("/api/wiki/stats")
    assert r.status_code == 200
    # sha is empty string, not an error.
    assert isinstance(r.json()["last_commit_sha"], str)


# -------------------------------------------------------------------- /edit

def test_edit_returns_api_key_required_when_key_absent(client_with_wiki):
    """With no API key configured, POST /edit returns api_key_required (HTTP 200)."""
    client, _wiki = client_with_wiki
    r = client.post(
        "/api/wiki/edit",
        json={"path": "targets/cbl-b.md", "instruction": "Add a note."},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "api_key_required"
    assert "message" in body


# -------------------------------------------------------------------- /page PATCH (stub)

def test_patch_page_returns_501():
    from backend.main import app
    client = TestClient(app)
    r = client.patch("/api/wiki/page", params={"path": "targets/cbl-b.md"})
    assert r.status_code == 501
    assert "Phase 3 final pass" in r.json()["detail"]


# ----- Phase 7a review fix: dot-directory exclusion (.graphify/, .qmd/, ...)

def test_dot_directory_files_excluded_from_tree(client_with_wiki):
    """Phase 7a review issue J. graphify writes .graphify/GRAPH_REPORT.md
    inside the wiki root; the wiki page walk must skip it (along with
    any other dot-directory like .qmd/ from qmd activation)."""
    client, wiki = client_with_wiki
    # Create a fake .graphify/ directory with a markdown file.
    (wiki / ".graphify").mkdir()
    (wiki / ".graphify" / "GRAPH_REPORT.md").write_text(
        "# Graph Report\n\nThis should NOT show up in the wiki tree.\n",
        encoding="utf-8",
    )
    r = client.get("/api/wiki/tree")
    assert r.status_code == 200
    body = r.json()
    # The fixture has 3 pages; the .graphify/ leak would have made it 4.
    assert body["total_pages"] == 3
    dir_names = [d["name"] for d in body["tree"]]
    assert ".graphify" not in dir_names
