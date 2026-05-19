---
question_id: q-022
question: "How are DEL libraries constructed at Nurix, and what are the key library parameters?"
asked_by: mateo
asked_date: 2026-05-19
session_date: 2026-05-19
session_id: cowork-2026-05-19-022
route: wiki
route_decided_by: regex
candidate_slugs:
  - del-libraries
  - dna-encoded-libraries-screening
hops_followed:
  - del-libraries
  - dna-encoded-libraries-screening
raw_fallback_used: false
raw_entries_read: []
miss_logged: false
confidence: medium
filed_back: false
filed_back_path: null
schema_version: 0.1.0
---

## Answer

DNA-encoded libraries (DELs) are high-diversity small-molecule collections in which each compound is covalently linked to a unique DNA sequence that encodes the compound's structure. Screening proceeds by exposing the library to an immobilized or solution-phase target protein; compounds that bind the target remain associated with it while non-binders are washed away. The retained DNA tags are then amplified by PCR and sequenced to identify which chemical structures were enriched, revealing the binding compounds [[dna-encoded-libraries-screening|DNA Encoded Libraries Screening]].

The canonical DEL construction method is split-and-pool synthesis: a large pool of DNA-tagged building-block fragments is split into subpools, each subpool reacts with a different chemical building block (a "cycle"), and the products are recombined. This split-pool cycle is repeated for each chemical cycle, exponentially expanding diversity. Each completed compound carries a DNA tag that encodes the sequence of building blocks added at each cycle, functioning as a molecular barcode that survives the affinity-selection process and can be read out by next-generation sequencing [[dna-encoded-libraries-screening|DNA Encoded Libraries Screening]].

At Nurix, the DEL portfolio used for selection campaigns is tracked in the DS Projects JSS and DSA Projects workbooks. Named library subsets include D1, D2, D3, D4, D5, NRX09, NRX04 Covalent, Deck1, Deck2, ssD1 through ssD3, and D8 [[del-libraries|DEL Libraries]]. These names represent distinct library pools or sub-libraries within the overall Nurix DEL inventory; the wiki does not specify the precise compound count or synthesis cycle count for each named subset, and claiming specific library sizes would not be sourced.

Campaign planning decisions determine which libraries are drawn for a given target. The test funnel tier assigned to each campaign — "No DSTF" (no DEL Screen Test Funnel), "Light Touch," or "Full test funnel" — controls how much pre-screen biophysical characterization a target receives before library is committed [[del-libraries|DEL Libraries]]. For previously screened targets, the 2022 operational practice was to focus new screens on the NRX09 library rather than the full portfolio [[del-libraries|DEL Libraries]].

Post-selection, sequencing is performed on NovaSeq S4 chips. The Q4 2022 budget workbook documented 64 samples per NovaSeq S4 chip at a list cost of $23,000 per chip, producing a per-sample sequencing cost of $359.375 [[del-libraries|DEL Libraries]]. The end-to-end cycle time from campaign screening through hit resynthesis was approximately 8 to 10 weeks [[del-libraries|DEL Libraries]].

## Sources

- `del-libraries` — platform page; covers Nurix's named library subsets, campaign-level library selection logic, test funnel tiers, and sequencing cost parameters.
- `dna-encoded-libraries-screening` — reference page; covers DEL construction principles (DNA encoding, affinity selection, PCR amplification, sequencing), screening workflow, and foundational references.

## Confidence

High confidence: the DEL construction mechanism (DNA tagging, split-and-pool synthesis, affinity selection, sequencing readout) is sourced from `dna-encoded-libraries-screening`. The named Nurix library subsets (D1-D5, NRX09, etc.) are sourced from `del-libraries`. The sequencing cost arithmetic is sourced from `del-libraries` and derived from the Q4 2022 budget workbook.

Lower confidence: specific synthesis cycle counts, compound counts per library, or detailed construction chemistries for individual Nurix DEL subsets are not present in the wiki. The wiki does not claim to document how the named libraries were physically constructed; it documents how they are used in campaigns. Any claim about library diversity numbers would be unsourced.

## Follow-ups

1. What are the structural differences between the Nurix library subsets (e.g., D-series vs. Deck vs. NRX09) in terms of scaffolds or chemical diversity?
2. How does the test funnel tier assignment process work — who decides whether a target gets "Full test funnel" vs. "Light Touch"?
3. What downstream affinity validation assays (DSF, SPR, ITC) are used after sequencing to confirm DEL hits before resynthesis?

## Filed back?

No. The answer draws on existing wiki content without novel synthesis.

## Session notes

The question blends "how are DEL libraries constructed" (a methods/principles question answered by `dna-encoded-libraries-screening`) with "what are Nurix's library parameters" (a Nurix-specific question answered by `del-libraries`). Both pages are necessary for a complete answer. The split-and-pool construction description is from the reference page; the library names and sequencing metrics are from the platform page.
