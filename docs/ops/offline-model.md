# Offline / Air-Gapped Model Deployment

**Status:** Documented, not built. This guide describes how to enable the offline path when conditions are met. See `ADR 0014` for the trigger criteria.

---

## When You Would Want This

Three scenarios justify switching away from the Anthropic API:

- **Air-gapped department.** A department with no outbound internet access (secure lab, data-room workstation, or compliance-restricted network segment) cannot reach the Anthropic API. The offline path runs entirely on-premises.
- **Cost ceiling reached.** If Anthropic API cost exceeds a per-month budget threshold acceptable to the team, the economics favor a one-time hardware investment plus per-query near-zero inference cost.
- **Latency floor required.** Interactive use in a lab context where sub-100 ms response times are expected — for example, a touch-screen lookup terminal in a protein-sciences lab — is not achievable over a WAN API call. A locally hosted inference server on the same LAN can meet this floor.

---

## Which Open-Weights Model to Use (as of 2026-05)

Two models are currently the right targets for this corpus:

- **Llama-3.1-8B-Instruct** (Meta) — the better default for general scientific Q&A. Strong instruction following, wide community support, well-tested LoRA adapters. (Verify against current HuggingFace Hub release notes before using — this recommendation was accurate as of 2026-05 but models evolve quickly.)
- **Qwen2.5-7B-Instruct** (Alibaba) — higher recall on dense scientific text with domain-specific terminology. Preferred if the primary use case is returning precise names, concentrations, or protocol steps. (Verify against current HuggingFace Hub release notes before using.)

Both models fit in 16 GB VRAM with 4-bit quantization, making them compatible with a single A10G or RTX 4090 workstation GPU.

---

## How to Fine-Tune via `packages/jojo_finetune`

Generate the dataset first, then run the training job:

```bash
# Step 1: generate the synthetic dataset (~5,000 examples, ~30 min on Sonnet 4.6)
jojo-finetune generate-dataset --n 5000

# Step 2: train with the HuggingFace LoRA backend
jojo-finetune train \
  --backend hf \
  --dataset data/finetune/v1.jsonl \
  --base-model meta-llama/Llama-3.1-8B-Instruct
```

The `train` command wraps HuggingFace `trl` SFTTrainer (verify `trl` version compatibility before use) and writes the adapter weights to `models/lora/v1/`. Training on 5,000 examples takes approximately 2–4 hours on a single A10G GPU.

---

## How to Host Locally

**Option A — vllm (recommended for LAN serving):**

```bash
python -m vllm.entrypoints.openai.api_server \
  --model models/lora/v1/ \
  --tensor-parallel-size 1 \
  --quantization awq \
  --port 8080
```

vllm exposes an OpenAI-compatible `/v1/completions` endpoint. Verify the `vllm` version against current release notes — the `--quantization awq` flag was valid as of the 0.4.x series but the flag name may change in later releases.

**Option B — llama.cpp (CPU fallback or low-VRAM):**

```bash
./server \
  -m models/lora/v1/model.gguf \
  -c 4096 \
  --n-gpu-layers 32 \
  --port 8080
```

Convert the LoRA adapter to GGUF format before using llama.cpp. The `--n-gpu-layers` value controls how much of the model runs on GPU; set to 0 for CPU-only. Verify current llama.cpp build instructions before use.

---

## How to Swap the Synthesis Endpoint

One key change in `%APPDATA%\JojoBot\config.json`:

```json
{
  "synthesis_endpoint": "http://localhost:8080/v1/completions"
}
```

The `synthesize.py` router reads `synthesis_endpoint` at startup. If the key is set to a localhost URL, it routes synthesis calls to that endpoint instead of the Anthropic API. If the key is absent or set to `"anthropic"`, the default API path is used. No other code changes are required.

---

## Trade-offs vs. Cloud Claude

| Dimension | Cloud Claude (default) | Offline fine-tuned model |
|---|---|---|
| Accuracy on benchmark | Baseline | ~30–50% lower |
| Latency | 2–8 s (API round-trip) | 5–10× longer per token on equivalent hardware; sub-100 ms achievable on GPU |
| Per-query cost | ~$0.003–0.015 | Near-zero after hardware |
| Data sovereignty | Data leaves building | Fully on-premises |
| Maintenance | None | Re-train when corpus changes significantly |

The accuracy gap is real and should be validated against the benchmark in `docs/qa/benchmark-questions.md` before deploying to production users.
