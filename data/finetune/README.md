# data/finetune/

Machine-generated synthetic dataset. Not source-of-truth. Produced by `jojo-finetune generate-dataset`. Target: ~5,000 examples at full scale; v1.jsonl is the seed from the initial run.

## Files

- `v1.jsonl` — seed dataset produced by the initial `generate-dataset` run.
- `benchmark.jsonl` — 50 question/answer pairs for evaluation. The 10 pairs
  currently checked in are dummies for CI. **Replace with real Phase 4 gold
  answers before running production eval.**

## Schema

Each line in `v1.jsonl` is a JSON object conforming to `FinetuneExample`:

```json
{
  "id": "<uuid4 hex>",
  "type": "paraphrase" | "fill_blank" | "synthesis",
  "citation": ["<slug>", ...],
  "input": "<prompt sent to model>",
  "output": "<expected completion>",
  "created_at": "<ISO 8601>"
}
```

Each line in `benchmark.jsonl`:

```json
{
  "id": "<id>",
  "question": "<question text>",
  "answer": "<gold answer>"
}
```
