"""Real-endpoint tests for /api/qa.

Mirrors the test_wiki_endpoints.py and test_raw_endpoints.py patterns:
construct a minimal fake wiki, hit the endpoints end-to-end through
TestClient. Synthesis-side endpoints exercise the api_key_required
shape (since the test environment has no API key configured).
"""

from __future__ import annotations

import json
import textwrap
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# -------------------------------------------------------------------- helpers


def _write_wiki(tmp_path: Path) -> Path:
    """Five-page fake wiki with cross-links for graph tests."""
    wiki = tmp_path / "ask_jojo_wiki"
    wiki.mkdir()

    (wiki / "_index.md").write_text(
        textwrap.dedent(
            """\
            # Wiki Index

            ## Program

            - [[cbl-b|CBL-B Program]] — `programs/cbl-b.md`
            - [[del-screening|DEL Screening]] — `programs/del-screening.md`
            - [[pellino-1|Pellino-1 Program]] — `programs/pellino-1.md`

            ## Target

            - [[cbl-b-target|CBL-B Target]] — `targets/cbl-b.md`

            ## Concept

            - [[targeted-protein-degradation|Targeted Protein Degradation]] — `concepts/tpd.md`
            """
        ),
        encoding="utf-8",
    )

    for sub in ("programs", "targets", "concepts"):
        (wiki / sub).mkdir()

    (wiki / "programs" / "cbl-b.md").write_text(
        "---\nslug: cbl-b\ntitle: CBL-B Program\ntype: program\n---\n\n"
        "Links to [[cbl-b-target]] and [[del-screening]].\n",
        encoding="utf-8",
    )
    (wiki / "programs" / "del-screening.md").write_text(
        "---\nslug: del-screening\ntitle: DEL Screening\ntype: program\n---\n\n"
        "DEL screening at Nurix.\n",
        encoding="utf-8",
    )
    (wiki / "programs" / "pellino-1.md").write_text(
        "---\nslug: pellino-1\ntitle: Pellino-1 Program\ntype: program\n---\n\n"
        "Pellino-1 program detail.\n",
        encoding="utf-8",
    )
    (wiki / "targets" / "cbl-b.md").write_text(
        "---\nslug: cbl-b-target\ntitle: CBL-B Target\ntype: target\n---\n\n"
        "[[cbl-b]] backlink target.\n",
        encoding="utf-8",
    )
    (wiki / "concepts" / "tpd.md").write_text(
        "---\nslug: targeted-protein-degradation\ntitle: TPD\ntype: concept\n---\n\n"
        "Targeted protein degradation overview.\n",
        encoding="utf-8",
    )

    (wiki / "_backlinks.json").write_text(
        json.dumps(
            {
                "CBL-B Target": ["cbl-b"],
                "DEL Screening": ["cbl-b"],
            }
        ),
        encoding="utf-8",
    )

    return wiki


@pytest.fixture()
def client_with_wiki(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    wiki = _write_wiki(tmp_path)
    monkeypatch.setenv("JOJO_WIKI_ROOT", str(wiki))

    # Build the graph file once so /api/qa/path doesn't have to.
    from jojo_qa import graph as graph_mod

    g = graph_mod.build(wiki)
    graph_mod.write(g, wiki)

    from backend.main import app

    return TestClient(app), wiki


# -------------------------------------------------------------------- /route


def test_route_v1_for_akta_question(client_with_wiki) -> None:
    client, _ = client_with_wiki
    r = client.get("/api/qa/route", params={"q": "What's the AKTA SOP?"})
    assert r.status_code == 200
    body = r.json()
    assert body["route"] == "v1"
    assert "akta" in body["matched_keywords"]


def test_route_wiki_for_program_question(client_with_wiki) -> None:
    client, _ = client_with_wiki
    r = client.get(
        "/api/qa/route", params={"q": "What's the CBL-B program status?"}
    )
    assert r.status_code == 200
    assert r.json()["route"] == "wiki"


def test_route_requires_q(client_with_wiki) -> None:
    client, _ = client_with_wiki
    r = client.get("/api/qa/route")
    assert r.status_code == 422  # FastAPI validation


# -------------------------------------------------------------------- /index


def test_index_returns_all_entries(client_with_wiki) -> None:
    client, _ = client_with_wiki
    r = client.get("/api/qa/index")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 5
    slugs = [e["slug"] for e in body["entries"]]
    assert "cbl-b" in slugs
    assert "pellino-1" in slugs


# -------------------------------------------------------------------- /retrieve


def test_retrieve_assembles_bundle(client_with_wiki) -> None:
    client, _ = client_with_wiki
    r = client.get(
        "/api/qa/retrieve",
        params={"q": "What is the CBL-B Program?", "k": 3},
    )
    assert r.status_code == 200
    bundle = r.json()
    assert bundle["question"] == "What is the CBL-B Program?"
    assert bundle["router"]["route"] == "wiki"
    assert any(c["slug"] == "cbl-b" for c in bundle["candidates"])
    # graph_neighborhood populated since include_neighbors defaults True.
    assert "graph_neighborhood" in bundle


def test_retrieve_v1_route_returns_empty_candidates(client_with_wiki) -> None:
    client, _ = client_with_wiki
    r = client.get("/api/qa/retrieve", params={"q": "AKTA buffer SOP"})
    assert r.status_code == 200
    bundle = r.json()
    assert bundle["router"]["route"] == "v1"
    assert bundle["candidates"] == []


# -------------------------------------------------------------------- /path


def test_path_finds_direct_edge(client_with_wiki) -> None:
    client, _ = client_with_wiki
    r = client.get("/api/qa/path", params={"from": "cbl-b", "to": "cbl-b-target"})
    assert r.status_code == 200
    body = r.json()
    assert body["path"] == ["cbl-b", "cbl-b-target"]
    assert body["hops"] == 1


def test_path_disconnected(client_with_wiki) -> None:
    client, _ = client_with_wiki
    r = client.get(
        "/api/qa/path", params={"from": "cbl-b", "to": "targeted-protein-degradation"}
    )
    assert r.status_code == 200
    body = r.json()
    assert body["path"] is None


def test_path_invalid_slug(client_with_wiki) -> None:
    client, _ = client_with_wiki
    r = client.get("/api/qa/path", params={"from": "BadSlug!", "to": "cbl-b"})
    assert r.status_code == 400


# -------------------------------------------------------------------- /graph


def test_graph_stats(client_with_wiki) -> None:
    client, _ = client_with_wiki
    r = client.get("/api/qa/graph")
    assert r.status_code == 200
    body = r.json()
    assert body["node_count"] == 5
    assert body["edge_count"] >= 2


# -------------------------------------------------------------------- /qmd-status


def test_qmd_status(client_with_wiki) -> None:
    client, _ = client_with_wiki
    r = client.get("/api/qa/qmd-status")
    assert r.status_code == 200
    body = r.json()
    assert "active" in body
    assert "qmd_available" in body
    assert "triggers" in body


# -------------------------------------------------------------------- POST /query


def test_query_returns_api_key_required_when_no_key(client_with_wiki) -> None:
    client, _ = client_with_wiki
    r = client.post("/api/qa/query", json={"question": "What is CBL-B?"})
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "api_key_required"
    assert "retrieval_bundle" in body
    bundle = body["retrieval_bundle"]
    assert bundle["router"]["route"] == "wiki"


def test_query_invalid_depth(client_with_wiki) -> None:
    client, _ = client_with_wiki
    r = client.post(
        "/api/qa/query",
        json={"question": "x", "depth": "not-a-real-tier"},
    )
    assert r.status_code == 400


def test_query_invalid_route_hint(client_with_wiki) -> None:
    client, _ = client_with_wiki
    r = client.post(
        "/api/qa/query",
        json={"question": "x", "route_hint": "magic"},
    )
    assert r.status_code == 400


def test_query_route_hint_overrides(client_with_wiki) -> None:
    """An operator-provided ``route_hint`` is reflected in the bundle."""
    client, _ = client_with_wiki
    r = client.post(
        "/api/qa/query",
        json={"question": "Tell me about CBL-B", "route_hint": "v1"},
    )
    body = r.json()
    assert body["retrieval_bundle"]["router"]["route"] == "v1"


# -------------------------------------------------------------------- POST /explain


def test_explain_deterministic_no_key(client_with_wiki) -> None:
    client, _ = client_with_wiki
    r = client.post(
        "/api/qa/explain",
        json={
            "question": "How are CBL-B and DEL screening connected?",
            "answer_slugs": ["cbl-b", "del-screening", "cbl-b-target"],
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "deterministic-only"
    # Three slugs -> three pairs.
    assert len(body["graph_pairs"]) == 3


# -------------------------------------------------------------------- POST /file-back


def test_file_back_writes_derived_page(client_with_wiki) -> None:
    client, wiki = client_with_wiki
    r = client.post(
        "/api/qa/file-back",
        json={
            "title": "Delphi ACS Release Narrative",
            "body": "## Status\n\nDerived synthesis from Cowork session.\n",
            "corpus": "protein-sciences",
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "filed"
    assert body["path"].startswith("derived/")
    out_path = Path(body["absolute_path"])
    assert out_path.exists()
    contents = out_path.read_text(encoding="utf-8")
    assert "title: Delphi ACS Release Narrative" in contents
    assert "type: derived" in contents
    assert "## Status" in contents


def test_file_back_slug_sanitized(client_with_wiki) -> None:
    client, _ = client_with_wiki
    r = client.post(
        "/api/qa/file-back",
        json={
            "title": "Some / illegal :: chars",
            "body": "body",
            "slug": "../../../escape-attempt",
        },
    )
    assert r.status_code == 200
    body = r.json()
    # Sanitized: no ../ should remain.
    assert "../" not in body["path"]
    assert body["path"].startswith("derived/")


# -------------------------------------------------------------------- POST /misses


def test_post_miss_records_entry(
    client_with_wiki,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, _ = client_with_wiki
    log = tmp_path / "misses.jsonl"
    monkeypatch.setenv("JOJO_QA_MISSES", str(log))
    r = client.post(
        "/api/qa/misses",
        json={
            "question": "What's the maintenance schedule for the Refeyn?",
            "reason": "no-candidates",
            "session_id": "test-001",
        },
    )
    assert r.status_code == 200
    assert r.json()["status"] == "logged"
    assert log.exists()
    line = log.read_text(encoding="utf-8").strip()
    data = json.loads(line)
    assert data["question"].startswith("What's the maintenance")


def test_get_misses_summary(
    client_with_wiki,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, _ = client_with_wiki
    log = tmp_path / "misses.jsonl"
    monkeypatch.setenv("JOJO_QA_MISSES", str(log))
    # Seed via the POST endpoint.
    client.post(
        "/api/qa/misses",
        json={"question": "q1", "reason": "no-candidates"},
    )
    r = client.get("/api/qa/misses")
    assert r.status_code == 200
    body = r.json()
    assert "total_misses" in body
    assert "by_route" in body
