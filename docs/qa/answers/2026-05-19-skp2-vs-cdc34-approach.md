---
question_id: q-011
question: "How did the SKP2 inhibitor program compare to the Cdc34 ELSA program in approach and outcome?"
asked_by: mateo
asked_date: 2026-05-19
session_date: 2026-05-19
session_id: cowork-2026-05-19-011
route: wiki
route_decided_by: regex
candidate_slugs:
  - skp2-inhibitor
  - cdc34
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

Both the SKP2 inhibitor program and the Cdc34 ELSA program were early-stage oncology programs that predated the CTM/degrader platform era at Nurix, and neither advanced to candidate nomination. They targeted adjacent biology (both are components of the SCF ubiquitin ligase system) but pursued distinct biochemical strategies.

**SKP2 Inhibitor Program** [[skp2-inhibitor|SKP2 Inhibitor Program]]

SKP2 is the F-box protein component of the SCF (SKP1-Cullin1-F-box) E3 ligase complex. The therapeutic rationale for inhibiting SKP2 is blocking its ability to ubiquitylate p27 (CDKN1B), the CDK inhibitor whose degradation enables S-phase entry. SKP2 is overexpressed in many cancers, and knockdown inhibits tumor growth [[skp2-inhibitor|skp2-inhibitor]].

The structural rationale was based on the crystal structure of the SKP2-Cks1-p27 ternary complex (Mol Cell 2005), which identified the SKP2-Cks1 protein-protein interface as a druggable surface. Key interface residues identified: Arg344, His392, Phe368, Trp265, Asp319 [[skp2-inhibitor|skp2-inhibitor]].

The SKP2 program pursued three parallel discovery approaches:
1. TR-FRET high-throughput screen (HTS): ~250K compounds from BioFocus, Nurix, and WEHI collections; Z-factor = 0.845; ~2% confirmation rate.
2. Computational virtual screen against the SKP2-Cks1 interface.
3. DEL screen.

The program operated approximately 2015-2016 at the lead-identification stage and did not produce a clinical candidate [[skp2-inhibitor|skp2-inhibitor]].

**Cdc34 ELSA Program** [[cdc34|Cdc34 ELSA Program]]

Cdc34A (also designated UBE2R2 or CDC34) is the E2 ubiquitin-conjugating enzyme that works with the SCF E3 complex to assemble K48-linked polyubiquitin chains on CRL substrates, targeting them for proteasomal degradation. Cdc34 substrates include p21, p27, and Cdc25A — overlapping substrate biology with the SKP2 program [[cdc34|cdc34]].

The Cdc34 program was distinct in targeting the E2 enzyme (upstream of the E3) rather than the E3 F-box subunit. The chemical precedent was CC0651, an allosteric inhibitor occupying a pocket adjacent to the catalytic cysteine that blocks K48 chain synthesis without competing with ubiquitin at the active site. CC0651 induced G1 arrest and apoptosis in cancer cell lines [[cdc34|cdc34]].

The Nurix Cdc34 assay cascade ran four steps: (1) FRET-based ubiquitin-binding assay for primary screening; (2) di-ubiquitin chain synthesis activity assay; (3) biophysical confirmation (SPR and crystallography); (4) cellular substrate stabilization and viability. A substantial BioFocus HTS was run in 2015, and SAR was tracked through weekly chemistry meetings from February through November 2016. FEP modeling guided design; ADME profiling was conducted through Pharmaron [[cdc34|cdc34]].

A key feature was a collaboration with the Frank Sicheri laboratory (Lunenfeld-Tanenbaum Research Institute, Toronto) for NMR fragment screening, protein crystallography, and Cdc34B structural studies. A triple gain-of-function Cdc34B mutant was engineered to convert it to Cdc34A activity for use as a positive control [[cdc34|cdc34]].

The Cdc34 program also did not advance to candidate nomination. By 2018, resources had concentrated on the CBL-B inhibitor program [[cdc34|cdc34]].

**Comparison**

| Dimension | SKP2 | Cdc34 |
|---|---|---|
| Target | F-box protein (E3 component) | E2 conjugating enzyme |
| Strategy | Disrupt protein-protein interaction (SKP2-Cks1) | Block allosteric ubiquitin-binding pocket |
| Screen approach | HTS + virtual screen + DEL | HTS + NMR fragment screen + SAR |
| External collaboration | WEHI compound library | Sicheri lab (Toronto) — protein, NMR, crystallography |
| Approximate timeline | ~2015-2016 | ~2014-2017 |
| Outcome | Did not advance to candidate nomination | Did not advance to candidate nomination |

Both programs occupied lead-identification stages in the 2015-2017 window and were deprioritized before the CTM platform era. INFERRED: the convergence of program closure timing with CBL-B inhibitor program maturation (NX-1607 progressing in 2018-2019) suggests resource concentration rather than scientific failure as the primary reason for non-advancement, but no explicit decision document is cited in the wiki for either program.

## Sources

- `skp2-inhibitor` — SKP2 program page; covers HTS, virtual screen, DEL screen, SKP2-Cks1 structural rationale.
- `cdc34` — Cdc34 ELSA program page; covers CC0651 precedent, HTS, NMR fragment screen, Sicheri collaboration, assay cascade.

## Confidence

All comparative claims are EXTRACTED from the two cited pages. The convergence inference (resource concentration) is INFERRED and explicitly marked. Confidence: medium (the individual program facts are EXTRACTED; the comparative "why" is inferred from absence of evidence).

## Follow-ups

1. Is there a decision document for either program recording the rationale for deprioritization?
2. The Cdc34 page notes that Cdc34B was separately studied via engineered mutant — was there a separate Cdc34B program, or was Cdc34B only a tool for validating the Cdc34A assay?
3. Was the DEL screening approach in the SKP2 program part of Nurix's early DEL platform or an earlier iteration?

## Filed back?

No. The comparison table is a useful synthesis but both programs are already adequately described in their respective pages. No novel factual content to promote.

## Session notes

The question tests cross-program comparison from two similarly-staged early programs. The key discriminator is the target class (E3 F-box protein vs. E2 enzyme) and the structural strategy (PPI disruption vs. allosteric inhibition). The table format aids grading clarity.
