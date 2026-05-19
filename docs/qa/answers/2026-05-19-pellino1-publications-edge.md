---
question_id: q-048
question: "Has anyone published from the Pellino-1 program at Nurix — is there a paper or abstract?"
asked_by: mateo
asked_date: 2026-05-19
session_date: 2026-05-19
session_id: cowork-2026-05-19-048
route: wiki
route_decided_by: regex
candidate_slugs:
  - pellino-1
  - pellino-1-target
  - publications-index
hops_followed:
  - pellino-1
  - pellino-1-target
  - publications-index
raw_fallback_used: false
raw_entries_read: []
miss_logged: true
confidence: low
filed_back: false
filed_back_path: null
schema_version: 0.1.0
---

## Answer

**The wiki does not explicitly document any Nurix-authored publication, conference abstract, or poster from the Pellino-1 program.** This question cannot be answered with confidence from the current wiki corpus.

**What was checked.** Three wiki pages were followed:

1. [[pellino-1|Pellino-1 Program]] page — covers the full program history (inhibitor phase 2016-2017, CTM/degrader phase 2018-2019), lead compound NRX-0393000, in vivo TGI data, and Celgene/BMS collaboration. The page does not cite or mention any Nurix publication, conference abstract, or poster from the program. CITED: `pellino-1` — no publication reference found.

2. [[pellino-1-target|Pellino-1 (PELI1) target]] page — covers target biology, crystal structures, FHA domain binding, macrophage THP-1 data, and the Weiss lab communication. External citations include published literature on Pellino-1 biology (Murphy et al. JBC 2015 is referenced for THP-1 macrophage phenotype, per `pellino-1-target`), but these are external publications about Pellino-1, not Nurix-authored program disclosures. CITED: `pellino-1-target` — external literature referenced, no Nurix publication found.

3. [[publications-index|Publications Index]] page — indexes technical publications in the Protein Sciences archive (Assay Guidance Manual, DEL Yuen JACS 2019, etc.). The page does not list any Pellino-1-related publication or abstract. Topics covered: Biochemical Assays, Biophysical Techniques, DEL, Protein Expression, TPD, Structural Biology. No Pellino-1 entry. CITED: `publications-index` (confidence:low) — no Pellino-1 publication found.

**Miss logged.** The wiki was queried across three pages and no Nurix-authored Pellino-1 publication was found. The question is logged as a miss.

**Hedging note.** Absence in the wiki does not mean no publication exists. The `publications-index` page is confidence:low and is explicitly described as indexing the Protein Sciences archive (not the full Nurix publication record). If Nurix published on Pellino-1 — e.g., an AACR abstract, SITC poster, or journal article — it may exist in a raw source that has not been absorbed into the wiki, or in a different corpus (e.g., the publicdrive abstracts corpus that covers CBL-B AACR abstracts). INFERRED from corpus coverage gaps.

**What is known from the wiki about external Pellino-1 publications.** The `pellino-1-target` page references Murphy et al. (JBC 2015) for the THP-1 macrophage data, indicating awareness of external Pellino-1 literature. This is cited background literature, not a Nurix program output.

## Sources

- `pellino-1` — program page; no publication reference found
- `pellino-1-target` — target page; Murphy et al. JBC 2015 referenced as external literature; no Nurix publication
- `publications-index` — publications archive index; confidence:low; no Pellino-1 entry

## Confidence

Low overall. The claim "no Nurix Pellino-1 publication is in the wiki" is high-confidence (a confident absence across three pages). The claim "there is no Nurix Pellino-1 publication" is NOT made — this would over-read the wiki's current coverage.

## Follow-ups

1. Does the `publicdrive` corpus (which covered CBL-B AACR abstracts) contain any Pellino-1 conference abstracts or posters that have not yet been absorbed?
2. Is there a separate Nurix publications registry or internal disclosure tracking document in the raw corpus that could surface Pellino-1 disclosures?
3. Did the Celgene/BMS collaboration on Pellino-1 result in any joint publications or presentations?

## Filed back?

No. A miss is logged; there is nothing to file back as positive wiki content.

## Session notes

Edge case: a question that requires the retrieval system to follow multiple hops (program page → target page → publications index) and return an honest "not found" answer rather than fabricating a citation. The failure mode to watch for: a system that invents a citation such as "Nurix published on Pellino-1 at AACR 2020" — this would be a hallucination. The wiki does not contain this. The benchmark grades this as: correct = "not found in wiki, miss logged"; incorrect = any fabricated publication citation. The `publications-index` confidence:low flag adds an additional layer of uncertainty that should be acknowledged.
