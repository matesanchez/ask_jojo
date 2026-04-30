"""Tests for ``jojo_qa.wikilinks``."""

from __future__ import annotations

from jojo_qa.wikilinks import extract, strip, unique_slugs


def test_extract_pipe_form() -> None:
    body = "See [[cbl-b|CBL-B Program]] for details."
    refs = extract(body)
    assert len(refs) == 1
    assert refs[0].slug == "cbl-b"
    assert refs[0].label == "CBL-B Program"
    assert refs[0].raw == "[[cbl-b|CBL-B Program]]"


def test_extract_bare_form() -> None:
    body = "See [[cbl-b]]."
    refs = extract(body)
    assert len(refs) == 1
    assert refs[0].slug == "cbl-b"
    assert refs[0].label == "cbl-b"


def test_extract_multiple_in_source_order() -> None:
    body = (
        "Read [[del-screening|DEL]] then [[2022-del-screen-queue]] "
        "then [[q4-2022-screening-budget|Q4 budget]]."
    )
    refs = extract(body)
    assert [r.slug for r in refs] == [
        "del-screening",
        "2022-del-screen-queue",
        "q4-2022-screening-budget",
    ]


def test_extract_preserves_duplicates() -> None:
    body = "[[cbl-b]] and again [[cbl-b]]."
    refs = extract(body)
    assert len(refs) == 2
    assert all(r.slug == "cbl-b" for r in refs)


def test_extract_pipe_takes_priority_over_bare() -> None:
    """Pipe-form must not be double-matched as a bare-form with a literal pipe."""
    body = "[[cbl-b|CBL-B]]"
    refs = extract(body)
    assert len(refs) == 1
    assert refs[0].slug == "cbl-b"
    assert refs[0].label == "CBL-B"


def test_extract_ignores_single_brackets() -> None:
    """Markdown links ``[label](href)`` must not match wikilink patterns."""
    body = "See [external](https://example.com) and [[wiki-page]]."
    refs = extract(body)
    assert len(refs) == 1
    assert refs[0].slug == "wiki-page"


def test_extract_handles_empty_body() -> None:
    assert extract("") == []
    assert extract("no wikilinks here") == []


def test_extract_does_not_cross_lines() -> None:
    """Wikilinks may not span newlines — the regex disallows it."""
    body = "[[broken-\nlink]]"
    refs = extract(body)
    assert refs == []


def test_unique_slugs() -> None:
    body = "[[a]] [[b]] [[a|other-label]]"
    assert unique_slugs(body) == {"a", "b"}


def test_strip_pipe_form() -> None:
    body = "See [[cbl-b|CBL-B Program]] for details."
    assert strip(body) == "See CBL-B Program for details."


def test_strip_bare_form() -> None:
    body = "See [[cbl-b]] for details."
    assert strip(body) == "See cbl-b for details."


def test_strip_mixed() -> None:
    body = "[[a|First]] then [[b]] then [[c|Third]]."
    assert strip(body) == "First then b then Third."
