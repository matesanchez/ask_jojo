# Phase 4 Q&A Benchmark — Canonical Questions

**Status:** 50 entries complete (2026-05-19). Phase 4 benchmark fully seeded.
**Governing ADR:** `docs/ADR/0011-qa-via-cowork-while-api-pending.md`
**Phase 4 exit criterion:** ≥80% "correct and well-cited" on this file's questions, per two reviewers (PLAN.md §6 Phase 4).

This file is the **canonical** Phase 4 evaluation set: 50 Nurix questions with domain-reviewer-approved gold answers, expected routes, and expected cited slugs. The benchmark grades:

- the **router** (every question carries an `expected_route`),
- the **retrieval** (every question carries `expected_cited_slugs` — the gold answer's bibliography),
- the **synthesis** (every question carries a `gold_answer` and a `notes` field describing what a "correct" answer must include).

The harness in `scripts/run_benchmark.py` runs in two modes:

- `--dry-run` — router-only, fully deterministic, runs in CI today. Asserts `router.classify(question) == expected_route`.
- `--full` — router + synthesis, gated on `anthropic_api_key`. Skipped in CI today; runs on API day.

Until then, the gold answers are produced by Cowork sessions (per ADR 0011) and live alongside the benchmark in `docs/qa/answers/`. A benchmark entry's `gold_answer_file` field points to the corresponding answer.

## Schema (per entry)

```yaml
- id: q-001
  question: "What's the difference between NX-1607 and NX-0255?"
  expected_route: wiki
  expected_cited_slugs:
    - cbl-b
    - cbl-b-cmc
    - cbl-b-preclinical-profile
  category: program-comparison
  difficulty: easy
  gold_answer_file: docs/qa/answers/2026-04-30-cbl-b-nx1607-vs-nx0255.md
  notes: |
    Correct answers must distinguish NX-1607 (lead clinical CBL-B inhibitor)
    from NX-0255 (backup CBL-B inhibitor) and state at least one differentiator
    (chemotype, ADME profile, clinical stage). Hallucinated "clinical Phase II"
    or "approved" claims are immediate fails.
  added: 2026-04-30
  added_by: mateo
```

## Categories

The 50 questions distribute across categories so the benchmark grades the router, retrieval, and synthesis evenly:

| Category | Count | Description |
|---|---|---|
| program-comparison | 5 | Cross-program differentiators (NX-1607 vs NX-0255, BTK vs IRAK4, etc.) |
| target-biology | 7 | What is target X, what does it do, why are we drugging it |
| platform-mechanism | 7 | DEL, Delphi, CRBN, PROTAC mechanism questions |
| historical-decision | 7 | Why did we do X? Cited program decisions |
| protocol-method | 6 | Wet-lab method questions sourced from `methods/` and `protocols/` |
| relational | 5 | "What's the connection between X and Y?" — exercises graph hop-following |
| router-stress | 4 | Edge cases: ÄKTA-on-program, buffer-on-program, mixed-keyword questions |
| v1-routing | 4 | Pure ÄKTA / UNICORN / chromatography questions; expected_route = `v1` |
| edge | 5 | Out-of-scope, ambiguous, multi-corpus questions; expected_route + raw fallback |

50 entries across 9 categories. Cowork sessions: 2026-04-30 (q-001–q-005), 2026-05-19 (q-006–q-050).

---

## q-001 — CBL-B: NX-1607 vs NX-0255

- **Question:** What's the difference between NX-1607 and NX-0255, and what's the current clinical status of each?
- **Expected route:** `wiki`
- **Expected cited slugs:** `cbl-b`, `cbl-b-cmc`, `cbl-b-preclinical-profile`, `cbl-b-ind-pharmacology`, `cbl-b-target`
- **Category:** program-comparison
- **Difficulty:** easy
- **Gold answer file:** `docs/qa/answers/2026-04-30-cbl-b-nx1607-vs-nx0255.md`
- **Notes:** A correct answer distinguishes NX-1607 (lead clinical CBL-B inhibitor; orally bioavailable; profiled in mCRPC and other indications per `cbl-b-ind-pharmacology`) from NX-0255 (backup / second clinical-stage CBL-B inhibitor; differentiated chemotype). Must cite at least three slugs from the expected list. "Clinical Phase II" or "approved" claims that aren't sourced from the wiki are fails.
- **Added:** 2026-04-30 by mateo

## q-002 — Pellino-1 program: Peli2 redundancy

- **Question:** Did the Weiss lab Peli2 redundancy finding in Jurkat ever change our position on the Pellino-1 program direction?
- **Expected route:** `wiki`
- **Expected cited slugs:** `pellino-1` (program), `pellino-1-target` (target)
- **Category:** historical-decision
- **Difficulty:** medium
- **Gold answer file:** `docs/qa/answers/2026-04-30-pellino-1-peli2-redundancy.md`
- **Notes:** Correct answer references the Weiss lab Peli2 redundancy finding in Jurkat (cited from the Pellino-1 program page; absorb checkpoint 19, ~2026-04-25 commit `2f56204`) and discusses how it interacted with the Nurix Peli2-KO TGI / MC38 negative result and the THP-1 macrophage data. Must distinguish the *target* page (cell biology) from the *program* page (decisions / direction). Confidence on the "did it change direction" claim is at most medium since the wiki may not have an explicit decision page on this. Inferring causality without a cited decision page is a fail.
- **Added:** 2026-04-30 by mateo

## q-003 — DEL screening at Nurix in 2022

- **Question:** How was DEL screening organized at Nurix in 2022, and what programs were in the queue?
- **Expected route:** `wiki`
- **Expected cited slugs:** `del-screening`, `del-libraries`, `2022-del-screen-queue`, `dsa-early-discovery-cadence-2022`, `q4-2022-screening-budget`
- **Category:** platform-mechanism
- **Difficulty:** easy
- **Gold answer file:** `docs/qa/answers/2026-04-30-del-screening-2022.md`
- **Notes:** Correct answer describes the DEL screening program structure as of 2022 — DSA (DEL Screening and Analysis) early-discovery cadence, the Q4 2022 budget that capped screening capacity, the queued programs from `2022-del-screen-queue` (e.g. SIAH1 buffer screening). Must cite at least three slugs from the expected list. Speculative additions about programs not on the queue are fails.
- **Added:** 2026-04-30 by mateo

## q-004 — Delphi ACS releases through 2025

- **Question:** Walk me through the major Delphi ACS releases from inception through 2025 — what changed in each, and what was the major decision behind each scope?
- **Expected route:** `wiki`
- **Expected cited slugs:** `delphi`, `delphi-acs-scope`, `delphi-pre-acs-timeline`, `delphi-acs2024-1-release`, `delphi-acs2025-1-release`, `delphi-acs2025-2-release`, `delphi-acs2025-3-release`, `delphi-acs2024-1-uat-cycle`, `delphi-acs2025-1-uat-cycle`, `delphi-acs2025-2-uat-cycle`
- **Category:** historical-decision
- **Difficulty:** hard
- **Gold answer file:** `docs/qa/answers/2026-04-30-delphi-acs-releases-2025.md`
- **Notes:** Correct answer is a chronological walkthrough citing each release decision page. Must distinguish *release* pages from *UAT cycle* pages and explain the relationship (UAT precedes release; UAT cycle pages capture the scope-decision artifacts). The pre-ACS era (`delphi-pre-acs-timeline`) is the right anchor for what came before ACS2024.1. Inventing release versions not in the cited slugs is a fail. Scope notes ("ACS2025.2 added X") must be sourced from a cited decision page; un-cited scope claims are fails.
- **Added:** 2026-04-30 by mateo

## q-005 — ÄKTA buffer prep (router test)

- **Question:** What's the standard buffer prep procedure for an ÄKTA Pure 25 run on the BTK program?
- **Expected route:** `v1`
- **Expected cited slugs:** _(none — `v1` route bypasses the wiki)_
- **Category:** v1-routing
- **Difficulty:** easy
- **Gold answer file:** `docs/qa/answers/2026-04-30-akta-buffer-prep-v1-routing.md`
- **Notes:** This is a **router test**, not a synthesis test. The correct response is a routing slip pointing at v1.0 because the question contains both `akta` and `buffer` and `purif` (implicitly). The session does *not* attempt to answer it from the wiki. A correct router decision is the entire grade for this entry. The wiki has near-zero ÄKTA content (`equipment/akta/` directory is empty per the current `_index.md`); v1.0 has the answer. The mention of "BTK program" is a red herring meant to test that the router does not over-rotate to `wiki` because of the program-keyword. The session note should record whether the regex tripped on the program-keyword.
- **Added:** 2026-04-30 by mateo

---

## q-006 — BTK vs. IRAK4 program direction

- **Question:** What are the key differences in program direction between the BTK CTM program and the IRAK4 DEL screen effort, and how far did each advance?
- **Expected route:** `wiki`
- **Expected cited slugs:** `btk-ctm`, `irak4`
- **Category:** program-comparison
- **Difficulty:** medium
- **Gold answer file:** `docs/qa/answers/2026-05-19-btk-vs-irak4-program-direction.md`
- **Notes:** Correct answer distinguishes BTK CTM (clinical-stage; NX-2127, NX-5948) from IRAK4 (target-only page; DEL campaign 1; no program page; tracer compounds NRX-0392248 and NRX-0395372). Must note the absence of an IRAK4 program page as the structural indicator of program-stage difference. CTM-hook designation for IRAK4 must be noted if present. Fabricated IRAK4 clinical compounds or program milestones are fails.
- **Added:** 2026-05-19 by mateo

## q-007 — CBL-B CTM exploration vs. CBL-B preclinical profile

- **Question:** What's the relationship between the CBL-B CTM exploration page and the CBL-B preclinical profile page — do they cover the same compounds, or different stages?
- **Expected route:** `wiki`
- **Expected cited slugs:** `cbl-b-ctm`, `cbl-b-preclinical-profile`
- **Category:** program-comparison
- **Difficulty:** easy
- **Gold answer file:** `docs/qa/answers/2026-05-19-cbl-b-ctm-vs-preclinical.md`
- **Notes:** Correct answer establishes that the two pages cover non-overlapping compound classes: `cbl-b-ctm` covers degrader (CTM) compounds (NRX-0395686, NRX-0398194, NRX-0400149) that did not advance; `cbl-b-preclinical-profile` covers CBL-B inhibitors (NX-1607/NRX-0391607, NX-0255/NRX-0390255, NRX-0388766) that did advance to IND. Must note GSPT1 co-degradation as the NRX-0398194 liability. Merging the two compound sets (claiming NX-1607 is a CTM) is an immediate fail.
- **Added:** 2026-05-19 by mateo

## q-008 — ITK CTM merged page resolution

- **Question:** What happened to the ITK CTM page (slug: itk-ctm-merged) — is it a separate program, or was it consolidated somewhere?
- **Expected route:** `wiki`
- **Expected cited slugs:** `itk-ctm-merged`, `itk`
- **Category:** relational
- **Difficulty:** easy
- **Gold answer file:** `docs/qa/answers/2026-05-19-itk-vs-itk-ctm-merged.md`
- **Notes:** Correct answer resolves the redirect: `itk-ctm-merged` is a deleted stub (status: deleted, tags: redirect) pointing to `programs/itk.md`. The unified ITK page covers the full program. Key ITK facts from the unified page: first CTM NRX-0387327 DC50 = 30 nM; optimized NRX-0395826 DC50 = 4.1 pM; NHP compounds NRX-0401647, NRX-0401650, NRX-0404422; colitis indication; GSPT1 and LCK co-degradation liabilities. A response that returns only the stub content without following the hop to `itk` is incomplete.
- **Added:** 2026-05-19 by mateo

## q-009 — Pellino-1 program page vs. target page scope

- **Question:** What is the difference in scope between the Pellino-1 program page and the Pellino-1 target page — what does each cover that the other doesn't?
- **Expected route:** `wiki`
- **Expected cited slugs:** `pellino-1`, `pellino-1-target`
- **Category:** program-comparison
- **Difficulty:** medium
- **Gold answer file:** `docs/qa/answers/2026-05-19-pellino-1-program-vs-target-pages.md`
- **Notes:** Correct answer must assign content to the right page. Program page: chemistry milestones (NRX-0393000, DC50 2.46 nM; pan-Pellino HiBiT result); in vivo mouse TGI data; 2019 medchem plan; program hurdles July 2020; Celgene collaboration; Lewis Lanier consultation. Target page: Jurkat CRISPR-KO experiments; Weiss lab communication; primary T-cell siRNA data; THP-1 macrophage assay; RIP3 biomarker; Pellino family sequence identity and affinity table. Assigning program-layer facts to the target page (or vice versa) is a partial fail.
- **Added:** 2026-05-19 by mateo

## q-010 — CRBN platform and TPD concept relationship

- **Question:** What is the CRBN platform at Nurix, and how does it relate to the targeted protein degradation concept page?
- **Expected route:** `wiki`
- **Expected cited slugs:** `crbn-cereblon-platform`, `targeted-protein-degradation`
- **Category:** platform-mechanism
- **Difficulty:** easy
- **Gold answer file:** `docs/qa/answers/2026-05-19-crbn-platform-and-tpd.md`
- **Notes:** Correct answer must surface the `confidence: low` and `pending-backfill-from-raw` status of `crbn-cereblon-platform` explicitly. CRBN platform page content must be marked low-confidence or EXTRACTED/LOW-CONFIDENCE. TPD concept page facts (PROTAC vs. molecular glue mechanisms; CRBN as primary ligase) are medium-confidence. An answer that presents CRBN platform claims as established facts without confidence caveat is a partial fail.
- **Added:** 2026-05-19 by mateo

## q-011 — SKP2 inhibitor program vs. Cdc34 ELSA program

- **Question:** How did the SKP2 inhibitor program compare to the Cdc34 ELSA program in approach and outcome?
- **Expected route:** `wiki`
- **Expected cited slugs:** `skp2-inhibitor`, `cdc34`
- **Category:** program-comparison
- **Difficulty:** medium
- **Gold answer file:** `docs/qa/answers/2026-05-19-skp2-vs-cdc34-approach.md`
- **Notes:** Correct answer distinguishes targets (SKP2 = E3 F-box protein; Cdc34 = E2 conjugating enzyme), strategies (SKP2: PPI disruption of SKP2-Cks1 interface; Cdc34: allosteric inhibition, CC0651 precedent), and external collaborations (SKP2: WEHI compound library; Cdc34: Sicheri lab NMR and crystallography). Both programs ~2015-2017, no candidate nomination. Must mention CC0651 for Cdc34 and the SKP2-Cks1 crystal structure rationale for SKP2. Fabricated IND-stage data for either program is an immediate fail.
- **Added:** 2026-05-19 by mateo

## q-012 — TYK2 vs. JAK1 program prioritization (designed miss)

- **Question:** What's Nurix's program direction on TYK2 versus JAK1 — which one did we prioritize and why?
- **Expected route:** `raw`
- **Expected cited slugs:** _(none — no wiki pages exist for TYK2 or JAK1)_
- **Category:** edge
- **Difficulty:** easy
- **Gold answer file:** `docs/qa/answers/2026-05-19-tyk2-jak1-miss.md`
- **Notes:** This is a **designed miss**. Neither TYK2 nor JAK1 has a wiki page as of 2026-05-19. The correct system response is: report no wiki coverage, log a miss, optionally note that a raw search might surface relevant documents. Any synthesis answer providing a TYK2 vs. JAK1 comparison without citing a specific wiki slug is an **immediate fail** — this tests hallucination resistance.
- **Added:** 2026-05-19 by mateo

## q-013 — CBL-B biology and therapeutic rationale

- **Question:** What does CBL-B do biologically, and why is it a therapeutic target for immuno-oncology?
- **Expected route:** `wiki`
- **Expected cited slugs:** `cbl-b-target`, `cbl-b`
- **Category:** target-biology
- **Difficulty:** easy
- **Gold answer file:** `docs/qa/answers/2026-05-19-cbl-b-what-it-does.md`
- **Notes:** Correct answer covers: pY363 conformational switch; Cbl-b KO mice (5-10x IL-2/IFNγ); ligase-inactive RING mutant genetic surrogate; NK cell mechanism (TAM receptors → LAT1 degradation); TGF-β/SMAD7 axis. Must cite both `cbl-b-target` and `cbl-b`. An answer citing only one page is incomplete.
- **Added:** 2026-05-19 by mateo

## q-014 — IRAK4 in TLR signaling and DEL screen strategy

- **Question:** What is IRAK4's role in TLR signaling, and what was the DEL screen strategy for it?
- **Expected route:** `wiki`
- **Expected cited slugs:** `irak4`
- **Category:** target-biology
- **Difficulty:** easy
- **Gold answer file:** `docs/qa/answers/2026-05-19-irak4-tlr-signaling.md`
- **Notes:** Correct answer covers: IRAK4 as serine-threonine kinase; MYD88/IRAK4/IRAK2 myddosome; NF-κB translocation; death domain (9-106) and kinase domain (186-458) boundaries; CTM hook designation; DEL campaign 1 (14 samples); Tracer 1 NRX-0392248 (parent NRX-0391649, IC50 = 120 nM) and Tracer 2 NRX-0395372 (parent NRX-0393640, IC50 = 1 nM). AP-1 is NOT on the page — mentioning AP-1 without citation is a fail.
- **Added:** 2026-05-19 by mateo

## q-015 — BTK in BCR signaling and the BTK CTM program

- **Question:** What is BTK's role in B-cell receptor signaling, and how does Nurix's BTK CTM program exploit that biology?
- **Expected route:** `wiki`
- **Expected cited slugs:** `btk`, `btk-ctm`
- **Category:** target-biology
- **Difficulty:** easy
- **Gold answer file:** `docs/qa/answers/2026-05-19-btk-bcr-signaling-and-program.md`
- **Notes:** Correct answer covers: BTK as TEC family non-receptor kinase; BCR → PLC-γ2 → NF-κB axis; three generations of FDA-approved inhibitors; C481S covalent resistance mutation; CTM rationale (sub-stoichiometric catalytic degradation; retains C481S activity); NX-2127 (dual BTK+IKZF1/3 degrader; Science paper); NX-5948 (fumarate salt; SDI/ASD formulation). Must cite both `btk` and `btk-ctm`. Claiming NX-2127 or NX-5948 are inhibitors rather than degraders is a fail.
- **Added:** 2026-05-19 by mateo

## q-016 — Pellino-1 vs. Pellino-2 in mouse tumor immunity

- **Question:** What do the mouse genetics say about Pellino-1 versus Pellino-2 in tumor immunity, and how did that shape the Pellino-1 program?
- **Expected route:** `wiki`
- **Expected cited slugs:** `pellino-1`, `pellino-1-target`
- **Category:** historical-decision
- **Difficulty:** medium
- **Gold answer file:** `docs/qa/answers/2026-05-19-pellino1-vs-pellino2-mouse.md`
- **Notes:** Correct answer covers: Peli1-/- TC-1 TGI (p<0.0001) and improved MC38 survival; Peli2-/- no TGI in TC-1, no T-cell hyperactivation, no MC38 effect; 2019 medchem plan double-KO design; pan-Pellino activity of NRX-0393000 (Peli2 DC50 = 1.4 nM) as a chemical property not a strategic redirection. Inverting the mouse phenotypes (claiming Peli2-/- showed TGI) is an immediate fail.
- **Added:** 2026-05-19 by mateo

## q-017 — ZAP-70 platform and T-cell activation (low-confidence page)

- **Question:** What is ZAP-70's role in T-cell activation, and what does the Nurix ZAP-70 platform page say about the program?
- **Expected route:** `wiki`
- **Expected cited slugs:** `zap-70-platform`
- **Category:** target-biology
- **Difficulty:** easy
- **Gold answer file:** `docs/qa/answers/2026-05-19-zap70-tcell-activation.md`
- **Notes:** Correct answer must surface the `confidence: low` and `pending-backfill-from-raw` status of `zap-70-platform` explicitly. Any detailed ZAP-70 TCR mechanism description not cited from a specific wiki slug is a **fail** — this tests external-knowledge suppression on a low-coverage page.
- **Added:** 2026-05-19 by mateo

## q-018 — FEM1B target biology and status

- **Question:** What does the wiki say about FEM1B as a target — biology, protein production status, and program context?
- **Expected route:** `wiki`
- **Expected cited slugs:** `fem1b`
- **Category:** target-biology
- **Difficulty:** easy
- **Gold answer file:** `docs/qa/answers/2026-05-19-fem1b-target.md`
- **Notes:** Correct answer is minimal by design: FEM1B is a ubiquitin ligase family member; no therapeutic rationale stated in wiki; protein sourced from GenScript (November 2022, Isabel Morgado); 71 entries; "Nairi protein" designation; no program page; confidence: low. Any answer providing FEM1B biology not from a specific wiki slug is a **fail**.
- **Added:** 2026-05-19 by mateo

## q-019 — STAT6 in IL-4 signaling and DEL screen design

- **Question:** What is STAT6's role in IL-4 signaling, and how did Nurix design the DEL screen for it?
- **Expected route:** `wiki`
- **Expected cited slugs:** `stat6`
- **Category:** target-biology
- **Difficulty:** medium
- **Gold answer file:** `docs/qa/answers/2026-05-19-stat6-il4-signaling.md`
- **Notes:** Correct answer covers: STAT6 as IL-4-downstream transcription factor; Y641 phosphorylation driving dimerization and nuclear translocation; four target forms; HEPES pH 7.0 buffer; IL-4Rα pY peptide supplement (NRX-0396575); DNA ligand KD123 (Kd = 0.079 µM); nine-condition C1 P1 selection pool; Low Complexity end-of-year designation 2022. Fabricated STAT6 construct residue numbers or affinity values are fails.
- **Added:** 2026-05-19 by mateo

## q-020 — IRF5 in autoimmune disease and DEL screen structure

- **Question:** What is IRF5's role in autoimmune disease, and how was the Nurix DEL screen for it structured?
- **Expected route:** `wiki`
- **Expected cited slugs:** `irf5`
- **Category:** target-biology
- **Difficulty:** medium
- **Gold answer file:** `docs/qa/answers/2026-05-19-irf5-autoimmune.md`
- **Notes:** Correct answer covers: IRF5 as PRR-downstream proinflammatory transcription factor; SLE/RA/IBD disease relevance; CTM-hook connection to IRAK4 CTM program; four domain types; IRF6 as paralog and counterscreen; five DEL campaigns (C1-C5); five target forms including phosphomimetic dimer (DDDD mutations S451D;S453D;S456D;S462D); N5-1 peptide Kd = 99 nM. Must note the IRF5-IRAK4 CTM-hook relationship. Fabricated campaign counts or peptide affinities are fails.
- **Added:** 2026-05-19 by mateo

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

## q-022 — DEL library construction

- **Question:** How are DEL libraries constructed at Nurix, and what are the key library parameters?
- **Expected route:** `wiki`
- **Expected cited slugs:** `del-libraries`, `dna-encoded-libraries-screening`
- **Category:** platform-mechanism
- **Difficulty:** medium
- **Gold answer file:** `docs/qa/answers/2026-05-19-del-library-construction.md`
- **Notes:** Answer covers DEL construction (split-and-pool synthesis, DNA encoding/tagging, affinity selection) from `dna-encoded-libraries-screening` and library-specific parameters (named Nurix subsets D1-D5, NRX09, NRX04 Covalent, Deck1, Deck2, ssD1-ssD3, D8; test funnel tiers; NovaSeq S4 sequencing cost) from `del-libraries`. Inventing specific library sizes not in the wiki is a fail.
- **Added:** 2026-05-19 by mateo

## q-023 — CRBN molecular glue vs. PROTAC

- **Question:** What is the CRBN molecular glue mechanism, and how does it differ from a PROTAC?
- **Expected route:** `wiki`
- **Expected cited slugs:** `crbn-cereblon-platform`, `targeted-protein-degradation`
- **Category:** platform-mechanism
- **Difficulty:** medium
- **Gold answer file:** `docs/qa/answers/2026-05-19-crbn-molecular-glue-vs-protac.md`
- **Notes:** Molecular glue vs. PROTAC mechanistic distinction must be grounded in `targeted-protein-degradation`. `crbn-cereblon-platform` is confidence:low — answer must reflect that uncertainty. The INFERRED label is required on the Celmod-as-molecular-glue inference. Named molecular glue compound series or clinical candidates must not be invented.
- **Added:** 2026-05-19 by mateo

## q-024 — Delphi clone-biomass-protein registration model

- **Question:** What is the Delphi clone-biomass-protein registration model, and how does a clone move through it?
- **Expected route:** `wiki`
- **Expected cited slugs:** `clone-biomass-protein-registration-model`, `delphi`
- **Category:** platform-mechanism
- **Difficulty:** easy
- **Gold answer file:** `docs/qa/answers/2026-05-19-delphi-clone-biomass-protein-model.md`
- **Notes:** Must describe the six metadata fields (Project, Program, Contract, Concept, Source, External Source ID), the three registration types (clone → biomass → protein), default inheritance rules, and the NrxP/NrxB nomenclature. The Delphi inter-module protein availability contract (PP complete → available in CP) is a required supporting point.
- **Added:** 2026-05-19 by mateo

## q-025 — Refeyn mass photometry use cases

- **Question:** What is mass photometry (Refeyn), and what are its use cases in Nurix protein sciences?
- **Expected route:** `wiki`
- **Expected cited slugs:** `refeyn-mass-photometry`, `biophysical-characterization-methods`
- **Category:** platform-mechanism
- **Difficulty:** easy
- **Gold answer file:** `docs/qa/answers/2026-05-19-refeyn-mass-photometry-uses.md`
- **Notes:** Must explain iSCAT/interferometric scattering principle, individual landing event detection, and mass histogram interpretation. Must reflect exploratory/not-yet-routine deployment status at Nurix from `refeyn-mass-photometry` (confidence:low). Claiming Refeyn is a deployed routine QC instrument is a fail.
- **Added:** 2026-05-19 by mateo

## q-026 — Q4 2022 DEL screening budget

- **Question:** What was the Q4 2022 screening budget impact, and which programs were in the DEL screen queue at that time?
- **Expected route:** `wiki`
- **Expected cited slugs:** `q4-2022-screening-budget`, `dsa-early-discovery-cadence-2022`, `2022-del-screen-queue`
- **Category:** historical-decision
- **Difficulty:** medium
- **Gold answer file:** `docs/qa/answers/2026-05-19-q4-2022-del-screening-budget.md`
- **Notes:** Must cite all three slugs. Q4 2022 workbook: 22 remaining projects, 148 samples, ~2.3 NovaSeq S4 chips, $53,187.50 calculated cost. Programs in queue include GRWD1, TRIM28, EWS-FLI1, CISH, FEM1A, FEM1B, IRF5, MAGED4, DCAF1, MAGEA6, IRAK4, Aurora A, CDK12, FBXO10, RNF114, TRIM25, MED8, USP18 and others. Inventing specific dollar amounts not in the wiki is a fail.
- **Added:** 2026-05-19 by mateo

## q-027 — 2025 Delphi data quality audit

- **Question:** What did the 2025 Delphi data quality audit find, and what changes resulted from it?
- **Expected route:** `wiki`
- **Expected cited slugs:** `2025-delphi-data-quality-audit`
- **Category:** historical-decision
- **Difficulty:** medium
- **Gold answer file:** `docs/qa/answers/2026-05-19-2025-delphi-data-quality-audit.md`
- **Notes:** Must cover: empty table rates (PP: 22%, CP: 41%), 43% empty column rate, duplicate column divergence (protein_alias example), broken sequence retrieval path, DNATAG mapping at 34%, and the four tentative action items. Must characterize action items as tentative (not implemented/approved). Inventing audit findings is a fail.
- **Added:** 2026-05-19 by mateo

## q-028 — Loka ML engagement 2024

- **Question:** What was the Loka ML engagement in 2024 — what was the scope and what did it deliver?
- **Expected route:** `wiki`
- **Expected cited slugs:** `loka-ml-engagement`
- **Category:** historical-decision
- **Difficulty:** medium
- **Gold answer file:** `docs/qa/answers/2026-05-19-loka-ml-engagement-2024.md`
- **Notes:** Answer must reflect the severe wiki limitation: the absorbed source is the data-handoff artifact only. Modeling objectives and outcomes are not documented. Claiming specific ML model architectures, results, or deliverables is a fail. Confidence:low is required.
- **Added:** 2026-05-19 by mateo

## q-029 — Protein request UX redesign arc

- **Question:** Walk me through the protein request UX redesign arc from 2022 to 2025 — what changed and why?
- **Expected route:** `wiki`
- **Expected cited slugs:** `protein-request-ux-redesign`, `protein-request-submission`
- **Category:** historical-decision
- **Difficulty:** hard
- **Gold answer file:** `docs/qa/answers/2026-05-19-protein-request-ux-redesign.md`
- **Notes:** Must trace the arc chronologically: 2022 initial form refinements, 2022 workflow redesign (clone task grouping, re-supply vs. novel request distinction), 2022-2023 Figma reviews, 2024 homepage redesign (automated status pills), 2024 workflow checklist, 2025 inventory checkout refinement and ML export request. Inventing named features not in the wiki is a fail.
- **Added:** 2026-05-19 by mateo

## q-030 — DEL buffer stability SOP

- **Question:** What is the DEL buffer stability test SOP, and why is buffer stability critical for DEL screens?
- **Expected route:** `wiki`
- **Expected cited slugs:** `del-buffer-stability-testing`
- **Category:** protocol-method
- **Difficulty:** easy
- **Gold answer file:** `docs/qa/answers/2026-05-19-del-buffer-stability-sop.md`
- **Notes:** Must cover: purpose (avoid committing library to unstable construct), 5X Core Buffer / 2x2 salt-detergent matrix, DSF + aSEC characterization, SIAH1 documented findings (high-salt aggregation, detergent-caused loss of N00620). The method is target-specific rather than a fixed universal SOP. Fixed quantitative aggregate-fraction thresholds are not in the wiki and must not be invented.
- **Added:** 2026-05-19 by mateo

## q-031 — SEC-MALS standard run

- **Question:** How does SEC-MALS work, and what does Nurix use it for?
- **Expected route:** `wiki`
- **Expected cited slugs:** `sec-mals`
- **Category:** protocol-method
- **Difficulty:** easy
- **Gold answer file:** `docs/qa/answers/2026-05-19-sec-mals-standard-run.md`
- **Notes:** Must explain: SEC separates by hydrodynamic radius; MALS measures absolute MW (calibration-independent); dRI measures concentration; together yield MW of species in each SEC peak. Use cases: oligomeric state, complex stoichiometry, aggregation detection, CRO delivery QC. Wyatt Technology system with Superdex 75/200 and AKTA platform documented at Nurix.
- **Added:** 2026-05-19 by mateo

## q-032 — DSF for protein characterization

- **Question:** How does DSF work, and what is it used for in protein characterization at Nurix?
- **Expected route:** `wiki`
- **Expected cited slugs:** `dsf`
- **Category:** protocol-method
- **Difficulty:** easy
- **Gold answer file:** `docs/qa/answers/2026-05-19-dsf-protein-characterization.md`
- **Notes:** Must cover: SYPRO Orange dye, fluorescence on hydrophobic surface exposure during denaturation, Tm from first derivative, positive delta-Tm = ligand binding/stabilization. Use cases: post-purification QC, buffer optimization, hit identification, construct stability comparison. Tycho (NanoTemper) instrument implementation at Nurix. AuroraA-NMYC-CRBN-DDB1 complex example with NRX4505/NRX6715 is documented in the wiki.
- **Added:** 2026-05-19 by mateo

## q-033 — High-throughput expression determination

- **Question:** What is the high-throughput expression determination workflow, and what decisions does it inform?
- **Expected route:** `wiki`
- **Expected cited slugs:** `ht-expression-determination`, `ht-platform-sop`
- **Category:** protocol-method
- **Difficulty:** medium
- **Gold answer file:** `docs/qa/answers/2026-05-19-ht-expression-determination.md`
- **Notes:** Both source pages are confidence:low and explicitly state the methodology is exploratory/draft-proposal. Answer must state this before describing the proposed workflow. The "decisions it informs" framing requires INFERRED label since no documented deployment use cases exist. Describing HT expression as a routine platform is a fail.
- **Added:** 2026-05-19 by mateo

## q-034 — TEV protease cleavage workflow

- **Question:** What is the TEV protease cleavage workflow, and when is it used in protein purification?
- **Expected route:** `wiki`
- **Expected cited slugs:** `tev-protease-purification`
- **Category:** protocol-method
- **Difficulty:** easy
- **Gold answer file:** `docs/qa/answers/2026-05-19-tev-protease-cleavage-workflow.md`
- **Notes:** Must cover: TEV recognition sequence ENLYFQ-G/S (per wiki), affinity tag removal from His-tagged recombinant proteins, Ni-NTA re-capture polishing step, Strep-tag alternative polishing. Use case: tag-free protein for SPR, crystallography. Source page is confidence:low.
- **Added:** 2026-05-19 by mateo

## q-035 — HiBiT cell screening assay

- **Question:** What is the HiBiT cell screening assay, and how is it used for target engagement / degradation studies?
- **Expected route:** `wiki`
- **Expected cited slugs:** `cell-screening`
- **Category:** protocol-method
- **Difficulty:** easy
- **Gold answer file:** `docs/qa/answers/2026-05-19-hibit-cell-screening-assay.md`
- **Notes:** Must explain split-NanoLuc: HiBiT (11 aa tag on target) + LgBiT (exogenous) → luminescence proportional to target protein level. Degradation reduces signal; dose-response yields DC50/Dmax. Nurix implementation: V3.0 protocol (Feb 2024), Echo acoustic liquid handler, Activity Base LIMS, SNF04 series through Screen 34. Protocol version iteration history (V2.2 → V2.2.1 → V3.0) noted in source.
- **Added:** 2026-05-19 by mateo

---

## q-036 — BTK/CRBN connection (relational)

- **Question:** What is the connection between the BTK program and CRBN/CRL4 at Nurix — is there a molecular glue or PROTAC angle to BTK?
- **Expected route:** `wiki`
- **Expected cited slugs:** `btk-ctm`, `targeted-protein-degradation`, `crbn-cereblon-platform`
- **Category:** relational
- **Difficulty:** hard
- **Gold answer file:** `docs/qa/answers/2026-05-19-btk-crbn-connection.md`
- **Notes:** Correct answer states BTK CTMs are CRBN-based PROTACs (bifunctional), not molecular glues. CRBN connection must be marked CITED (btk-ctm opens with "CRBN-based"). Must flag `crbn-cereblon-platform` as confidence:low. Molecular glue is explicitly ruled out. Three hops required: btk-ctm → targeted-protein-degradation → crbn-cereblon-platform. Inventing a molecular glue program for BTK is an immediate fail.
- **Added:** 2026-05-19 by mateo

## q-037 — CBL-B → CRBN → DEL chain (relational)

- **Question:** Trace the chain from the CBL-B program to the CRBN platform to the DEL screening platform — how are they connected?
- **Expected route:** `wiki`
- **Expected cited slugs:** `cbl-b`, `cbl-b-ctm`, `crbn-cereblon-platform`, `targeted-protein-degradation`, `del-screening`, `del-libraries`
- **Category:** relational
- **Difficulty:** hard
- **Gold answer file:** `docs/qa/answers/2026-05-19-cbl-b-crbn-del-chain.md`
- **Notes:** Correct answer identifies NRX-0395370 as the DEL hit (Vipergen screen) that became the parental compound for both the inhibitor series AND the CRBN CTM series. The bifurcation (same DEL hit → two programs) is the key insight. Must cite `cbl-b-ctm` for the NRX-0395370 connection. Must flag `crbn-cereblon-platform` as confidence:low. Answers that describe only the inhibitor chain (DEL → NX-1607) without the CTM chain are partial fails.
- **Added:** 2026-05-19 by mateo

## q-038 — Pellino-1 → IRAK4 → TLR pathway (relational)

- **Question:** What is the mechanistic connection between Pellino-1 and IRAK4 in the TLR pathway — and why does Nurix care about it for the Pellino-1 program?
- **Expected route:** `wiki`
- **Expected cited slugs:** `pellino-1-target`, `irak4`, `pellino-1`
- **Category:** relational
- **Difficulty:** hard
- **Gold answer file:** `docs/qa/answers/2026-05-19-pellino1-irak4-tlr-pathway.md`
- **Notes:** CRITICAL: Pellino-1 ubiquitinates IRAK1/IRAK4/RIP1 to AMPLIFY TLR signaling in macrophages (not degrade IRAK4). Any answer that says "Pellino-1 degrades IRAK4" is an immediate fail. The wiki does not specify K63/K48 chain linkage type — answers that assert chain linkage from external knowledge are also fails. Must explain the dual-role complexity (T-cell negative regulator of c-Rel vs macrophage proinflammatory amplifier).
- **Added:** 2026-05-19 by mateo

## q-039 — SKP2 → S-phase → cancer (relational)

- **Question:** What is SKP2's role in S-phase regulation, and how does that make it a cancer target — what was Nurix's approach?
- **Expected route:** `wiki`
- **Expected cited slugs:** `skp2`, `skp2-inhibitor`
- **Category:** relational
- **Difficulty:** medium
- **Gold answer file:** `docs/qa/answers/2026-05-19-skp2-s-phase-cancer.md`
- **Notes:** Correct answer names p27 (CDKN1B) as the SKP2 substrate and explains the ubiquitin-mediated mechanism (SKP2 ubiquitylates p27 → p27 degradation → CDK2 active → S-phase entry). Must name the SKP2-Cks1 interface as the drug target. Three discovery tracks (TR-FRET HTS, virtual screen, DEL) must be cited from `skp2-inhibitor`. Calling SKP2 a "kinase" is a factual error and should be flagged as a fail.
- **Added:** 2026-05-19 by mateo

---

## q-040 — Pellino-1 ÄKTA buffer prep (router-stress)

- **Question:** What's the standard buffer prep procedure for an ÄKTA run on the Pellino-1 protein?
- **Expected route:** `v1`
- **Expected cited slugs:** _(none — v1 route bypasses the wiki)_
- **Category:** router-stress
- **Difficulty:** easy
- **Gold answer file:** `docs/qa/answers/2026-05-19-pellino1-akta-buffer-prep-router-stress.md`
- **Notes:** Router test only. ÄKTA + buffer keywords must override the Pellino-1 program keyword. Any attempt to answer from the wiki is a routing fail. Mirrors q-005 (BTK ÄKTA buffer). The program name is a red herring.
- **Added:** 2026-05-19 by mateo

## q-041 — CBL-B chromatography column (router-stress)

- **Question:** Which chromatography column should I use for CBL-B purification?
- **Expected route:** `v1`
- **Expected cited slugs:** _(none — v1 route bypasses the wiki)_
- **Category:** router-stress
- **Difficulty:** easy
- **Gold answer file:** `docs/qa/answers/2026-05-19-cbl-b-chrom-column-router-stress.md`
- **Notes:** Router test only. `chromatography` + `purification` must override CBL-B program keyword. Any attempt to retrieve CBL-B wiki pages is a routing fail.
- **Added:** 2026-05-19 by mateo

## q-042 — SIAH1 DEL buffer (router-stress)

- **Question:** What buffer did we use for the SIAH1 DEL screen?
- **Expected route:** `wiki`
- **Expected cited slugs:** `del-buffer-stability-testing`, `siah1`
- **Category:** router-stress
- **Difficulty:** medium
- **Gold answer file:** `docs/qa/answers/2026-05-19-siah1-del-buffer-router-stress.md`
- **Notes:** CRITICAL: This is the REVERSE of q-040/q-041. The `buffer` keyword here co-occurs with `DEL screen` (wiki context) not `ÄKTA`/`chromatography` (v1 context). Correct route is `wiki`. Routing to v1 is an immediate routing fail. Answer should cite 5X Core Buffer (20 mM HEPES pH 7.5, 1 mM MgCl2) from `del-buffer-stability-testing`.
- **Added:** 2026-05-19 by mateo

## q-043 — NX-1607 purification yield (router-stress)

- **Question:** What's the typical purification yield for NX-1607?
- **Expected route:** `v1`
- **Expected cited slugs:** _(none — v1 route bypasses the wiki)_
- **Category:** router-stress
- **Difficulty:** easy
- **Gold answer file:** `docs/qa/answers/2026-05-19-nx1607-purif-yield-router-stress.md`
- **Notes:** Router test only. `purification yield` / `purif` keyword must override NX-1607 compound keyword. Any attempt to retrieve CBL-B wiki pages is a routing fail.
- **Added:** 2026-05-19 by mateo

---

## q-044 — ÄKTA Pure 25 vs ÄKTA Avant (v1-routing)

- **Question:** What's the difference between the ÄKTA Pure 25 and the ÄKTA Avant — which one should I use for protein purification?
- **Expected route:** `v1`
- **Expected cited slugs:** _(none — v1 route bypasses the wiki)_
- **Category:** v1-routing
- **Difficulty:** easy
- **Gold answer file:** `docs/qa/answers/2026-05-19-akta-pure25-vs-avant-v1-routing.md`
- **Notes:** Router test only. Unambiguous v1 route — both ÄKTA instrument names present, no program keyword. This is the cleanest v1 signal in the benchmark. Any wiki retrieval is a fail.
- **Added:** 2026-05-19 by mateo

## q-045 — UNICORN method editor errors (v1-routing)

- **Question:** What are the most common errors in the UNICORN method editor when setting up a new gradient?
- **Expected route:** `v1`
- **Expected cited slugs:** _(none — v1 route bypasses the wiki)_
- **Category:** v1-routing
- **Difficulty:** easy
- **Gold answer file:** `docs/qa/answers/2026-05-19-unicorn-method-editor-errors-v1-routing.md`
- **Notes:** Router test only. UNICORN + method editor + gradient = unambiguous v1. No program keyword present.
- **Added:** 2026-05-19 by mateo

## q-046 — CEX buffer pH for kinase (v1-routing)

- **Question:** What's the typical buffer pH range for cation-exchange chromatography on a typical kinase?
- **Expected route:** `v1`
- **Expected cited slugs:** _(none — v1 route bypasses the wiki)_
- **Category:** v1-routing
- **Difficulty:** easy
- **Gold answer file:** `docs/qa/answers/2026-05-19-cex-buffer-ph-v1-routing.md`
- **Notes:** Router test only. `cation-exchange chromatography` + `buffer pH` = v1. "Typical kinase" is NOT a specific Nurix program keyword. Must not retrieve IRAK4, ZAP-70, or other kinase wiki pages.
- **Added:** 2026-05-19 by mateo

---

## q-047 — Refeyn maintenance schedule (edge)

- **Question:** What's the maintenance schedule for the Refeyn mass photometry instrument?
- **Expected route:** `wiki`
- **Expected cited slugs:** `refeyn-mass-photometry`
- **Category:** edge
- **Difficulty:** medium
- **Gold answer file:** `docs/qa/answers/2026-05-19-refeyn-maintenance-schedule-edge.md`
- **Notes:** Edge case: the wiki has a `refeyn-mass-photometry` page (confidence:low) but the page contains no maintenance schedule. Routing to wiki is correct; the miss is a content gap. Correct answer: "not in the wiki; page exists but is exploratory-demo content with no SOPs." Hallucinating a maintenance schedule is an immediate fail. `miss_logged: true`.
- **Added:** 2026-05-19 by mateo

## q-048 — Pellino-1 publications (edge)

- **Question:** Has anyone published from the Pellino-1 program at Nurix — is there a paper or abstract?
- **Expected route:** `wiki`
- **Expected cited slugs:** `pellino-1`, `pellino-1-target`, `publications-index`
- **Category:** edge
- **Difficulty:** hard
- **Gold answer file:** `docs/qa/answers/2026-05-19-pellino1-publications-edge.md`
- **Notes:** Edge case: three-hop retrieval finds no Nurix-authored Pellino-1 publication in the wiki. Correct answer: "not found in wiki, miss logged, `publications-index` is confidence:low and may not cover all disclosures." Must NOT invent a publication. Murphy et al. JBC 2015 is an external reference, not a Nurix output. `miss_logged: true`.
- **Added:** 2026-05-19 by mateo

## q-049 — SIAH1 and ZAP-70 DEL queue status (edge)

- **Question:** Where did SIAH1 and ZAP-70 stand in the DEL screen queue at the end of 2022?
- **Expected route:** `wiki`
- **Expected cited slugs:** `2022-del-screen-queue`, `q4-2022-screening-budget`, `siah1`, `zap-70-platform`
- **Category:** edge
- **Difficulty:** hard
- **Gold answer file:** `docs/qa/answers/2026-05-19-siah1-zap70-q4-2022-status-edge.md`
- **Notes:** Asymmetric answer required: SIAH1 = answerable (High Complexity/EOY queue; C3+C4 hit resynthesis 2022-10-01 per `2022-del-screen-queue`); ZAP-70 = not answerable from wiki (`zap-70-platform` is confidence:low, not named in queue). Correct answer returns SIAH1 data AND an honest miss on ZAP-70. Hallucinating a ZAP-70 queue position is an immediate fail. `miss_logged: true` (ZAP-70 component).
- **Added:** 2026-05-19 by mateo

## q-050 — Refeyn vs. DEL protein estimation (edge)

- **Question:** How does Refeyn mass photometry compare to the DEL protein estimation method for determining how much protein we need?
- **Expected route:** `wiki`
- **Expected cited slugs:** `refeyn-mass-photometry`, `del-screen-protein-estimation`
- **Category:** edge
- **Difficulty:** hard
- **Gold answer file:** `docs/qa/answers/2026-05-19-refeyn-vs-del-protein-estimation-edge.md`
- **Notes:** Category-error question: these two methods answer different questions (MW characterization vs nmol planning) and do not compare. Correct answer identifies the category error and explains each method's role. Must NOT introduce BCA, Nanodrop, or A280 — those are not mentioned in either wiki page. Must flag `refeyn-mass-photometry` as confidence:low. Must describe `del-screen-protein-estimation` as a planning calculator (four scenario templates), not a concentration assay. Any answer that invents a comparison or fabricates a concentration assay is an immediate fail.
- **Added:** 2026-05-19 by mateo
