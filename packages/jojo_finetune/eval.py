"""Evaluation harness for JoJo Bot v2.0 fine-tuned models.

Runs a model (fine-tuned or baseline) against a 50-question benchmark and
scores results using word-overlap F1.

Supported backends:

- ``"synthesis"``  — calls ``jojo_qa.synthesize.answer()`` directly (live
  or api_key_required path). Useful as a baseline for the current wiki state.
- ``"bedrock"``    — calls the fine-tuned Bedrock endpoint.
- ``"hf"``         — calls the fine-tuned HF model locally.
- ``"dry-run"``    — returns fixed dummy responses; no API calls. Used in CI.
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import TypedDict

# ---------------------------------------------------------------------------
# Public types
# ---------------------------------------------------------------------------


class EvalResult(TypedDict):
    """Scored result for one benchmark question."""

    question_id: str
    question: str
    expected: str
    actual: str
    score: float       # 0.0–1.0; word-overlap F1
    latency_ms: int


class EvalReport(TypedDict):
    """Aggregated evaluation report."""

    model_id: str
    backend: str
    questions_total: int
    questions_scored: int
    accuracy_mean: float
    latency_mean_ms: float
    results: list[EvalResult]
    created_at: str


# ---------------------------------------------------------------------------
# Benchmark I/O
# ---------------------------------------------------------------------------


def load_benchmark(path: Path) -> list[dict[str, str]]:
    """Load benchmark question/answer pairs from a JSONL file.

    Args:
        path: path to the benchmark JSONL file.

    Returns:
        List of dicts with at minimum ``"id"``, ``"question"``, ``"answer"`` keys.

    Raises:
        FileNotFoundError: if ``path`` does not exist.
        ValueError: if any line is not valid JSON.
    """
    if not path.exists():
        raise FileNotFoundError(f"Benchmark file not found: {path}")

    items: list[dict[str, str]] = []
    with path.open(encoding="utf-8") as fh:
        for lineno, raw_line in enumerate(fh, start=1):
            line = raw_line.strip()
            if not line:
                continue
            try:
                items.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSON on line {lineno} of {path}: {exc}"
                ) from exc
    return items


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------


def score_pair(expected: str, actual: str) -> float:
    """Compute word-overlap F1 between ``expected`` and ``actual``.

    Tokenizes by lowercasing and splitting on whitespace/punctuation.
    Returns 1.0 for exact overlap (unordered), 0.0 for no common tokens.

    Args:
        expected: gold answer string.
        actual:   model answer string.

    Returns:
        F1 score in [0.0, 1.0].
    """
    import re

    def _tokens(text: str) -> list[str]:
        return re.findall(r"[a-z0-9]+", text.lower())

    exp_tokens = _tokens(expected)
    act_tokens = _tokens(actual)

    if not exp_tokens or not act_tokens:
        return 0.0

    exp_set = set(exp_tokens)
    act_set = set(act_tokens)
    common = exp_set & act_set

    if not common:
        return 0.0

    precision = len(common) / len(act_set)
    recall = len(common) / len(exp_set)

    if precision + recall == 0.0:
        return 0.0

    return 2 * precision * recall / (precision + recall)


# ---------------------------------------------------------------------------
# Model backends for eval
# ---------------------------------------------------------------------------


class _EvalBackend:
    """Internal protocol: must implement ``predict(question) -> str``."""

    def predict(self, question: str) -> str:  # noqa: ARG002
        raise NotImplementedError


class _DryRunEvalBackend(_EvalBackend):
    """Returns a fixed non-empty answer for all questions. No API calls."""

    _FIXED_ANSWER = "This is a dry-run answer for evaluation testing."

    def predict(self, question: str) -> str:  # noqa: ARG002
        return self._FIXED_ANSWER


class SynthesisBackend(_EvalBackend):
    """Calls ``jojo_qa.synthesize.answer()`` as the 'model under test'.

    This is the live in-session synthesis path — it runs the full
    retrieval + Anthropic synthesis pipeline. When no API key is
    configured it returns the api_key_required shape; the eval harness
    treats the ``message`` field as the actual answer in that case.

    Constructor:
        api_key:   Anthropic API key (falls back to config).
        wiki_root: path to ``ask_jojo_wiki/``. Falls back to
                   ``config.get("wiki_root")``.
    """

    def __init__(
        self,
        api_key: str | None = None,
        wiki_root: Path | None = None,
    ) -> None:
        from jojo_core import config

        self._api_key = api_key or config.get("anthropic_api_key", None)
        resolved_root = wiki_root or config.get("wiki_root", None)
        self._wiki_root: Path | None = Path(resolved_root) if resolved_root else None

    def predict(self, question: str) -> str:
        from jojo_qa import synthesize

        if self._wiki_root is None or not self._wiki_root.exists():
            return "wiki_root not configured"

        result = synthesize.answer(question, wiki_root=self._wiki_root)
        if result.get("status") == "answered":
            return str(result.get("answer", ""))
        # api_key_required or api_error shape
        return str(result.get("message", result.get("error", "")))


class _BedrockEvalBackend(_EvalBackend):
    """Calls a Bedrock endpoint (custom model) for inference."""

    def __init__(self, model_id: str) -> None:
        try:
            import boto3  # noqa: F401, PLC0415
        except ImportError as exc:
            raise ImportError(
                "boto3 is required for Bedrock eval. "
                "Install it with: pip install 'jojo_bot[finetune]'"
            ) from exc
        self._model_id = model_id

    def predict(self, question: str) -> str:
        import json as json_mod  # noqa: PLC0415

        import boto3  # noqa: PLC0415

        client = boto3.client("bedrock-runtime")
        body = json_mod.dumps(
            {"prompt": question, "max_tokens_to_sample": 512}
        )
        resp = client.invoke_model(modelId=self._model_id, body=body)
        result = json_mod.loads(resp["body"].read())
        return str(result.get("completion", ""))


class _HFEvalBackend(_EvalBackend):
    """Calls a local HuggingFace model for inference."""

    def __init__(self, model_id: str) -> None:
        try:
            from transformers import pipeline  # noqa: F401, PLC0415
        except ImportError as exc:
            raise ImportError(
                "transformers is required for HF eval. "
                "Install it with: pip install 'jojo_bot[finetune]'"
            ) from exc
        self._model_id = model_id

    def predict(self, question: str) -> str:
        from transformers import pipeline  # noqa: PLC0415

        pipe = pipeline("text-generation", model=self._model_id)
        outputs = pipe(question, max_new_tokens=256)
        return str(outputs[0].get("generated_text", ""))


# ---------------------------------------------------------------------------
# Main eval driver
# ---------------------------------------------------------------------------


def run_eval(
    model_id: str,
    backend_name: str,
    benchmark_path: Path,
    *,
    api_key: str | None = None,
    wiki_root: Path | None = None,
    dry_run: bool = False,
) -> EvalReport:
    """Run the evaluation harness against ``benchmark_path``.

    Args:
        model_id:        identifier of the model being evaluated.
        backend_name:    one of ``"synthesis"``, ``"bedrock"``, ``"hf"``,
                         ``"dry-run"``.
        benchmark_path:  path to benchmark JSONL file.
        api_key:         Anthropic API key (used by ``synthesis`` backend).
        wiki_root:       wiki path (used by ``synthesis`` backend).
        dry_run:         when True, use fixed dummy responses, no API calls.

    Returns:
        ``EvalReport`` with per-question results and aggregate statistics.
    """
    benchmark = load_benchmark(benchmark_path)

    # Choose eval backend
    backend: _EvalBackend
    if dry_run or backend_name == "dry-run":
        backend = _DryRunEvalBackend()
    elif backend_name == "synthesis":
        backend = SynthesisBackend(api_key=api_key, wiki_root=wiki_root)
    elif backend_name == "bedrock":
        backend = _BedrockEvalBackend(model_id)
    elif backend_name == "hf":
        backend = _HFEvalBackend(model_id)
    else:
        raise ValueError(
            f"Unknown eval backend: {backend_name!r}. "
            "Choose from 'synthesis', 'bedrock', 'hf', 'dry-run'."
        )

    results: list[EvalResult] = []
    for item in benchmark:
        question = str(item.get("question", ""))
        expected = str(item.get("answer", ""))
        q_id = str(item.get("id", question[:30]))

        t0 = time.monotonic()
        actual = backend.predict(question)
        latency_ms = int((time.monotonic() - t0) * 1000)

        score = score_pair(expected, actual)
        results.append(
            EvalResult(
                question_id=q_id,
                question=question,
                expected=expected,
                actual=actual,
                score=score,
                latency_ms=latency_ms,
            )
        )

    questions_total = len(results)
    questions_scored = len(results)  # all questions are scored (no skips)

    accuracy_mean = (
        sum(r["score"] for r in results) / questions_scored
        if questions_scored > 0
        else 0.0
    )
    latency_mean_ms = (
        sum(r["latency_ms"] for r in results) / questions_total
        if questions_total > 0
        else 0.0
    )

    return EvalReport(
        model_id=model_id,
        backend=backend_name,
        questions_total=questions_total,
        questions_scored=questions_scored,
        accuracy_mean=accuracy_mean,
        latency_mean_ms=latency_mean_ms,
        results=results,
        created_at=datetime.now(timezone.utc).isoformat(),
    )
