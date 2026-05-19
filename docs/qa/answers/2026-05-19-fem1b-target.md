---
question_id: q-018
question: "What does the wiki say about FEM1B as a target — biology, protein production status, and program context?"
asked_by: mateo
asked_date: 2026-05-19
session_date: 2026-05-19
session_id: cowork-2026-05-19-018
route: wiki
route_decided_by: regex
candidate_slugs:
  - fem1b
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

The wiki contains a single `fem1b` target page rated `confidence: low`. The page is sparse by design — it reflects limited absorbed source material.

**Biology** [[fem1b|FEM1B Target]]

The page identifies FEM1B (Feminization-1B) as a member of the ubiquitin ligase family. The therapeutic rationale for targeting FEM1B at Nurix is not stated in the absorbed materials. No signaling pathway context, disease indication, or mechanistic hypothesis for FEM1B is recorded on the page [[fem1b|fem1b]].

**Protein Production Status** [[fem1b|FEM1B Target]]

The `fem1b` page documents a purification campaign from November 2022 attributed to Isabel Morgado (Protein Chemistry). FEM1B material for this campaign was obtained from GenScript, an outsourced expression vendor — suggesting that at least for initial batches, protein production was sourced externally rather than produced in-house. The page notes a "Nairi protein" designation (INFERRED reference to Nairi Hartooni, a team member), suggesting this team member was closely involved with the FEM1B work [[fem1b|fem1b]].

Isabel Morgado's archive contains 71 entries related to FEM1B, spanning purification campaigns and characterization work initiated in November 2022 [[fem1b|fem1b]].

**Program Context**

The page contains no program context. There is no link to a FEM1B program page; no `fem1b-program` slug exists in the wiki. No compound data, DEL screening plans, or downstream assay results are captured for FEM1B in the current wiki [[fem1b|fem1b]].

**Limitations**

The low confidence rating on the page reflects: (a) a single source document (one purification presentation); (b) no biochemical characterization data absorbed; (c) no project strategy document absorbed; (d) no cross-validation from other team members' records in the absorbed corpus.

## Sources

- `fem1b` — FEM1B target page; confidence: low. Single source: `raw/onedrive/onedrive_protein-chemistry-isabel-morgado-nairi-protein-fem1b-nov2022-fem1b-purification-from-genescript-pptx.md`.

## Confidence

Low, matching the page's own confidence rating. The page is authored from a single purification presentation and explicitly notes that downstream use and assay results are unabsorbed.

## Follow-ups

1. What is FEM1B's biological function — the wiki page does not state it. Is FEM1B targeted as an E3 ligase for degrader-program hook purposes (analogous to CRBN or VHL), or as a therapeutic target for direct inhibition?
2. Are the 71 Isabel Morgado FEM1B entries absorbed in the current wiki, or only the November 2022 presentation?
3. Does the "Nairi protein" designation refer to a proprietary construct, and if so, is there a construct design document in the raw corpus?

## Filed back?

No. The page is already in the wiki; there is nothing new to add from this answer.

## Session notes

This is a minimal-coverage target question. The correct response is to accurately report the sparse content of the page (ubiquitin ligase family, GenScript protein sourcing, November 2022, 71 entries, low confidence) without embellishing. A response that provides biological detail about FEM1B (e.g., its role in the N-degron pathway or PROTAC biology) without citing a specific wiki slug is a fail.
