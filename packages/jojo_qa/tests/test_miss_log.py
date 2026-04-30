"""Tests for ``jojo_qa.miss_log``."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from jojo_qa import miss_log


@pytest.fixture()
def isolated_log(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    log = tmp_path / "misses.jsonl"
    monkeypatch.setenv("JOJO_QA_MISSES", str(log))
    return log


def test_append_creates_file(isolated_log: Path) -> None:
    miss_log.append("test question", reason="no-candidates")
    assert isolated_log.exists()
    line = isolated_log.read_text(encoding="utf-8").strip()
    data = json.loads(line)
    assert data["question"] == "test question"
    assert data["reason"] == "no-candidates"
    assert "timestamp" in data


def test_append_appends_not_overwrites(isolated_log: Path) -> None:
    miss_log.append("q1", reason="no-candidates")
    miss_log.append("q2", reason="partial-coverage")
    lines = isolated_log.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2


def test_append_records_raw_entries(isolated_log: Path) -> None:
    miss_log.append(
        "q3",
        reason="partial-coverage",
        raw_entries=["raw-a", "raw-b"],
        candidate_slugs=["slug-a"],
        session_id="cowork-test-001",
    )
    data = json.loads(isolated_log.read_text(encoding="utf-8").splitlines()[-1])
    assert data["raw_entries"] == ["raw-a", "raw-b"]
    assert data["candidate_slugs"] == ["slug-a"]
    assert data["session_id"] == "cowork-test-001"


def test_read_recent_returns_newest_first(isolated_log: Path) -> None:
    miss_log.append("q1", reason="no-candidates")
    miss_log.append("q2", reason="partial-coverage")
    miss_log.append("q3", reason="contradicted")
    recent = miss_log.read_recent(n=10)
    assert [e.question for e in recent] == ["q3", "q2", "q1"]


def test_read_recent_respects_n(isolated_log: Path) -> None:
    for i in range(5):
        miss_log.append(f"q{i}", reason="no-candidates")
    recent = miss_log.read_recent(n=2)
    assert len(recent) == 2


def test_read_recent_skips_malformed_lines(isolated_log: Path) -> None:
    miss_log.append("good", reason="no-candidates")
    # Sneak in a malformed line.
    isolated_log.write_text(
        isolated_log.read_text(encoding="utf-8") + "{not valid json}\n",
        encoding="utf-8",
    )
    miss_log.append("good-2", reason="no-candidates")
    recent = miss_log.read_recent(n=10)
    questions = [e.question for e in recent]
    assert "good" in questions
    assert "good-2" in questions


def test_read_recent_missing_file_returns_empty(tmp_path: Path) -> None:
    assert miss_log.read_recent(n=10, path=tmp_path / "nope.jsonl") == []


def test_summary_aggregates(isolated_log: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # Stub the session-count config so the miss-rate denominator is non-zero.
    from jojo_core import config as core_config

    monkeypatch.setattr(core_config, "get", lambda k, default=None, **_: {
        "qa_session_count": 100,
        "wiki_root": "x",
        "anthropic_api_key": None,
    }.get(k, default))

    miss_log.append("q1", reason="no-candidates", raw_entries=["raw-a"])
    miss_log.append("q2", reason="partial-coverage", raw_entries=["raw-a", "raw-b"])
    miss_log.append("q3", reason="no-candidates", candidate_slugs=["slug-x"])

    summary = miss_log.summary()
    assert summary["total_misses"] == 3
    assert summary["by_reason"] == {
        "no-candidates": 2,
        "partial-coverage": 1,
    }
    raw_dict = dict(summary["top_raw_entries"])
    assert raw_dict["raw-a"] == 2
    assert raw_dict["raw-b"] == 1


def test_summary_empty_log(isolated_log: Path) -> None:
    """Empty log returns the empty-summary template."""
    # File doesn't exist yet — note read_recent handles that.
    summary = miss_log.summary()
    assert summary["total_misses"] == 0
    assert summary["by_route"] == {}
    assert summary["by_reason"] == {}
