---
question_id: q-005
question: "What's the standard buffer prep procedure for an ÄKTA Pure 25 run on the BTK program?"
asked_by: mateo
asked_date: 2026-04-30
session_date: 2026-04-30
session_id: cowork-2026-04-30-005
route: v1
route_decided_by: regex
candidate_slugs: []
hops_followed: []
raw_fallback_used: false
raw_entries_read: []
miss_logged: false
confidence: high
filed_back: false
filed_back_path: null
schema_version: 0.1.0
---

## Answer

**Routing slip:** This question routes to the v1.0 ÄKTA / UNICORN path, not the wiki. The regex in `packages/jojo_qa/router.py` matches three of the v1 trigger keywords (`akta`, `buffer`, and `purif` implied by "buffer prep procedure for an ÄKTA Pure run"), and the fundamental subject is chromatography buffer prep, which is v1.0's specialty domain. The mention of "the BTK program" is incidental scoping — it does not change the underlying procedure, which is the same instrument and the same buffer-prep SOP regardless of which Nurix program supplies the protein.

The answer should be retrieved from v1.0 (the legacy JoJo Bot ÄKTA / Protein Purification Expert), which has access to the 232-document UNICORN / ÄKTA manual corpus indexed in v1.0's ChromaDB. Per `PLAN.md` §6 Phase 4, v1.0 remains the authoritative subsystem for chromatography questions through Phase 4 and beyond — there is no plan to migrate ÄKTA content into the wiki until v1.0 falls behind on coverage or until the `equipment/akta/` wiki directory is intentionally populated by an absorb pass against the manual corpus. As of 2026-04-30, the wiki has zero ÄKTA pages (the `equipment/` directory contains only `laboratory-instruments.md` and `refeyn-mass-photometry.md`).

To answer the question itself, the operator should issue it through the v1.0 chat path (Chat tab when wired in Phase 4 step 7; the v1.0 frontend until then) where it will be answered against the ÄKTA / UNICORN manual corpus with proper citations.

## Sources

None. This is a router-test answer, not a synthesis answer. The wiki is intentionally not consulted.

## Confidence

High on the routing decision. The question contains three v1-trigger keywords (`akta`, `buffer`, and an implicit `purif` via "buffer prep procedure for an ÄKTA Pure run"), and v1.0 is documented as the authoritative path for chromatography-related questions per `PLAN.md` §6 Phase 4 and `ADR 0011` "Routing rules" §2.

The only INFERRED claim is the implicit-`purif` detection — the regex only matches `purif` as a literal substring, and "Pure" (the instrument name) does not match `purif` because the regex uses word-boundary `\b`. The trigger here is the explicit `akta` and `buffer` keywords; `purif` is a soft trigger from the human reading. The router's regex correctly routes this to `v1` on `akta` alone.

## Follow-ups

1. Should the router also flag the *program-keyword on a v1-route question* pattern as an explicit edge case in `qa-prompt.md`'s "Routing edge cases"? This question's "BTK program" mention is the canonical example.
2. When the wiki's `equipment/akta/` directory is eventually populated, what's the migration trigger that flips this question's route from `v1` to `wiki`? Probably "wiki coverage threshold" (e.g. ≥10 ÄKTA pages with ≥80% coverage of v1.0's most-cited manual sections), and probably best captured as a future ADR rather than a regex change.
3. Are there any chromatography-adjacent questions where the wiki *does* have authoritative coverage today (e.g. SEC-MALS, which has a wiki page at `methods/sec-mals.md`)? If so, the router needs a "wiki override" list for those keywords; otherwise an SEC-MALS question containing "purification" might mis-route to v1.

## Filed back?

No. Router-test answers do not produce wiki content; they record a routing decision. Adding this answer file to `docs/qa/answers/` is the entire artifact.

## Session notes

This is the seed benchmark's `v1-routing` category exemplar. Three things worth noting for the prompt-tightening loop:

1. The "BTK program" red herring is exactly the kind of misdirection the regex backstop is supposed to handle correctly, and it does — `akta` alone is a sufficient v1-trigger, so the question routes correctly even without considering `buffer` or the `program` mention. Worth keeping as the canonical regression test for "router doesn't over-rotate to wiki on program-keyword."
2. The `purif` regex doesn't match "Pure" as a substring (good; the regex uses `\b` boundaries), but it would match "purification" in a follow-up question like "what's the BTK purification yield for the v3.5 buffer?" That follow-up would route to `v1` correctly.
3. The wiki's `methods/sec-mals.md` does contain chromatography-adjacent content (size-exclusion chromatography paired with multi-angle light scattering), and a question phrased as "What's the SEC-MALS analysis pipeline?" could plausibly route either way — the regex would catch `chromatograph` and route to `v1`, but the wiki has the better answer for *analysis* (vs. *operation*). Add to qa-prompt's edge-case list.

The session note here is more substantive than the answer itself, which is appropriate for a router-test entry. The benchmark grades router decisions, not synthesis depth, on `v1-routing` entries.
