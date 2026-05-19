---
question_id: q-014
question: "What is IRAK4's role in TLR signaling, and what was the DEL screen strategy for it?"
asked_by: mateo
asked_date: 2026-05-19
session_date: 2026-05-19
session_id: cowork-2026-05-19-014
route: wiki
route_decided_by: regex
candidate_slugs:
  - irak4
hops_followed: []
raw_fallback_used: false
raw_entries_read: []
miss_logged: false
confidence: medium
filed_back: false
filed_back_path: null
schema_version: 0.1.0
---

## Answer

**IRAK4 in TLR Signaling** [[irak4|IRAK4 Target]]

IRAK4 (interleukin-1 receptor-associated kinase 4) is a serine-threonine kinase and the master regulator of TLR (Toll-like receptor) and IL-1R (interleukin-1 receptor) signaling. Upon TLR activation, IRAK4 is recruited to MYD88, forming the myddosome complex together with IRAK2, culminating in NF-κB translocation and activation of innate immune responses. IRAK4's documented substrates include IRAK1, IRAK2, and IRAK4 itself (autophosphorylation) [[irak4|irak4]].

IRAK4's domain organization comprises a death domain (residues 9-106) that mediates myddosome assembly and a serine-threonine kinase catalytic domain (residues 186-458) that contains the ATP-binding pocket. Both phosphorylated (active) and dephosphorylated (inactive) forms were screened in the DEL campaign [[irak4|irak4]].

**DEL Screen Strategy** [[irak4|IRAK4 Target]]

IRAK4 was targeted in DEL campaign 1, pursued specifically as a "CTM hook target" — meaning IRAK4 ligands identified through DEL were intended to serve as the target-binding warhead of a future CRBN-based CTM (degrader) compound, rather than as standalone kinase inhibitors [[irak4|irak4]].

Two tracer generations were developed:
- Tracer 1 (NRX-0392248): parent compound NRX-0391649 (IC50 = 120 nM kinase assay); Kd = 55 nM for phosphorylated IRAK4, 230 nM for dephosphorylated IRAK4 by SPR.
- Tracer 2 (NRX-0395372): parent compound NRX-0393640 (IC50 = 1 nM kinase, Kd = 0.29 nM SPR); tracer Kd = 28 nM by SPR; ATP-binding pocket, phosphorylated IRAK4.

Key supplements used in the DEL campaigns: AMP-PNP (ATP mimetic; Km 1.4-600 µM); Type I inhibitor PF-06650833/NRX-0389796 (IC50 = 0.2 nM, phosphorylated IRAK4); Type II inhibitor Ponatinib/NRX-0391651 (Kd = 67 nM, dephosphorylated IRAK4) [[irak4|irak4]].

The wiki records IRAK4 as a single-source entry (IRAK4 Target Review and DEL Screen Plan, dated March 31, 2020). No subsequent chemistry results, DEL hit data, or CTM compound progression from IRAK4 DEL campaign 1 are captured in the current wiki [[irak4|irak4]].

## Sources

- `irak4` — IRAK4 target page; covers myddosome biology, kinase domain boundaries, CTM hook designation, DEL campaign 1 strategy, and the two tracer compounds.

## Confidence

All claims are EXTRACTED from the single `irak4` target page. The wiki rates this page at `confidence: medium` with a single source document (corpus: del-screen-team). No downstream chemistry or biological validation data is available in the wiki. Confidence: medium, limited by single-source grounding and absence of downstream data.

## Follow-ups

1. What was the outcome of IRAK4 DEL campaign 1 — did it yield confirmed hits that were resynthesized, and did Tracer 2's sub-nanomolar parent (NRX-0393640 Kd = 0.29 nM) inform downstream chemistry?
2. The IRAK4 page notes the target as a "CTM hook" — was the intended CTM degrading IRAK4 itself, or using IRAK4 as a hook to degrade an IRAK4-interacting partner?
3. Is there a separate IRAK4 program page that captured downstream chemistry, or did the program not advance beyond DEL planning?

## Filed back?

No. The answer is a direct summary of the single available wiki page.

## Session notes

This is a target-biology question with a single-page answer. It tests whether the retrieval correctly surfaces `irak4` rather than adjacent targets (e.g., IRAK1, MYD88, or TLR pages that don't exist). The death-domain / kinase-domain boundary numbers and the two tracer IDs are the specific factual discriminators between a correct answer and a hallucinated one.
