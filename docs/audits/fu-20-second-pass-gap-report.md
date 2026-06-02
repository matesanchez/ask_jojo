# FU-20 Second-Pass Gap Report (2026-06-01)

**Purpose:** after the batch-2 absorption, re-scan the raw corpus against the wiki to quantify what knowledge is still missing.

## Absorption progress

| Metric | Count |
| --- | --- |
| knowledge_promote entries (recovery backlog) | 5,636 |
| — of which high-confidence | 2,368 |
| Absorbed so far (batches 1 + 2, this session) | 227 |
| Wiki pages created this session | 23 (+ literature index) |
| **Remaining knowledge_promote to absorb** | **5,409 (96.0%)** |

The session absorbed roughly **4% of the FU-20 knowledge backlog** — a substantial, fully source-grounded batch (228 distinct raw entries cited across 23 pages, 30/30 sampled hashes verified against the immutable manifest), but far from complete.

## Coverage-lint second pass

`jojo-lint coverage` (weekly check) re-run after batch 2: **still FAIL**, 12 person/folder-name skip categories still flagged (departed_individual, individual_user_data, external_literature, safety_binders, admin_records, individual_desktop, individual_user_scratch, procurement_records, vendor_operational_document, internship_admin, chat_attachments, and the literature-title category). This is expected: the check samples the whole skip population, and 96% of the knowledge content is still unabsorbed. The check will move toward PASS as the backlog is worked down in future sessions.

## What still needs absorbing (priority order)

1. **High-confidence knowledge_promote remainder (~2,140 entries).** The strongest candidates: more analytical-chemistry characterization, additional target literature, internal presentations. These should be the next sessions' focus.
2. **Low-confidence knowledge_promote (~3,187 entries).** PDFs/docs defaulting to "likely literature — needs entry-level review." Cheaper to clear but lower yield; many will reclassify to personal/software on closer read.
3. **FU-21 literature topic pages (~10–12 remaining)** over the 2,060 external_literature entries.
4. **FU-22 / FU-23 missed slice** (~2.5% of the absorbed tail) — small, deferred.

## Honest conclusion

The wiki is meaningfully more representative of the raw corpus than at session start (153 → 170 pages), and every new page is source-grounded. But **the wiki is not yet a complete representation of the raw folder** — ~96% of the identified knowledge backlog remains. Reaching the recovery's ">=90% of named subjects answerable" exit gate is a multi-session effort. The exe build does not depend on this (the wiki loads at runtime), so the app can ship at any point and absorb-recovered pages flow into the wiki folder as they are produced.
