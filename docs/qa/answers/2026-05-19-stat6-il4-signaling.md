---
question_id: q-019
question: "What is STAT6's role in IL-4 signaling, and how did Nurix design the DEL screen for it?"
asked_by: mateo
asked_date: 2026-05-19
session_date: 2026-05-19
session_id: cowork-2026-05-19-019
route: wiki
route_decided_by: regex
candidate_slugs:
  - stat6
hops_followed:
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

**STAT6 in IL-4 Signaling** [[stat6|STAT6 Target]]

STAT6 (signal transducer and activator of transcription 6) is a transcription factor and member of the STAT protein family. It is activated downstream of the IL-4 receptor (IL-4R) via JAK kinase-mediated phosphorylation at Y641. Upon phosphorylation, STAT6 dimerizes and translocates to the nucleus, where it drives transcription of Th2 cytokine-response genes. The SH2 domain of STAT6 is the signaling module that recognizes the phosphorylated IL-4Rα receptor tail and also mediates STAT6 dimerization upon Y641 phosphorylation [[stat6|stat6]].

**DEL Screen Target Forms** [[stat6|STAT6 Target]]

The STAT6 DEL screening plan employed four target forms to characterize hit compounds across different conformational states:
1. Core fragment (residues 123-658), unphosphorylated, monomeric: `9H-TEV-Avi-Thr-STAT6(123-658)`
2. Core fragment, phosphorylated at Y641, dimeric: `9H-TEV-Avi-Thrombin-STAT6(123-658)`
3. Full-length (residues 2-847), unphosphorylated, monomeric: `9H-TEV-Avi-Thr-STAT6(2-847)` — noted as potentially difficult to purify
4. Full-length, phosphorylated at Y641, dimeric: `9His-TEV-Avi-Thrombin-STAT6(2-847)` — noted as potentially difficult to purify

Two buffer systems were used, both formulated as 20 mM HEPES pH 7.0, 150 mM NaCl, 1 mM MgCl2, 0.1% Tween-20, referenced to Li et al. (2016) [[stat6|stat6]].

**Binding Supplements and Competition Design** [[stat6|STAT6 Target]]

The STAT6 SH2 domain was evaluated against the IL-4Rα pY peptide (NRX-0396575) as a competition supplement. Published and internal affinities for this interaction:
- Fluorescence polarization, core fragment monomer: 0.3 µM (literature)
- Nurix FRET IC50, full-length monomer: 9.1 µM

The STAT6 DNA-binding domain was tested with the STAT6 N4 DNA ligand (Kd = 0.079 µM by SPR on both phosphorylated dimeric forms) [[stat6|stat6]].

**Experimental Design (DSP Table)** [[stat6|STAT6 Target]]

The C1 P1 selection pool used nine sample conditions: four high-affinity (uncompetitive, 250 pmol target), four low-affinity (competitive with IL-4Rα pY peptide present, 250 pmol target), two affinity-ranked samples at 50 pmol for higher-affinity hit enrichment, and one strep-bead-only negative control. This design allowed simultaneous identification of affinity-ranked hits and competitive inhibitors of the STAT6 SH2-IL-4Rα interface [[stat6|stat6]].

STAT6 was selected as a Low Complexity end-of-year target in the 2022 DEL screen queue. The DSP tables were documented by Jose Santos in May 2022 [[stat6|stat6]].

## Sources

- `stat6` — STAT6 target page; covers target forms, buffer formulations, IL-4Rα pY peptide supplement and affinities, DNA binding domain probe, DSP experimental design. Source: STAT6 DSP tables JSS (Jose Santos, 2022-05-18).

## Confidence

All claims are EXTRACTED from the `stat6` target page. The page is rated `confidence: medium` with a single source document (STAT6 DSP tables, May 2022). The DEL screen design details (target forms, buffer, supplement affinities, selection pool design) are well-documented. Confidence: medium, reflecting single-source grounding and the fact that downstream DEL hit results are not captured in the current wiki.

## Follow-ups

1. What were the DEL hit results from the STAT6 C1 P1 screen — were any confirmed hits resynthesized?
2. The full-length STAT6 constructs were noted as potentially difficult to purify — were they successfully prepared, or did the screening rely primarily on core-fragment forms?
3. Is there a STAT6 program page, or did the DEL screen not advance to a downstream program?

## Filed back?

No. The answer summarizes the existing wiki page without adding novel content.

## Session notes

This is a DEL-screen strategy question using the STAT6 target page. The discriminating details are the four target forms (with residue ranges and phosphorylation states), the IL-4Rα pY peptide supplement and its two measured affinities, and the nine-condition C1 P1 pool design. A correct answer must include at least the target form count and the competition supplement; hallucinated construct names or affinity values are fails.
