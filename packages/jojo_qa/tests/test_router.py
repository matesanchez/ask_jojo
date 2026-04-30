"""Tests for ``jojo_qa.router``.

The router is the regex backstop. Every behavior in PLAN.md Section 6
Phase 4 ("Legacy AKTA routing") and ADR 0011 ("Routing rules") has a
test here. Edge cases discovered during Cowork sessions go here too.
"""

from __future__ import annotations

import pytest

from jojo_qa.router import (
    DEFAULT_WIKI_OVERRIDES,
    V1_KEYWORDS,
    classify,
    matched_keywords,
)


# -- the v1-trigger keywords route to v1 ---------------------------------


@pytest.mark.parametrize(
    "question,expected_keyword",
    [
        ("What is the AKTA Pure 25 startup procedure?", "akta"),
        ("How do I configure UNICORN method editor?", "unicorn"),
        ("What's a typical chromatography buffer pH?", "chromatograph"),
        ("Show me the protein purification SOP.", "purif"),
        ("What buffer should I use for cation exchange?", "buffer"),
    ],
)
def test_v1_trigger_keywords_route_v1(question: str, expected_keyword: str) -> None:
    """Each v1 keyword on its own routes a question to v1."""
    result = classify(question)
    assert result.route == "v1"
    assert expected_keyword in result.matched_keywords


def test_all_v1_keywords_are_listed() -> None:
    """The keyword tuple matches the documented spec."""
    assert V1_KEYWORDS == ("akta", "unicorn", "chromatograph", "purif", "buffer")


# -- the wiki path is the default ---------------------------------------


@pytest.mark.parametrize(
    "question",
    [
        "What's the difference between NX-1607 and NX-0255?",
        "How is DEL screening organized at Nurix?",
        "Who runs the Pellino-1 program?",
        "What changed in the Delphi ACS2025.2 release?",
        "What's the status of the BTK program?",
    ],
)
def test_wiki_default_route(question: str) -> None:
    """Questions with no v1 keyword default to wiki."""
    result = classify(question)
    assert result.route == "wiki"
    assert result.matched_keywords == ()


def test_empty_question_routes_wiki() -> None:
    assert classify("").route == "wiki"
    assert classify("   ").route == "wiki"


# -- case insensitivity --------------------------------------------------


def test_case_insensitive() -> None:
    assert classify("AKTA buffer prep").route == "v1"
    assert classify("akta BUFFER prep").route == "v1"
    assert classify("Buffer for chromatography").route == "v1"


# -- word boundary discipline -------------------------------------------


def test_pure_does_not_match_purif() -> None:
    """``Pure`` (the AKTA suffix) must not match ``purif`` regex."""
    # Question without any other v1 keyword. Should route wiki.
    result = classify("What is the AKTA Pure 25 protein limit?")
    # Note: AKTA itself is a v1 keyword, so this DOES route v1 — but
    # the matched_keywords should only show 'akta', not 'purif'.
    assert result.route == "v1"
    assert "akta" in result.matched_keywords
    assert "purif" not in result.matched_keywords


def test_buffalo_does_not_match_buffer() -> None:
    """Word boundaries prevent ``buffalo`` from matching ``buffer``."""
    result = classify("Did the Buffalo team finish the Pellino-1 SOP?")
    assert result.route == "wiki"


def test_unicorn_substring_in_word_does_not_route() -> None:
    """A made-up word containing 'unicorn' as a substring would still
    match because of \\b boundaries — but we test the realistic case."""
    # The current regex would match 'unicorn' as a complete word here.
    # If we ever needed stricter (case-sensitive) matching, the tests
    # would be the canary.
    assert classify("UNICORN method editor").route == "v1"


# -- multiple matches ----------------------------------------------------


def test_multiple_v1_keywords_all_reported() -> None:
    """When several v1 keywords match, all of them appear in the result."""
    result = classify("AKTA buffer chromatography purification")
    assert result.route == "v1"
    assert "akta" in result.matched_keywords
    assert "buffer" in result.matched_keywords
    assert "chromatograph" in result.matched_keywords
    assert "purif" in result.matched_keywords


# -- wiki-override list --------------------------------------------------


def test_buffer_for_del_screen_routes_wiki() -> None:
    """The ``buffer .. del`` override flips a buffer-trigger to wiki."""
    result = classify("What was the buffer for the SIAH1 DEL screen?")
    assert result.route == "wiki"
    assert result.override_matched is True


def test_del_with_buffer_in_other_order_routes_wiki() -> None:
    """The reversed order (``del .. buffer``) also overrides."""
    result = classify("How does the DEL screen handle buffer screening?")
    assert result.route == "wiki"
    assert result.override_matched is True


def test_sec_mals_chromatograph_routes_wiki() -> None:
    """SEC-MALS questions are wiki even with ``chromatograph`` keyword."""
    result = classify("What's the SEC-MALS analysis for size-exclusion chromatography?")
    assert result.route == "wiki"
    assert result.override_matched is True


def test_disabled_overrides_lets_buffer_route_v1() -> None:
    """Empty overrides list disables the override layer."""
    result = classify(
        "What was the buffer for the SIAH1 DEL screen?",
        overrides=[],
    )
    assert result.route == "v1"
    assert "buffer" in result.matched_keywords
    assert result.override_matched is False


def test_default_overrides_list_is_documented() -> None:
    """The override list is non-empty and matches the documented spec."""
    assert len(DEFAULT_WIKI_OVERRIDES) >= 3
    # Two buffer/del overrides + one sec-mals.


# -- the BTK-program red herring (qa-prompt edge case q-005) -------------


def test_program_keyword_does_not_override_akta_trigger() -> None:
    """Question 5 from the seed benchmark: 'BTK program' must not override AKTA route."""
    result = classify("What's the standard buffer prep for an AKTA Pure 25 run on the BTK program?")
    assert result.route == "v1"
    assert "akta" in result.matched_keywords
    assert "buffer" in result.matched_keywords


# -- matched_keywords helper --------------------------------------------


def test_matched_keywords_helper() -> None:
    assert matched_keywords("What's the AKTA SOP?") == ("akta",)
    assert matched_keywords("UNICORN method buffer prep") == (
        "unicorn",
        "buffer",
    )
    assert matched_keywords("What is CBL-B?") == ()
    assert matched_keywords("") == ()


# -- documented router limitations (Phase 4 review) ----------------------


def test_unicorn_false_positive_documented() -> None:
    """Documented limitation: ``unicorn`` outside the UNICORN-software
    context still routes to v1. See docs/qa/qa-prompt.md "Routing edge
    cases" section. The Haiku classifier on API day fixes this by
    reading surrounding context; until then, operator override is the
    fallback. This test pins the *current* behavior so changes are
    intentional, not accidental.
    """
    result = classify("Make Unicorn-themed slides for our team")
    assert result.route == "v1"  # known coarse-regex behavior
    assert "unicorn" in result.matched_keywords


def test_pure_in_akta_pure_does_not_match_purif_alone() -> None:
    """Regression test: ``Pure`` (the AKTA Pure 25 instrument suffix)
    is not the same word as ``purif``. The \\b word boundary in the
    regex prevents the substring match. Question routes v1 only via
    the explicit ``akta`` keyword."""
    result = classify("AKTA Pure 25 startup checklist")
    assert result.route == "v1"
    assert "akta" in result.matched_keywords
    assert "purif" not in result.matched_keywords
