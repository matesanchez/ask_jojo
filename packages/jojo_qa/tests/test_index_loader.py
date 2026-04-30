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


# -- enrichment from frontmatter ----------------------------------------


@pytest.fixture()
def fake_wiki_with_aliases(tmp_path: Path) -> Path:
    """Wiki with one page that has aliases (block form) and tags (inline)."""
    (tmp_path / "_index.md").write_text(
        textwrap.dedent(
            """\
            # Wiki Index

            ## Program

            - [[pellino-1|Pellino-1 Program]] — `programs/pellino-1.md`
            - [[cbl-b|CBL-B Program]] — `programs/cbl-b.md`
            """
        ),
        encoding="utf-8",
    )
    (tmp_path / "programs").mkdir()
    (tmp_path / "programs" / "pellino-1.md").write_text(
        textwrap.dedent(
            """\
            ---
            title: Pellino-1 Program
            slug: pellino-1
            type: program
            aliases:
              - Peli1
              - Peli2 redundancy
              - PELI1 program
              - Weiss lab
            tags: [program, ubiquitin-ligase]
            ---

            Body content here.
            """
        ),
        encoding="utf-8",
    )
    (tmp_path / "programs" / "cbl-b.md").write_text(
        "---\nslug: cbl-b\ntitle: CBL-B Program\n---\n\nBody.\n",
        encoding="utf-8",
    )
    return tmp_path


def test_load_index_unenriched_has_empty_aliases(fake_wiki_with_aliases: Path) -> None:
    entries = load_index(fake_wiki_with_aliases)
    by_slug = index_by_slug(entries)
    assert by_slug["pellino-1"].aliases == ()
    assert by_slug["pellino-1"].tags == ()


def test_load_index_enriched_populates_aliases(fake_wiki_with_aliases: Path) -> None:
    entries = load_index(fake_wiki_with_aliases, enrich=True)
    by_slug = index_by_slug(entries)
    aliases = by_slug["pellino-1"].aliases
    assert "Peli1" in aliases
    assert "Peli2 redundancy" in aliases
    assert "PELI1 program" in aliases


def test_load_index_enriched_populates_inline_tags(fake_wiki_with_aliases: Path) -> None:
    entries = load_index(fake_wiki_with_aliases, enrich=True)
    by_slug = index_by_slug(entries)
    tags = by_slug["pellino-1"].tags
    assert "program" in tags
    assert "ubiquitin-ligase" in tags


def test_rank_candidates_finds_via_alias(fake_wiki_with_aliases: Path) -> None:
    """The Pellino-1 question that motivated Phase 4 review issue #2.3."""
    entries = load_index(fake_wiki_with_aliases, enrich=True)
    top = rank_candidates(entries, "Did Peli2 redundancy change our position?", k=3)
    slugs = [e.slug for e in top]
    assert "pellino-1" in slugs


def test_rank_candidates_alias_outranks_unrelated(fake_wiki_with_aliases: Path) -> None:
    """Question matching only an alias should still surface the page."""
    entries = load_index(fake_wiki_with_aliases, enrich=True)
    top = rank_candidates(entries, "Weiss lab", k=2)
    assert top
    assert top[0].slug == "pellino-1"


# -- collision warning + grouped variant --------------------------------


def test_index_by_slug_warns_on_collision(fake_wiki: Path) -> None:
    """When two entries share a slug, ``index_by_slug`` warns."""
    from jojo_qa.index_loader import IndexEntry

    entries = [
        IndexEntry(slug="x", title="X-program", path="programs/x.md", type="program"),
        IndexEntry(slug="x", title="X-target", path="targets/x.md", type="target"),
    ]
    with pytest.warns(UserWarning, match="slug collision"):
        result = index_by_slug(entries)
    # Last-write still wins for backwards compatibility.
    assert result["x"].type == "target"


def test_entries_by_slug_grouped_preserves_collisions() -> None:
    """The grouped variant returns all entries for each slug."""
    from jojo_qa.index_loader import IndexEntry, entries_by_slug_grouped

    entries = [
        IndexEntry(slug="x", title="X-program", path="programs/x.md", type="program"),
        IndexEntry(slug="x", title="X-target", path="targets/x.md", type="target"),
        IndexEntry(slug="y", title="Y", path="programs/y.md", type="program"),
    ]
    grouped = entries_by_slug_grouped(entries)
    assert len(grouped["x"]) == 2
    assert len(grouped["y"]) == 1
    types = {e.type for e in grouped["x"]}
    assert types == {"program", "target"}
