"""Tests for ``jojo_qa.graph``."""

from __future__ import annotations

import json
import textwrap
from pathlib import Path

import pytest

from jojo_qa import graph as graph_mod


@pytest.fixture()
def fake_wiki(tmp_path: Path) -> Path:
    """Three pages with bidirectional wikilinks for graph construction.

    Layout:
        cbl-b   <->  cbl-b-target
        cbl-b   <->  del-screening
        cbl-b-target -- (no edge to del-screening)
    """
    (tmp_path / "_index.md").write_text(
        textwrap.dedent(
            """\
            # Wiki Index

            ## Program

            - [[cbl-b|CBL-B Program]] — `programs/cbl-b.md`
            - [[del-screening|DEL Screening Program]] — `programs/del-screening.md`

            ## Target

            - [[cbl-b-target|CBL-B Target]] — `targets/cbl-b.md`
            """
        ),
        encoding="utf-8",
    )
    (tmp_path / "programs").mkdir()
    (tmp_path / "targets").mkdir()

    (tmp_path / "programs" / "cbl-b.md").write_text(
        "---\nslug: cbl-b\n---\n\nLinks: [[cbl-b-target]] and [[del-screening]].\n",
        encoding="utf-8",
    )
    (tmp_path / "programs" / "del-screening.md").write_text(
        "---\nslug: del-screening\n---\n\nLinks: [[cbl-b]].\n",
        encoding="utf-8",
    )
    (tmp_path / "targets" / "cbl-b.md").write_text(
        "---\nslug: cbl-b-target\n---\n\nNo outgoing links here.\n",
        encoding="utf-8",
    )
    return tmp_path


def test_build_basic(fake_wiki: Path) -> None:
    g = graph_mod.build(fake_wiki)
    assert set(g.nodes.keys()) == {"cbl-b", "cbl-b-target", "del-screening"}
    edges_set = {tuple(sorted(e)) for e in g.edges}
    assert ("cbl-b", "cbl-b-target") in edges_set
    assert ("cbl-b", "del-screening") in edges_set


def test_adjacency_is_undirected(fake_wiki: Path) -> None:
    g = graph_mod.build(fake_wiki)
    assert "cbl-b" in g.adjacency["cbl-b-target"]
    assert "cbl-b-target" in g.adjacency["cbl-b"]


def test_adjacency_dedups(fake_wiki: Path) -> None:
    """Each adjacency list has unique entries."""
    g = graph_mod.build(fake_wiki)
    for slug, neighbors in g.adjacency.items():
        _ = slug
        assert len(neighbors) == len(set(neighbors))


def test_no_self_loops(fake_wiki: Path) -> None:
    g = graph_mod.build(fake_wiki)
    for a, b in g.edges:
        assert a != b


def test_skips_broken_links(tmp_path: Path) -> None:
    """A wikilink to a slug not in the index must be skipped."""
    (tmp_path / "_index.md").write_text(
        "# Wiki Index\n\n## Program\n\n- [[a|A]] — `programs/a.md`\n",
        encoding="utf-8",
    )
    (tmp_path / "programs").mkdir()
    (tmp_path / "programs" / "a.md").write_text(
        "Body links to [[nonexistent-slug]].\n",
        encoding="utf-8",
    )
    g = graph_mod.build(tmp_path)
    assert g.nodes == {"a": {"title": "A", "type": "program", "path": "programs/a.md"}}
    assert g.edges == []


def test_write_then_load_roundtrip(fake_wiki: Path) -> None:
    g = graph_mod.build(fake_wiki)
    out = graph_mod.write(g, fake_wiki)
    assert out.exists()
    g2 = graph_mod.load(fake_wiki)
    assert set(g2.nodes.keys()) == set(g.nodes.keys())
    assert set(g2.edges) == set(g.edges)


def test_write_emits_valid_json(fake_wiki: Path) -> None:
    g = graph_mod.build(fake_wiki)
    out = graph_mod.write(g, fake_wiki)
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert "nodes" in payload
    assert "edges" in payload
    assert "adjacency" in payload
    assert payload["schema_version"] == "0.1.0"


def test_graphify_compatible_node_shape(fake_wiki: Path) -> None:
    """Graphify expects ``{"slug", "title", "type", "path"}`` per node."""
    g = graph_mod.build(fake_wiki)
    out_payload = g.to_json()
    for node in out_payload["nodes"]:
        assert "slug" in node
        assert "title" in node
        assert "type" in node
        assert "path" in node


# -- BFS shortest-path --------------------------------------------------


def test_shortest_path_direct(fake_wiki: Path) -> None:
    g = graph_mod.build(fake_wiki)
    path = graph_mod.shortest_path(g, "cbl-b", "cbl-b-target")
    assert path == ["cbl-b", "cbl-b-target"]


def test_shortest_path_two_hops(fake_wiki: Path) -> None:
    g = graph_mod.build(fake_wiki)
    path = graph_mod.shortest_path(g, "cbl-b-target", "del-screening")
    assert path == ["cbl-b-target", "cbl-b", "del-screening"]


def test_shortest_path_same_node(fake_wiki: Path) -> None:
    g = graph_mod.build(fake_wiki)
    assert graph_mod.shortest_path(g, "cbl-b", "cbl-b") == ["cbl-b"]


def test_shortest_path_missing_node(fake_wiki: Path) -> None:
    g = graph_mod.build(fake_wiki)
    assert graph_mod.shortest_path(g, "cbl-b", "nonexistent") is None
    assert graph_mod.shortest_path(g, "nonexistent", "cbl-b") is None


def test_shortest_path_disconnected(tmp_path: Path) -> None:
    """Two components with no edge between them -> None path."""
    (tmp_path / "_index.md").write_text(
        textwrap.dedent(
            """\
            # Wiki Index

            ## Program

            - [[island-a|Island A]] — `programs/island-a.md`
            - [[island-b|Island B]] — `programs/island-b.md`
            """
        ),
        encoding="utf-8",
    )
    (tmp_path / "programs").mkdir()
    (tmp_path / "programs" / "island-a.md").write_text("No links.\n", encoding="utf-8")
    (tmp_path / "programs" / "island-b.md").write_text("No links.\n", encoding="utf-8")
    g = graph_mod.build(tmp_path)
    assert graph_mod.shortest_path(g, "island-a", "island-b") is None


# -- neighbors ---------------------------------------------------------


def test_neighbors_one_hop(fake_wiki: Path) -> None:
    g = graph_mod.build(fake_wiki)
    one_hop = graph_mod.neighbors(g, "cbl-b", hops=1)
    assert one_hop == {"cbl-b-target", "del-screening"}


def test_neighbors_two_hops(fake_wiki: Path) -> None:
    g = graph_mod.build(fake_wiki)
    # cbl-b-target's 1-hop is just cbl-b; 2-hop adds del-screening.
    two_hop = graph_mod.neighbors(g, "cbl-b-target", hops=2)
    assert two_hop == {"cbl-b", "del-screening"}


def test_neighbors_zero_hops_returns_empty(fake_wiki: Path) -> None:
    g = graph_mod.build(fake_wiki)
    assert graph_mod.neighbors(g, "cbl-b", hops=0) == set()


def test_neighbors_missing_slug_returns_empty(fake_wiki: Path) -> None:
    g = graph_mod.build(fake_wiki)
    assert graph_mod.neighbors(g, "nonexistent", hops=1) == set()


# -- statistics --------------------------------------------------------


def test_stats_basic(fake_wiki: Path) -> None:
    g = graph_mod.build(fake_wiki)
    s = graph_mod.stats(g)
    assert s["node_count"] == 3
    assert s["edge_count"] == 2
    assert s["orphan_count"] == 0
    assert s["max_degree"] == 2  # cbl-b has two neighbors
    assert s["connected_components"] == 1


def test_stats_disconnected_components(tmp_path: Path) -> None:
    (tmp_path / "_index.md").write_text(
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
    (tmp_path / "programs").mkdir()
    (tmp_path / "programs" / "a.md").write_text("Lonely.\n", encoding="utf-8")
    (tmp_path / "programs" / "b.md").write_text("Lonely.\n", encoding="utf-8")
    g = graph_mod.build(tmp_path)
    s = graph_mod.stats(g)
    assert s["connected_components"] == 2
    assert s["orphan_count"] == 2
