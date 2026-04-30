"""Tests for ``jojo_qa.raw_fallback``."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from jojo_qa.raw_fallback import score_entry, search


def _entry(**kwargs):
    """Build a minimal manifest entry with sensible defaults."""
    base = {
        "title": "",
        "source_type": "drive",
        "source_url": "",
        "path": "",
        "tags": [],
    }
    base.update(kwargs)
    return base


def test_score_entry_title_match() -> None:
    e = _entry(title="CBL-B AACR 2019 Abstract")
    assert score_entry(e, {"cbl-b"}) == 3
    assert score_entry(e, {"aacr"}) == 3


def test_score_entry_url_path_match() -> None:
    e = _entry(
        title="Some other title",
        source_url="https://nurix.sharepoint.com/sites/CBL-B-team/cbl-aacr-2019.pptx",
    )
    assert score_entry(e, {"cbl-b"}) == 2  # appears in URL but not title


def test_score_entry_tag_match() -> None:
    e = _entry(title="other", source_url="other", tags=["program", "cbl-b"])
    assert score_entry(e, {"cbl-b"}) == 1


def test_score_entry_no_match() -> None:
    e = _entry(title="random", source_url="random", tags=[])
    assert score_entry(e, {"cbl-b"}) == 0


def test_score_entry_empty_query() -> None:
    e = _entry(title="anything")
    assert score_entry(e, set()) == 0


@pytest.fixture()
def fake_manifest(tmp_path: Path) -> Path:
    payload = {
        "schema_version": "0.1.0",
        "entries": {
            "cbl-aacr-2019": _entry(
                title="CBL-B AACR 2019 Abstract",
                source_type="publicdrive",
                source_url="cbl-aacr-2019-abstract.docx",
                path="publicdrive/cbl-aacr-2019-abstract.md",
                tags=["program", "cbl-b"],
            ),
            "cbl-cmc-jo-ann-2019": _entry(
                title="CBL CMC Jo-Ann 2019",
                source_type="publicdrive",
                source_url="cbl-cmc-2019.pptx",
                path="publicdrive/cbl-cmc-2019.md",
                tags=["cmc"],
            ),
            "del-screen-2022": _entry(
                title="DEL Screen Plans 2022",
                source_type="sharepoint",
                source_url="del-protein-screen-2022.pptx",
                path="sharepoint/del-protein-screen-2022.md",
                tags=["del", "screening"],
            ),
            "akta-pure-25-sop": _entry(
                title="AKTA Pure 25 startup SOP",
                source_type="onedrive",
                source_url="akta-pure-25-sop.docx",
                path="onedrive/akta-pure-25-sop.md",
                tags=["akta", "purification"],
            ),
        },
    }
    p = tmp_path / "manifest.json"
    p.write_text(json.dumps(payload), encoding="utf-8")
    return p


def test_search_returns_top_hits(fake_manifest: Path) -> None:
    hits = search(fake_manifest, "cbl-b 2019", k=3)
    # The CBL-B entries should outrank others.
    assert hits[0].entry_id == "cbl-aacr-2019"
    assert any(h.entry_id == "cbl-cmc-jo-ann-2019" for h in hits)


def test_search_respects_k(fake_manifest: Path) -> None:
    hits = search(fake_manifest, "cbl-b 2019", k=1)
    assert len(hits) == 1


def test_search_excludes_zero_scores(fake_manifest: Path) -> None:
    hits = search(fake_manifest, "cbl-b 2019", k=10)
    # The akta entry has zero overlap with "cbl-b 2019".
    assert all(h.entry_id != "akta-pure-25-sop" for h in hits)


def test_search_empty_query(fake_manifest: Path) -> None:
    assert search(fake_manifest, "") == []


def test_search_missing_manifest(tmp_path: Path) -> None:
    assert search(tmp_path / "nope.json", "cbl-b") == []


def test_search_corrupt_manifest(tmp_path: Path) -> None:
    p = tmp_path / "manifest.json"
    p.write_text("{not valid json", encoding="utf-8")
    assert search(p, "cbl-b") == []


def test_search_handles_non_dict_entry(tmp_path: Path) -> None:
    """Entries that aren't dicts should be skipped, not crash."""
    p = tmp_path / "manifest.json"
    p.write_text(
        json.dumps({"entries": {"good": {"title": "CBL-B"}, "bad": "string"}}),
        encoding="utf-8",
    )
    hits = search(p, "cbl-b")
    assert len(hits) == 1
    assert hits[0].entry_id == "good"


def test_search_returns_source_type(fake_manifest: Path) -> None:
    hits = search(fake_manifest, "cbl-b", k=10)
    by_id = {h.entry_id: h for h in hits}
    assert by_id["cbl-aacr-2019"].source_type == "publicdrive"
