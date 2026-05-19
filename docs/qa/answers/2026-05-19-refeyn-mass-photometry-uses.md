---
question_id: q-025
question: "What is mass photometry (Refeyn), and what are its use cases in Nurix protein sciences?"
asked_by: mateo
asked_date: 2026-05-19
session_date: 2026-05-19
session_id: cowork-2026-05-19-025
route: wiki
route_decided_by: regex
candidate_slugs:
  - refeyn-mass-photometry
  - biophysical-characterization-methods
hops_followed:
  - refeyn-mass-photometry
  - biophysical-characterization-methods
raw_fallback_used: false
raw_entries_read: []
miss_logged: false
confidence: medium
filed_back: false
filed_back_path: null
schema_version: 0.1.0
---

## Answer

**Principle**

Mass photometry is a label-free optical technique for measuring protein mass in solution from individual molecular landing events. The REFEYN OneMP instrument detects individual protein molecules as they bind to a glass coverslip surface. Each binding event causes a local change in refractive index, detected by interferometric scattering microscopy (iSCAT). The optical contrast produced by each individual protein is proportional to its molecular weight. By accumulating data from many individual landing events, the instrument builds a mass distribution histogram whose peaks correspond to distinct species (monomers, dimers, higher-order assemblies) present in the sample [[refeyn-mass-photometry|REFEYN Mass Photometry]].

Key practical features: measurements require only 1-2 microliters of sample at 0.1-1 micromolar concentration; no calibration standards or immobilization of the protein are required; results are available in minutes; and the single-molecule resolution allows distinguishing monomers from oligomers in real time [[refeyn-mass-photometry|REFEYN Mass Photometry]].

Limitations include the requirement that proteins bind the glass surface transiently (hydrophobic proteins often produce better signal than hydrophilic ones), susceptibility to background noise from aggregates or dust, a limited dynamic range for very small proteins (below ~5 kDa), and reduced signal quality in detergent-containing samples [[refeyn-mass-photometry|REFEYN Mass Photometry]].

**Use cases and context within protein characterization**

Mass photometry fits into the broader biophysical characterization workflow alongside SEC-MALS and DLS. Within that workflow, mass photometry offers rapid oligomeric-state and assembly stoichiometry determination without the chromatographic separation step that SEC-MALS requires [[biophysical-characterization-methods|Biophysical Characterization Methods]]. For example, a 1:1:1 ternary complex of three proteins would appear as a peak at the summed molecular weight of all three components, allowing direct stoichiometry readout in a single experiment [[refeyn-mass-photometry|REFEYN Mass Photometry]].

The wiki documents that Nurix conducted a proof-of-concept demonstration of the REFEYN instrument for protein molecular-weight determination, evaluated as a potential complement to SEC-MALS for rapid, label-free molecular weight determination without chromatographic separation. The instrument was assessed with application notes on detergent compatibility, optimization for various protein types, and preliminary data from a demonstration panel of proteins [[refeyn-mass-photometry|REFEYN Mass Photometry]].

INFERRED: integration of mass photometry into routine protein QC workflows has not yet occurred as of the wiki's last review. The `refeyn-mass-photometry` page explicitly states that no routine SOPs are in place and characterizes the evaluation as exploratory. The potential benefits cited — rapid oligomeric-state screening and interaction kinetics — justify further evaluation, but comparison to established methods (SEC-MALS, DLS) would be needed before replacing current procedures [[refeyn-mass-photometry|REFEYN Mass Photometry]].

## Sources

- `refeyn-mass-photometry` — primary equipment page; covers the iSCAT principle, sample preparation, data interpretation, Nurix proof-of-concept evaluation, advantages, and limitations. **Note: confidence:low.**
- `biophysical-characterization-methods` — reference page; situates mass photometry in the broader characterization workflow alongside SEC-MALS, DLS, DSF, SPR, and ITC.

## Confidence

Medium confidence overall. The iSCAT detection principle, mass histogram interpretation, and application to oligomeric-state/stoichiometry determination are directly extracted from `refeyn-mass-photometry`. The characterization workflow context is sourced from `biophysical-characterization-methods`.

Lower confidence: `refeyn-mass-photometry` itself is confidence:low (its raw source is a demo cluster with provisional hash). The wiki description of the Nurix evaluation as "exploratory" is consistent with limited routine use. No specific Nurix proteins screened by mass photometry are documented in the wiki.

## Follow-ups

1. Has the Refeyn instrument been formally approved for protein QC at Nurix, or did the evaluation conclude without adoption?
2. For which target classes (e.g., multi-subunit E3 ligase complexes, ternary complex assemblies) would mass photometry provide data not obtainable from SEC-MALS or DLS?
3. What were the specific findings from the Nurix demonstration protein panel — were any constructs found to aggregate unexpectedly?

## Filed back?

No. The answer summarizes existing wiki content.

## Session notes

Both cited pages are necessary: `refeyn-mass-photometry` provides the mechanism and Nurix-specific evaluation context; `biophysical-characterization-methods` provides the workflow positioning. The `refeyn-mass-photometry` page's confidence:low status reflects a demo-cluster source that has not been fully validated. The answer correctly reflects the exploratory status of the instrument at Nurix rather than overstating its deployment.
