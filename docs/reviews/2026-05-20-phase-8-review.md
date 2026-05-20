# Phase 8 Review — Fine-tune Pipeline

**Date:** 2026-05-20
**Reviewer:** sub-agent (Opus, cold-context, read-only)
**Verdict:** PASS 12/12 items — no blockers

---

## Checklist

1. `packages/jojo_finetune/__init__.py` — **PASS** (exists, declares package docstring + `__version__`).
2. `packages/jojo_finetune/dataset.py` — **PASS**. `walk_wiki` (L110), `generate_dataset` (L335), `GENERATION_PROMPTS` (L55), `FinetuneExample` TypedDict (L40), dry-run generators all present. Citation structurally non-empty in every generator.
3. `packages/jojo_finetune/train.py` — **PASS**. `FineTuneBackend` ABC, `DryRunBackend`, `BedrockBackend`, `HuggingFaceBackend`, `get_backend` all present. Heavy deps (boto3, peft, transformers, trl) wrapped in try/except; module imports cleanly without them; `DryRunBackend` instantiates; heavy backends raise clear `ImportError` with install hints.
4. `packages/jojo_finetune/eval.py` — **PASS**. `run_eval`, `score_pair`, `SynthesisBackend` (calls `jojo_qa.synthesize.answer`), `EvalReport` TypedDict all present.
5. `packages/jojo_finetune/cli.py` — **PASS**. argparse subcommands `generate-dataset`, `train`, `eval` with `main()` entry point.
6. `pyproject.toml` — **PASS**. `jojo-finetune` console script wired; `[finetune]` optional-deps extra with boto3/peft/transformers/trl/datasets; `packages/jojo_finetune` in wheel targets.
7. `data/finetune/v1.jsonl` — **PASS**. 50 lines; all records have `id`, `type`, `citation`, `input`, `output`, `created_at`; zero records have empty `citation`.
8. `data/finetune/benchmark.jsonl` — **PASS**. 10 lines; every record has non-empty `question` and `answer`.
9. `tests/jojo_finetune/` (3 files) — **PASS**. dataset=6, train=10, eval=14 tests; all ≥ 5.
10. `docs/ADR/0014-finetune-strategy.md` — **PASS**. Synthetic-data risks (model collapse, hallucination amplification) + guardrails (citation requirement, eval gate). References ADR 0004, 0009, 0013. Header note explains slot renumbering from 0013.
11. `docs/ops/offline-model.md` — **PASS**. When-to-use, model recommendations, fine-tune commands, vllm/llama.cpp hosting, `synthesis_endpoint` config key, trade-offs table. "Verify against current release notes" caveats at L21, L22, L43, L59, L71.
12. Workspace `README.md` — **PASS**. "Offline / air-gapped deployment" section added with all required pointers.

---

## pytest

```
python -m pytest tests/jojo_finetune/ -v --tb=short
30 passed, 0 failed (0.23s)
```

Heavy-dep isolation verified: `import jojo_finetune.train` succeeds with boto3/peft/transformers/trl absent.

---

## Informational Notes

- ADR 0014 Status is "Proposed". Orchestrator may ratify before v2.0 tag — not a blocker.
- `v1.jsonl` 50 records are hand-curated seed (writer agent), not dry-run output. Correct for an initial seed per the exit criterion.

---

## VERDICT

**Phase 8: PASS** — all exit criterion items met. Ready for stress tests + audits + v2.0.0 tag.
