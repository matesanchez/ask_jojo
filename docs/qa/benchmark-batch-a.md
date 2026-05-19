# Phase 4 Q&A Benchmark — Batch A (q-006 through q-020)

**Status:** Seeded with 15 entries (2026-05-19). Batch A covers q-006 through q-020.
**Parent file:** `docs/qa/benchmark-questions.md`
**Governing ADR:** `docs/ADR/0011-qa-via-cowork-while-api-pending.md`

This file contains the second wave of Phase 4 benchmark entries, extending the canonical evaluation set from 5 to 20 entries. Format matches `benchmark-questions.md`. All gold answers were produced in the 2026-05-19 Cowork session.

---

## q-006 — BTK vs. IRAK4 program direction

- **Question:** What are the key differences in program direction between the BTK CTM program and the IRAK4 DEL screen effort, and how far did each advance?
- **Expected route:** `wiki`
- **Expected cited slugs:** `btk-ctm`, `irak4`
- **Category:** program-comparison
- **Difficulty:** medium
- **Gold answer file:** `docs/qa/answers/2026-05-19-btk-vs-irak4-program-direction.md`
- **Notes:** Correct answer distinguishes BTK CTM (clinical-stage; NX-2127, NX-5948) from IRAK4 (target-only page; DEL campaign 1; no program page; tracer compounds NRX-0392248 and NRX-0395372). Must note the absence of an IRAK4 program page as the structural indicator of program-stage difference. CTM-hook designation for IRAK4 must be noted if present. Fabricated IRAK4 clinical compounds or program milestones are fails.
- **Added:** 2026-05-19 by mdelosrios

## q-007 — CBL-B CTM exploration vs. CBL-B preclinical profile

- **Question:** What's the relationship between the CBL-B CTM exploration page and the CBL-B preclinical profile page — do they cover the same compounds, or different stages?
- **Expected route:** `wiki`
- **Expected cited slugs:** `cbl-b-ctm`, `cbl-b-preclinical-profile`
- **Category:** program-comparison
- **Difficulty:** easy
- **Gold answer file:** `docs/qa/answers/2026-05-19-cbl-b-ctm-vs-preclinical.md`
- **Notes:** Correct answer establishes that the two pages cover non-overlapping compound classes: `cbl-b-ctm` covers degrader (CTM) compounds (NRX-0395686, NRX-0398194, NRX-0400149) that did not advance; `cbl-b-preclinical-profile` covers CBL-B inhibitors (NX-1607/NRX-0391607, NX-0255/NRX-0390255, NRX-0388766) that did advance to IND. Must note GSPT1 co-degradation as the NRX-0398194 liability. Merging the two compound sets (claiming NX-1607 is a CTM) is an immediate fail.
- **Added:** 2026-05-19 by mdelosrios

## q-008 — ITK CTM merged page resolution

- **Question:** What happened to the ITK CTM page (slug: itk-ctm-merged) — is it a separate program, or was it consolidated somewhere?
- **Expected route:** `wiki`
- **Expected cited slugs:** `itk-ctm-merged`, `itk`
- **Category:** relational
- **Difficulty:** easy
- **Gold answer file:** `docs/qa/answers/2026-05-19-itk-vs-itk-ctm-merged.md`
- **Notes:** Correct answer resolves the redirect: `itk-ctm-merged` is a deleted stub (status: deleted, tags: redirect) pointing to `programs/itk.md`. The unified ITK page covers the full program. Key ITK facts from the unified page: first CTM NRX-0387327 DC50 = 30 nM; optimized NRX-0395826 DC50 = 4.1 pM; NHP compounds NRX-0401647, NRX-0401650, NRX-0404422; colitis indication; GSPT1 and LCK co-degradation liabilities. A response that returns only the stub content (one line) without following the hop to `itk` is incomplete.
- **Added:** 2026-05-19 by mdelosrios

## q-009 — Pellino-1 program page vs. target page scope

- **Question:** What is the difference in scope between the Pellino-1 program page and the Pellino-1 target page — what does each cover that the other doesn't?
- **Expected route:** `wiki`
- **Expected cited slugs:** `pellino-1`, `pellino-1-target`
- **Category:** program-comparison
- **Difficulty:** medium
- **Gold answer file:** `docs/qa/answers/2026-05-19-pellino-1-program-vs-target-pages.md`
- **Notes:** Correct answer must assign content to the right page. Program page: chemistry milestones (NRX-0393000, DC50 2.46 nM; pan-Pellino HiBiT result); in vivo mouse TGI data; 2019 medchem plan (Peli1-KO vs Peli2-KO vs double-KO strategy); program hurdles July 2020; Celgene collaboration; Lewis Lanier consultation. Target page: Jurkat CRISPR-KO experiments; Weiss lab communication; primary T-cell siRNA data; THP-1 macrophage assay; RIP3 biomarker; Pellino family sequence identity and affinity table. Assigning program-layer facts to the target page (or vice versa) is a partial fail.
- **Added:** 2026-05-19 by mdelosrios

## q-010 — CRBN platform and TPD concept relationship

- **Question:** What is the CRBN platform at Nurix, and how does it relate to the targeted protein degradation concept page?
- **Expected route:** `wiki`
- **Expected cited slugs:** `crbn-cereblon-platform`, `targeted-protein-degradation`
- **Category:** platform-mechanism
- **Difficulty:** easy
- **Gold answer file:** `docs/qa/answers/2026-05-19-crbn-platform-and-tpd.md`
- **Notes:** Correct answer must surface the `confidence: low` and `pending-backfill-from-raw` status of `crbn-cereblon-platform` explicitly. CRBN platform page content (80 entries 2020-2025; DSF, aSEC, SEC-MALS; DDB1 complex; baculovirus expression) must be marked low-confidence or EXTRACTED/LOW-CONFIDENCE. TPD concept page facts (PROTAC vs. molecular glue mechanisms; CRBN as primary ligase; Keystone 2021; seed-stage internal targets) are medium-confidence. An answer that presents CRBN platform claims as established facts without confidence caveat is a partial fail.
- **Added:** 2026-05-19 by mdelosrios

## q-011 — SKP2 inhibitor program vs. Cdc34 ELSA program

- **Question:** How did the SKP2 inhibitor program compare to the Cdc34 ELSA program in approach and outcome?
- **Expected route:** `wiki`
- **Expected cited slugs:** `skp2-inhibitor`, `cdc34`
- **Category:** program-comparison
- **Difficulty:** medium
- **Gold answer file:** `docs/qa/answers/2026-05-19-skp2-vs-cdc34-approach.md`
- **Notes:** Correct answer distinguishes targets (SKP2 = E3 F-box protein; Cdc34 = E2 conjugating enzyme), strategies (SKP2: PPI disruption of SKP2-Cks1 interface; Cdc34: allosteric inhibition of ubiquitin-binding pocket, CC0651 precedent), and external collaborations (SKP2: WEHI compound library; Cdc34: Sicheri lab NMR and crystallography). Both programs: ~2015-2017, no candidate nomination. Must mention CC0651 for Cdc34 and the SKP2-Cks1 crystal structure rationale for SKP2. Fabricated IND-stage data for either program is an immediate fail.
- **Added:** 2026-05-19 by mdelosrios

## q-012 — TYK2 vs. JAK1 program prioritization (designed miss)

- **Question:** What's Nurix's program direction on TYK2 versus JAK1 — which one did we prioritize and why?
- **Expected route:** `raw`
- **Expected cited slugs:** _(none — no wiki pages exist for TYK2 or JAK1)_
- **Category:** edge
- **Difficulty:** easy
- **Gold answer file:** `docs/qa/answers/2026-05-19-tyk2-jak1-miss.md`
- **Notes:** This is a **designed miss**. Neither TYK2 nor JAK1 has a wiki page as of 2026-05-19 (verified by Glob). The correct system response is: report no wiki coverage, log a miss, optionally note that a raw search might surface relevant documents. The correct route is `raw` (fall-through), NOT `wiki`. Any synthesis answer providing a TYK2 vs. JAK1 comparison from Nurix's perspective without citing a specific wiki slug is an **immediate fail** — this tests hallucination resistance. The question was written to sound like a standard program-comparison question (cf. q-006, q-007) but is a trap.
- **Added:** 2026-05-19 by mdelosrios

## q-013 — CBL-B biology and therapeutic rationale

- **Question:** What does CBL-B do biologically, and why is it a therapeutic target for immuno-oncology?
- **Expected route:** `wiki`
- **Expected cited slugs:** `cbl-b-target`, `cbl-b`
- **Category:** target-biology
- **Difficulty:** easy
- **Gold answer file:** `docs/qa/answers/2026-05-19-cbl-b-what-it-does.md`
- **Notes:** Correct answer covers: pY363 conformational switch (closed/inactive → open/active via LHR/RING); Cbl-b KO mice (5-10x IL-2/IFNγ); ligase-inactive RING mutant genetic surrogate; NK cell mechanism (TAM receptors TYRO3/AXL/MERTK → LAT1 degradation); TGF-β/SMAD7 axis. The PSA/clinical claim must be marked INFERRED (wiki states it; PSA reduction is immune-mediated per in vitro LnCaP data). Must cite both `cbl-b-target` and `cbl-b`. An answer citing only one page is incomplete.
- **Added:** 2026-05-19 by mdelosrios

## q-014 — IRAK4 in TLR signaling and DEL screen strategy

- **Question:** What is IRAK4's role in TLR signaling, and what was the DEL screen strategy for it?
- **Expected route:** `wiki`
- **Expected cited slugs:** `irak4`
- **Category:** target-biology
- **Difficulty:** easy
- **Gold answer file:** `docs/qa/answers/2026-05-19-irak4-tlr-signaling.md`
- **Notes:** Correct answer covers: IRAK4 as serine-threonine kinase; MYD88/IRAK4/IRAK2 myddosome; NF-κB translocation; death domain (9-106) and kinase domain (186-458) boundaries; IRAK1/IRAK2/IRAK4 as documented substrates; CTM hook designation; DEL campaign 1 (14 samples, phosphorylated vs. dephosphorylated IRAK4); Tracer 1 NRX-0392248 (parent NRX-0391649, IC50 = 120 nM) and Tracer 2 NRX-0395372 (parent NRX-0393640, IC50 = 1 nM). Single source document is the IRAK4 Target Review and DEL Screen Plan (2020-03-31). AP-1 is NOT on the page — mentioning AP-1 without citation is a fail. Fabricated DEL hit data or downstream compound data are fails.
- **Added:** 2026-05-19 by mdelosrios

## q-015 — BTK in BCR signaling and the BTK CTM program

- **Question:** What is BTK's role in B-cell receptor signaling, and how does Nurix's BTK CTM program exploit that biology?
- **Expected route:** `wiki`
- **Expected cited slugs:** `btk`, `btk-ctm`
- **Category:** target-biology
- **Difficulty:** easy
- **Gold answer file:** `docs/qa/answers/2026-05-19-btk-bcr-signaling-and-program.md`
- **Notes:** Correct answer covers: BTK as TEC family non-receptor kinase; BCR → PLC-γ2 → NF-κB axis; three generations of FDA-approved inhibitors; C481S covalent resistance mutation; CTM rationale (sub-stoichiometric catalytic degradation; retains C481S activity); NRX-0390492 proof-of-concept; NX-2127 (dual BTK+IKZF1/3 degrader; Science paper); NX-5948 (fumarate salt; SDI/ASD formulation; dog PK Jan 2026). Must cite both `btk` (BCR biology) and `btk-ctm` (clinical compounds). Claiming NX-2127 or NX-5948 are inhibitors rather than degraders is a fail.
- **Added:** 2026-05-19 by mdelosrios

## q-016 — Pellino-1 vs. Pellino-2 in mouse tumor immunity

- **Question:** What do the mouse genetics say about Pellino-1 versus Pellino-2 in tumor immunity, and how did that shape the Pellino-1 program?
- **Expected route:** `wiki`
- **Expected cited slugs:** `pellino-1`, `pellino-1-target`
- **Category:** historical-decision
- **Difficulty:** medium
- **Gold answer file:** `docs/qa/answers/2026-05-19-pellino1-vs-pellino2-mouse.md`
- **Notes:** Correct answer covers: Peli1-/- TC-1 TGI (p<0.0001) and improved MC38 survival; Peli2-/- no TGI in TC-1, no T-cell hyperactivation, no MC38 effect; 2019 medchem plan double-KO design; pan-Pellino activity of NRX-0393000 (Peli2 DC50 = 1.4 nM) as a chemical property not a strategic redirection; Peli1/Peli2 82% sequence identity. The pIRAK1 affinity difference (Peli2 0.18 µM > Peli1 0.77 µM) is a bonus fact. Stating the program "abandoned Peli2" without citing the double-KO strategy is incomplete. Inverting the mouse phenotypes (claiming Peli2-/- showed TGI) is an immediate fail.
- **Added:** 2026-05-19 by mdelosrios

## q-017 — ZAP-70 platform and T-cell activation (low-confidence page)

- **Question:** What is ZAP-70's role in T-cell activation, and what does the Nurix ZAP-70 platform page say about the program?
- **Expected route:** `wiki`
- **Expected cited slugs:** `zap-70-platform`
- **Category:** target-biology
- **Difficulty:** easy
- **Gold answer file:** `docs/qa/answers/2026-05-19-zap70-tcell-activation.md`
- **Notes:** Correct answer must surface the `confidence: low` and `pending-backfill-from-raw` status of `zap-70-platform` explicitly. Platform page content (ZAP-70 as Src-family kinase in TCR signaling; kinase/regulatory/full-length construct variants; bacterial and insect cell expression; 165 project entries 2018-2025; links to baculovirus-expression and snf-series-projects) must be marked low-confidence or EXTRACTED/LOW-CONFIDENCE. Any detailed ZAP-70 TCR mechanism description not cited from a specific wiki slug is a **fail** — this tests external-knowledge suppression on a low-coverage page.
- **Added:** 2026-05-19 by mdelosrios

## q-018 — FEM1B target biology and status

- **Question:** What does the wiki say about FEM1B as a target — biology, protein production status, and program context?
- **Expected route:** `wiki`
- **Expected cited slugs:** `fem1b`
- **Category:** target-biology
- **Difficulty:** easy
- **Gold answer file:** `docs/qa/answers/2026-05-19-fem1b-target.md`
- **Notes:** Correct answer is minimal by design: FEM1B is a ubiquitin ligase family member; no therapeutic rationale stated in wiki; protein sourced from GenScript (November 2022, Isabel Morgado); 71 entries in Isabel's archive; "Nairi protein" designation; no program page; confidence: low; single source document. Any answer providing FEM1B biology (e.g., N-degron pathway role, PROTAC application) without citing a specific wiki slug is a **fail**.
- **Added:** 2026-05-19 by mdelosrios

## q-019 — STAT6 in IL-4 signaling and DEL screen design

- **Question:** What is STAT6's role in IL-4 signaling, and how did Nurix design the DEL screen for it?
- **Expected route:** `wiki`
- **Expected cited slugs:** `stat6`
- **Category:** target-biology
- **Difficulty:** medium
- **Gold answer file:** `docs/qa/answers/2026-05-19-stat6-il4-signaling.md`
- **Notes:** Correct answer covers: STAT6 as IL-4-downstream transcription factor; Y641 phosphorylation driving dimerization and nuclear translocation; four target forms (core fragment/full-length × unphosphorylated-monomer/phosphorylated-dimer); HEPES pH 7.0 buffer; IL-4Rα pY peptide supplement (NRX-0396575; affinities 0.3 µM FP and 9.1 µM Nurix FRET); DNA ligand KD123 (Kd = 0.079 µM); nine-condition C1 P1 selection pool; Low Complexity end-of-year designation 2022. Fabricated STAT6 construct residue numbers or affinity values are fails.
- **Added:** 2026-05-19 by mdelosrios

## q-020 — IRF5 in autoimmune disease and DEL screen structure

- **Question:** What is IRF5's role in autoimmune disease, and how was the Nurix DEL screen for it structured?
- **Expected route:** `wiki`
- **Expected cited slugs:** `irf5`
- **Category:** target-biology
- **Difficulty:** medium
- **Gold answer file:** `docs/qa/answers/2026-05-19-irf5-autoimmune.md`
- **Notes:** Correct answer covers: IRF5 as PRR-downstream proinflammatory transcription factor; SLE/RA/IBD disease relevance; CTM-hook connection to IRAK4 CTM program; four domain types (DBD, ID, TAD/IAD, CTD/AID); IRF6 as paralog and counterscreen; five DEL campaigns (C1-C5); five target forms including phosphomimetic dimer (DDDD mutations S451D;S453D;S456D;S462D); N5-1 peptide Kd = 99 nM; CPP peptides Kd ~0.5 µM; cytosolic buffer pH 7.2; personnel (Ya-Wen Lu, Emily Low, Herman Yuen, Marcella Gilmore C1-C3, Bill Sonnenburg C4-C5). Must note the IRF5-IRAK4 CTM-hook relationship. Fabricated campaign counts or peptide affinities are fails.
- **Added:** 2026-05-19 by mdelosrios

---

## Batch A category distribution

| Category | Count | Questions |
|---|---|---|
| program-comparison | 5 | q-006, q-007, q-009, q-010, q-011 |
| target-biology | 7 | q-013, q-014, q-015, q-017, q-018, q-019, q-020 |
| relational | 1 | q-008 |
| historical-decision | 1 | q-016 |
| edge | 1 | q-012 |

Running total after Batch A: 20 entries (5 from `benchmark-questions.md` + 15 from this file).
