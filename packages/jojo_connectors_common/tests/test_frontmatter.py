import pytest

from jojo_connectors_common.frontmatter import (
    FRONTMATTER_FIELDS,
    AccessLevel,
    SourceType,
    build_frontmatter,
    parse_frontmatter,
    split_frontmatter,
)


def _sample_frontmatter():
    return build_frontmatter(
        entry_id="drive_some-doc",
        source_type="drive",
        source_url="file:///Public/Drive/some-doc.docx",
        source_id="Public/Drive/some-doc.docx",
        title="Some Doc",
        sha256="0" * 64,
        author="Mateo",
        tags=["protein-sciences", "sop"],
    )


def test_build_frontmatter_coerces_str_enums():
    fm = _sample_frontmatter()
    assert fm.source_type is SourceType.DRIVE
    assert fm.access_level is AccessLevel.ALL_FTE


def test_frontmatter_dict_carries_all_required_fields():
    fm = _sample_frontmatter()
    d = fm.to_dict()
    for name in FRONTMATTER_FIELDS:
        assert name in d


def test_frontmatter_yaml_roundtrips():
    fm = _sample_frontmatter()
    yaml_block = fm.to_yaml()
    assert yaml_block.startswith("---\n")
    assert yaml_block.endswith("---\n")
    combined = yaml_block + "\n# Body\n"
    parsed = parse_frontmatter(combined)
    assert parsed is not None
    assert parsed.title == "Some Doc"
    assert parsed.source_type is SourceType.DRIVE
    assert parsed.tags == ["protein-sciences", "sop"]


def test_split_frontmatter_no_block():
    assert split_frontmatter("plain body") == ({}, "plain body")


def test_parse_frontmatter_rejects_missing_required():
    bad = "---\nid: x\n---\nbody\n"
    with pytest.raises(ValueError):
        parse_frontmatter(bad)


def test_frontmatter_preserves_extra_fields():
    fm = build_frontmatter(
        entry_id="drive_x",
        source_type="drive",
        source_url="",
        source_id="x",
        title="x",
        sha256="0" * 64,
        extra={"pinned": True, "owner_team": "protein-sciences"},
    )
    d = fm.to_dict()
    assert d["pinned"] is True
    assert d["owner_team"] == "protein-sciences"
