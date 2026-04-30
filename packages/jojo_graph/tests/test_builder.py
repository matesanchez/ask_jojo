"""Tests for jojo_graph.builder.

Most tests use the fallback path (graphify isn't installed in CI).
The graphify path is exercised when graphify is actually present.
"""

from __future__ import annotations

import json
import textwrap
from pathlib import Path

import pytest

from jojo_graph import builder


@pytest.fixture()
def fake_wiki(tmp_path: Path) -> Path:
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
    (tmp_path / "programs" / "a.md").write_text(
        "---\nslug: a\ntype: program\n---\n\nLinks: [[b]]\n",
        encoding="utf-8",
    )
    (tmp_path / "programs" / "b.md").write_text(
        "---\nslug: b\ntype: program\n---\n\nLinks: [[a]]\n",
        encoding="utf-8",
    )
    return tmp_path


def test_is_graphify_available_returns_bool() -> None:
    """Returns True or False; never raises."""
    assert isinstance(builder.is_graphify_available(), bool)


def test_rebuild_fallback_creates_artifacts(fake_wiki: Path) -> None:
    """When graphify isn't on PATH, the fallback builder produces all
    three artifacts under .graphify/."""
    artifacts = builder.rebuild(fake_wiki)
    assert artifacts.graph_html.exists()
    assert artifacts.graph_json.exists()
    assert artifacts.graph_report.exists()
    assert artifacts.node_count == 2
    assert artifacts.edge_count == 1


def test_fallback_html_is_valid_svg_doc(fake_wiki: Path) -> None:
    artifacts = builder.rebuild(fake_wiki)
    html = artifacts.graph_html.read_text(encoding="utf-8")
    assert html.startswith("<!doctype html>")
    assert "<svg" in html
    assert "</html>" in html


def test_fallback_report_has_summary(fake_wiki: Path) -> None:
    artifacts = builder.rebuild(fake_wiki)
    report = artifacts.graph_report.read_text(encoding="utf-8")
    assert "# Graph Report" in report
    assert "**Nodes:** 2" in report
    assert "**Edges:** 1" in report


def test_stats_reads_from_artifacts(fake_wiki: Path) -> None:
    builder.rebuild(fake_wiki)
    s = builder.stats(fake_wiki)
    # The fallback path returns rich stats from qa_graph.stats().
    # The graphify path would return a slimmer set; both shapes have
    # node_count + edge_count.
    assert s["node_count"] == 2
    assert s["edge_count"] == 1
    assert s["source"] in ("graphify", "fallback")


def test_html_path_and_report_path(fake_wiki: Path) -> None:
    """Path helpers point at the right location even before rebuild."""
    h = builder.html_path(fake_wiki)
    r = builder.report_path(fake_wiki)
    assert h.name == "graph.html"
    assert r.name == "GRAPH_REPORT.md"
    assert h.parent.name == ".graphify"


def test_rebuild_emits_graphify_compatible_json(fake_wiki: Path) -> None:
    """The fallback graph.json has the same shape as graphify's output
    (nodes / edges / adjacency keys) so the Graph tab can consume
    either."""
    artifacts = builder.rebuild(fake_wiki)
    data = json.loads(artifacts.graph_json.read_text(encoding="utf-8"))
    assert "nodes" in data
    assert "edges" in data


def test_used_fallback_flag(fake_wiki: Path) -> None:
    """When graphify isn't installed, used_fallback should be True."""
    if builder.is_graphify_available():
        pytest.skip("graphify is installed; can't test fallback")
    artifacts = builder.rebuild(fake_wiki)
    assert artifacts.used_fallback is True
