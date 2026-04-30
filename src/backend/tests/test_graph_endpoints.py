"""Tests for /api/graph/."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client_with_wiki(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    wiki = tmp_path / "ask_jojo_wiki"
    wiki.mkdir()
    (wiki / "_index.md").write_text(
        textwrap.dedent(
            """\
            # Wiki Index

            ## Program

            - [[a|A]] — `programs/a.md`
            - [[b|B]] — `programs/b.md`
            """
        ),
        encoding="utf-8",
    )
    (wiki / "programs").mkdir()
    (wiki / "programs" / "a.md").write_text(
        "---\nslug: a\n---\n\nLinks: [[b]]\n",
        encoding="utf-8",
    )
    (wiki / "programs" / "b.md").write_text(
        "---\nslug: b\n---\n\nLinks: [[a]]\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("JOJO_WIKI_ROOT", str(wiki))
    from backend.main import app
    return TestClient(app), wiki


def test_available_endpoint(client_with_wiki) -> None:
    client, _ = client_with_wiki
    r = client.get("/api/graph/available")
    assert r.status_code == 200
    body = r.json()
    assert body["source"] in ("graphify", "fallback")


def test_html_404_before_rebuild(client_with_wiki) -> None:
    client, _ = client_with_wiki
    r = client.get("/api/graph/html")
    assert r.status_code == 404


def test_rebuild_then_html(client_with_wiki) -> None:
    client, wiki = client_with_wiki
    r = client.post("/api/graph/rebuild")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["node_count"] == 2

    # html now exists
    r = client.get("/api/graph/html")
    assert r.status_code == 200
    text = r.text
    assert "<!doctype html>" in text


def test_rebuild_then_report(client_with_wiki) -> None:
    client, _ = client_with_wiki
    client.post("/api/graph/rebuild")
    r = client.get("/api/graph/report")
    assert r.status_code == 200
    assert "Graph Report" in r.text


def test_rebuild_then_json(client_with_wiki) -> None:
    client, _ = client_with_wiki
    client.post("/api/graph/rebuild")
    r = client.get("/api/graph/json")
    assert r.status_code == 200
    body = r.json()
    assert "nodes" in body
    assert "edges" in body


def test_stats_endpoint(client_with_wiki) -> None:
    client, _ = client_with_wiki
    client.post("/api/graph/rebuild")
    r = client.get("/api/graph/stats")
    assert r.status_code == 200
    body = r.json()
    assert body["node_count"] == 2
    assert body["edge_count"] == 1
    assert body["source"] in ("graphify", "fallback")
