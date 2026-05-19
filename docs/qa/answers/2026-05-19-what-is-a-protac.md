---
question_id: q-021
question: "What is a PROTAC, and how does Nurix use targeted protein degradation in its programs?"
asked_by: mateo
asked_date: 2026-05-19
session_date: 2026-05-19
session_id: cowork-2026-05-19-021
route: wiki
route_decided_by: regex
candidate_slugs:
  - targeted-protein-degradation
  - cbl-b-ctm
hops_followed:
  - targeted-protein-degradation
  - cbl-b-ctm
raw_fallback_used: false
raw_entries_read: []
miss_logged: false
confidence: high
filed_back: false
filed_back_path: null
schema_version: 0.1.0
---

## Answer

A PROTAC (Proteolysis Targeting Chimera) is a bifunctional small molecule composed of three parts: a ligand that binds the target protein, a chemical linker, and a ligand that recruits an E3 ubiquitin ligase. By holding the target and the ligase in physical proximity, the PROTAC induces the ligase to ubiquitylate the target protein, flagging it for degradation by the 26S proteasome. Unlike a classical occupancy-based inhibitor — which must remain bound to block function — a PROTAC molecule drives destruction of the target and is then released to act catalytically on additional copies. The effect is therefore irreversible (at the protein level) and substoichiometric relative to the target [[targeted-protein-degradation|Targeted Protein Degradation]].

The mechanistic rationale for PROTACs rests on the ubiquitin-proteasome system, which uses approximately 600 known E3 ligases to encode substrate-specificity decisions across the proteome. By choosing which E3 ligase to recruit, a PROTAC designer can influence cell-type selectivity, target-degradation kinetics, and the likelihood of productive ternary complex formation (the three-body interaction of target, PROTAC, and ligase). Classical E3 ligases exploited in PROTAC design include Cereblon (CRBN), Von Hippel-Lindau (VHL), IAP, KEAP1, and MDM2, among others [[targeted-protein-degradation|Targeted Protein Degradation]].

Targeted protein degradation (TPD) encompasses both PROTACs and molecular glue degraders. Molecular glue degraders are typically smaller monofunctional compounds that stabilize a native protein-protein interaction between a target (neosubstrate) and an E3 ligase without requiring a bifunctional linker. Both modalities converge on ubiquitylation and proteasomal destruction as the effector mechanism [[targeted-protein-degradation|Targeted Protein Degradation]].

Nurix uses TPD as the primary discovery modality for a range of internal programs. The company's internal degradation programs apply TPD to seed-stage targets including HRAS, NRAS, MYCN, ARID1B, and others tracked in the DEL Screening Program. A concrete example is the CBL-B chemical tool molecule (CTM) program: starting from NRX-0395370, a DEL-series hit from a Vipergen screen, Nurix built a CRBN-recruiting PROTAC series to produce CBL-B degraders. The CBL-B CTM program used selective CBL-B degradation as a complementary pharmacological tool alongside inhibitor programs, and HiBiT cell assays were used to quantify target depletion [[cbl-b-ctm|CBL-B CTM Program]]. A 2021 Keystone symposium on TPD hosted leading researchers presenting on E3-ligase reprogramming and lysosomal degradation pathway approaches, reflecting the broader scientific context in which Nurix's TPD work is situated [[targeted-protein-degradation|Targeted Protein Degradation]].

## Sources

- `targeted-protein-degradation` — primary mechanistic page; covers PROTAC mechanism, molecular glue distinction, E3 ligase catalog, and Nurix program overview.
- `cbl-b-ctm` — program page; documents NRX-0395370 as a DEL-derived CRBN-recruiting PROTAC and grounds the Nurix application example.

## Confidence

High confidence: the PROTAC mechanism description (bifunctional molecule, E3 recruitment, ubiquitylation, proteasomal degradation) is directly extracted from `targeted-protein-degradation`. The CBL-B CTM example is sourced from `cbl-b-ctm`. The E3 ligase list is sourced from `targeted-protein-degradation`. No facts in the answer are invented.

Lower confidence: the statement that Nurix applies TPD to "HRAS, NRAS, MYCN, ARID1B" etc. is drawn from `targeted-protein-degradation` which itself is confidence:medium; these are named in that page as tracked targets in the DEL Screening Program, not as current confirmed TPD programs, so they should be understood as "seed-stage targets in the DEL program" rather than advanced TPD programs with clinical readouts.

## Follow-ups

1. How does the linker chemistry in a PROTAC affect ternary complex formation geometry, and what are the Nurix-preferred linker types?
2. Which Nurix programs have progressed from PROTAC tool molecules to formal IND-enabling studies?
3. What cell-based assays does Nurix use beyond HiBiT to confirm productive target degradation (e.g., mass-spectrometry proteomics, CETSA)?

## Filed back?

No. The answer synthesizes two existing wiki pages without producing novel content warranting wiki promotion.

## Session notes

This question tests the fundamental mechanism explanation plus at least one grounded Nurix program example. The CBL-B CTM page was the cleanest source of a specific Nurix PROTAC example — a DEL-derived CRBN-recruiting series with quantified HiBiT readout. The `targeted-protein-degradation` page covers both PROTAC and molecular glue modalities, so citing it for the mechanistic distinction between the two is appropriate even though the question only asks about PROTACs.
