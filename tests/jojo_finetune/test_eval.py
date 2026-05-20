"""Tests for jojo_finetune.eval.

All tests use dry_run=True or load_benchmark directly, so no API calls
are made in CI.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from jojo_finetune.eval import EvalReport, EvalResult, load_benchmark, run_eval, score_pair

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def benchmark_path(tmp_path: Path) -> Path:
    """10-pair benchmark JSONL."""
    path = tmp_path / "benchmark.jsonl"
    pairs = [
        {
            "id": f"bq-{i:03d}",
            "question": f"What is concept {i}?",
            "answer": f"Concept {i} is a thing in the wiki.",
        }
        for i in range(1, 11)
    ]
    path.write_text(
        "\n".join(json.dumps(p) for p in pairs) + "\n",
        encoding="utf-8",
    )
    return path


# ---------------------------------------------------------------------------
# score_pair tests
# ---------------------------------------------------------------------------


def test_score_pair_exact_match() -> None:
    """Identical strings should produce F1 = 1.0."""
    assert score_pair("the quick brown fox", "the quick brown fox") == pytest.approx(1.0)


def test_score_pair_no_overlap() -> None:
    """Completely disjoint tokens produce F1 = 0.0."""
    assert score_pair("alpha beta gamma", "delta epsilon zeta") == pytest.approx(0.0)


def test_score_pair_partial_overlap() -> None:
    """Partial overlap produces 0 < F1 < 1."""
    score = score_pair("the quick brown fox", "the lazy brown dog")
    assert 0.0 < score < 1.0


def test_score_pair_empty_expected() -> None:
    """Empty expected string produces 0.0."""
    assert score_pair("", "some answer") == pytest.approx(0.0)


def test_score_pair_empty_actual() -> None:
    """Empty actual string produces 0.0."""
    assert score_pair("expected answer", "") == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# load_benchmark tests
# ---------------------------------------------------------------------------


def test_load_benchmark(benchmark_path: Path) -> None:
    """load_benchmark reads all 10 pairs correctly."""
    items = load_benchmark(benchmark_path)
    assert len(items) == 10
    assert items[0]["id"] == "bq-001"
    assert "question" in items[0]
    assert "answer" in items[0]


def test_load_benchmark_round_trip(tmp_path: Path) -> None:
    """Write JSONL manually and read it back; fields match."""
    path = tmp_path / "bench.jsonl"
    pairs = [
        {"id": "q1", "question": "What is X?", "answer": "X is a protein."},
        {"id": "q2", "question": "What does Y do?", "answer": "Y activates Z."},
    ]
    path.write_text("\n".join(json.dumps(p) for p in pairs), encoding="utf-8")

    loaded = load_benchmark(path)
    assert len(loaded) == 2
    assert loaded[0] == pairs[0]
    assert loaded[1] == pairs[1]


def test_load_benchmark_missing_file(tmp_path: Path) -> None:
    """load_benchmark raises FileNotFoundError for a missing file."""
    with pytest.raises(FileNotFoundError):
        load_benchmark(tmp_path / "nonexistent.jsonl")


# ---------------------------------------------------------------------------
# run_eval tests
# ---------------------------------------------------------------------------


def test_dry_run_eval(benchmark_path: Path) -> None:
    """run_eval in dry-run mode returns an EvalReport with all questions scored."""
    report = run_eval("dry-run-model", "dry-run", benchmark_path, dry_run=True)

    _assert_valid_report(report)
    assert report["questions_scored"] == report["questions_total"]
    assert report["questions_total"] == 10
    assert report["model_id"] == "dry-run-model"
    assert report["backend"] == "dry-run"


def test_dry_run_eval_all_results_have_fields(benchmark_path: Path) -> None:
    """Every EvalResult has the required fields with correct types."""
    report = run_eval("dry-run-model", "dry-run", benchmark_path, dry_run=True)

    for result in report["results"]:
        _assert_valid_result(result)


def test_dry_run_eval_scores_are_in_range(benchmark_path: Path) -> None:
    """All scores are in [0.0, 1.0]."""
    report = run_eval("dry-run-model", "dry-run", benchmark_path, dry_run=True)
    for result in report["results"]:
        assert 0.0 <= result["score"] <= 1.0


def test_run_eval_unknown_backend(benchmark_path: Path) -> None:
    """Unknown backend name raises ValueError."""
    with pytest.raises(ValueError, match="Unknown eval backend"):
        run_eval("model", "unknown-backend", benchmark_path)


def test_run_eval_missing_benchmark(tmp_path: Path) -> None:
    """Missing benchmark file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        run_eval("model", "dry-run", tmp_path / "missing.jsonl", dry_run=True)


def test_dry_run_accuracy_mean_computed(benchmark_path: Path) -> None:
    """accuracy_mean is the mean of per-question scores."""
    report = run_eval("dry-run-model", "dry-run", benchmark_path, dry_run=True)
    scores = [r["score"] for r in report["results"]]
    expected_mean = sum(scores) / len(scores)
    assert report["accuracy_mean"] == pytest.approx(expected_mean)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _assert_valid_report(report: EvalReport) -> None:
    assert isinstance(report["model_id"], str)
    assert isinstance(report["backend"], str)
    assert isinstance(report["questions_total"], int) and report["questions_total"] > 0
    assert isinstance(report["questions_scored"], int)
    assert report["questions_scored"] <= report["questions_total"]
    assert isinstance(report["accuracy_mean"], float)
    assert isinstance(report["latency_mean_ms"], float)
    assert isinstance(report["results"], list)
    assert isinstance(report["created_at"], str) and "T" in report["created_at"]


def _assert_valid_result(result: EvalResult) -> None:
    assert isinstance(result["question_id"], str)
    assert isinstance(result["question"], str)
    assert isinstance(result["expected"], str)
    assert isinstance(result["actual"], str)
    assert isinstance(result["score"], float)
    assert isinstance(result["latency_ms"], int)
    assert result["latency_ms"] >= 0
