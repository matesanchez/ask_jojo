"""Tests for ``jojo_qa.router``.

As of 2026-06-05 v1 routing is RETIRED. v2 is the single, all-encompassing
knowledge surface: every question routes to ``wiki`` and is answered from it.
Nothing is deflected to the legacy AKTA/UNICORN system. ``matched_keywords``
still reports legacy keyword hits (for the UI badge), but they do not change
the route.
"""

from __future__ import annotations

import pytest

from jojo_qa.router import V1_KEYWORDS, classify, matched_keywords


@pytest.mark.parametrize(
    "question",
    [
        "What is the AKTA Pure 25 startup procedure?",
        "How do I configure UNICORN method editor?",
        "Show me the protein purification SOP.",
        "What buffer should I use for cation exchange?",
        "What's a typical chromatography buffer pH?",
        "What is the ADAR1 purification protocol?",
        "What's the difference between NX-1607 and NX-0255?",
        "How is DEL screening organized at Nurix?",
        "Make Unicorn-themed slides for our team",
    ],
)
def test_everything_routes_wiki(question: str) -> None:
    """No question is deflected; everything is answered from the wiki."""
    assert classify(question).route == "wiki"


def test_empty_question_routes_wiki() -> None:
    assert classify("").route == "wiki"
    assert classify("   ").route == "wiki"


def test_overrides_param_is_accepted_and_noop() -> None:
    """The overrides kwarg is still accepted (API compat) and never flips to v1."""
    assert classify("AKTA buffer prep", overrides=[]).route == "wiki"
    assert classify("AKTA buffer prep", overrides=["whatever"]).route == "wiki"


def test_matched_keywords_still_reported_for_badge() -> None:
    """Legacy keywords are still surfaced (informational) but do not deflect."""
    r = classify("What is the AKTA SOP?")
    assert r.route == "wiki"
    assert "akta" in r.matched_keywords  # reported, but route is wiki


def test_matched_keywords_helper() -> None:
    assert matched_keywords("What's the AKTA SOP?") == ("akta",)
    assert matched_keywords("UNICORN method editor") == ("unicorn",)
    assert matched_keywords("What is CBL-B?") == ()
    assert matched_keywords("") == ()


def test_v1_keywords_constant_unchanged() -> None:
    """The keyword constant is retained for matched_keywords/badge use."""
    assert V1_KEYWORDS == ("akta", "unicorn")
