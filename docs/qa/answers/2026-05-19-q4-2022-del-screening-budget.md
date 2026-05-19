---
question_id: q-026
question: "What was the Q4 2022 screening budget impact, and which programs were in the DEL screen queue at that time?"
asked_by: mateo
asked_date: 2026-05-19
session_date: 2026-05-19
session_id: cowork-2026-05-19-026
route: wiki
route_decided_by: regex
candidate_slugs:
  - q4-2022-screening-budget
  - dsa-early-discovery-cadence-2022
  - 2022-del-screen-queue
hops_followed:
  - q4-2022-screening-budget
  - dsa-early-discovery-cadence-2022
  - 2022-del-screen-queue
raw_fallback_used: false
raw_entries_read: []
miss_logged: false
confidence: medium
filed_back: false
filed_back_path: null
schema_version: 0.1.0
---

## Answer

**The Q4 2022 budget**

On October 4, 2022, Jose Santos compiled the "Q42022_DSAProjects_RemainingScreensandBudget" workbook to answer two planning questions simultaneously: which campaigns still needed to run in Q4 2022, and what that implied in NovaSeq S4 sequencing costs [[q4-2022-screening-budget|Q4 2022 Screening Budget]].

The workbook enumerated 22 remaining projects and 148 total sequencing samples for the quarter. The sequencing budget calculation was based on a NovaSeq S4 chip capacity of 64 samples per chip at a list cost of $23,000 per chip. At 148 samples, the quarter required approximately 2.3125 chips, yielding a calculated sequencing cost of $53,187.50 for the quarter (at a per-sample unit cost of $359.375) [[q4-2022-screening-budget|Q4 2022 Screening Budget]]. This chip-cost arithmetic was the primary mechanism by which the protein-sciences team converted campaign plans into finance asks.

The workbook did not contain a decision to cap or reduce the screening queue; it was a planning-and-costing document. Whether all 22 projects ran to completion in Q4 2022 is not stated in the workbook itself [[q4-2022-screening-budget|Q4 2022 Screening Budget]].

**Programs in the Q4 2022 screen queue**

The Q4 2022 budget workbook enumerated projects spanning: GRWD1, TRIM28, EWS-FLI1, CISH, FEM1A, FEM1B, IRF5, MAGED4, DCAF1, MAGEA6, IRAK4, Aurora A, CDK12, FBXO10, RNF114, TRIM25, MED8, USP18, and adjacent entries [[q4-2022-screening-budget|Q4 2022 Screening Budget]].

This list is consistent with the broader 2022 annual queue that had been established earlier in the year. The 2022 DEL queue was organized as a two-by-two grid (High Complexity vs. Low Complexity, June 1 vs. end-of-year delivery). The end-of-year High Complexity targets included GLD07, AURKA/MYCN, EWS-FLI1, and SIAH1; the end-of-year Low Complexity targets included HPK1, BRAF, CISH, Tet-2, SGC Ligases, Internal Ligases, the Ligandability Panel, SMARCA2, STAT6, and IRAK4 [[2022-del-screen-queue|2022 DEL Screen Queue]].

**Cadence and operational context**

The DSA Early Discovery biweekly meeting cadence ran from August through November 2022, covering the period immediately preceding and including Q4. The October-November 2022 updates explicitly noted that the last quarter of the year would be "heavily focused on ligases which includes targets in the ligandability effort" [[dsa-early-discovery-cadence-2022|DSA Early Discovery Cadence 2022]]. At peak periods in the September-October window, approximately 20-25 campaigns were reaching hit-resynthesis each week, out of roughly 80-100 active campaign records tracked in the system [[dsa-early-discovery-cadence-2022|DSA Early Discovery Cadence 2022]].

INFERRED: the $53,187.50 sequencing cost for 148 samples represents the expected spend ceiling for Q4 sequencing, not a cap that reduced the queue. The Q4 budget workbook was a costing exercise; the 22-project queue was the planned work, not a subset reduced from a larger request. Whether any prioritization decisions were made to reach 22 projects (vs. deferring other targets) is not documented in the absorbed sources.

## Sources

- `q4-2022-screening-budget` — decision page; documents the Q4 2022 workbook, the 22-project / 148-sample calculation, and the NovaSeq S4 chip-cost arithmetic.
- `2022-del-screen-queue` — decision page; documents the full 2022 annual screen queue organized by complexity and delivery window.
- `dsa-early-discovery-cadence-2022` — decision page; documents the August-November 2022 biweekly meeting cadence, Q4 ligase focus, and campaign throughput observations.

## Confidence

Medium confidence. All three pages are confidence:medium with sourced raw files. The program names in the Q4 workbook and the 2022 annual queue are extracted from primary source artifacts. The $53,187.50 budget figure is derived arithmetic (148 samples / 64 per chip × $23,000 per chip) confirmed by the wiki page.

The INFERRED claim — that the workbook was a costing exercise rather than a cap-driven reduction — is reasonable given the workbook's framing ("remaining screens and budget") but is not explicitly stated in the source.

## Follow-ups

1. Were all 22 Q4 2022 projects completed by year-end, or did any roll into Q1 2023? The budget workbook doesn't confirm execution status.
2. Did the ligase-heavy Q4 focus reflect a strategic decision (ligandability effort prioritization) or simply the natural queue position of those targets?
3. What was the per-chip sample cost in Q1 2023 — did the NovaSeq S4 pricing change from the $23,000 list price used in the Q4 2022 calculation?

## Filed back?

No. The answer synthesizes three existing wiki pages without novel content.

## Session notes

All three expected slugs were necessary for a complete answer. The budget workbook (`q4-2022-screening-budget`) provides the cost mechanics; the queue document (`2022-del-screen-queue`) provides the program list context; the cadence page (`dsa-early-discovery-cadence-2022`) provides the operational context (Q4 ligase focus, throughput data). The specific dollar amounts in the answer are sourced from the wiki, not invented.
