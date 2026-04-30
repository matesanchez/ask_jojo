# External Domain-Reviewer Pass — Scoping Document

**Status:** Proposed (2026-04-30). Awaiting Mateo to confirm reviewer slate.
**Owner:** Mateo de los Rios.
**Related:** ADR 0011, PLAN.md §6 Phase 2 exit criterion (≥80% domain-reviewer acceptance), ADR 0010.

## Why

Phase 2 exit was declared on 2026-04-30 with the program owner (Mateo) reviewing the top-10 wiki pages and accepting them. The PLAN.md §6 Phase 2 exit criterion reads "≥3 domain reviewers judge the top-10 pages 'accurate and useful'." A program-owner-only review satisfies the criterion's intent in a one-operator project, but Phase 4 Q&A is going to cite these pages to a wider audience — and a wider audience expects independent corroboration.

The external pass is also a rare, high-leverage chance to catch subtle errors before the bot starts citing pages confidently. Once Phase 4 lights up and the wiki starts being a primary information surface for Protein Sciences scientists, there's no graceful way to retract a page that's been cited; better to harden the foundation now.

This pass is *not* a re-do of Phase 2. The wiki structure, taxonomy, and prompt are not under review. Only the *content* of a hand-picked subset of pages is.

## Scope

**In scope:** the 30 highest-traffic and highest-confidence wiki pages in the Protein Sciences corpus. Selection criteria:

1. The 5 most-cited pages by inbound `_backlinks.json` count (currently includes `cbl-b`, `cbl-b-target`, `del-screening`, `delphi`, and `targeted-protein-degradation` based on the 138-page index).
2. The 10 most-recently-touched pages from `git log --pretty=format:%H ask_jojo_wiki/` (recency biases toward content the absorb pipeline has been working on most actively).
3. The 5 highest-degree nodes in `_graph.json` (currently `delphi` at degree 36 — Delphi is the structural anchor of the Protein Sciences corpus).
4. The 10 pages flagged with `confidence: high` in frontmatter (these are the ones the Q&A pipeline trusts most by construction; if any of them are wrong, the bot will be most confident exactly where it's most wrong).

The four selection criteria overlap; the union is roughly 30 pages.

**Out of scope:**

- The full 138-page wiki. A 30-page sample is sufficient to grade the synthesis discipline; expansion can be a Phase 6 lint-priority signal rather than a scheduled review.
- The `_needs_review.md`-flagged pages (the 13 backfilled today). Those are already known to be `confidence: low`.
- The `derived/` directory (Q&A output). This is reviewed per-Cowork-session by the operator at write-back time.
- Anything in `equipment/akta/` (handled by v1.0).

## Reviewers

Three reviewers per the PLAN.md criterion. Suggested slate (Mateo to confirm):

1. **Mateo de los Rios** (program owner). Already reviewed the top-10. Continues to be one of the three.
2. **A second Protein Sciences scientist** with deep coverage of the DEL screening + Delphi corpus (the two largest topical clusters). Candidates Mateo can name: Emily Low (authored several Delphi schematics cited in the wiki), Jose Santos (authored the 2022 DEL queue), or Jo-Ann Wilson (CBL-B CMC). One reviewer covers a *cluster* — pick whichever cluster has the most program-cited pages today.
3. **A third reviewer outside the immediate authoring chain** — someone whose name does not appear in the wiki's source paths. The point is to test whether a Protein Sciences scientist who *did not* generate the source material can still verify the wiki's claims from the cited raw sources. This is the strongest signal that the wiki is a working knowledge surface, not a self-confirming bubble.

## Mechanism

Each reviewer gets:

- A markdown link to each of the 30 pages in the Wiki tab (deep-links work today via `/wiki?slug=<slug>`).
- A one-page review form (a Google Form, an internal SharePoint list, or a markdown checklist in `docs/qa/reviews/<reviewer>-<date>.md` — operator's choice).
- A 30-minute orientation showing the Wiki tab, the citation chain (page -> Raw tab via the source-link click), and the EXTRACTED-vs-INFERRED convention.
- Two weeks (calendar) to review.

Per page, the reviewer marks one of:

- **Accept (correct and useful)** — the page reads accurately given the cited sources, and a Protein Sciences scientist would learn something true from it.
- **Accept with edits** — substantively correct but has at least one specific issue (named in a free-text field). Goes to a follow-up absorb pass to fix.
- **Reject** — substantively incorrect, contradicted by sources, or hallucinated content. Page is flagged in `_needs_review.md` and removed from the candidate-retrieval pool until fixed.

The page-level decision is the unit. A "Reject" on any one of the 30 pages does *not* fail the whole pass; it fails that page. The pass overall grades on the **acceptance rate**.

## Pass criterion

The PLAN.md criterion is "≥80% accurate and useful per ≥3 reviewers". For the 30-page sample, that's ≥24 pages (80%) with at least two of three reviewers marking either Accept or Accept with edits. Any page with a Reject from two of three reviewers is treated as a structural defect — the absorb pipeline gets a follow-up fix-up pass before Phase 4 lights up at scale.

If the pass falls below 80%, the implication is that the wiki's synthesis discipline is more brittle than Mateo's first-pass review suggested, and Phase 4 should not light up at scale until the pattern is named and fixed in the absorb prompt. The fix is to update `docs/compile/compile-prompt.md` and re-absorb the affected raw entries.

## Output

When the pass finishes, write `docs/qa/reviews/external-pass-2026-MM.md` with:

- Acceptance rate per page, per reviewer.
- Pattern-level findings (e.g. "5 of 30 pages had ungrounded specific numbers in the Overview section" -> a prompt-tightening rule).
- A list of pages flagged for follow-up absorb.
- An updated `_needs_review.md` reflecting the rejections.

Update Phase 2's status note in `docs/v2_status.md` with the pass result. If the pass is clean, the entry says "Phase 2 cross-validated by external reviewer pass on YYYY-MM-DD". If not clean, it says "Phase 2 partially re-opened by external reviewer pass; X pages flagged" with a link to the follow-up absorb queue.

## Why now (vs after FU-10)

This pass should run *before* the API key lands, not after. Three reasons:

1. **Cowork sessions are still producing gold answers.** Every gold answer that cites a flawed page is a benchmark entry that grades on flawed content. Catching the page-level errors before the gold answers accumulate makes the benchmark more trustworthy.
2. **The reviewer pool is human.** It does not scale with API rate limits. Doing the pass now means we don't wait on FU-10 for *anything* on the Phase 4 critical path.
3. **The prompt-tightening loop benefits.** Every rejection produces a structural finding (e.g. "the wiki conflated NX-1607 and NX-0255 dosing"); those findings tighten `docs/compile/compile-prompt.md` and `docs/qa/qa-prompt.md`. The earlier the loop runs, the more sessions it benefits.

## Estimated cost

3 reviewers × 30 pages × ~4 minutes per page = ~6 hours of total reviewer time. Plus ~2 hours operator time to package, distribute, and aggregate.

## Trigger

Mateo greenlights, names the second and third reviewers, and the operator (also Mateo today) sends the review packets within 7 days. Calendar window for reviewer responses: 14 days. Result-write-up + `_needs_review.md` updates: 2 days. Total: 23 days from greenlight to closed loop.

The earliest realistic completion window is therefore roughly 2026-05-23. That timing is fine: it lands before the FU-10 unblock window in any reasonable scenario, and it also lands after the first 5–10 Cowork Q&A sessions have populated `docs/qa/answers/` with gold-answer benchmark seed material — both of which sharpen the review.
