# ADR 0011 — Q&A via Cowork Sessions While API Access Is Pending

**Status:** Accepted
**Date:** 2026-04-30
**Deciders:** Mateo de los Rios
**Related:** `ADR 0010` (compile via Cowork while API pending), `ADR 0001` (wiki over RAG), `ADR 0000` (v2 roadmap — Phase 4), `schema/CLAUDE.md` (wiki constitution), `docs/follow-ups.md` FU-10 (Anthropic API key — AWS payment leg)

## Context

Phase 4 (Q&A over the Wiki) replaces v1.0's RAG-based answering with a wiki-driven, index-first retrieval pipeline for everything except chromatography questions, which stay on the v1.0 ÄKTA path. The design always assumed two model calls per question: a cheap Haiku 4.5 router pre-pass that classifies the query as `v1` (ÄKTA / UNICORN / chromatography / buffer / purification) or `wiki` (everything else), and a Sonnet 4.6 retrieval+synthesis pass that reads `_index.md`, picks 3–8 candidate pages, follows `[[wikilinks]]` 1–2 hops, and writes a grounded answer. Hard questions optionally promote to Opus 4.6 via a depth toggle. See `PLAN.md` §6 Phase 4 and the budget model in `docs/budget-model.xlsx`.

Three things are true at the same time:

1. **Phase 4 is unblocked everywhere except model access.** Phases 0–3 are complete (`docs/v2_status.md`). The wiki holds 138 pages (`ask_jojo_wiki/_index.md`). The Wiki tab, Raw tab, and Ops tab are live (`src/frontend/app/(tabs)/`). `_backlinks.json` and `_index.md` exist. The retrieval contract is described in PLAN.md §6 Phase 4 and the synthesis prompt is templated there.
2. **The Anthropic API key is not coming soon.** FU-10 (AWS payment-method onboarding for Anthropic API billing) has been stuck since 2026-04-22. ADR 0010 already accepted this for Phase 2 absorb; the same constraint applies to Phase 4.
3. **Phase 4 has substantial *deterministic* work that does not need model access.** The query router has a regex backstop spec already (`\bakta|unicorn|chromatograph|purif|buffer`); the index loader, wikilink extractor, graph builder, and raw-fallback search are pure-Python utilities; the file-back endpoint is a `git commit` away from a model-driven write loop; the benchmark harness is human-authored gold answers. None of these touch a model.

Separately — the same way ADR 0010 carved Phase 2 — Cowork sessions can play the role of the Sonnet/Opus retrieval+synthesis call today. A fresh Cowork session, given the wiki constitution, the system prompt, and a question, can read `_index.md`, pick 3–8 pages, follow wikilinks, and write a grounded answer with the same EXTRACTED-vs-INFERRED discipline `schema/CLAUDE.md` requires of the absorb loop. The session lacks the latency target (`p95 < 8s`) and cannot run nightly CI, but the *output discipline* matches what `jojo_qa.query()` will eventually emit.

## Decision

**Run Phase 4 Q&A via human-triggered Cowork sessions until API access lands, while shipping all the deterministic plumbing that does not depend on model access. Transplant the prompt and queue into `jojo_qa.query` unchanged when the key lands.**

Concretely:

1. **`packages/jojo_qa/` ships its deterministic core now.** Six modules land as real, tested code: `router.py` (regex query router), `index_loader.py` (parse `_index.md` into a slug → metadata map), `wikilinks.py` (extract `[[slug|label]]` patterns), `graph.py` (build `_graph.json` adjacency from `_backlinks.json` + body link extraction; BFS shortest-path), `raw_fallback.py` (manifest substring search), `miss_log.py` (append-only JSONL of retrieval misses for the next absorb pass). None of them call a model. All have tests.

2. **`src/backend/routers/qa_router.py` ships with deterministic endpoints live and synthesis endpoints feature-flagged.** `GET /api/qa/route`, `GET /api/qa/path`, `GET /api/qa/index`, `GET /api/qa/retrieve` (assembles the bundle a Cowork session needs as input), `GET /api/qa/graph`, and `POST /api/qa/file-back` execute against real wiki state today. `POST /api/qa/query` and `POST /api/qa/explain` check `config.get("anthropic_api_key", None)`; when absent they return a 200 OK shape `{"status": "api_key_required", "retrieval_bundle": {...}}` whose `retrieval_bundle` is the exact paste-in payload a Cowork session consumes. Mirrors the Phase 3 `POST /api/wiki/edit` feature-flag pattern.

3. **`docs/qa/qa-prompt.md` is the operational entry point.** Self-contained prompt Mateo (or the eventual `jojo_qa.write` system prompt) loads into a fresh Cowork session. Points the session at the wiki constitution, `_index.md`, the candidate pages selected by the deterministic retrieval bundle, and the question. Tells it to (a) acknowledge the route, (b) expand to 1–2 wikilink hops where useful, (c) answer in markdown with `[[slug|label]]` inline citations, (d) state confidence per claim, (e) separate EXTRACTED from INFERRED, (f) propose 3 wiki-aware follow-up questions, (g) propose a `wiki/derived/<date>-<slug>.md` if the answer contains >200 words of novel synthesis. Living specification of what `jojo_qa.synthesize` will eventually encode.

4. **`docs/qa/queue.md` is the question queue.** Same shape as `docs/compile/queue.md`. Each Cowork session claims the next unanswered question, writes its gold answer to `docs/qa/answers/<date>-<slug>.md`, ticks the box, commits. The queue file becomes the input to `jojo-qa replay --queue docs/qa/queue.md` on API day.

5. **`docs/qa/benchmark-questions.md` is the 50-question benchmark.** Authoring this document is human work and is on the critical path for declaring Phase 4 done. The benchmark grades Phase 4 exit (≥80% correct, well-cited per two reviewers, p95 latency < 8s — the latency leg is API-only, the correctness leg is gradeable today). Each question carries: text, expected route, expected cited slugs, and a domain-reviewer-approved gold answer. The first 5 entries seed the loop; subsequent additions piggyback on Cowork session output (every session that produces a gold answer adds it back here).

6. **Output is written to `ask_jojo_wiki/derived/` for promoted answers.** The whole point of Phase 4 is the compounding loop — Q&A produces synthesis that feeds the next Q&A. Hiding novel synthesis in a scratch directory while waiting for the API would defer that loop for no gain. The `wiki/derived/` directory is in scope for the compile pipeline's promotion pass (per `SCHEMA.md` §2) so any Phase 4 output that earns its place gets promoted to the main taxonomy at the next absorb checkpoint.

7. **Commits use a Q&A-flavored constitutional format.** Per `schema/CLAUDE.md` §9, wiki commits are prefixed by their operation: `absorb(...)`, `checkpoint(...)`, `lint(...)`. We add `qa(...)` as the prefix for derived-page commits coming out of Q&A sessions: `qa(<corpus>): <slug> filed under derived/`. A `Co-Authored-By: Claude Sonnet 4.6 via Cowork <noreply@anthropic.com>` trailer disambiguates from API-triggered commits, identical to ADR 0010's convention.

8. **Phase 4 exit criterion is unchanged.** 50-question benchmark ≥80% "correct and well-cited" per two reviewers, mean cost per question < $0.20 at current corpus size, legacy ÄKTA path still works, cross-domain Nurix questions return cited grounded answers. The *correctness* leg is gradeable today via Cowork. The *latency* and *cost* legs grade only on API day. That is acceptable: latency and cost are operational constraints on the production loop, not the answer quality the wiki is supposed to deliver.

## Rationale

Three reasons.

1. **The hard parts are the prompt, the routing rules, and the benchmark — and those need pressure-testing anyway.** Whether the model call comes from `anthropic.Anthropic().messages.create(...)` or from a Cowork session, the work product is the same: an answer in `docs/qa/answers/` (or a draft in `wiki/derived/`) that obeys the constitution, cites real wiki pages, and grades against a gold answer. The per-question writing discipline is what we need to stress-test before writing autonomous Q&A code. Running it by hand for 50 questions tightens the prompt we will eventually bake into `jojo_qa.synthesize`. Starting the API-driven loop on day one would have meant debugging prompt issues through CI instead of in the same window producing the answer.

2. **Zero disposable work.** The artifacts produced this phase — the regex router, the retrieval-bundle helpers, the `_graph.json` builder, the prompt, the queue, the gold answers, the 50-question benchmark, and the deterministic API endpoints — all persist into the API-driven phase unchanged. The deterministic plumbing IS Phase 4's load-bearing infrastructure; the model call is the last 20% that drops in. Even on API day, the regex router stays as the safety net under a Haiku classifier (regex first, classifier when ambiguous) so misclassified ÄKTA queries can never silently route to the wiki path.

3. **Parallel unblocks, no critical-path dependency.** This keeps Phase 4 off the "wait for AWS → wait for IT → wait for Anthropic onboarding" chain. Phase 4 can produce real Q&A output, real benchmark gold answers, and real `wiki/derived/` content this week. The compounding loop starts the first time someone asks a question whose answer ends up filed back in the wiki and then cited by a later question.

Two alternatives considered:

- **Wait for the API.** Rejected for the same reasons ADR 0010 rejected it. We'd produce zero Q&A output in the interim, the benchmark would not get authored, and the prompt would still need stress-testing on API day.
- **Skip Phase 4 entirely until the API key lands; advance to Phase 5/6 in parallel.** Rejected because Phase 5 (rich outputs) is downstream of Phase 4 (the Q&A pipeline is what produces the markdown that Phase 5 renders), and Phase 6 (lint) is also gated on FU-10. Doing Phase 4's deterministic plumbing now is the only forward-progress lever available on the critical path.

## Consequences

### Positive

- Phase 4 produces real Q&A output and a 50-question benchmark in the weeks after Phase 3 exits, not "whenever AWS clears."
- Every Q&A session gets a built-in review pass (human reads the answer, accepts or fixes). Phase 4 exit-criterion grading (≥80% "correct and well-cited" per two reviewers) starts the moment the first 5 gold answers are filed, not after the first API call.
- The deterministic plumbing — router, index loader, graph builder, raw fallback, miss log, file-back endpoint — is the load-bearing infrastructure of Phase 4 either way. Building it now means the API-key day delivers a working pipeline, not a build phase.
- The prompt file (`docs/qa/qa-prompt.md`) becomes a living spec — every time a Cowork session surfaces a gap ("what do I do when the question crosses the v1/wiki boundary?", "how should I cite a confident-but-INFERRED claim?"), the answer goes into the prompt and the next session benefits.
- The benchmark grows alongside the loop: every gold answer fed back into `docs/qa/benchmark-questions.md` doubles as a Phase 4 grading datum. By the time the API key lands, the benchmark is real-world stress-tested against the wiki we have, not invented scenarios.
- Zero new runtime dependencies for the model-call path. The deterministic plumbing pulls in nothing beyond stdlib + `pyyaml` (already in `[ingest]`).

### Negative

- **Throughput is operator-gated.** Cowork sessions run when Mateo starts them. The budget model assumed ~200–500 questions/day at the API tier; manual sessions will run at whatever rate Mateo opens them. That is a feature of the "API pending" state, not a reason to avoid the approach.
- **No automated per-run evaluation.** The `jojo_qa` benchmark harness (`scripts/run_benchmark.py`) is supposed to run against the 50 gold answers on every commit. In this phase, the harness runs *router-only* in CI (deterministic, fast); the synthesis grading is "Mateo opens the diff and reads it." Good for correctness, weak for regression detection on the synthesis side. Mitigation: the first API-tier run replays the queue and grades its synthesis output against the human-triggered gold answers — natural regression baseline.
- **Latency leg of the exit criterion is not gradeable until API day.** PLAN.md §6 Phase 4 specifies p95 < 8s. Cowork sessions are human-scale (minutes per question). That is acknowledged as an operational rather than correctness gate; we declare Phase 4 "correctness-exited" when the 50-question benchmark grades ≥80% via Cowork, and "production-exited" when API-driven runs hit the latency target.
- **Queue bookkeeping is manual.** If Mateo forgets to tick a box, the next session re-answers that question. Q&A is idempotent at the answer-file level (writes overwrite by date+slug filename), so double-processing wastes a session but does not corrupt output. Fine for now; `jojo-qa replay` will own the queue state programmatically when it lands.
- **Commit provenance is mixed.** Some `wiki/derived/` commits come from human-triggered Cowork sessions, some will eventually come from API-triggered jobs. The `Co-Authored-By:` trailer disambiguates, identical to ADR 0010.
- **FU-10 (API key) stays open into Phase 4.** Unchanged from ADR 0010. This ADR explicitly accepts it as non-blocking for Phase 4 start, which mirrors PLAN.md §6 Phase 4's implicit assumption.
- **Two roles of "model" collapse into one operator.** The Haiku router and the Sonnet synthesizer are different model tiers in the budget model. In a Cowork session, both roles run as the same human-triggered session. The regex backstop in `router.py` covers the routing decision deterministically, so the loss is only that we don't measure Haiku-class router accuracy in this phase. The first API-tier run will fill that gap.

## Revisit When

- The API key lands. Everything in this ADR is designed to collapse at that point: port the prompt into `packages/jojo_qa/synthesize.py` as the system prompt; port queue state into the `jojo-qa replay` CLI; keep the gold answers as-is; flip `POST /api/qa/query` from `api_key_required` to live; keep the regex router as the safety net under Haiku. First automated run replays the human-triggered queue as its regression test.
- The human-triggered queue stalls (no sessions run for > 7 days). Signal that the prompt has a sharp edge or that Mateo is blocked elsewhere. Reason to revisit shape, not phase.
- A reviewer rejects a pattern of answers on the same structural issue — citation form, confidence calibration, EXTRACTED-vs-INFERRED discipline. Fix is to tighten the prompt, not the mechanism. Updates land in `docs/qa/qa-prompt.md` and propagate to the next session.
- `_index.md` crosses 200 pages. Triggers `qmd` activation per PLAN.md §6 Phase 4 step 5. ADR will need to address the BM25/vector pre-filter changing the retrieval bundle shape; the rest of the pipeline (router, synthesis, file-back) is unaffected.
- A second operator wants to run Q&A sessions. The queue file is the sync point, but this ADR assumes one operator at a time. Two concurrent operators would need a locking convention on the queue (or `jojo-qa` to ship first, whichever comes first).
