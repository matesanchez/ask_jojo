---
question_id: q-007
question: "What's the relationship between the CBL-B CTM exploration page and the CBL-B preclinical profile page — do they cover the same compounds, or different stages?"
asked_by: mateo
asked_date: 2026-05-19
session_date: 2026-05-19
session_id: cowork-2026-05-19-007
route: wiki
route_decided_by: regex
candidate_slugs:
  - cbl-b-ctm
  - cbl-b-preclinical-profile
hops_followed:
  - cbl-b
raw_fallback_used: false
raw_entries_read: []
miss_logged: false
confidence: high
filed_back: false
filed_back_path: null
schema_version: 0.1.0
---

## Answer

The `cbl-b-ctm` and `cbl-b-preclinical-profile` pages cover different compound classes at different program stages. They do not overlap in the compounds they describe.

**CBL-B CTM Page** [[cbl-b-ctm|CBL-B CTM Exploration]]

The `cbl-b-ctm` page documents the early 2017-2018 exploration of degrader (CTM) approaches to CBL-B. The starting chemistry was the Wylie strategy using VHL-based CTMs. The parental compound NRX-0395370 was a DEL-derived CBL-B inhibitor (IC50 = 12 nM, ~10x selectivity over c-CBL) used as the CBL-B binding warhead for CTM construction. The first CTM NRX-0395686 showed only modest degradation (DC50 ~250 nM, Dmax ~20-50%), establishing that a CTM could be made but was not yet potent enough for a program lead [[cbl-b-ctm|cbl-b-ctm]].

A second-generation CTM, NRX-0398194, achieved more efficient degradation (~75%) but introduced a critical liability: co-degradation of GSPT1, which prevented any T-cell cytokine enhancement in cellular assays, making this compound unsuitable as a lead [[cbl-b-ctm|cbl-b-ctm]]. A HiBiT screening platform was subsequently deployed in Jurkat cells to triage degrader candidates in a higher-throughput format. The best compound from the second-round HiBiT screen was NRX-0400149 (Dmax 67.2%) [[cbl-b-ctm|cbl-b-ctm]].

None of these CTM compounds (NRX-0395686, NRX-0398194, NRX-0400149) appear in the preclinical profile page.

**CBL-B Preclinical Profile Page** [[cbl-b-preclinical-profile|CBL-B Preclinical Profile]]

The preclinical profile page documents the three compounds that entered preclinical (IND-enabling) profiling as CBL-B *inhibitors*, not degraders. These are NRX-0388766, NRX-0390255 (NX-0255), and NRX-0391607 (NX-1607). The page records the July 2019 drug candidate (DC) criteria, Q3 2019 candidate selection, and the differentiated profiles of the two clinical candidates:

- NX-1607 (NRX-0391607): oral lead; IC50 < 10 nM; IND filing planned H1 2021; estimated human dose ~100 mg QD; hERG at 8 µM (slightly below the 10 µM criterion but accepted); intended for systemic immuno-oncology (mCRPC and other indications) [[cbl-b-preclinical-profile|cbl-b-preclinical-profile]].
- NX-0255 (NRX-0390255): ex vivo cell-therapy use (TIL and CAR-T programs); DeTIL-0255 and DeCART programs; IND Q4 2020 [[cbl-b-preclinical-profile|cbl-b-preclinical-profile]].
- NRX-0388766 was de-selected due to an aniline metabolite concern, though the safety evaluation of that metabolite was ultimately acceptable [[cbl-b-preclinical-profile|cbl-b-preclinical-profile]].

**Relationship Summary**

The two pages document sequential but non-overlapping compound classes. The `cbl-b-ctm` page captures a degrader (PROTAC/CTM) modality that was explored in 2017-2018 but did not produce an IND candidate. The `cbl-b-preclinical-profile` page captures the inhibitor series that did produce IND candidates (NX-1607 and NX-0255). The CTM exploration was a parallel effort during the same period that the inhibitor program was maturing; the CTM compounds are all in the NRX-039xxxx range, while the preclinical inhibitor compounds span NRX-038xxxx to NRX-039xxxx. No compound from the CTM page advanced to preclinical profiling.

Both pages link back to the parent [[cbl-b|CBL-B Program]] page, which provides the overarching program context.

## Sources

- `cbl-b-ctm` — CTM exploration page; covers DEL-derived parental NRX-0395370, first CTM NRX-0395686, GSPT1-co-degrader NRX-0398194, HiBiT screening, NRX-0400149.
- `cbl-b-preclinical-profile` — IND-enabling profiling page; covers NRX-0388766, NX-0255 (NRX-0390255), NX-1607 (NRX-0391607), DC criteria July 2019, candidate selection Q3 2019.
- `cbl-b` (program page) — read for context; not directly cited.

## Confidence

All claims in this answer are EXTRACTED from the two cited wiki pages. No inferences required beyond the structural observation (which is itself directly supported by the compound set difference). Confidence: high.

## Follow-ups

1. Were any of the CTM compounds from `cbl-b-ctm` (particularly NRX-0400149) further profiled before the decision to deprioritize the degrader approach in favor of the inhibitor program?
2. Does the `cbl-b-cmc` page document the formulation of NX-1607 as the oral lead, and does it confirm the hERG note from the preclinical profile page?
3. Is there a design decision artifact that explicitly records the choice to advance the inhibitor program over the CTM program?

## Filed back?

No. This is a cross-page comparison answer that simply enumerates what is already present in the two cited pages. There is no novel synthesis beyond what the wiki already contains.

## Session notes

The question is designed to stress-test retrieval pairing: will the system pull both `cbl-b-ctm` and `cbl-b-preclinical-profile` together, or only one? The answer requires both pages and cannot be constructed from either alone. A correct retrieval bundle must include both.
