# FU-20 Reclassification Summary

**Generated:** 2026-06-01  
**Method:** entry-level filename/title/source_id pattern classification + SHA256 duplicate detection (per `GOAL_PROMPT_WIKI_RECOVERY.md` sub-phase 1.1).  
**Input:** `docs/compile/queue.md` skip lines for `departed_individual` + `individual_user_data`.  
**Output:** `docs/audits/fu-20-reclassification.jsonl` (8450 records).

## Bucket totals

| Category | Population | knowledge_promote | personal_confirmed | software_confirmed | duplicate_of_already_absorbed |
| --- | --- | --- | --- | --- | --- |
| `departed_individual` | 2955 | 1360 | 1539 | 45 | 11 |
| `individual_user_data` | 5495 | 4276 | 611 | 550 | 58 |

**Combined knowledge_promote: 5636 of 8450 (66.7%)** — consistent with the FU-20 audit's ~57% estimate.

## Confidence distribution (knowledge_promote)

- high: 2368
- medium: 81
- low: 3187

High-confidence promotions are the priority absorb set; low-confidence default-promotes warrant entry-level human review before absorb.
