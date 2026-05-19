---
question_id: q-008
question: "What happened to the ITK CTM page (slug: itk-ctm-merged) — is it a separate program, or was it consolidated somewhere?"
asked_by: mateo
asked_date: 2026-05-19
session_date: 2026-05-19
session_id: cowork-2026-05-19-008
route: wiki
route_decided_by: regex
candidate_slugs:
  - itk-ctm-merged
  - itk
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

The `itk-ctm-merged` page is a redirect stub, not a live content page. It contains a single line of prose: the page was merged into the unified [[itk|ITK Program]] page (`programs/itk.md`) during the 2026-04-29 absorb pass. The stub carries `status: deleted` and a `tags: [redirect]` marker in its frontmatter [[itk-ctm-merged|itk-ctm-merged]].

The content that was formerly on (or intended for) the `itk-ctm-merged` page now lives in the unified `itk` program page. The ITK program page covers both the chemical optimization arc and the program-level decisions in a single page.

**What the unified ITK program page contains** [[itk|ITK Program]]

The ITK program page records a CRBN-based CTM degrader program targeting ITK (IL-2-inducible T-cell kinase). Key documented facts include:

- First CTM NRX-0387327: DC50 = 30 nM.
- Optimized lead NRX-0395826: DC50 = 4.1 pM — a >7,000-fold potency improvement from the first CTM [[itk|itk]].
- Late-stage isomers NRX-0401647 and NRX-0401650, both progressed to NHP studies in 2021 [[itk|itk]].
- NRX-0404422 as a third NHP compound [[itk|itk]].
- GSPT1 liability identified and the lead series separated to avoid co-degradation [[itk|itk]].
- Colitis selected as the primary therapeutic indication [[itk|itk]].
- DEL hit NRX-0390015: Kd = 50 nM with 22-fold selectivity for ITK over BTK, used as the initial hook [[itk|itk]].
- Off-target liabilities documented: LCK co-degradation (DC50 = 13.7 nM) and PTK2B co-degradation [[itk|itk]].

The consolidation of the CTM exploration content into the unified program page reflects the wiki's "one concern per page" principle: the CTM approach and the broader ITK program are the same concern — there was no separate strategic effort that warranted a standalone CTM page once the program was mature.

## Sources

- `itk-ctm-merged` — redirect stub; carries the merge notice and `status: deleted`.
- `itk` — unified ITK program page; all substantive content resides here.

## Confidence

Both claims are EXTRACTED directly from the wiki pages. The redirect stub is unambiguous; the ITK program page is the authoritative current location of the content. Confidence: high.

## Follow-ups

1. Was there a pre-merge version of the `itk-ctm-merged` page in an earlier absorb pass that contained distinct content (e.g., early-stage CTM chemistry) not present in the current unified `itk` page?
2. The ITK program page lists NHP studies for NRX-0401647, NRX-0401650, and NRX-0404422 in 2021 — did any of these advance to IND, or is the NHP stage the furthest documented in the wiki?
3. Does the colitis indication assignment reflect a formal program-level decision document, or is it stated without a cited decision artifact?

## Filed back?

No. The answer is a navigation/redirect resolution. The sole fact (the merge happened on 2026-04-29) is already in the wiki stub itself.

## Session notes

This question tests redirect-resolution behavior. A system that naively reads `itk-ctm-merged` and returns only the stub's one line would fail; a correct answer notes the redirect and follows the hop to `itk` to surface the substantive content. The benchmark entry should require the retrieval system to resolve the redirect before grading synthesis.
