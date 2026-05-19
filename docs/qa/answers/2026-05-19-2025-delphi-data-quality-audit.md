---
question_id: q-027
question: "What did the 2025 Delphi data quality audit find, and what changes resulted from it?"
asked_by: mateo
asked_date: 2026-05-19
session_date: 2026-05-19
session_id: cowork-2026-05-19-027
route: wiki
route_decided_by: regex
candidate_slugs:
  - 2025-delphi-data-quality-audit
hops_followed:
  - 2025-delphi-data-quality-audit
raw_fallback_used: false
raw_entries_read: []
miss_logged: false
confidence: high
filed_back: false
filed_back_path: null
schema_version: 0.1.0
---

## Answer

The 2025 [[delphi|Delphi]] data quality audit was authored by Herman Yuen on 2025-07-02. It was presented as an internal evaluation with tentative action items rather than an approved remediation plan. The audit was triggered by a specific practical failure: existing Delphi queries for sequence retrieval — joining from selection name (`sel_name`) through to `final_sequence` — were returning incomplete results. The evaluation traced the incompleteness to a combination of structural issues in the database [[2025-delphi-data-quality-audit|2025 Delphi Data Quality Audit]].

**Key findings**

*Empty tables and columns.* Protein Production (PP) contained 77 tables of which 17 were empty — a 22% empty-table rate. Tables prefixed with "ZZZ_" were flagged as likely abandoned. Campaign Planning (CP) contained 171 tables of which 70 were empty — a 41% empty-table rate. Across both modules combined, 1,439 of 3,369 columns (43%) were empty [[2025-delphi-data-quality-audit|2025 Delphi Data Quality Audit]].

*Duplicate columns with divergent values.* The same column name appeared in multiple tables with inconsistent fill rates and, in some cases, divergent values. The evaluation used `protein_alias` as the worked example: it exists in both `screening_plans` (CP) and `campaign_proteins` (CP) with different fill rates. A parallel issue was identified between `protein_target_information` (PTI) in Campaign Planning and `protein_target_form` (PTF) in Protein Production [[2025-delphi-data-quality-audit|2025 Delphi Data Quality Audit]].

*Broken sequence retrieval path.* The original query joining `del_screening.campaigns_stages_report` to `del_screening.reporting_tables` to `del_screening.campaigns_stages` was flagged as outdated. The evaluation identified a viable replacement path: join `CAMPAIGN_PLANNING.CAMPAIGNS` → `CAMPAIGN_PLANNING.SCREENING_PLANS` → `PROTEIN_PRODUCTION.LARGE_SCALE_PURIFICATION_TASKS` → `PROTEIN_PRODUCTION.CAMPAIGN_PROTEINS`, connected by `shared protein_target_form_id`. This path is incomplete because `protein_target_information_id` in `screening_plans` is populated at approximately 4%, and a subset of records has an empty `large_scale_purification_task_id` that breaks the connection from protein ID to selection name [[2025-delphi-data-quality-audit|2025 Delphi Data Quality Audit]].

*DNATAG consistency.* Mapping Protein IDs from the curated sequence table to DNATAG records mapped only 34% of selections, leaving 89 targets unmapped. Historical DNA protein IDs use name-based identifiers while the curated table uses IDs starting with the letter "N," creating 884 unmapped entries across 59 targets. Worked examples of ID mismatches were documented for CDK, IRF5, MYCN, FEM1C, and TRIM28 (e.g., Delphi recording construct "1B" for FEM1C while DNATAG records "1A") [[2025-delphi-data-quality-audit|2025 Delphi Data Quality Audit]].

**Tentative action items and consequences**

The evaluation listed four tentative action items (not yet approved at the time of authorship): (1) backfilling `large_scale_purification_task_id` as an "easy win" to reconnect many selections inside Delphi; (2) correcting DNATAG Protein ID formatting in coordination with John; (3) storing sequences directly in DNATAG for historical records that cannot be reconnected through Delphi joins; and (4) sequencing backfill for a large set of targets with no sequences at all, enumerated as: STAT6, UBE3A, WWP2, GB tag polypeptide, GLK, GRWD1, DCAF12, HPK1, IRAK4, UBR5, VHL, NR4A1, SHP2, SMARCA2, FEM1C, TRIP12, STS1, PNPLA2, PNPLA3, CHIP, NR4A2, MDM2, BRAF, FBW7, CRBN/DDB1, ITCH, PBRM1, HUWE1, CBP, UBR1, ITK, ADAR2, bTRCP, UHRF1, SHP1, NSP1, SYK, PLpro, 14-3-3 epsilon/zeta, KEAP1, SEH, ADAR1, KLHDC2, STS2, IRAK1, KRAS, PELLINO 1, cRAF, BPGM, NRDP1, RFWD2, gCatenin [[2025-delphi-data-quality-audit|2025 Delphi Data Quality Audit]].

The audit's core consequence is that Delphi cannot be used as an authoritative sequence source without the `large_scale_purification_task_id` backfill and the DNATAG ID harmonization. Analytics built on the original `del_screening.campaigns_stages_report` join path were silently returning partial results.

## Sources

- `2025-delphi-data-quality-audit` — primary decision page; documents all audit findings, the broken query path, the DNATAG mismatch analysis, and the tentative action items. Confidence:high.

## Confidence

High confidence. The `2025-delphi-data-quality-audit` page is confidence:high with a clearly identified source (Herman Yuen evaluation, 2025-07-02). All quantitative findings (empty table counts, empty column counts, DNATAG mapping rate, `protein_target_information_id` fill rate) are sourced from that page, which in turn cites specific slides in the evaluation deck.

The characterization of the action items as "tentative" is explicit in the source: the evaluation labels them as "Tentative action items" without confirmation of approval. No implementation outcomes are documented in the wiki; it is unknown which items (if any) have been completed.

## Follow-ups

1. Have any of the four tentative action items been implemented — in particular, has the `large_scale_purification_task_id` backfill been completed?
2. Was the DNATAG ID harmonization completed in coordination with John, and if so, what proportion of the 884 unmapped entries were resolved?
3. Is there a follow-up audit document (2026 or later) that assesses whether the remediation reduced the empty-table and empty-column rates?

## Filed back?

No. The answer describes the existing wiki audit page without producing novel synthesis.

## Session notes

This question maps cleanly to a single primary page with high confidence and detailed content. The key discipline is not overstating the consequences: the audit identified problems and listed tentative action items; it did not document implemented fixes. The answer correctly characterizes this as a findings-and-tentative-recommendations document rather than a completed remediation.
