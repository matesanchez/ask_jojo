---
question_id: q-006
question: "What are the key differences in program direction between the BTK CTM program and the IRAK4 DEL screen effort, and how far did each advance?"
asked_by: mateo
asked_date: 2026-05-19
session_date: 2026-05-19
session_id: cowork-2026-05-19-006
route: wiki
route_decided_by: regex
candidate_slugs:
  - btk-ctm
  - irak4
hops_followed:
  - targeted-protein-degradation
raw_fallback_used: false
raw_entries_read: []
miss_logged: false
confidence: medium
filed_back: false
filed_back_path: null
schema_version: 0.1.0
---

## Answer

The BTK CTM program and the IRAK4 DEL screen effort represent fundamentally different program types at different stages of maturity, sharing no direct strategic relationship beyond both being pursued under Nurix's broader targeted-protein-degradation platform.

**BTK CTM Program** [[btk-ctm|BTK CTM Program]]

The BTK program is a CRBN-based targeted-protein-degradation program directed at B-cell malignancies and autoimmune disease. The scientific rationale for degradation over inhibition is explicit: three generations of FDA-approved BTK inhibitors exist, and the C481S resistance mutation renders covalent inhibitors ineffective. A CTM (CRBN-targeting molecule, Nurix's term for their PROTAC-class degraders) retains activity against C481S mutant BTK through sub-stoichiometric catalytic action rather than occupancy-based blockade [[btk-ctm|btk-ctm]]. A proof-of-concept CTM, NRX-0390492, was developed and profiled in HTRF degradation assays in Ramos and TMD8 cell lines [[btk-ctm|btk-ctm]].

The program has advanced to clinical-stage compounds. NX-2127 degrades both BTK and IKZF1/IKZF3 (a dual-degrader profile published in a Science paper on C481S resistance), and NX-5948 is the most advanced compound in the program, currently in pharmaceutical development with a dog PK study completed January 2026. NX-5948 is a fumarate salt formulated using SDI/ASD strategy due to poor aqueous solubility [[btk-ctm|btk-ctm]]. The BTK program is thus a fully developed, multi-compound clinical-stage effort.

**IRAK4 DEL Screen Effort** [[irak4|IRAK4 Target]]

IRAK4 is a serine-threonine kinase and master regulator of TLR/IL-1R signaling through its role in the MYD88 myddosome complex. The wiki documents IRAK4 as a DEL screen campaign 1 target, pursued as a potential CTM hook — i.e., IRAK4 was evaluated as an anchor for future CTM (degrader) design. The program produced two tracer compounds (NRX-0392248 Tracer 1 and NRX-0395372 Tracer 2), which are the biophysical probes used to enable DEL selection [[irak4|irak4]].

The wiki has no IRAK4 program page — there is only a target page. This is significant: the IRAK4 effort is documented at the target-characterization and DEL-planning stage, not at the program (candidate nomination or lead optimization) stage. The target page sources a single document (IRAK4 Target Review and DEL Screen Plan, March 2020) and records the IRAK4 kinase domain boundaries (death domain 9-106, kinase domain 186-458), the myddosome biology, and the DEL campaign 1 design [[irak4|irak4]]. No chemical leads, in vitro biological data, or downstream IND-stage material is documented in the current wiki.

**Comparison**

The BTK CTM program advanced from proof-of-concept CTM through clinical candidates and into clinical trials. The IRAK4 effort is documented through DEL planning and tracer development — a hook-identification stage. INFERRED: IRAK4 was evaluated as a potential CTM entry target, but the wiki does not record any downstream program formation; the trajectory from DEL hit to CTM compound to program is not captured. The absence of an IRAK4 program page and the single-source citation for the target page suggest the IRAK4 effort did not advance to the same degree as BTK within the period covered by the wiki.

The two efforts also differ mechanistically: BTK is targeted for direct CTM-mediated degradation of BTK kinase as the therapeutic mechanism; IRAK4 was being developed as a hook for a CTM (suggesting IRAK4 ligands would form part of the bifunctional degrader molecule, not necessarily be the degradation target).

## Sources

- `btk-ctm` (program page for the BTK CTM program) — covers clinical compounds NX-2127, NX-5948; proof-of-concept CTM NRX-0390492; rationale for degradation over inhibition.
- `irak4` (target page) — covers IRAK4 biology, myddosome, DEL campaign 1 planning, and tracers NRX-0392248 and NRX-0395372. Single source document: IRAK4 Target Review and DEL Screen Plan 20200331.

## Confidence

Highest-confidence claims: (a) BTK program has clinical-stage compounds NX-2127 and NX-5948; (b) the IRAK4 wiki entry is a target page only with no corresponding program page; (c) two IRAK4 tracers are named and the DEL campaign 1 is documented.

Lowest-confidence claim: "IRAK4 was evaluated as a hook for a CTM, not as the degradation target." INFERRED from the phrase "CTM hook target" in the IRAK4 wiki page. The wiki page states this terminology but the inference about strategic intent (IRAK4 ligand as part of a bifunctional degrader vs. IRAK4 as the degradation target) is drawn from that language rather than from an explicit strategy document. Confidence medium overall.

## Follow-ups

1. Is there a corresponding IRAK4 program page that was not captured in this absorb — i.e., did the IRAK4 DEL hit lead to a downstream program with chemistry?
2. Does the BTK program wiki cover NX-5948's clinical indication and Phase assignment, or is that detail in a separate IND-pharmacology page?
3. What is the relationship between the IRAK4 tracer compounds and the CBL-B CTM program — was the IRAK4 hook being considered as a CBL-B CTM component?

## Filed back?

No. The answer synthesizes two pages without producing novel content beyond their cross-comparison. The INFERRED claim about CTM-hook intent is too speculative to file as a wiki fact.

## Session notes

This question probes whether the benchmark can distinguish a clinical-stage program (BTK) from an early-stage target-only entry (IRAK4). The key discriminator is the presence vs. absence of a program page. The answer correctly anchors on that structural difference in the wiki rather than on inferring biology from domain knowledge.
