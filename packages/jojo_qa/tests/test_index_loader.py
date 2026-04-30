"""Tests for ``jojo_qa.index_loader``."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from jojo_qa.index_loader import (
    IndexEntry,
    index_by_slug,
    load_index,
    rank_candidates,
)


@pytest.fixture()
def fake_wiki(tmp_path: Path) -> Path:
    """Three-page fake wiki with a representative ``_index.md``."""
    (tmp_path / "_index.md").write_text(
        textwrap.dedent(
            """\
            # Wiki Index
            Total pages: 3

            ## Concept

            - [[targeted-protein-degradation|Targeted Protein Degradation]] — `concepts/targeted-protein-degradation.md`

            ## Program

            - [[cbl-b|CBL-B Program]] — `programs/cbl-b.md`
            - [[pellino-1|Pellino-1 Program]] — `programs/pellino-1.md`

            ## Target

            - [[cbl-b-target|CBL-B Target]] — `targets/cbl-b.md`
            """
        ),
        encoding="utf-8",
    )
    return tmp_path


def test_load_index_basic(fake_wiki: Path) -> None:
    entries = load_index(fake_wiki)
    assert len(entries) == 4
    slugs = [e.slug for e in entries]
    assert slugs == [
        "targeted-protein-degradation",
        "cbl-b",
        "pellino-1",
        "cbl-b-target",
    ]


def test_load_index_types_normalized(fake_wiki: Path) -> None:
    entries = load_index(fake_wiki)
    assert {e.type for e in entries} == {"concept", "program", "target"}


def test_load_index_titles_extracted(fake_wiki: Path) -> None:
    entries = load_index(fake_wiki)
    by_slug = index_by_slug(entries)
    assert by_slug["cbl-b"].title == "CBL-B Program"
    assert by_slug["pellino-1"].title == "Pellino-1 Program"


def test_load_index_paths_extracted(fake_wiki: Path) -> None:
    entries = load_index(fake_wiki)
    by_slug = index_by_slug(entries)
    assert by_slug["cbl-b"].path == "programs/cbl-b.md"
    assert by_slug["cbl-b-target"].path == "targets/cbl-b.md"


def test_load_index_directory_property(fake_wiki: Path) -> None:
    entries = load_index(fake_wiki)
    by_slug = index_by_slug(entries)
    assert by_slug["cbl-b"].directory == "programs"
    assert by_slug["targeted-protein-degradation"].directory == "concepts"


def test_load_index_missing_file(tmp_path: Path) -> None:
    """Missing index file returns empty list, no exception."""
    assert load_index(tmp_path) == []


def test_load_index_handles_bare_wikilinks(tmp_path: Path) -> None:
    """Bare ``[[slug]]`` (no pipe) — title falls back to slug."""
    (tmp_path / "_index.md").write_text(
        "# Wiki Index\n\n## Program\n\n- [[cbl-b]] — `programs/cbl-b.md`\n",
        encoding="utf-8",
    )
    entries = load_index(tmp_path)
    assert len(entries) == 1
    assert entries[0].slug == "cbl-b"
    assert entries[0].title == "cbl-b"


def test_load_index_ignores_non_matching_lines(tmp_path: Path) -> None:
    """Prose between sections is silently ignored."""
    (tmp_path / "_index.md").write_text(
        textwrap.dedent(
            """\
            # Wiki Index
            Total pages: 1

            Some narrative prose that should not parse as an entry.

            ## Program

            - [[cbl-b|CBL-B Program]] — `programs/cbl-b.md`

            More prose that gets ignored.
            """
        ),
        encoding="utf-8",
    )
    entries = load_index(tmp_path)
    assert len(entries) == 1


# -- candidate ranking --------------------------------------------------


def test_rank_candidates_finds_cbl_b(fake_wiki: Path) -> None:
    """A question containing 'cbl-b' should surface the CBL-B entries."""
    entries = load_index(fake_wiki)
    top = rank_candidates(entries, "What's the difference between CBL-B and IRAK4?", k=3)
    slugs = [e.slug for e in top]
    assert "cbl-b" in slugs
    assert "cbl-b-target" in slugs


def test_rank_candidates_orders_by_score(fake_wiki: Path) -> None:
    """A question matching the slug AND title beats a question matching only the title."""
    entries = load_index(fake_wiki)
    # 'pellino-1' matches the slug exactly + appears in the title.
    top = rank_candidates(entries, "Pellino-1 program direction", k=3)
    assert top[0].slug == "pellino-1"


def test_rank_candidates_excludes_zero_scores(fake_wiki: Path) -> None:
    """Entries that don't share any token with the question are excluded."""
    entries = load_index(fake_wiki)
    top = rank_candidates(entries, "AKTA chromatography buffer", k=8)
    assert top == []  # No entry shares tokens with these v1-domain words.


def test_rank_candidates_handles_empty_question(fake_wiki: Path) -> None:
    entries = load_index(fake_wiki)
    assert rank_candidates(entries, "", k=8) == []


def test_index_entry_is_frozen() -> None:
    """``IndexEntry`` is frozen — mutating attributes raises."""
    e = IndexEntry(slug="x", title="X", path="x/x.md", type="program")
    with pytest.raises(Exception):
        e.slug = "y"  # type: ignore[misc]
