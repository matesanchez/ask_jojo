---
question_id: q-028
question: "What was the Loka ML engagement in 2024 — what was the scope and what did it deliver?"
asked_by: mateo
asked_date: 2026-05-19
session_date: 2026-05-19
session_id: cowork-2026-05-19-028
route: wiki
route_decided_by: regex
candidate_slugs:
  - loka-ml-engagement
hops_followed:
  - loka-ml-engagement
raw_fallback_used: false
raw_entries_read: []
miss_logged: false
confidence: low
filed_back: false
filed_back_path: null
schema_version: 0.1.0
---

## Answer

In September 2024, Nurix Protein Sciences prepared a bulk export of target form information for delivery to Loka ML, an external machine learning vendor. The export was compiled by September 9, 2024 and captured metadata for approximately 130+ unique target protein constructs [[loka-ml-engagement|Loka ML Engagement 2024]].

**Data submitted**

The export file (20240909-bulk_info_for_ps.xlsx) contained target metadata organized by target alias and form designation. Fields included: target form alias, target name, canonical target identifier (e.g., AURKA_NC15, BCT_NC34), positive hit counts (n_pos), negative hit counts (n_neg), and total screening observations (n_total). The dataset represented a historical snapshot of DEL screening results and protein construct metadata at the point of vendor handoff [[loka-ml-engagement|Loka ML Engagement 2024]].

Targets represented in the export included Aurora A (AURKA) in multiple constructs and domains, ADAR1 fragments, Beta-Catenin (BCT) variants, BRCA1 isoforms and domains, and BTK wild-type and mutant forms, among others [[loka-ml-engagement|Loka ML Engagement 2024]].

**Scope and stated rationale**

The wiki characterizes the engagement as intended to enable Loka ML to develop predictive models on Nurix protein data, potentially accelerating lead optimization and hit prioritization by leveraging vendor model capabilities trained on multi-company datasets [[loka-ml-engagement|Loka ML Engagement 2024]].

**What the wiki does not document**

The `loka-ml-engagement` wiki page is confidence:low and explicitly notes that the specific modeling objectives, timeline, contractual terms, and deliverables of the Loka ML engagement are not documented in the exported data file and would be found in related contracts or project kickoff documentation [[loka-ml-engagement|Loka ML Engagement 2024]]. The wiki records only the data handoff artifact, not the engagement scope or outcomes.

INFERRED: the bulk export was a data-preparation step at the start of (or early in) the engagement, enabling Loka ML to begin model development. Whether models were delivered, what their architecture was, or how their outputs were used in Nurix workflows is not documented in the absorbed wiki sources. Any claim about delivered ML model results would be unsourced.

## Sources

- `loka-ml-engagement` — decision page; documents the September 2024 bulk export of DEL screening metadata to Loka ML, the data fields included, and the stated rationale. **Note: confidence:low; modeling objectives and outcomes are not documented.**

## Confidence

Low confidence for this answer overall, reflecting the `loka-ml-engagement` page's own confidence:low status. The data export facts (date, file name, target list, fields) are directly extracted from the wiki and are likely accurate for the handoff artifact. Everything about engagement scope, deliverables, and outcomes is outside the scope of the absorbed sources.

## Follow-ups

1. Were the Loka ML modeling objectives formally documented in a project charter or SOW? If so, those documents have not been absorbed into the wiki.
2. What ML outputs did Loka ML deliver — predictive hit scores, construct expression models, or something else?
3. Was the Loka ML engagement a one-time data handoff or an ongoing partnership with iterative data deliveries and model updates?

## Filed back?

No. The answer reflects the limited content available in the wiki page; there is nothing novel to promote.

## Session notes

This is a hard question for JoJo Bot because the wiki only captures the data-handoff artifact, not the engagement scope or outcomes. The honest answer acknowledges this gap explicitly. The confidence:low marking on both the page and this answer correctly signals to the reader that the wiki is not the right source for a full picture of the Loka ML engagement — the contracts and kickoff documentation would need to be absorbed first.
