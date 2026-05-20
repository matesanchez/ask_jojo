"""Fine-tune training pipeline for JoJo Bot v2.0.

Abstracts two real backends (AWS Bedrock, HuggingFace PEFT) plus a
``DryRunBackend`` used in CI to validate JSONL format without submitting
real jobs.

All heavy optional dependencies (boto3, peft, transformers, trl) are
imported lazily so ``import jojo_finetune.train`` works cleanly without
them installed.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import TypedDict

# ---------------------------------------------------------------------------
# Public types
# ---------------------------------------------------------------------------


class FineTuneJob(TypedDict):
    """Status record for a fine-tune job."""

    job_id: str
    backend: str
    status: str        # "queued" | "running" | "complete" | "failed"
    model_id: str | None
    created_at: str
    metadata: dict[str, str]


# ---------------------------------------------------------------------------
# Abstract base
# ---------------------------------------------------------------------------


class FineTuneBackend(ABC):
    """Abstract contract that each backend must satisfy."""

    @abstractmethod
    def submit(self, dataset_path: Path, base_model: str, **kwargs: object) -> FineTuneJob:
        """Submit a new fine-tune job.

        Args:
            dataset_path: path to the JSONL training file.
            base_model:   model identifier for the base checkpoint.
            **kwargs:     backend-specific options.

        Returns:
            ``FineTuneJob`` describing the submitted job.
        """
        ...

    @abstractmethod
    def status(self, job_id: str) -> FineTuneJob:
        """Fetch the current status of a job.

        Args:
            job_id: backend-specific job identifier.

        Returns:
            Current ``FineTuneJob`` state.
        """
        ...

    @abstractmethod
    def dry_run(self, dataset_path: Path) -> dict[str, object]:
        """Validate the dataset without submitting.

        Args:
            dataset_path: path to the JSONL training file.

        Returns:
            Dict with validation results (``valid``, ``record_count``, etc.).

        Raises:
            ValueError: if the dataset is empty or malformed.
        """
        ...


# ---------------------------------------------------------------------------
# Shared JSONL validation helper
# ---------------------------------------------------------------------------


def _validate_jsonl(dataset_path: Path) -> list[dict[str, object]]:
    """Read and parse ``dataset_path`` as JSONL.

    Returns the list of parsed records.

    Raises:
        ValueError: if the file is missing, empty, or contains invalid JSON lines.
    """
    if not dataset_path.exists():
        raise ValueError(f"Dataset file not found: {dataset_path}")

    records: list[dict[str, object]] = []
    with dataset_path.open(encoding="utf-8") as fh:
        for lineno, raw_line in enumerate(fh, start=1):
            line = raw_line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSON on line {lineno} of {dataset_path}: {exc}"
                ) from exc

    if not records:
        raise ValueError(
            f"Dataset {dataset_path} is empty (0 records). "
            "Run `jojo-finetune generate-dataset` first."
        )
    return records


# ---------------------------------------------------------------------------
# DryRunBackend
# ---------------------------------------------------------------------------


class DryRunBackend(FineTuneBackend):
    """Validate-only backend. No external calls. Used by tests and CI."""

    _BACKEND_NAME = "dry-run"

    def submit(self, dataset_path: Path, base_model: str, **kwargs: object) -> FineTuneJob:
        """Validate the dataset and return a completed mock job."""
        records = _validate_jsonl(dataset_path)  # raises on empty
        return FineTuneJob(
            job_id=f"dry-run-{len(records)}-records",
            backend=self._BACKEND_NAME,
            status="complete",
            model_id="dry-run-model",
            created_at=datetime.now(timezone.utc).isoformat(),
            metadata={"record_count": str(len(records)), "base_model": base_model},
        )

    def status(self, job_id: str) -> FineTuneJob:
        return FineTuneJob(
            job_id=job_id,
            backend=self._BACKEND_NAME,
            status="complete",
            model_id="dry-run-model",
            created_at=datetime.now(timezone.utc).isoformat(),
            metadata={},
        )

    def dry_run(self, dataset_path: Path) -> dict[str, object]:
        records = _validate_jsonl(dataset_path)
        return {
            "valid": True,
            "record_count": len(records),
            "backend": self._BACKEND_NAME,
        }


# ---------------------------------------------------------------------------
# BedrockBackend
# ---------------------------------------------------------------------------


class BedrockBackend(FineTuneBackend):
    """Fine-tune on AWS Bedrock via ``boto3.client('bedrock')``."""

    _BACKEND_NAME = "bedrock"
    DEFAULT_BASE_MODEL = "anthropic.claude-sonnet-4-6-v1:0"

    def __init__(self) -> None:
        try:
            import boto3  # noqa: F401, PLC0415
        except ImportError as exc:
            raise ImportError(
                "boto3 is required for BedrockBackend. "
                "Install it with: pip install 'jojo_bot[finetune]'"
            ) from exc

    def _client(self) -> object:
        import boto3  # noqa: PLC0415

        return boto3.client("bedrock")

    def submit(self, dataset_path: Path, base_model: str, **kwargs: object) -> FineTuneJob:
        """Submit a Bedrock ``CreateModelCustomizationJob``."""
        records = _validate_jsonl(dataset_path)
        client = self._client()

        job_name = kwargs.get("job_name", f"jojo-finetune-{len(records)}")
        output_model_name = kwargs.get("output_model_name", f"{job_name}-model")
        role_arn = kwargs.get("role_arn", "")

        resp = client.create_model_customization_job(  # type: ignore[union-attr]
            jobName=job_name,
            baseModelIdentifier=base_model,
            customModelName=output_model_name,
            roleArn=role_arn,
            trainingDataConfig={"s3Uri": str(dataset_path)},
        )

        job_id = resp.get("jobArn", job_name)
        return FineTuneJob(
            job_id=str(job_id),
            backend=self._BACKEND_NAME,
            status="queued",
            model_id=None,
            created_at=datetime.now(timezone.utc).isoformat(),
            metadata={"base_model": base_model, "record_count": str(len(records))},
        )

    def status(self, job_id: str) -> FineTuneJob:
        """Fetch the current status of a Bedrock customization job."""
        client = self._client()
        resp = client.get_model_customization_job(jobIdentifier=job_id)  # type: ignore[union-attr]

        raw_status = str(resp.get("status", "unknown")).lower()
        _STATUS_MAP = {
            "inprogress": "running",
            "completed": "complete",
            "failed": "failed",
            "stopping": "running",
            "stopped": "failed",
        }
        status = _STATUS_MAP.get(raw_status, raw_status)
        model_id: str | None = resp.get("outputModelArn") or None

        return FineTuneJob(
            job_id=job_id,
            backend=self._BACKEND_NAME,
            status=status,
            model_id=model_id,
            created_at=datetime.now(timezone.utc).isoformat(),
            metadata={"raw_status": raw_status},
        )

    def dry_run(self, dataset_path: Path) -> dict[str, object]:
        records = _validate_jsonl(dataset_path)
        return {
            "valid": True,
            "record_count": len(records),
            "backend": self._BACKEND_NAME,
            "note": "dry_run: no Bedrock job submitted",
        }


# ---------------------------------------------------------------------------
# HuggingFaceBackend
# ---------------------------------------------------------------------------


class HuggingFaceBackend(FineTuneBackend):
    """Fine-tune with PEFT LoRA via ``trl.SFTTrainer``."""

    _BACKEND_NAME = "hf"
    DEFAULT_BASE_MODEL = "meta-llama/Llama-3.1-8B-Instruct"

    def __init__(self) -> None:
        missing: list[str] = []
        for pkg in ("peft", "transformers", "trl"):
            try:
                __import__(pkg)
            except ImportError:
                missing.append(pkg)
        if missing:
            raise ImportError(
                f"Missing packages for HuggingFaceBackend: {', '.join(missing)}. "
                "Install with: pip install 'jojo_bot[finetune]'"
            )

    def submit(self, dataset_path: Path, base_model: str, **kwargs: object) -> FineTuneJob:
        """Launch LoRA fine-tuning via SFTTrainer."""
        from datasets import Dataset  # noqa: PLC0415
        from peft import LoraConfig, TaskType, get_peft_model  # noqa: PLC0415
        from transformers import AutoModelForCausalLM, AutoTokenizer  # noqa: PLC0415
        from trl import SFTConfig, SFTTrainer  # noqa: PLC0415

        records = _validate_jsonl(dataset_path)

        # Load base model + tokenizer
        tokenizer = AutoTokenizer.from_pretrained(base_model)
        model = AutoModelForCausalLM.from_pretrained(base_model)

        # LoRA config
        lora_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            r=kwargs.get("lora_r", 8),
            lora_alpha=kwargs.get("lora_alpha", 32),
            target_modules=["q_proj", "v_proj"],
            lora_dropout=0.1,
        )
        model = get_peft_model(model, lora_config)

        # Build HF dataset from JSONL
        hf_dataset = Dataset.from_list(
            [{"text": f"{r.get('input', '')} {r.get('output', '')}"} for r in records]
        )

        output_dir = str(kwargs.get("output_dir", dataset_path.parent / "hf_output"))
        training_args = SFTConfig(
            output_dir=output_dir,
            num_train_epochs=int(kwargs.get("epochs", 1)),
            per_device_train_batch_size=int(kwargs.get("batch_size", 2)),
            logging_steps=10,
        )

        trainer = SFTTrainer(
            model=model,
            train_dataset=hf_dataset,
            args=training_args,
            tokenizer=tokenizer,
            dataset_text_field="text",
        )
        trainer.train()
        trainer.save_model(output_dir)

        return FineTuneJob(
            job_id=f"hf-lora-{len(records)}-records",
            backend=self._BACKEND_NAME,
            status="complete",
            model_id=output_dir,
            created_at=datetime.now(timezone.utc).isoformat(),
            metadata={
                "base_model": base_model,
                "record_count": str(len(records)),
                "output_dir": output_dir,
            },
        )

    def status(self, job_id: str) -> FineTuneJob:
        """HF training is synchronous; status is always complete after submit."""
        return FineTuneJob(
            job_id=job_id,
            backend=self._BACKEND_NAME,
            status="complete",
            model_id=job_id,
            created_at=datetime.now(timezone.utc).isoformat(),
            metadata={},
        )

    def dry_run(self, dataset_path: Path) -> dict[str, object]:
        records = _validate_jsonl(dataset_path)
        return {
            "valid": True,
            "record_count": len(records),
            "backend": self._BACKEND_NAME,
            "note": "dry_run: no HF trainer launched",
        }


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def get_backend(name: str) -> FineTuneBackend:
    """Instantiate and return a backend by name.

    Args:
        name: one of ``"bedrock"``, ``"hf"``, ``"dry-run"``.

    Returns:
        The corresponding ``FineTuneBackend`` instance.

    Raises:
        ValueError: if ``name`` is not a known backend.
    """
    if name == "bedrock":
        return BedrockBackend()
    if name == "hf":
        return HuggingFaceBackend()
    if name == "dry-run":
        return DryRunBackend()
    raise ValueError(
        f"Unknown backend: {name!r}. Choose from 'bedrock', 'hf', 'dry-run'."
    )
