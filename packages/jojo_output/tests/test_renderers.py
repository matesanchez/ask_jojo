"""Tests for the deterministic-renderer family.

The renderers that don't require optional system dependencies
(matplotlib via the sandbox; weasyprint for PDFs; python-docx /
python-pptx for Office) are exercised here directly. Optional-deps
renderers get skipped gracefully when their library is absent.
"""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("pydantic")

from jojo_output.renderers import (
    MarkdownSpec,
    MarpSpec,
    TableSpec,
    render_markdown,
    render_marp,
    render_table,
)
from jojo_output.renderers.marp import Slide
from jojo_output.renderers.table import render_csv, render_xlsx

# ---------------------------------------------------------------- markdown


def test_markdown_passthrough() -> None:
    spec = MarkdownSpec(body="Hello **world**", rewrite_wikilinks=False)
    assert render_markdown(spec) == "Hello **world**"


def test_markdown_wikilink_rewrite() -> None:
    spec = MarkdownSpec(body="See [[cbl-b|CBL-B]] and [[del-screening]].")
    out = render_markdown(spec)
    assert "[CBL-B](/wiki?slug=cbl-b)" in out
    assert "[del-screening](/wiki?slug=del-screening)" in out


def test_markdown_title_prepended() -> None:
    spec = MarkdownSpec(body="Body content.", title="My Title")
    out = render_markdown(spec)
    assert out.startswith("# My Title\n\n")


def test_markdown_custom_wikilink_base() -> None:
    spec = MarkdownSpec(body="See [[cbl-b]].", wikilink_base="/wiki/")
    out = render_markdown(spec)
    assert "[cbl-b](/wiki/cbl-b)" in out


# ---------------------------------------------------------------- table


def test_table_markdown() -> None:
    spec = TableSpec(
        columns=["Compound", "IC50 (nM)"],
        rows=[["NX-1607", 10], ["NX-0255", 35]],
    )
    md = render_table(spec)["markdown"]
    assert "| Compound | IC50 (nM) |" in md
    assert "| NX-1607 | 10 |" in md
    assert "| NX-0255 | 35 |" in md
    # Separator row.
    assert "| --- | --- |" in md


def test_table_csv() -> None:
    spec = TableSpec(
        columns=["a", "b"],
        rows=[[1, 2], [3, 4]],
    )
    csv_text = render_csv(spec)
    assert csv_text.splitlines()[0] == "a,b"
    assert "1,2" in csv_text


def test_table_with_title_and_footnote() -> None:
    spec = TableSpec(
        columns=["x"],
        rows=[[1]],
        title="A Title",
        footnote="Note.",
    )
    md = render_table(spec)["markdown"]
    assert "**A Title**" in md
    assert "_Note._" in md


def test_table_pipe_escaped_in_cells() -> None:
    spec = TableSpec(columns=["a"], rows=[["pipe|inside"]])
    md = render_table(spec)["markdown"]
    assert "pipe\\|inside" in md


def test_table_xlsx_writes_file(tmp_path: Path) -> None:
    pytest.importorskip("openpyxl")
    spec = TableSpec(columns=["a", "b"], rows=[[1, 2]])
    out = tmp_path / "table.xlsx"
    render_xlsx(spec, out)
    assert out.exists()
    assert out.stat().st_size > 100


# ---------------------------------------------------------------- marp


def test_marp_minimal() -> None:
    spec = MarpSpec(
        title="Test deck",
        slides=[Slide(title="Slide 1", body="Body 1"), Slide(title="Slide 2", bullets=["a", "b"])],
    )
    out = render_marp(spec)
    assert out.startswith("---\nmarp: true\n")
    assert "# Slide 1" in out
    assert "Body 1" in out
    assert "- a" in out
    assert "- b" in out


def test_marp_empty_deck() -> None:
    spec = MarpSpec()
    out = render_marp(spec)
    assert "marp: true" in out
    assert "(empty deck)" in out


def test_marp_speaker_notes() -> None:
    spec = MarpSpec(slides=[Slide(title="X", notes="Speaker reminder")])
    out = render_marp(spec)
    assert "<!-- Speaker reminder -->" in out


def test_marp_paginate_off() -> None:
    spec = MarpSpec(paginate=False, slides=[Slide(title="x")])
    out = render_marp(spec)
    assert "paginate: false" in out


def test_marp_too_many_slides_rejected() -> None:
    with pytest.raises(Exception, match="too many slides"):
        MarpSpec(slides=[Slide(title=f"s{i}") for i in range(80)])


def test_marp_too_many_bullets_rejected() -> None:
    with pytest.raises(Exception, match="too many bullets"):
        Slide(bullets=[f"b{i}" for i in range(20)])


# ---------------------------------------------------------------- docx (optional)


def test_docx_renders_when_python_docx_available(tmp_path: Path) -> None:
    pytest.importorskip("docx")
    from jojo_output.renderers.docx_renderer import (
        DocxSection,
        DocxSpec,
        render_docx,
    )

    spec = DocxSpec(
        title="Test Memo",
        sections=[
            DocxSection(heading="Overview", body="Some prose."),
            DocxSection(heading="Findings", bullets=["a", "b", "c"]),
        ],
    )
    out = tmp_path / "memo.docx"
    render_docx(spec, out)
    assert out.exists()
    assert out.stat().st_size > 1000


# ---------------------------------------------------------------- pptx (optional)


def test_pptx_renders_when_python_pptx_available(tmp_path: Path) -> None:
    pytest.importorskip("pptx")
    from jojo_output.renderers.pptx_renderer import (
        PptxSlide,
        PptxSpec,
        render_pptx,
    )

    spec = PptxSpec(
        title="Test Deck",
        slides=[
            PptxSlide(layout="title_content", title="Slide 1", bullets=["a", "b"]),
            PptxSlide(layout="section", title="Section break"),
        ],
    )
    out = tmp_path / "deck.pptx"
    render_pptx(spec, out)
    assert out.exists()
    assert out.stat().st_size > 1000
