# Phase 4 Q&A Benchmark — Canonical Questions

**Status:** Seeded with 5 entries (2026-04-30). Target: 50 entries by Phase 4 exit.
**Governing ADR:** `docs/ADR/0011-qa-via-cowork-while-api-pending.md`
**Phase 4 exit criterion:** ≥80% "correct and well-cited" on this file's questions, per two reviewers (PLAN.md §6 Phase 4).

This file is the **canonical** Phase 4 evaluation set: 50 Nurix questions with domain-reviewer-approved gold answers, expected routes, and expected cited slugs. The benchmark grades:

- the **router** (every question carries an `expected_route`),
- the **retrieval** (every question carries `expected_cited_slugs` — the gold answer's bibliography),
- the **synthesis** (every question carries a `gold_answer` and a `notes` field describing what a "correct" answer must include).

The harness in `scripts/run_benchmark.py` runs in two modes:

- `--dry-run` — router-only, fully deterministic, runs in CI today. Asserts `router.classify(question) == expected_route`.
- `--full` — router + synthesis, gated on `anthropic_api_key`. Skipped in CI today; runs on API day.

Until then, the gold answers are produced by Cowork sessions (per ADR 0011) and live alongside the benchmark in `docs/qa/answers/`. A benchmark entry's `gold_answer_file` field points to the corresponding answer.

## Schema (per entry)

```yaml
- id: q-001
  question: "What's the difference between NX-1607 and NX-0255?"
  expected_route: wiki
  expected_cited_slugs:
    - cbl-b
    - cbl-b-cmc
    - cbl-b-preclinical-profile
  category: program-comparison
  difficulty: easy
  gold_answer_file: docs/qa/answers/2026-04-30-cbl-b-nx1607-vs-nx0255.md
  notes: |
    Correct answers must distinguish NX-1607 (lead clinical CBL-B inhibitor)
    from NX-0255 (backup CBL-B inhibitor) and state at least one differentiator
    (chemotype, ADME profile, clinical stage). Hallucinated "clinical Phase II"
    or "approved" claims are immediate fails.
  added: 2026-04-30
  added_by: mateo
```

## Categories

The 50 questions distribute across categories so the benchmark grades the router, retrieval, and synthesis evenly:

| Category | Target count | Description |
|---|---|---|
| program-comparison | 8 | Cross-program differentiators (NX-1607 vs NX-0255, BTK vs IRAK4, etc.) |
| target-biology | 8 | What is target X, what does it do, why are we drugging it |
| platform-mechanism | 6 | DEL, Delphi, CRBN, PROTAC mechanism questions |
| historical-decision | 6 | Why did we do X? Cited program decisions |
| protocol-method | 6 | Wet-lab method questions sourced from `methods/` and `protocols/` |
| relational | 4 | "What's the connection between X and Y?" — exercises graph hop-following |
| router-stress | 4 | Edge cases: ÄKTA-on-program, buffer-on-program, mixed-keyword questions |
| v1-routing | 4 | Pure ÄKTA / UNICORN / chromatography questions; expected_route = `v1` |
| edge | 4 | Out-of-scope, ambiguous, multi-corpus questions; expected_route + raw fallback |

Current seeding: 5 entries, distributed across 4 categories (program-comparison ×1, historical-decision ×1, platform-mechanism ×1, program-comparison ×1, v1-routing ×1).

---

## q-001 — CBL-B: NX-1607 vs NX-0255

- **Question:** What's the difference between NX-1607 and NX-0255, and what's the current clinical status of each?
- **Expected route:** `wiki`
- **Expected cited slugs:** `cbl-b`, `cbl-b-cmc`, `cbl-b-preclinical-profile`, `cbl-b-ind-pharmacology`, `cbl-b-target`
- **Category:** program-comparison
- **Difficulty:** easy
- **Gold answer file:** `docs/qa/answers/2026-04-30-cbl-b-nx1607-vs-nx0255.md`
- **Notes:** A correct answer distinguishes NX-1607 (lead clinical CBL-B inhibitor; orally bioavailable; profiled in mCRPC and other indications per `cbl-b-ind-pharmacology`) from NX-0255 (backup / second clinical-stage CBL-B inhibitor; differentiated chemotype). Must cite at least three slugs from the expected list. "Clinical Phase II" or "approved" claims that aren't sourced from the wiki are fails.
- **Added:** 2026-04-30 by mateo

## q-002 — Pellino-1 program: Peli2 redundancy

- **Question:** Did the Weiss lab Peli2 redundancy finding in Jurkat ever change our position on the Pellino-1 program direction?
- **Expected route:** `wiki`
- **Expected cited slugs:** `pellino-1` (program), `pellino-1` (target)
- **Category:** historical-decision
- **Difficulty:** medium
- **Gold answer file:** `docs/qa/answers/2026-04-30-pellino-1-peli2-redundancy.md`
- **Notes:** Correct answer references the Weiss lab Peli2 redundancy finding in Jurkat (cited from the Pellino-1 program page; absorb checkpoint 19, ~2026-04-25 commit `2f56204`) and discusses how it interacted with the Nurix Peli2-KO TGI / MC38 negative result and the THP-1 macrophage data. Must distinguish the *target* page (cell biology) from the *program* page (decisions / direction). Confidence on the "did it change direction" claim is at most medium since the wiki may not have an explicit decision page on this. Inferring causality without a cited decision page is a fail.
- **Added:** 2026-04-30 by mateo

## q-003 — DEL screening at Nurix in 2022

- **Question:** How was DEL screening organized at Nurix in 2022, and what programs were in the queue?
- **Expected route:** `wiki`
- **Expected cited slugs:** `del-screening`, `del-libraries`, `2022-del-screen-queue`, `dsa-early-discovery-cadence-2022`, `q4-2022-screening-budget`
- **Category:** platform-mechanism
- **Difficulty:** easy
- **Gold answer file:** `docs/qa/answers/2026-04-30-del-screening-2022.md`
- **Notes:** Correct answer describes the DEL screening program structure as of 2022 — DSA (DEL Screening and Analysis) early-discovery cadence, the Q4 2022 budget that capped screening capacity, the queued programs from `2022-del-screen-queue` (e.g. SIAH1 buffer screening). Must cite at least three slugs from the expected list. Speculative additions about programs not on the queue are fails.
- **Added:** 2026-04-30 by mateo

## q-004 — Delphi ACS releases through 2025

- **Question:** Walk me through the major Delphi ACS releases from inception through 2025 — what changed in each, and what was the major decision behind each scope?
- **Expected route:** `wiki`
- **Expected cited slugs:** `delphi`, `delphi-acs-scope`, `delphi-pre-acs-timeline`, `delphi-acs2024-1-release`, `delphi-acs2025-1-release`, `delphi-acs2025-2-release`, `delphi-acs2025-3-release`, `delphi-acs2024-1-uat-cycle`, `delphi-acs2025-1-uat-cycle`, `delphi-acs2025-2-uat-cycle`
- **Category:** historical-decision
- **Difficulty:** hard
- **Gold answer file:** `docs/qa/answers/2026-04-30-delphi-acs-releases-2025.md`
- **Notes:** Correct answer is a chronological walkthrough citing each release decision page. Must distinguish *release* pages from *UAT cycle* pages and explain the relationship (UAT precedes release; UAT cycle pages capture the scope-decision artifacts). The pre-ACS era (`delphi-pre-acs-timeline`) is the right anchor for what came before ACS2024.1. Inventing release versions not in the cited slugs is a fail. Scope notes ("ACS2025.2 added X") must be sourced from a cited decision page; un-cited scope claims are fails.
- **Added:** 2026-04-30 by mateo

## q-005 — ÄKTA buffer prep (router test)

- **Question:** What's the standard buffer prep procedure for an ÄKTA Pure 25 run on the BTK program?
- **Expected route:** `v1`
- **Expected cited slugs:** _(none — `v1` route bypasses the wiki)_
- **Category:** v1-routing
- **Difficulty:** easy
- **Gold answer file:** `docs/qa/answers/2026-04-30-akta-buffer-prep-v1-routing.md`
- **Notes:** This is a **router test**, not a synthesis test. The correct response is a routing slip pointing at v1.0 because the question contains both `akta` and `buffer` and `purif` (implicitly). The session does *not* attempt to answer it from the wiki. A correct router decision is the entire grade for this entry. The wiki has near-zero ÄKTA content (`equipment/akta/` directory is empty per the current `_index.md`); v1.0 has the answer. The mention of "BTK program" is a red herring meant to test that the router does not over-rotate to `wiki` because of the program-keyword. The session note should record whether the regex tripped on the program-keyword.
- **Added:** 2026-04-30 by mateo

---

## Backlog (categories with target counts)

The remaining 45 entries should distribute roughly per the table at the top. Topics to seed (one-line stubs; flesh out into full entries when added):

- **program-comparison (need 7 more):** BTK vs IRAK4 program direction; CBL-B preclinical vs clinical chemistries; ITK vs ITK-merged program scope; Pellino-1 program vs Pellino-1 target page divergence; CRBN platform vs molecular-glue platform comparison; SKP2 vs CDC34 program approach; TYK2 vs JAK1 prioritization.
- **target-biology (need 8):** What does CBL-B do; IRAK4 in TLR signaling; what is BTK's role in B-cell receptor signaling; Pellino-1 vs Pellino-2 redundancy; ZAP-70 in T-cell activation; FEM1B mechanism; STAT6 in IL-4 signaling; IRF5 in autoimmune disease.
- **platform-mechanism (need 5 more):** What is a PROTAC; DEL library construction; CRBN molecular glue mechanism; Delphi clone-biomass-protein registration model; refeyn mass photometry use cases.
- **historical-decision (need 4 more):** Q4 2022 screening budget impact; the 2025 Delphi data quality audit; the Loka ML 2024 engagement; the protein request UX redesign 2022-2025 arc.
- **protocol-method (need 6):** DEL buffer stability test SOP; SEC-MALS standard run; DSF for protein characterization; HT expression determination; TEV protease cleavage workflow; cell screening HiBiT assay.
- **relational (need 4):** Connection between BTK and CK1α (graph stress); CBL-B → CRBN → DEL platform chain; Pellino-1 → IRAK4 → TLR pathway; SKP2 → S-phase regulation → cancer.
- **router-stress (need 4):** "Pellino-1 ÄKTA buffer prep" (mixed keywords; should route `v1` — see qa-prompt edge case); "CBL-B chromatography column choice" (chromatography keyword on program; route `v1`); "buffer for the SIAH1 DEL screen" (`buffer` keyword; route `wiki` per edge case); "purification yield for NX-1607" (`purif` keyword on program; route `v1`).
- **v1-routing (need 3 more):** "ÄKTA Pure 25 vs ÄKTA Avant"; "UNICORN method-editor common errors"; "buffer pH for cation-exchange chromatography on a typical kinase".
- **edge (need 4):** "What's the maintenance schedule for the Refeyn?" (cross-corpus; equipment/program ambiguity); "Has anyone published from the Pellino-1 program?" (mixed wiki + raw; needs publications-index hop); a question whose answer requires reading 3+ raw files (forces miss-log path); a question that is genuinely ambiguous between routes.

Each backlog stub becomes a full benchmark entry the session it gets answered. Adding entries weekly through the API-pending phase keeps the benchmark growing alongside the Cowork loop.
