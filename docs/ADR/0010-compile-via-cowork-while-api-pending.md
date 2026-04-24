# ADR 0010 — Compile via Cowork Sessions While API Access Is Pending

**Status:** Accepted
**Date:** 2026-04-24
**Deciders:** Mateo de los Rios
**Related:** `ADR 0001` (wiki over RAG), `ADR 0000` (v2 roadmap — Phase 2), `schema/CLAUDE.md` (wiki constitution), `docs/follow-ups.md` FU-10 (Anthropic API key — AWS payment leg)

## Context

Phase 2 (Wiki Compile) needs a Claude model to read raw files from `ask_jojo_raw/`, plan against the wiki constitution in `schema/CLAUDE.md`, and write new or updated pages into `ask_jojo_wiki/`. The design always assumed those calls come from the `jojo_compile` package talking to the Anthropic API on a rotating Sonnet 4.6 / Haiku 4.5 / Opus 4.6 schedule (see `PLAN.md` §4 D8 and the budget model in `docs/budget-model.xlsx`).

Two things are true at the same time:

1. **Phase 2 is unblocked everywhere except model access.** Phase 1 exit is met (`docs/phase-1-exit-evidence.md`), the raw corpus has 19k+ files across four connectors, the schema / taxonomy / absorb-loop contract is written (`schema/CLAUDE.md` v0.1.0, `ask_jojo_wiki/SCHEMA.md` v0.1.0), and the `ask_jojo_wiki/` repo exists and is empty.
2. **The Anthropic API key is not coming soon.** The AWS payment-method leg for Anthropic API billing is stuck; we don't have an ETA. Waiting on it to start Phase 2 means calendar slippage of unknown size and nothing to show for the Phase 1 → Phase 2 transition.

Separately, we do have Claude access — just not via the API. Mateo's Nurix login has access to Claude.ai and the Cowork desktop app (which is what wrote this document). Cowork sessions can read `ask_jojo_raw/` and `ask_jojo_wiki/` directly via the file tools, run ruff / pytest through the shell, and produce diffs the operator reviews and commits. They cannot, however, be triggered by `jojo_compile absorb` — there is no programmatic entry point, and each session is human-initiated.

A related constraint: Phase 2 absorb has a lot of human-judgment load even with API access. The 15-entry checkpoint (`schema/CLAUDE.md` §3), the EXTRACTED vs INFERRED discipline, the contradiction policy, and the taxonomy-reorganization pass all benefit from early human review. Shipping a fully autonomous `jojo_compile absorb` loop on day one is a worse idea than running the same loop with a human in the read/review seat, regardless of API status.

## Decision

**Run Phase 2 absorb via human-triggered Cowork sessions until API access lands, then transplant the mechanics into `jojo_compile absorb` unchanged.**

Concretely:

1. **`packages/jojo_compile/` stays stubbed.** Module shape, CLI skeleton, and the eight submodule names (`absorb.py`, `plan.py`, `write.py`, `verify.py`, `link.py`, `checkpoint.py`, `breakdown.py`, `reorganize.py`) from `PLAN.md` §6 Phase 2 are still the target; no real logic lands inside them yet. The public shape of the eventual `absorb()` call is being designed against exactly what the Cowork session does by hand this phase.

2. **`docs/compile/compile-prompt.md` is the operational entry point.** A self-contained prompt Mateo pastes into a fresh Cowork session. It points the session at the wiki constitution, the taxonomy, the raw corpus, and the queue — and tells it to write pages with the exact frontmatter/citation/style discipline the autonomous loop will eventually enforce. The prompt is the living specification of what `jojo_compile absorb` has to reproduce.

3. **`docs/compile/queue.md` is the batch tracker.** A markdown file with an unchecked list of raw-entry IDs, grouped into batches of ~10. Each Cowork session claims the next unchecked batch, absorbs it, ticks the boxes, commits, and stops. No global state beyond the queue file and the wiki repo itself; resumption is just "open queue file, find next unchecked batch."

4. **Commits use the constitutional format.** Per `schema/CLAUDE.md` §9, wiki commits are `absorb(<corpus>): <N> pages touched, <M> created`. Human-triggered Cowork sessions use the same prefix. A `Co-Authored-By:` trailer (`Co-Authored-By: Claude Sonnet 4.6 via Cowork <noreply@anthropic.com>`) identifies the provenance so later lint passes can distinguish human-triggered from API-triggered absorbs if that ever matters. (Not expected to matter — the output discipline is identical by construction.)

5. **Output is written to the real `ask_jojo_wiki/` repo, not a scratch dir.** The whole point of running this phase at all is to produce a wiki the domain reviewer can accept ≥80% of on first pass (Phase 2 exit criterion). Hiding output in a scratch area while waiting for the API would delay that feedback loop for no gain. The wiki repo stays private per `ADR 0006`.

6. **Phase 2 exit criterion is unchanged.** Domain-reviewer acceptance ≥80% of Protein Sciences pages, no hallucinations traceable to cited sources. The *mechanism* of production doesn't move the bar.

## Rationale

Three reasons.

1. **The hard parts are the schema, taxonomy, and prompt — and those need pressure-testing anyway.** Whether the model call comes from `anthropic.Anthropic().messages.create(...)` or from a Cowork session, the work product is the same: a page in `ask_jojo_wiki/` that obeys `SCHEMA.md` and cites real raw sources. The per-page writing discipline is what we need to stress-test before writing autonomous absorb code. Running it by hand for a few dozen entries first *tightens* the prompt we'll eventually bake into `write.py`. Starting the API-driven loop on day one would have meant debugging prompt issues through a CI pipeline instead of in the same window that's producing the output.

2. **Zero disposable work.** The artifacts produced this phase — wiki pages, `_index.md`, `_backlinks.json` once we generate it, the queue, and the prompt itself — all persist into the API-driven phase. The queue becomes the input to `jojo_compile absorb --queue docs/compile/queue.md`. The prompt becomes the system prompt of `write.py`. The pages stay where they are. The only thing that changes on API day is what pushes the "go" button: a scheduled task instead of a human.

3. **Parallel unblocks, no critical-path dependency.** This keeps the team off the "wait for AWS → wait for IT → wait for Anthropic onboarding" dependency chain. Phase 1 unattended-soak is running in the background (closes 2026-04-30, see `docs/phase-1-exit-evidence.md`). Phase 3 Wiki-tab UI work can start against pages produced manually. None of it depends on the API key landing this week or next.

An alternative considered: **wait for the API.** Rejected for the reasons above — we'd produce zero wiki in the interim, domain review wouldn't start, and we'd still have to pressure-test the prompt when the key finally lands. Another: **run compile via Claude Code with a per-file prompt.** Rejected because the Cowork session has the same file-tools + shell surface plus a cleaner human-in-the-loop review model; Claude Code is aimed at software engineering, not markdown synthesis, and would be the wrong vehicle.

## Consequences

### Positive

- Phase 2 produces real wiki output in the week after Phase 1 exits, not "whenever AWS clears."
- Every absorb run gets a built-in review pass (human opens diff, merges or fixes). Domain-reviewer acceptance rate at Phase 2 exit will be more informative, not less, because the easy mistakes get caught early.
- The prompt file (`docs/compile/compile-prompt.md`) becomes a living spec — every time a session surfaces a gap ("what do I do when two sources contradict?", "does this page belong in `methods/` or `protocols/`?"), the answer goes into the prompt, and the next session benefits. By API day, the prompt has been stress-tested against real corpus material, not invented scenarios.
- Zero new runtime dependencies. No new packages, no new env vars, no new scheduled tasks. The installer (`ops/installer/Install-JojoBot.ps1`) doesn't change.

### Negative

- **Throughput is operator-gated.** A Cowork session runs when Mateo starts it. The budget model assumed ~200–500 pages/week at the API tier; manual sessions will run at whatever rate Mateo opens them, which is lower. That is a feature of the "API pending" state, not a reason to avoid the approach.
- **No automated per-run evaluation.** `jojo_compile absorb` is supposed to run against a golden-set eval on every checkpoint. In this phase, evaluation is "Mateo opens the diff and reads it." Good for correctness, weak for regression detection. Mitigation: the first API-tier run should replay the same queue and compare its output to the human-triggered pages, which gives us a natural regression baseline.
- **Queue bookkeeping is manual.** If Mateo forgets to tick a box, the next session re-absorbs that entry. The absorb pipeline is idempotent at the *page* level (per `schema/CLAUDE.md` §3: "integrate new material into existing structure, don't chronicle it"), so double-processing wastes a session but doesn't corrupt output. Fine for now; `jojo_compile absorb` will own the queue state programmatically when it lands.
- **Commit provenance is mixed.** Some wiki commits come from human-triggered Cowork sessions, some will eventually come from API-triggered jobs. The `Co-Authored-By:` trailer disambiguates, but anyone reading `git log` has to know that. Documented in `docs/compile/compile-prompt.md` so it's not folklore.
- **FU-10 (API key) stays open past Phase 1.** Not a new cost — it was already open as a Phase 0 checklist line — but this ADR explicitly accepts it as non-blocking for Phase 2 start, which is a change from `PLAN.md` §6 Phase 2's implicit "wait until keys land" framing.

## Revisit When

- The API key lands. Everything in this ADR is designed to collapse at that point: port the prompt into `packages/jojo_compile/write.py` as the model system prompt; port queue state into the `jojo_compile absorb` CLI; keep the pages as-is. First automated run replays the human-triggered queue as its regression test.
- The human-triggered queue stalls (no sessions run for > 7 days). That's a signal Mateo is blocked elsewhere or the prompt has a sharp edge; either way it's a reason to revisit the shape, not the phase.
- Domain reviewer rejects a pattern of pages on the same structural issue — frontmatter, citation style, length. The fix is to tighten the prompt, not the mechanism. Updates land in `docs/compile/compile-prompt.md` and propagate to the next session.
- A second operator wants to run absorb sessions. The queue file is the sync point, but the ADR assumes one operator at a time today. Two concurrent operators would need a locking convention on the queue (or `jojo_compile absorb` to ship first, whichever comes first).
