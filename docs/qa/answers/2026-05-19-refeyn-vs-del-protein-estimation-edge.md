---
question_id: q-050
question: "How does Refeyn mass photometry compare to the DEL protein estimation method for determining how much protein we need?"
asked_by: mateo
asked_date: 2026-05-19
session_date: 2026-05-19
session_id: cowork-2026-05-19-050
route: wiki
route_decided_by: regex
candidate_slugs:
  - refeyn-mass-photometry
  - del-screen-protein-estimation
hops_followed:
  - refeyn-mass-photometry
  - del-screen-protein-estimation
raw_fallback_used: false
raw_entries_read: []
miss_logged: false
confidence: medium
filed_back: false
filed_back_path: null
schema_version: 0.1.0
---

## Answer

**These two methods answer fundamentally different questions and do not directly compare.** The question contains a category error: Refeyn mass photometry determines what a protein IS (its molecular weight and oligomeric state); the DEL protein estimation method determines how much of the protein you NEED (nanomoles per campaign). They operate at different stages of the protein science workflow and are not substitutable. INFERRED from cross-reading `refeyn-mass-photometry` and `del-screen-protein-estimation`.

---

**[[refeyn-mass-photometry|REFEYN Mass Photometry]] — what it does.** CITED from `refeyn-mass-photometry` (confidence:low).

Refeyn mass photometry is a label-free optical technique for measuring protein molecular weight and oligomeric state. It tells you the mass of individual protein molecules by detecting optical contrast changes as proteins bind to a coverslip. Output: a mass distribution histogram showing peaks corresponding to monomers, dimers, or other species. Applications: molecular-weight verification, oligomeric-state determination, binding studies. It answers: "What is this protein's mass? Is it monomeric or dimeric? Are there multiple species?" It does NOT answer: "How many nanomoles do I need for my DEL campaign?"

**[[del-screen-protein-estimation|DEL Screen Protein Estimation]] — what it does.** CITED from `del-screen-protein-estimation`.

The DEL protein estimation method is a pre-campaign planning calculator. It converts a campaign's shape (number of protein domains, supplement requirements, round count) into a per-campaign nanomole requirement. The reference is a password-protected Excel workbook ("Average screen plan for protein estimates 20220412 wks") with four scenario templates:

- Scenario 1: two non-overlapping domains, apo, ~5 nmol per domain
- Scenario 2: full-length construct + one domain, apo
- Scenario 3: two domains, supplement-bound
- Scenario 4: full-length construct + one domain, supplement-bound

The scenarios are AVERAGES based on 250 pmol of immobilized target per selection, 3 rounds per campaign, bead-only and counter-target controls. Output: a nanomole number that drives protein production scheduling. It answers: "How much protein do I need to produce before committing to this campaign?" It does NOT characterize the protein's identity or oligomeric state.

**Where each fits in the workflow.** INFERRED from cross-reading the two pages:

1. **Protein QC (Refeyn's role):** After protein production, Refeyn could verify that the protein is the correct MW and in the expected oligomeric state (monomer vs dimer). This is a QUALITY CONTROL step before campaign commit.
2. **Campaign planning (DEL estimation's role):** Before protein production begins, the protein estimation workbook tells the team how many nanomoles to produce. This is a PLANNING step.

These are sequential, not competing: planning → production → QC → campaign. Refeyn answers a QC question; the estimation workbook answers a planning question. There is no scenario in which you would choose one over the other for "determining how much protein you need" — the protein estimation workbook is the method for that; Refeyn does not address it.

**Caveat on Refeyn.** The `refeyn-mass-photometry` page is confidence:low and describes the REFEYN as "exploratory / demo stage" at Nurix with "no routine SOPs in place." Integration into routine protein QC had not yet occurred as of the last update to that page. Whether Refeyn has since been deployed in the DEL program protein QC workflow is not stated in the wiki.

## Sources

- `refeyn-mass-photometry` — REFEYN instrument description; mass photometry principle; Nurix demo status; confidence:low
- `del-screen-protein-estimation` — planning calculator; four scenario templates; nanomole requirement computation; workbook structure

## Confidence

Medium overall. The distinction between the two methods (MW characterization vs nmol planning) is CITED from both pages and is clean. The workflow sequencing claim (QC → planning as sequential, not competing) is INFERRED from cross-reading. The Refeyn confidence:low flag propagates uncertainty into any claims about its specific role in the DEL workflow.

No claim is made about BCA, Nanodrop, A280, or any other concentration assay — those are not mentioned in either wiki page and would constitute fabricated external knowledge.

## Follow-ups

1. Does the `del-screen-protein-estimation` workbook or any downstream absorb document use protein concentration data from a specific assay (BCA, Nanodrop, A280) to verify that the nanomole target has been met?
2. Has the Refeyn been formally integrated into the DEL target protein QC workflow since the demo stage? If so, is there a newer wiki page or raw source that documents this?
3. Is there a protein QC checklist for DEL campaign commit that specifies which characterization methods are required (e.g., SEC, DSF, mass photometry)?

## Filed back?

No. The answer synthesizes two existing wiki pages and identifies the category error in the question. The synthesis does not constitute a novel wiki entity.

## Session notes

Edge case designed to catch a category error. The question asks to "compare" two methods that operate at different workflow stages and answer different questions. A correct system returns the disambiguation (QC vs planning) and does not fabricate a comparison that doesn't exist. The failure mode to watch for: a system that invents a comparison — e.g., "Refeyn is more accurate than BCA for measuring protein concentration, which is then used in the DEL estimation workbook" — would be fabricating both the BCA comparison and the integration between these two tools. Neither wiki page mentions BCA, Nanodrop, or A280. The benchmark note for q-050 should flag any answer that introduces concentration assays not present in the wiki as an immediate fail.
