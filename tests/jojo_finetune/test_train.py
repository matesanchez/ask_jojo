"""Tests for jojo_finetune.train.

All tests use DryRunBackend so no external calls are made.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from jojo_finetune.train import DryRunBackend, FineTuneJob, get_backend

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def valid_dataset(tmp_path: Path) -> Path:
    """A JSONL file with 3 valid FinetuneExample-shaped records."""
    path = tmp_path / "train.jsonl"
    records = [
        {
            "id": f"ex-{i:03d}",
            "type": "paraphrase",
            "citation": ["alpha"],
            "input": f"Paraphrase: example {i}",
            "output": f"Paraphrased output {i}.",
            "created_at": "2026-05-19T00:00:00+00:00",
        }
        for i in range(3)
    ]
    path.write_text(
        "\n".join(json.dumps(r) for r in records) + "\n",
        encoding="utf-8",
    )
    return path


@pytest.fixture()
def empty_dataset(tmp_path: Path) -> Path:
    """An empty JSONL file (0 records)."""
    path = tmp_path / "empty.jsonl"
    path.write_text("", encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_dry_run_backend_submit(valid_dataset: Path) -> None:
    """DryRunBackend.submit returns a FineTuneJob with status='complete'."""
    backend = DryRunBackend()
    job = backend.submit(valid_dataset, "base-model-v1")

    _assert_valid_job(job)
    assert job["status"] == "complete"
    assert job["backend"] == "dry-run"
    assert job["model_id"] == "dry-run-model"
    assert int(job["metadata"].get("record_count", 0)) == 3


def test_dry_run_validates_empty_dataset(empty_dataset: Path) -> None:
    """Submitting an empty JSONL file raises ValueError."""
    backend = DryRunBackend()
    with pytest.raises(ValueError, match="empty"):
        backend.submit(empty_dataset, "base-model-v1")


def test_get_backend_unknown() -> None:
    """get_backend with an unknown name raises ValueError."""
    with pytest.raises(ValueError, match="Unknown backend"):
        get_backend("nope")


def test_get_backend_dry_run_returns_dry_run_backend() -> None:
    """get_backend('dry-run') returns a DryRunBackend instance."""
    backend = get_backend("dry-run")
    assert isinstance(backend, DryRunBackend)


def test_dry_run_backend_status() -> None:
    """DryRunBackend.status returns a complete job for any job_id."""
    backend = DryRunBackend()
    job = backend.status("any-job-id")
    _assert_valid_job(job)
    assert job["status"] == "complete"
    assert job["job_id"] == "any-job-id"


def test_dry_run_backend_dry_run(valid_dataset: Path) -> None:
    """DryRunBackend.dry_run returns valid: True and correct record_count."""
    backend = DryRunBackend()
    result = backend.dry_run(valid_dataset)
    assert result["valid"] is True
    assert result["record_count"] == 3
    assert result["backend"] == "dry-run"


def test_dry_run_backend_dry_run_empty(empty_dataset: Path) -> None:
    """DryRunBackend.dry_run also raises ValueError on an empty dataset."""
    backend = DryRunBackend()
    with pytest.raises(ValueError, match="empty"):
        backend.dry_run(empty_dataset)


def test_get_backend_bedrock_raises_without_boto3() -> None:
    """BedrockBackend constructor raises ImportError when boto3 is absent."""
    import unittest.mock as mock

    from jojo_finetune.train import BedrockBackend

    with mock.patch.dict("sys.modules", {"boto3": None}):
        with pytest.raises((ImportError, TypeError)):
            # TypeError can occur if the mock makes __import__ return None
            # for the try/except import check inside __init__.
            BedrockBackend()


def test_get_backend_hf_raises_without_peft() -> None:
    """HuggingFaceBackend constructor raises ImportError when peft is absent."""
    import unittest.mock as mock

    from jojo_finetune.train import HuggingFaceBackend

    with mock.patch.dict("sys.modules", {"peft": None, "transformers": None, "trl": None}):
        with pytest.raises((ImportError, TypeError)):
            HuggingFaceBackend()


def test_validate_jsonl_missing_file(tmp_path: Path) -> None:
    """_validate_jsonl raises ValueError (file-not-found path)."""
    from jojo_finetune.train import _validate_jsonl

    missing = tmp_path / "nonexistent.jsonl"
    with pytest.raises(ValueError, match="not found"):
        _validate_jsonl(missing)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _assert_valid_job(job: FineTuneJob) -> None:
    assert isinstance(job["job_id"], str) and len(job["job_id"]) > 0
    assert isinstance(job["backend"], str)
    assert job["status"] in {"queued", "running", "complete", "failed"}
    # model_id may be None or str
    assert job["model_id"] is None or isinstance(job["model_id"], str)
    assert isinstance(job["created_at"], str)
    assert isinstance(job["metadata"], dict)
