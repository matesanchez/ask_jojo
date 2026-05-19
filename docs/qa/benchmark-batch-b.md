# Benchmark Batch B — q-021 through q-035

Staged: 2026-05-19 by mateo
Categories: platform-mechanism (q-021 to q-025), historical-decision (q-026 to q-029), protocol-method (q-030 to q-035)

---

## q-021 — What is a PROTAC?

- **Question:** What is a PROTAC, and how does Nurix use targeted protein degradation in its programs?
- **Expected route:** `wiki`
- **Expected cited slugs:** `targeted-protein-degradation`, `cbl-b-ctm`
- **Category:** platform-mechanism
- **Difficulty:** easy
- **Gold answer file:** `docs/qa/answers/2026-05-19-what-is-a-protac.md`
- **Notes:** Must explain the PROTAC/degrader mechanism (bifunctional molecule, E3 ligase recruitment, ubiquitination, proteasomal degradation) citing `targeted-protein-degradation`. Must cite a Nurix program example (CBL-B CTM uses a CRBN-recruiting degrader series starting from NRX-0395370). Hallucinating specific clinical degrader candidates without sourcing is a fail.
- **Added:** 2026-05-19 by mateo

---

## q-022 — DEL Library Construction

- **Question:** How are DEL libraries constructed at Nurix, and what are the key library parameters?
- **Expected route:** `wiki`
- **Expected cited slugs:** `del-libraries`, `dna-encoded-libraries-screening`
- **Category:** platform-mechanism
- **Difficulty:** medium
- **Gold answer file:** `docs/qa/answers/2026-05-19-del-library-construction.md`
- **Notes:** Answer covers DEL construction (split-and-pool synthesis, DNA encoding/tagging, affinity selection against target protein) from `dna-encoded-libraries-screening` and library-specific parameters (named Nurix subsets D1-D5, NRX09, NRX04 Covalent, Deck1, Deck2, ssD1-ssD3, D8; test funnel tiers; NovaSeq S4 sequencing cost) from `del-libraries`. Inventing specific library sizes not in the wiki is a fail.
- **Added:** 2026-05-19 by mateo

---

## q-023 — CRBN Molecular Glue vs. PROTAC

- **Question:** What is the CRBN molecular glue mechanism, and how does it differ from a PROTAC?
- **Expected route:** `wiki`
- **Expected cited slugs:** `crbn-cereblon-platform`, `targeted-protein-degradation`
- **Category:** platform-mechanism
- **Difficulty:** medium
- **Gold answer file:** `docs/qa/answers/2026-05-19-crbn-molecular-glue-vs-protac.md`
- **Notes:** Molecular glue vs. PROTAC mechanistic distinction must be grounded in `targeted-protein-degradation`. `crbn-cereblon-platform` is confidence:low with pending-backfill sources — answer must reflect that uncertainty. Named molecular glue compound series or clinical candidates must not be invented. The INFERRED label is required on the Celmod-as-molecular-glue inference.
- **Added:** 2026-05-19 by mateo

---

## q-024 — Delphi Clone-Biomass-Protein Registration Model

- **Question:** What is the Delphi clone-biomass-protein registration model, and how does a clone move through it?
- **Expected route:** `wiki`
- **Expected cited slugs:** `clone-biomass-protein-registration-model`, `delphi`
- **Category:** platform-mechanism
- **Difficulty:** easy
- **Gold answer file:** `docs/qa/answers/2026-05-19-delphi-clone-biomass-protein-model.md`
- **Notes:** Must describe the six metadata fields (Project, Program, Contract, Concept, Source, External Source ID), the three registration types (clone → biomass → protein), default inheritance rules, and the NrxP/NrxB nomenclature. The Delphi inter-module protein availability contract (PP complete → available in CP) is a required supporting point.
- **Added:** 2026-05-19 by mateo

---

## q-025 — Refeyn Mass Photometry

- **Question:** What is mass photometry (Refeyn), and what are its use cases in Nurix protein sciences?
- **Expected route:** `wiki`
- **Expected cited slugs:** `refeyn-mass-photometry`, `biophysical-characterization-methods`
- **Category:** platform-mechanism
- **Difficulty:** easy
- **Gold answer file:** `docs/qa/answers/2026-05-19-refeyn-mass-photometry-uses.md`
- **Notes:** Must explain iSCAT/interferometric scattering principle, individual landing event detection, and mass histogram interpretation. Use cases: oligomeric state, assembly stoichiometry, homogeneity screening. Must reflect exploratory/not-yet-routine deployment status at Nurix from `refeyn-mass-photometry` (confidence:low). Claiming Refeyn is a deployed routine QC instrument is a fail.
- **Added:** 2026-05-19 by mateo

---

## q-026 — Q4 2022 DEL Screening Budget

- **Question:** What was the Q4 2022 screening budget impact, and which programs were in the DEL screen queue at that time?
- **Expected route:** `wiki`
- **Expected cited slugs:** `q4-2022-screening-budget`, `dsa-early-discovery-cadence-2022`, `2022-del-screen-queue`
- **Category:** historical-decision
- **Difficulty:** medium
- **Gold answer file:** `docs/qa/answers/2026-05-19-q4-2022-del-screening-budget.md`
- **Notes:** Must cite all three slugs. Q4 2022 workbook: 22 remaining projects, 148 samples, ~2.3 NovaSeq S4 chips, $53,187.50 calculated cost. Programs in queue include GRWD1, TRIM28, EWS-FLI1, CISH, FEM1A, FEM1B, IRF5, MAGED4, DCAF1, MAGEA6, IRAK4, Aurora A, CDK12, FBXO10, RNF114, TRIM25, MED8, USP18 and others. Inventing specific dollar amounts not in the wiki is a fail.
- **Added:** 2026-05-19 by mateo

---

## q-027 — 2025 Delphi Data Quality Audit

- **Question:** What did the 2025 Delphi data quality audit find, and what changes resulted from it?
- **Expected route:** `wiki`
- **Expected cited slugs:** `2025-delphi-data-quality-audit`
- **Category:** historical-decision
- **Difficulty:** medium
- **Gold answer file:** `docs/qa/answers/2026-05-19-2025-delphi-data-quality-audit.md`
- **Notes:** Must cover: empty table rates (PP: 22%, CP: 41%), 43% empty column rate, duplicate column divergence (protein_alias example, PTI vs PTF), broken sequence retrieval path (outdated query, viable replacement path, `large_scale_purification_task_id` gap), DNATAG mapping at 34%, and the four tentative action items. Must characterize action items as tentative (not implemented/approved). Inventing audit findings is a fail.
- **Added:** 2026-05-19 by mateo

---

## q-028 — Loka ML Engagement 2024

- **Question:** What was the Loka ML engagement in 2024 — what was the scope and what did it deliver?
- **Expected route:** `wiki`
- **Expected cited slugs:** `loka-ml-engagement`
- **Category:** historical-decision
- **Difficulty:** medium
- **Gold answer file:** `docs/qa/answers/2026-05-19-loka-ml-engagement-2024.md`
- **Notes:** Answer must reflect the severe wiki limitation: the absorbed source is the data-handoff artifact only (20240909-bulk_info_for_ps.xlsx), not any engagement scope document, contract, or deliverable. Modeling objectives and outcomes are explicitly not documented. Claiming specific ML model architectures, results, or deliverables is a fail. Confidence:low is required.
- **Added:** 2026-05-19 by mateo

---

## q-029 — Protein Request UX Redesign Arc

- **Question:** Walk me through the protein request UX redesign arc from 2022 to 2025 — what changed and why?
- **Expected route:** `wiki`
- **Expected cited slugs:** `protein-request-ux-redesign`, `protein-request-submission`
- **Category:** historical-decision
- **Difficulty:** hard
- **Gold answer file:** `docs/qa/answers/2026-05-19-protein-request-ux-redesign.md`
- **Notes:** Must trace the arc chronologically: 2022 initial form refinements (biotinylation checkbox, requester field, checkout honor system formalization), 2022 workflow redesign (clone task grouping, re-supply vs. novel request distinction), 2022-2023 Figma reviews (unit display, picklist labeling, biomass inventory table), 2024 homepage redesign (automated status pills), 2024 workflow checklist (BirA mandatory fields, biotinylation commitment), 2025 inventory checkout refinement (rack/position columns) and ML export request. Inventing named features not in the wiki is a fail.
- **Added:** 2026-05-19 by mateo

---

## q-030 — DEL Buffer Stability SOP

- **Question:** What is the DEL buffer stability test SOP, and why is buffer stability critical for DEL screens?
- **Expected route:** `wiki`
- **Expected cited slugs:** `del-buffer-stability-testing`
- **Category:** protocol-method
- **Difficulty:** easy
- **Gold answer file:** `docs/qa/answers/2026-05-19-del-buffer-stability-sop.md`
- **Notes:** Must cover: purpose (avoid committing library to unstable construct), 5X Core Buffer / 2x2 salt-detergent matrix, DSF + aSEC characterization, SIAH1 documented findings (high-salt aggregation, detergent-caused loss of N00620). The method is target-specific rather than a fixed universal SOP — must reflect this. Fixed quantitative aggregate-fraction thresholds are not in the wiki and must not be invented.
- **Added:** 2026-05-19 by mateo

---

## q-031 — SEC-MALS

- **Question:** How does SEC-MALS work, and what does Nurix use it for?
- **Expected route:** `wiki`
- **Expected cited slugs:** `sec-mals`
- **Category:** protocol-method
- **Difficulty:** easy
- **Gold answer file:** `docs/qa/answers/2026-05-19-sec-mals-standard-run.md`
- **Notes:** Must explain: SEC separates by hydrodynamic radius; MALS measures absolute MW (calibration-independent, light scattering at multiple angles); dRI measures concentration; together yield MW of species in each SEC peak. Use cases: oligomeric state, complex stoichiometry, aggregation detection, CRO delivery QC. Wyatt Technology system with Superdex 75/200 and AKTA platform documented at Nurix.
- **Added:** 2026-05-19 by mateo

---

## q-032 — DSF Protein Characterization

- **Question:** How does DSF work, and what is it used for in protein characterization at Nurix?
- **Expected route:** `wiki`
- **Expected cited slugs:** `dsf`
- **Category:** protocol-method
- **Difficulty:** easy
- **Gold answer file:** `docs/qa/answers/2026-05-19-dsf-protein-characterization.md`
- **Notes:** Must cover: SYPRO Orange dye, fluorescence on hydrophobic surface exposure during denaturation, Tm from first derivative, positive delta-Tm = ligand binding/stabilization. Use cases: post-purification QC, buffer optimization, hit identification, construct stability comparison. Tycho (NanoTemper) instrument implementation at Nurix. AuroraA-NMYC-CRBN-DDB1 complex example with NRX4505/NRX6715 is documented in the wiki.
- **Added:** 2026-05-19 by mateo

---

## q-033 — High-Throughput Expression Determination

- **Question:** What is the high-throughput expression determination workflow, and what decisions does it inform?
- **Expected route:** `wiki`
- **Expected cited slugs:** `ht-expression-determination`, `ht-platform-sop`
- **Category:** protocol-method
- **Difficulty:** medium
- **Gold answer file:** `docs/qa/answers/2026-05-19-ht-expression-determination.md`
- **Notes:** Both source pages are confidence:low and explicitly state the methodology is exploratory/draft-proposal as of 2026. Answer must state this before describing the proposed workflow. Must not describe this as a deployed routine process. The "decisions it informs" framing requires INFERRED label since no documented deployment use cases exist. Describing HT expression as a routine platform is a fail.
- **Added:** 2026-05-19 by mateo

---

## q-034 — TEV Protease Cleavage Workflow

- **Question:** What is the TEV protease cleavage workflow, and when is it used in protein purification?
- **Expected route:** `wiki`
- **Expected cited slugs:** `tev-protease-purification`
- **Category:** protocol-method
- **Difficulty:** easy
- **Gold answer file:** `docs/qa/answers/2026-05-19-tev-protease-cleavage-workflow.md`
- **Notes:** Must cover: TEV recognition sequence ENLYFQ-G/S (per wiki — not ENLYFQ/S), affinity tag removal from His-tagged recombinant proteins, Ni-NTA re-capture polishing step, Strep-tag alternative polishing. Use case: tag-free protein for SPR, crystallography. Must note that detailed empirical reaction conditions are not yet fully absorbed in the wiki. Source page is confidence:low.
- **Added:** 2026-05-19 by mateo

---

## q-035 — HiBiT Cell Screening Assay

- **Question:** What is the HiBiT cell screening assay, and how is it used for target engagement / degradation studies?
- **Expected route:** `wiki`
- **Expected cited slugs:** `cell-screening`
- **Category:** protocol-method
- **Difficulty:** easy
- **Gold answer file:** `docs/qa/answers/2026-05-19-hibit-cell-screening-assay.md`
- **Notes:** Must explain split-NanoLuc: HiBiT (11 aa tag on target) + LgBiT (exogenous) → luminescence proportional to target protein level. Degradation reduces signal; dose-response yields DC50/Dmax. Nurix implementation: V3.0 protocol (Feb 2024), Echo acoustic liquid handler, Activity Base LIMS, SNF04 series through Screen 34. Protocol version iteration history (V2.2 → V2.2.1 → V3.0) noted in source.
- **Added:** 2026-05-19 by mateo
