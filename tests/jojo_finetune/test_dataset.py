"""Tests for jojo_finetune.dataset.

All tests use dry_run=True so there are no API calls in CI.
"""

from __future__ import annotations

import json
import textwrap
from pathlib import Path

import pytest

from jojo_finetune.dataset import (
    EXAMPLE_TYPES,
    FinetuneExample,
    generate_dataset,
    walk_wiki,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def fake_wiki(tmp_path: Path) -> Path:
    """Minimal wiki with 5 pages long enough to pass the 200-char threshold."""
    (tmp_path / "_index.md").write_text(
        textwrap.dedent(
            """\
            # Wiki Index

            ## Program

            - [[alpha|Alpha Program]] — `programs/alpha.md`
            - [[beta|Beta Program]] — `programs/beta.md`
            - [[gamma|Gamma Target]] — `programs/gamma.md`

            ## Target

            - [[delta|Delta Discovery]] — `targets/delta.md`
            - [[epsilon|Epsilon Research]] — `targets/epsilon.md`
            """
        ),
        encoding="utf-8",
    )
    (tmp_path / "programs").mkdir()
    (tmp_path / "targets").mkdir()

    long_body = "This is a detailed description of the {name} program at Nurix. " * 6

    for name, subdir, fname in [
        ("Alpha", "programs", "alpha.md"),
        ("Beta", "programs", "beta.md"),
        ("Gamma", "programs", "gamma.md"),
        ("Delta", "targets", "delta.md"),
        ("Epsilon", "targets", "epsilon.md"),
    ]:
        (tmp_path / subdir / fname).write_text(
            f"---\nslug: {name.lower()}\n---\n\n" + long_body.format(name=name),
            encoding="utf-8",
        )
    return tmp_path


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_dry_run_generates_records(fake_wiki: Path, tmp_path: Path) -> None:
    """generate_dataset(..., dry_run=True, n=10) produces exactly 10 records."""
    output = tmp_path / "out.jsonl"
    examples = generate_dataset(fake_wiki, output, n=10, dry_run=True)

    assert len(examples) == 10
    assert output.exists()

    # All records must satisfy the FinetuneExample shape
    for ex in examples:
        _assert_valid_example(ex)


def test_jsonl_round_trip(fake_wiki: Path, tmp_path: Path) -> None:
    """Write 5 records and read them back; all fields survive serialisation."""
    output = tmp_path / "round_trip.jsonl"
    examples = generate_dataset(fake_wiki, output, n=5, dry_run=True)
    assert len(examples) == 5

    lines = output.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 5

    for original, raw_line in zip(examples, lines, strict=True):
        loaded = json.loads(raw_line)
        assert loaded["id"] == original["id"]
        assert loaded["type"] == original["type"]
        assert loaded["citation"] == original["citation"]
        assert loaded["input"] == original["input"]
        assert loaded["output"] == original["output"]
        assert loaded["created_at"] == original["created_at"]


def test_all_records_have_citation(fake_wiki: Path, tmp_path: Path) -> None:
    """Every dry-run record has a non-empty citation list."""
    output = tmp_path / "citations.jsonl"
    examples = generate_dataset(fake_wiki, output, n=12, dry_run=True)

    for ex in examples:
        assert len(ex["citation"]) >= 1, f"Record {ex['id']} has empty citation"
        for slug in ex["citation"]:
            assert isinstance(slug, str) and len(slug) > 0


def test_example_types_covered(fake_wiki: Path, tmp_path: Path) -> None:
    """All three example types appear in a sufficiently large dry-run."""
    output = tmp_path / "types.jsonl"
    # n=9 ensures each type has at least 3 examples
    examples = generate_dataset(fake_wiki, output, n=9, dry_run=True)

    types_seen = {ex["type"] for ex in examples}
    for t in EXAMPLE_TYPES:
        assert t in types_seen, f"Type {t!r} not generated"


def test_walk_wiki_skips_short_pages(tmp_path: Path) -> None:
    """Pages shorter than 200 chars are excluded from walk_wiki results."""
    (tmp_path / "_index.md").write_text(
        textwrap.dedent(
            """\
            # Wiki Index

            ## Target

            - [[short|Short Page]] — `targets/short.md`
            - [[long|Long Page]] — `targets/long.md`
            """
        ),
        encoding="utf-8",
    )
    (tmp_path / "targets").mkdir()
    (tmp_path / "targets" / "short.md").write_text(
        "Too short.", encoding="utf-8"
    )
    (tmp_path / "targets" / "long.md").write_text(
        "This is a long page with enough content. " * 10,
        encoding="utf-8",
    )

    pages = walk_wiki(tmp_path)
    slugs = [p["slug"] for p in pages]
    assert "short" not in slugs
    assert "long" in slugs


def test_dry_run_raises_when_too_few_pages(tmp_path: Path) -> None:
    """generate_dataset raises RuntimeError when the wiki has < 2 eligible pages."""
    (tmp_path / "_index.md").write_text(
        textwrap.dedent(
            """\
            # Wiki Index

            ## Target

            - [[only|Only Page]] — `targets/only.md`
            """
        ),
        encoding="utf-8",
    )
    (tmp_path / "targets").mkdir()
    (tmp_path / "targets" / "only.md").write_text(
        "This page has enough content to pass the threshold. " * 5,
        encoding="utf-8",
    )

    output = tmp_path / "fail.jsonl"
    with pytest.raises(RuntimeError, match="fewer than 2"):
        generate_dataset(tmp_path, output, n=5, dry_run=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _assert_valid_example(ex: FinetuneExample) -> None:
    assert isinstance(ex["id"], str) and len(ex["id"]) > 0
    assert ex["type"] in EXAMPLE_TYPES
    assert isinstance(ex["citation"], list) and len(ex["citation"]) >= 1
    assert isinstance(ex["input"], str) and len(ex["input"]) > 0
    assert isinstance(ex["output"], str) and len(ex["output"]) > 0
    assert isinstance(ex["created_at"], str) and "T" in ex["created_at"]
