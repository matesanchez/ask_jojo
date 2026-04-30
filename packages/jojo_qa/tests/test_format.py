"""Tests for ``jojo_qa.format``.

Same shape as ``test_router.py``: pin the regex behavior so future
changes to the classifier are intentional. Edge cases discovered
during Cowork sessions get added here as regression tests.
"""

from __future__ import annotations

import pytest

from jojo_qa.format import (
    FormatResult,
    available_formats,
    classify,
)


# -- happy paths ----------------------------------------------------------


@pytest.mark.parametrize(
    "question,expected",
    [
        ("What is CBL-B?", "markdown"),
        ("Explain the DEL screening pipeline.", "markdown"),
        ("Tell me about Pellino-1.", "markdown"),
        ("Make slides comparing NX-1607 and NX-0255.", "marp"),
        ("Create a slide deck for the Q1 Delphi review.", "marp"),
        ("Plot CBL-B IC50 vs concentration.", "matplotlib"),
        ("Make a histogram of confidence scores.", "matplotlib"),
        ("Make an interactive chart of throughput.", "plotly"),
        ("Compare NX-1607 and NX-0255 in a table.", "table"),
        ("Diagram the relationships between programs and targets.", "mermaid"),
        ("Write me a memo about the 2025 research goals.", "docx"),
        ("Export the answer as a PDF.", "pdf"),
        ("Give me a PowerPoint of the BTK status.", "pptx"),
    ],
)
def test_classify_happy_paths(question: str, expected: str) -> None:
    result = classify(question)
    assert result.format == expected, f"{question!r} -> got {result.format} expected {expected}"


def test_default_markdown_for_unrelated_question() -> None:
    result = classify("Who reviewed the 2025 Delphi data quality audit?")
    assert result.format == "markdown"
    assert result.confidence == "low"


def test_empty_question() -> None:
    result = classify("")
    assert result.format == "markdown"
    assert result.confidence == "low"


def test_whitespace_question() -> None:
    assert classify("   \n\t").format == "markdown"


# -- confidence bucketing ------------------------------------------------


def test_explicit_keyword_high_confidence() -> None:
    result = classify("Export the answer as a PDF.")
    assert result.confidence == "high"


def test_default_low_confidence() -> None:
    result = classify("What is CBL-B?")
    assert result.confidence == "low"


# -- candidate scores ----------------------------------------------------


def test_candidate_scores_includes_best() -> None:
    """The returned dict includes scores for every format that triggered."""
    result = classify("Export the comparison table as a PDF.")
    # Both pdf and table patterns should fire.
    assert "pdf" in result.candidate_scores
    assert "table" in result.candidate_scores


def test_explicit_format_outranks_implicit() -> None:
    """Explicit ``as a PDF`` wins over implicit memo/report when both fire."""
    result = classify("Write me a memo and export it as a PDF.")
    assert result.format == "pdf"


# -- matched keywords ----------------------------------------------------


def test_matched_keywords_populated() -> None:
    result = classify("Make slides comparing NX-1607 and NX-0255.")
    assert result.matched_keywords
    # Expect something like 'Make slides' or 'make slides comparing'.
    assert any("slides" in m.lower() for m in result.matched_keywords)


# -- edge cases / known limitations -------------------------------------


def test_chart_keyword_with_no_vs() -> None:
    """Soft pattern: 'show me a chart of X' triggers matplotlib."""
    result = classify("Make a chart of throughput by month.")
    assert result.format == "matplotlib"


def test_diagram_keyword_picks_mermaid() -> None:
    result = classify("Diagram the JoJo Bot architecture.")
    assert result.format == "mermaid"


def test_memo_does_not_match_with_table_keyword() -> None:
    """The docx pattern explicitly excludes questions that also mention
    table / chart / plot / slide / deck so the more specific format wins."""
    result = classify("Write me a memo with a comparison in a table.")
    # 'in a table' wins (explicit table keyword).
    assert result.format == "table"


def test_format_result_is_frozen() -> None:
    """``FormatResult`` is frozen — mutating attributes raises."""
    r = classify("test")
    with pytest.raises(Exception):
        r.format = "marp"  # type: ignore[misc]


# -- public surface ------------------------------------------------------


def test_available_formats_complete() -> None:
    formats = available_formats()
    assert "markdown" in formats
    assert "marp" in formats
    assert "matplotlib" in formats
    assert "table" in formats
    assert "mermaid" in formats
    assert len(formats) == 9
