---
question_id: q-017
question: "What is ZAP-70's role in T-cell activation, and what does the Nurix ZAP-70 platform page say about the program?"
asked_by: mateo
asked_date: 2026-05-19
session_date: 2026-05-19
session_id: cowork-2026-05-19-017
route: wiki
route_decided_by: regex
candidate_slugs:
  - zap-70-platform
hops_followed: []
raw_fallback_used: false
raw_entries_read: []
miss_logged: false
confidence: low
filed_back: false
filed_back_path: null
schema_version: 0.1.0
---

## Answer

IMPORTANT: The `zap-70-platform` wiki page carries `confidence: low` with a `pending-backfill-from-raw` source placeholder. All claims drawn from that page are marked accordingly.

**ZAP-70 Biology (from the wiki page)**

The `zap-70-platform` page describes ZAP-70 (zeta-chain-associated protein 70) as a critical Src-family kinase in T-cell receptor (TCR) signaling, targeted for modulation via both direct kinase inhibition and post-translational modification including ubiquitination and phosphorylation [EXTRACTED, LOW CONFIDENCE from zap-70-platform].

The page does not elaborate on the specific ZAP-70 signaling mechanism (e.g., ZAP-70's role downstream of CD3ζ ITAM phosphorylation) — the platform page is a protein-production infrastructure record, not a target-biology page. The low-confidence rating and pending source backfill mean the biological statements should not be treated as authoritative [[zap-70-platform|ZAP-70 Platform]].

**What the Platform Page Documents** [[zap-70-platform|ZAP-70 Platform]]

The platform page records protein production scope [EXTRACTED, LOW CONFIDENCE]:
- Construct variants: kinase domain, regulatory domain, and full-length ZAP-70.
- Expression systems: bacterial and insect cell systems.
- Co-expression with regulatory proteins and binding partners.
- Biophysical and biochemical screening activities.
- 165 project entries spanning 2018-2025 with sustained activity in protein production and assay development [EXTRACTED, LOW CONFIDENCE].

The page links to [[baculovirus-expression]], [[methods/cell-screening]], and [[programs/snf-series-projects]], suggesting the ZAP-70 protein production work was used in support of cell-screening campaigns and possibly the SNF-series projects [[zap-70-platform|zap-70-platform]].

**Limitations of the Available Wiki Content**

The wiki does not contain a `zap-70-target` page. The `zap-70-platform` page is a program-type page, not a target-type page, and is rated low confidence pending source backfill. There is no program-strategy information, no compound data, and no indication-selection data for ZAP-70 captured in the current wiki. The page describes a protein production platform active from 2018-2025 with 165 entries, but the downstream use of that protein (screening, degrader development, structural biology, or other) is not documented in the current wiki.

## Sources

- `zap-70-platform` — ZAP-70 platform page; confidence: low; pending source backfill. Covers construct variants, expression systems, 165 project entries 2018-2025.

## Confidence

Low. The single available page carries `confidence: low` with a `pending-backfill-from-raw` placeholder. No target-biology page for ZAP-70 exists in the wiki. All claims from the platform page are presented with low-confidence caveats.

## Follow-ups

1. When will `zap-70-platform` sources be backfilled — what raw entries cover ZAP-70 protein production?
2. Is there a ZAP-70 target page planned, or is the biology being covered in the context of a related program (e.g., ITK, which also involves TCR signaling)?
3. Do any of the 165 ZAP-70 project entries include co-crystallization or DEL screening results that would document downstream chemistry?

## Filed back?

No. Low-confidence content should not be filed back into the wiki.

## Session notes

This question tests behavior when the only available page is low-confidence. A correct response must: (a) surface the low-confidence caveat explicitly; (b) report what the page does contain (protein production scope, construct types, entry count, date range); (c) note the absence of a target-biology page; (d) NOT supplement with external knowledge about ZAP-70's TCR signaling role. Any answer that provides a detailed ZAP-70 mechanism description without citing a specific wiki page is a fail for this entry.
