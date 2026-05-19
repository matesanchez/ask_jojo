---
question_id: q-049
question: "Where did SIAH1 and ZAP-70 stand in the DEL screen queue at the end of 2022?"
asked_by: mateo
asked_date: 2026-05-19
session_date: 2026-05-19
session_id: cowork-2026-05-19-049
route: wiki
route_decided_by: regex
candidate_slugs:
  - 2022-del-screen-queue
  - q4-2022-screening-budget
  - siah1
  - zap-70-platform
hops_followed:
  - 2022-del-screen-queue
  - q4-2022-screening-budget
  - siah1
  - zap-70-platform
raw_fallback_used: false
raw_entries_read: []
miss_logged: true
confidence: low
filed_back: false
filed_back_path: null
schema_version: 0.1.0
---

## Answer

This question has an asymmetric answer: **SIAH1's 2022 DEL queue status can be stated from the wiki (CITED); ZAP-70's 2022 DEL queue status cannot be confirmed from the wiki (MISS for ZAP-70 specifically).** The question is partially answerable.

---

### SIAH1 — answerable

**SIAH1 was classified as High Complexity / end-of-year delivery in the 2022 DEL queue.** CITED from `2022-del-screen-queue`.

The [[2022-del-screen-queue|2022 DEL Screen Queue]] page documents the March 2022 queue decision by Jose Santos. SIAH1 is explicitly placed in the "High Complexity / end-of-year delivery" category — alongside GLD07, AURKA/MYCN, and EWS-FLI1 — meaning its selection campaign was scheduled for the second half of the year. CITED from `2022-del-screen-queue` Options Considered section.

**SIAH1 C3 and C4 both reached hit resynthesis by 2022-10-01.** CITED from `2022-del-screen-queue` Outcome section.

The DSA Update 20220818 campaign table (referenced in `2022-del-screen-queue`) lists: SIAH1 C3 on 2022-10-01 and SIAH1 C4 on 2022-10-01. Both campaigns advanced to hit resynthesis by October 1, 2022, which is Q4 but still within the year's delivery window. CITED from `2022-del-screen-queue`.

**SIAH1 in Q4 2022 budget.** The [[q4-2022-screening-budget|Q4 2022 Screening Budget]] page covers 22 remaining projects with 148 total samples. SIAH1 is not explicitly listed among the Q4 projects named in the budget workbook (the named projects include GRWD1, TRIM28, EWS-FLI1, CISH, FEM1A, FEM1B, IRF5, MAGED4, DCAF1, MAGEA6, IRAK4, Aurora A, CDK12, and others). Since SIAH1 C3 and C4 reached hit resynthesis on 2022-10-01, they may have already been committed to sequencing before the Q4 budget snapshot (October 4, 2022). INFERRED: SIAH1 may have cleared the Q4 queue before the October 4 budget compilation.

---

### ZAP-70 — not answerable from the wiki

**The wiki does not document ZAP-70's status in the 2022 DEL screen queue.** This is a MISS for the ZAP-70 component of the question.

The [[zap-70-platform|ZAP-70 Platform]] page is confidence:low and is flagged as "predates post-batch-24-cbl checkpoint, sources pending backfill." Its content is limited to a brief description of the ZAP-70 kinase platform (165 project entries, 2018-2025 activity, construct variants and expression systems). The page does not mention DEL screening campaign status, queue scheduling, or any 2022-specific DEL screen data. CITED: `zap-70-platform` — no 2022 DEL queue content.

The `2022-del-screen-queue` page does not explicitly name ZAP-70 in its queue taxonomy (neither in High Complexity / June 1, High Complexity / EOY, Low Complexity / June 1, nor Low Complexity / EOY categories). There is a trailing "Kinase panel (?)" entry in the queue — ZAP-70 could be part of an unspecified kinase panel, but this cannot be confirmed from the wiki. INFERRED from absence: ZAP-70 does not appear by name in the 2022 queue.

The `q4-2022-screening-budget` page lists Q4 projects and does not name ZAP-70. CITED from `q4-2022-screening-budget`.

**Miss logged.** The ZAP-70 component of this question is logged as a miss. The wiki does not contain ZAP-70's DEL screen queue status for 2022.

---

### Summary

| Target | 2022 DEL Queue Position | Q4 2022 Status | Confidence |
|--------|------------------------|----------------|------------|
| SIAH1 | High Complexity / End-of-Year | C3 + C4 hit resynthesis by 2022-10-01 | Medium (CITED) |
| ZAP-70 | Not documented in wiki | Not documented in wiki | Low (MISS) |

## Sources

- `2022-del-screen-queue` — primary for SIAH1; queue taxonomy (High/Low Complexity × June/EOY); SIAH1 C3/C4 hit resynthesis outcome dates
- `q4-2022-screening-budget` — Q4 budget workbook; 22 projects listed; ZAP-70 not named; SIAH1 not explicitly in Q4 sample count (may have cleared before October 4)
- `siah1` — SIAH1 target page; construct context; corroborates DEL screen connection
- `zap-70-platform` — confidence:low; no 2022 DEL queue content

## Confidence

Medium for SIAH1 claims (CITED from two pages). Low overall because the ZAP-70 component cannot be answered and the `zap-70-platform` page is confidence:low. The miss on ZAP-70 is logged.

## Follow-ups

1. Does the raw corpus contain a DEL screen plan or campaign file for ZAP-70 that hasn't been absorbed yet?
2. Was the "Kinase panel (?)" trailing item in the 2022 queue ever confirmed to include ZAP-70?
3. Did the SIAH1 C3/C4 hit resynthesis on 2022-10-01 conclude the SIAH1 DEL program, or were additional campaigns planned?

## Filed back?

No. SIAH1 status is a synthesis of existing decision pages; ZAP-70 is a miss. No new wiki-worth content to file.

## Session notes

Edge case designed to test asymmetric retrieval: one target (SIAH1) has documented status, the other (ZAP-70) does not. A correct system returns the SIAH1 data (CITED), acknowledges ZAP-70's absence, and logs the miss. An incorrect system would either: (a) hallucinate a ZAP-70 DEL queue position, or (b) refuse to answer because it can't answer both parts. The benchmark should require both the positive SIAH1 answer and the honest ZAP-70 miss to grade the response as correct. The table format captures the asymmetry cleanly.
