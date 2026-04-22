from pathlib import Path

import pytest

from jojo_ingest.converters import ConverterNotFound, convert, is_supported


def test_is_supported_matrix():
    for ext in ("docx", "xlsx", "pptx", "pdf", "md", "txt"):
        assert is_supported(f"x.{ext}"), f"{ext} should be supported"
    assert not is_supported("x.psd")


def test_text_converter_roundtrips(sample_text: Path):
    out = convert(sample_text)
    assert "Plain-text note." in out
    assert "Second line." in out


def test_docx_produces_headings_and_bullets(sample_docx: Path):
    out = convert(sample_docx)
    # mammoth emits ATX-style headings:
    assert "Sample Protocol" in out
    assert "Procedure" in out
    # Bullet list items survive:
    assert "Step one" in out
    assert "Step two" in out


def test_xlsx_produces_one_table_per_sheet(sample_xlsx: Path):
    out = convert(sample_xlsx)
    assert "## Readings" in out
    assert "## Calibration" in out
    # Headers preserved:
    assert "Time (min)" in out
    assert "OD600" in out
    # Values preserved:
    assert "log phase" in out
    # Markdown table separator present:
    assert "| ---" in out


def test_pptx_produces_slide_sections(sample_pptx: Path):
    out = convert(sample_pptx)
    assert "## Slide 1" in out
    assert "## Slide 2" in out
    assert "Introduction" in out
    assert "Cmax" in out
    assert "AUC" in out


def test_pdf_produces_page_sections(sample_pdf: Path):
    out = convert(sample_pdf)
    assert "## Page 1" in out
    assert "## Page 2" in out
    assert "short PDF" in out
    assert "second page" in out.lower()


def test_unknown_extension_raises(tmp_path: Path):
    bad = tmp_path / "file.xyz"
    bad.write_bytes(b"\x00\x01\x02")
    with pytest.raises(ConverterNotFound):
        convert(bad)
