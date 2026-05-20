"""End-to-end tests for /api/output/.

Mirrors the test_qa_endpoints.py pattern: minimal fake wiki, hit the
endpoints through TestClient. Optional-deps renderers (docx/pptx/pdf)
get skipped when their library isn't installed.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client_with_wiki(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    wiki = tmp_path / "ask_jojo_wiki"
    wiki.mkdir()
    (wiki / "outputs").mkdir()
    monkeypatch.setenv("JOJO_WIKI_ROOT", str(wiki))

    # Force the matplotlib sandbox into in-process mode (no subprocess).
    # The sandbox runner imports the POSIX-only ``resource`` module; skip the
    # flag on Windows where that module is absent (matplotlib tests are
    # already skipped via pytest.importorskip("matplotlib") on that platform).
    try:
        from jojo_output.sandbox import runner as runner_mod  # noqa: PLC0415

        monkeypatch.setattr(runner_mod, "RUN_IN_PROCESS", True)
    except ModuleNotFoundError:
        pass  # resource module not available on Windows

    from backend.main import app

    return TestClient(app), wiki


# ---------------------------------------------------------------- format classifier


def test_classify_format_marp(client_with_wiki) -> None:
    client, _ = client_with_wiki
    r = client.get("/api/output/classify-format", params={"q": "Make slides comparing X and Y"})
    assert r.status_code == 200
    body = r.json()
    assert body["format"] == "marp"
    assert body["confidence"] == "high"


def test_classify_format_default_markdown(client_with_wiki) -> None:
    client, _ = client_with_wiki
    r = client.get("/api/output/classify-format", params={"q": "What is CBL-B?"})
    assert r.status_code == 200
    assert r.json()["format"] == "markdown"


def test_list_formats(client_with_wiki) -> None:
    client, _ = client_with_wiki
    r = client.get("/api/output/formats")
    assert r.status_code == 200
    formats = r.json()["formats"]
    assert "markdown" in formats
    assert "marp" in formats
    assert len(formats) == 9


@pytest.mark.skipif(
    __import__("sys").platform == "win32",
    reason="sandbox runner imports POSIX-only 'resource' module; skip on Windows",
)
def test_list_plot_types(client_with_wiki) -> None:
    client, _ = client_with_wiki
    r = client.get("/api/output/plot-types")
    assert r.status_code == 200
    types = r.json()["plot_types"]
    assert "bar" in types
    assert "line" in types


# ---------------------------------------------------------------- render


def test_render_markdown(client_with_wiki) -> None:
    client, _ = client_with_wiki
    r = client.post(
        "/api/output/render",
        json={
            "format": "markdown",
            "spec": {"body": "Hello [[cbl-b|CBL-B]]", "title": "Test"},
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["format"] == "markdown"
    assert "[CBL-B](/wiki?slug=cbl-b)" in body["text"]
    assert "# Test" in body["text"]


def test_render_table(client_with_wiki) -> None:
    client, _ = client_with_wiki
    r = client.post(
        "/api/output/render",
        json={
            "format": "table",
            "spec": {
                "columns": ["Compound", "IC50"],
                "rows": [["NX-1607", 10], ["NX-0255", 35]],
            },
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["format"] == "table"
    assert "| Compound | IC50 |" in body["markdown"]
    assert "Compound,IC50" in body["csv"]


def test_render_marp(client_with_wiki) -> None:
    client, _ = client_with_wiki
    r = client.post(
        "/api/output/render",
        json={
            "format": "marp",
            "spec": {
                "title": "Test deck",
                "slides": [{"title": "S1", "body": "Body"}],
            },
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert "marp: true" in body["text"]
    assert "# S1" in body["text"]


def test_render_mermaid_passthrough(client_with_wiki) -> None:
    client, _ = client_with_wiki
    r = client.post(
        "/api/output/render",
        json={
            "format": "mermaid",
            "spec": {"body": "graph TD\n    A --> B"},
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert "```mermaid" in body["text"]
    assert "A --> B" in body["text"]


def test_render_matplotlib_inline(client_with_wiki) -> None:
    pytest.importorskip("matplotlib")
    client, _ = client_with_wiki
    r = client.post(
        "/api/output/render",
        json={
            "format": "matplotlib",
            "spec": {
                "plot_type": "bar",
                "title": "Test",
                "series": [{"label": "a", "x": ["x", "y"], "y": [1.0, 2.0]}],
            },
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["bytes_b64"]


def test_render_matplotlib_to_file(client_with_wiki) -> None:
    pytest.importorskip("matplotlib")
    client, wiki = client_with_wiki
    r = client.post(
        "/api/output/render",
        json={
            "format": "matplotlib",
            "spec": {
                "plot_type": "bar",
                "series": [{"label": "a", "x": ["x"], "y": [1.0]}],
            },
            "out_subpath": "test-chart.png",
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["out_path"] == "outputs/test-chart.png"
    assert (wiki / "outputs" / "test-chart.png").exists()


def test_render_validation_error_returns_422(client_with_wiki) -> None:
    pytest.importorskip("matplotlib")
    client, _ = client_with_wiki
    r = client.post(
        "/api/output/render",
        json={
            "format": "matplotlib",
            "spec": {"plot_type": "pie"},  # not a real plot type
        },
    )
    assert r.status_code == 422


def test_render_path_traversal_rejected(client_with_wiki) -> None:
    client, _ = client_with_wiki
    r = client.post(
        "/api/output/render",
        json={
            "format": "markdown",
            "spec": {"body": "x"},
            "out_subpath": "../../etc/passwd",
        },
    )
    assert r.status_code == 400


def test_render_unsupported_format(client_with_wiki) -> None:
    client, _ = client_with_wiki
    r = client.post(
        "/api/output/render",
        json={"format": "magic", "spec": {}},
    )
    # 'magic' fails Literal validation.
    assert r.status_code == 422


def test_render_plotly_inline(client_with_wiki) -> None:
    """Plotly render returns status ok with an HTML fragment."""
    client, _ = client_with_wiki
    r = client.post(
        "/api/output/render",
        json={
            "format": "plotly",
            "spec": {
                "plot_type": "bar",
                "title": "My Bar Chart",
                "series": [{"label": "A", "x": ["x1", "x2"], "y": [1.0, 2.0]}],
            },
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["format"] == "plotly"
    assert '<div id="plotly-' in body["html"]
    assert "Plotly.newPlot(" in body["html"]


def test_render_plotly_to_file(client_with_wiki) -> None:
    """Plotly render with out_subpath writes a file and returns the path."""
    client, wiki = client_with_wiki
    r = client.post(
        "/api/output/render",
        json={
            "format": "plotly",
            "spec": {
                "plot_type": "line",
                "series": [{"label": "s", "x": [1, 2], "y": [3, 4]}],
            },
            "out_subpath": "test-plotly.html",
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["out_path"] == "outputs/test-plotly.html"
    assert (wiki / "outputs" / "test-plotly.html").exists()


def test_render_plotly_invalid_plot_type_returns_422(client_with_wiki) -> None:
    """An unsupported plot_type raises HTTP 422."""
    client, _ = client_with_wiki
    r = client.post(
        "/api/output/render",
        json={"format": "plotly", "spec": {"plot_type": "treemap"}},
    )
    assert r.status_code == 422


# ---------------------------------------------------------------- file-back


def test_file_back_writes_outputs_page(client_with_wiki) -> None:
    client, wiki = client_with_wiki
    r = client.post(
        "/api/output/file-back",
        json={
            "title": "Test memo",
            "body": "## Summary\n\nMemo body.",
            "output_format": "markdown",
            "source_question": "Make me a memo about X",
            "source_session_id": "cowork-test-001",
            "parent_slugs": ["cbl-b"],
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "filed"
    assert body["path"].startswith("outputs/")
    page = (wiki / body["path"])
    assert page.exists()
    text = page.read_text()
    assert "type: output" in text
    assert "output_format: markdown" in text
    assert "source_session_id: cowork-test-001" in text


# ---------------------------------------------------------------- list / page


def test_list_outputs_empty(client_with_wiki) -> None:
    client, _ = client_with_wiki
    r = client.get("/api/output/list")
    assert r.status_code == 200
    assert r.json()["total"] == 0


def test_list_outputs_after_file_back(client_with_wiki) -> None:
    client, _ = client_with_wiki
    client.post(
        "/api/output/file-back",
        json={"title": "Test", "body": "x"},
    )
    r = client.get("/api/output/list")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 1
    assert body["outputs"][0]["title"] == "Test"
    assert body["outputs"][0]["output_format"] == "markdown"


def test_get_page_path_traversal_rejected(client_with_wiki) -> None:
    client, _ = client_with_wiki
    r = client.get("/api/output/page", params={"path": "../etc/passwd"})
    assert r.status_code == 400


def test_get_page_not_found(client_with_wiki) -> None:
    client, _ = client_with_wiki
    r = client.get("/api/output/page", params={"path": "outputs/nope.md"})
    assert r.status_code == 404
