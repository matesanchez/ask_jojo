# Phase 2 Absorb Queue — Protein Sciences

**Governing ADR:** `docs/ADR/0010-compile-via-cowork-while-api-pending.md`
**Prompt:** `docs/compile/compile-prompt.md`
**Target repo:** `ask_jojo_wiki/`
**Source repo:** `ask_jojo_raw/` (sharepoint + onedrive + publicdrive + drive)

This file is the batch tracker for the Phase 2 Cowork-compile loop. Each `## Batch N` block is an atomic unit of work — one Cowork session claims the first unticked batch, absorbs every entry in it, and commits once. Sessions do not straddle batches. Entries that can't be absorbed (malformed, missing, over-redacted) get ticked anyway with a skip note, so the queue stays a truthful "what have we looked at" index, not a "what have we absorbed successfully" index.

Entry IDs below are the keys from `ask_jojo_raw/manifest.json` — equivalently, the stem of the `.md` file under `ask_jojo_raw/<connector>/`. If an entry moved corpora between batches (rare, but happens if a SharePoint file surfaces in OneDrive too), the manifest's `supersedes` chain is the tiebreaker; absorb the current ID.

## How to add a batch

Append a `## Batch N` heading at the bottom of the file. Ten entries is the target; fewer is fine for the trailing batch, more is too many to keep attention on in one session. Pick entries that *cluster topically* — a session that touches ten DEL-screening files converges on a few strong program/method/decision pages; a session that touches ten unrelated files sprawls into twenty weak pages. Optimize for wiki coherence, not for chronological order in the corpus.

The first batch below is seeded with ten SharePoint entries from the Protein Sciences → DEL screening cluster, chosen so the session's first pages are programs / platforms / decisions in well-defined directories. Subsequent batches can widen into protocols, equipment, targets, etc.

---

## Batch 1 — DEL screening kickoff (Protein Sciences)

**Theme:** DEL screen planning and goals, 2022–2025. Expected outputs: a `programs/` page or two for DEL screening programs, one or two `platforms/` pages for DEL screening infrastructure, a handful of `decisions/` pages capturing queue / budget / planning calls, possibly a `targets/` page for SIAH1, possibly a `methods/` page for buffer stability testing. Exact output shape is a session call per the absorb loop in `schema/CLAUDE.md`.

**Connector:** sharepoint
**Access level:** all_fte

- [x] sharepoint_protein-science-documents-del-ps-goals-2025-research-goals-final-docx
- [x] sharepoint_protein-science-documents-del-screen-plans-del-protein-screen-2022-pptx
- [x] sharepoint_protein-science-documents-del-screen-plans-del-queue-2022-pptx
- [x] sharepoint_protein-science-documents-del-screen-plans-03232022-del-screen-plan-proteins-xlsx
- [x] sharepoint_protein-science-documents-del-buffer-screen-q42022-dsaprojects-remainingscreensandbudget-xlsx
- [x] sharepoint_protein-science-documents-del-buffer-screen-siah1-nbvc-n00619-1a-n00620-1-buffer-stability-testing-pptx
- [x] sharepoint_protein-science-documents-del-screen-plans-average-screen-plan-for-protein-estimates-20220412-wks-xlsx
- [x] sharepoint_protein-science-documents-del-screen-plans-ds-projects-jss-xlsx
- [x] sharepoint_protein-science-documents-del-screen-plans-dsa-projects-xlsx
- [x] sharepoint_protein-science-documents-del-screen-plans-dsa-update---early-discovery-group-meeting-20220818-pptx

---

## Batch 2 — Delphi product overview

**Theme:** Delphi is the Nurix protein-production / campaign-planning software stack that roughly 90% of the Protein Sciences SharePoint corpus is about. Before touching release-specific UAT material, ground a small set of overview pages: what the system is, how it's structured, the metadata model behind clone / biomass / protein registration, and the current-state schematic. Expected outputs: a `platforms/delphi.md` anchor page, a `concepts/` page or two on the clone-biomass-protein data model, possibly a `protocols/` entry for the Nurix metadata SOP. Every later Delphi batch cites back to these pages, so their quality sets the ceiling for the rest.

**Connector:** sharepoint
**Access level:** all_fte

- [x] sharepoint_protein-science-documents-delphi-campaign-planning---part-i-pdf
- [x] sharepoint_protein-science-documents-delphi-campaign-planning---part-ii-pdf
- [x] sharepoint_protein-science-documents-delphi-campaign-planning-release-notes-prod-v3-0-0-1-pdf
- [x] sharepoint_protein-science-documents-delphi-metadata-and-registration-of-clones-biomasses-and-proteins-pptx
- [x] sharepoint_protein-science-documents-delphi-metadata-and-registration-of-clones-biomasses-and-proteins-version2-pptx
- [x] sharepoint_protein-science-documents-delphi-nurix-metadata-sop-docx
- [x] sharepoint_protein-science-documents-delphi-20240202-delphi-workflow-schematic-el-pptx
- [x] sharepoint_protein-science-documents-delphi-20240216-delphi-schematic-pdf
- [x] sharepoint_protein-science-documents-delphi-20240228-delphi-schematic-pdf
- [x] sharepoint_protein-science-documents-delphi-20250702-protein-science-delphi-eval-from-herman-pptx

---

## Batch 3 — Delphi ACS initial UAT cycle (2020-2021)

**Theme:** The Advanced Construct Support (ACS) epic was Delphi's first major scope expansion — a multi-part UAT plan landed on 2021-05-27 across campaign-planning, protein-production requests, clone tasks, target forms, and sequence/structure. The 2020-10-19 pitch and the 2020-10/11 financials set the scope that the UAT was testing against. A coherent "Delphi ACS v1" story lives in these ten files. Expected outputs: a `decisions/` page for the ACS scope decision, one `projects/` page for the ACS rollout, and citations that the later ACS 2024/2025/2026 batches will anchor against.

**Connector:** sharepoint
**Access level:** all_fte

- [x] sharepoint_protein-science-documents-delphi-10-19-2020-advanced-construct-support-presentation-pptx
- [x] sharepoint_protein-science-documents-delphi-02-campaign-planning-uat-plan---project-landing-target-review-jose-docx
- [x] sharepoint_protein-science-documents-delphi-03-campaign-planning-uat-plan---target-seq-structure-jose-review-docx
- [x] sharepoint_protein-science-documents-delphi-04-campaign-planning-uat-plan---target-forms-jose-docx
- [x] sharepoint_protein-science-documents-delphi-delphi-uat-reviews-05-27-2021-uat-reviews-01-advanced-construct-support-uat-plan-campaign-planning-milestone-2-changes-eboni-a-docx
- [x] sharepoint_protein-science-documents-delphi-delphi-uat-reviews-05-27-2021-uat-reviews-01-advanced-construct-support-uat-plan-protein-production-requests-eboni-a-docx
- [x] sharepoint_protein-science-documents-delphi-delphi-uat-reviews-05-27-2021-uat-reviews-02-advanced-construct-support-uat-plan-clone-tasks-eboni-a-docx
- [x] sharepoint_protein-science-documents-delphi-delphi-uat-reviews-05-27-2021-uat-reviews-02-advanced-construct-support-uat-plan-target-form-jose-docx
- [x] sharepoint_protein-science-documents-delphi-delphi-uat-reviews-05-27-2021-uat-reviews-03-advanced-construct-support-uat-plan-sequence-and-structure-jose-pdf
- [x] sharepoint_protein-science-documents-delphi-financials-acs-combined-proposal-presentation-pptx

---

## Batch 4 — Delphi ACS2024.1 release cycle

**Theme:** One full release cycle, early 2025 calendar: the ACS2024.1 release notes (three companion docs — permissions, mutation menus, overall deck) plus the UAT testing that certified it (six DS-ticket test docs spanning 2024-11-20 through 2025-01-02). Coherent "what shipped + how it was tested" story. Expected outputs: a `decisions/` page for the ACS2024.1 release scope, anchors into a `projects/` page on the UAT process, and citations that feed the steady-state Delphi platform page from Batch 2.

**Connector:** sharepoint
**Access level:** all_fte

- [x] sharepoint_protein-science-documents-delphi-release-notes-acs2024-1-release-20250108-acs2024-1-cppermissions-docx
- [x] sharepoint_protein-science-documents-delphi-release-notes-acs2024-1-release-20250108-acs2024-1-mutationmenus-docx
- [x] sharepoint_protein-science-documents-delphi-release-notes-acs2024-1-release-20250108-acs2024-1-pptx
- [x] sharepoint_protein-science-documents-delphi-release-notes-acs2024-oct-release-20241015-new-delphi-releases-pptx
- [x] sharepoint_protein-science-documents-delphi-delphi-uat-reviews-acs2024-1-uat-testing-20241120-ds-1291-docx
- [x] sharepoint_protein-science-documents-delphi-delphi-uat-reviews-acs2024-1-uat-testing-20241220-ds-1124-docx
- [x] sharepoint_protein-science-documents-delphi-delphi-uat-reviews-acs2024-1-uat-testing-20241220-ds-1297-docx
- [x] sharepoint_protein-science-documents-delphi-delphi-uat-reviews-acs2024-1-uat-testing-20241220-ds-1361-docx
- [x] sharepoint_protein-science-documents-delphi-delphi-uat-reviews-acs2024-1-uat-testing-20241220-ds-725-docx
- [x] sharepoint_protein-science-documents-delphi-delphi-uat-reviews-acs2024-1-uat-testing-20250102-ds-399-docx

---

## Batch 5 — Delphi ACS2025.1 / ACS2025.2 release cycles

**Theme:** The next two Delphi release trains (2025-03 and 2025-04). Release notes for each plus representative UAT testing docs across DS-1283, DS-1290, DS-1300, DS-1366/1398, DS-1435, DS-1392, DS-1423, DS-1476. Follows the same pattern as Batch 4 — one `decisions/` page per release cycle, anchored to the ACS projects page. The post-2025.2 UAT snapshots (2026-02/03/04 series) are intentionally not in this batch; batch them with the ACS2026 release notes when those show up in higher resolution.

**Connector:** sharepoint
**Access level:** all_fte

- [x] sharepoint_protein-science-documents-delphi-release-notes-acs2025-1-release-20250320-delphi-acs2025-1-release-notes-pptx
- [x] sharepoint_protein-science-documents-delphi-release-notes-acs2025-2-release-20250422-delphi-acs2025-2-release-notes-pptx
- [x] sharepoint_protein-science-documents-delphi-delphi-uat-reviews-acs2025-1-uat-testing-ds-1283-20250220-ds-1283-docx
- [x] sharepoint_protein-science-documents-delphi-delphi-uat-reviews-acs2025-1-uat-testing-ds-1290-20250220-ds-1290-docx
- [x] sharepoint_protein-science-documents-delphi-delphi-uat-reviews-acs2025-1-uat-testing-ds-1300-20250218-uat-testing-ds-1300-docx
- [x] sharepoint_protein-science-documents-delphi-delphi-uat-reviews-acs2025-1-uat-testing-ds-1366-ds-1398-20250218-ds-1366-ds-1398-uat-testing-results-docx
- [x] sharepoint_protein-science-documents-delphi-delphi-uat-reviews-acs2025-1-uat-testing-ds-1435-ds-1435-uat-testing-20250225-docx
- [x] sharepoint_protein-science-documents-delphi-delphi-uat-reviews-acs2025-2-uat-testing-20250416-ds-1392-docx
- [x] sharepoint_protein-science-documents-delphi-delphi-uat-reviews-acs2025-2-uat-testing-20250416-ds-1423-docx
- [x] sharepoint_protein-science-documents-delphi-delphi-uat-reviews-acs2025-2-uat-testing-20250418-ds-1476-docx

---

## Batch 6 — Delphi DS841 lascexprtask mandatory-fields rollout (Nov 2023)

**Theme:** One concentrated release event — the DS841 change that added mandatory fields to the large-scale expression task (lascexprtask) in November 2023. Multiple before/after snapshots (flasks, lset, clone-infections tables) captured what changed and why. This is a natural "case-study" batch: the ten files together tell one story that should collapse into a single `decisions/` page (with embedded before/after tables) rather than ten separate stubs.

**Connector:** sharepoint
**Access level:** all_fte

- [x] sharepoint_protein-science-documents-delphi-20231031-ds841-changes-xlsx
- [x] sharepoint_protein-science-documents-delphi-20231108-ds841-changes-xlsx
- [x] sharepoint_protein-science-documents-delphi-copy-of-20231108-ds841-changes-xlsx
- [x] sharepoint_protein-science-documents-delphi-20231117-ds841-lascexprtask-mandatory-fields-20231117-ds841-lascexprtaskchanges-list-xlsx
- [x] sharepoint_protein-science-documents-delphi-20231117-ds841-lascexprtask-mandatory-fields-flasks-updated-xlsx
- [x] sharepoint_protein-science-documents-delphi-20231117-ds841-lascexprtask-mandatory-fields-flasks-updated-after-rollout-xlsx
- [x] sharepoint_protein-science-documents-delphi-20231117-ds841-lascexprtask-mandatory-fields-lset-clone-infections-updated-xlsx
- [x] sharepoint_protein-science-documents-delphi-20231117-ds841-lascexprtask-mandatory-fields-lset-clone-infections-updated-after-rollout-xlsx
- [x] sharepoint_protein-science-documents-delphi-20231117-ds841-lascexprtask-mandatory-fields-lset-updated-before-rollout-xlsx
- [x] sharepoint_protein-science-documents-delphi-20231117-ds841-lascexprtask-mandatory-fields-lset-updated-after-rollout-xlsx

---

## Batch 7 — Delphi SSEPT (small-scale expression task) feature evolution

**Theme:** The SSEPT feature — the small-scale expression task workflow inside Delphi — has its own multi-year design arc: the MOI (multiplicity of infection) redesign iterations in early 2024, the Excel table import/export mechanism, the results-import pipeline, and the running `sseptimporttable` snapshots that captured the schema across 2024-12 through 2025-06. Expected outputs: a `methods/` or `protocols/` page for SSEPT itself (with sub-sections on the import/export contracts) and a `decisions/` page for the MOI redesign choice.

**Connector:** sharepoint
**Access level:** all_fte

- [x] sharepoint_protein-science-documents-delphi-20240112-ssept-moi-redesign-pptx
- [x] sharepoint_protein-science-documents-delphi-20240222-ssept-moi-redesign-pptx
- [x] sharepoint_protein-science-documents-delphi-20240229-ssept-moi-redesign-pptx
- [x] sharepoint_protein-science-documents-delphi-20240311-moi-section-pptx
- [x] sharepoint_protein-science-documents-delphi-20240702-ssept-exceltable-export-import-xlsx
- [x] sharepoint_protein-science-documents-delphi-20241203-delphi-sseptimporttable-xlsx
- [x] sharepoint_protein-science-documents-delphi-20241203-ssept-resultsimport-pptx
- [x] sharepoint_protein-science-documents-delphi-20250114-delphi-sseptimporttable-xlsx
- [x] sharepoint_protein-science-documents-delphi-20250114-ssept-resultsimport-pptx
- [x] sharepoint_protein-science-documents-delphi-20250625-delphi-sseptimporttable-updated-xlsx

---

## Batch 8 — Delphi clone / GenScript / Dotmatics integration

**Theme:** The clone-side data flow: how cloned constructs get from GenScript (external DNA vendor) into Delphi, how metadata is tagged (fusion tags, cleavage linkers), how bulk clone imports work, and how Delphi reconciles against Dotmatics inventory. Cohesive "external-systems integration" story. Expected outputs: a `methods/` or `protocols/` page on the GenScript-to-Delphi workflow and a `concepts/` page on protein tagging / cleavage-linker conventions.

**Connector:** sharepoint
**Access level:** all_fte

- [x] sharepoint_protein-science-documents-delphi-clone-information-to-be-uploaded-from-genscript-pptx
- [x] sharepoint_protein-science-documents-delphi-com-workflow-tutorial-genscript-usages-pptx
- [x] sharepoint_protein-science-documents-delphi-com-workflow-tutorial-genscript-usages-2-pptx
- [x] sharepoint_protein-science-documents-delphi-clone-order-management-clone-order-management-release-notes-v1-1-0-pdf
- [x] sharepoint_protein-science-documents-delphi-20231120-ds889-cloneidduplications-xlsx
- [x] sharepoint_protein-science-documents-delphi-20230620-dotmaticsinventory-missingdescriptions-xlsx
- [x] sharepoint_protein-science-documents-delphi-20250408-clone-import-xlsx
- [x] sharepoint_protein-science-documents-delphi-20250604-delphi-clone-bulk-import-example-xlsx
- [x] sharepoint_protein-science-documents-delphi-20250604-delphi-clone-bulk-import-pptx
- [x] sharepoint_protein-science-documents-delphi-tags-fusion-cleavage-linkers-xlsx

---

## Batch 9 — Delphi project / target harmonization (Chemcart ↔ ChemReg ↔ DNAtag)

**Theme:** A running effort to reconcile project and target naming across Delphi, Chemcart, ChemReg, and the DNAtag system. Spans 2022 through late 2023. Expected outputs: a `decisions/` page on the naming-harmonization decision (why the cross-system mapping was needed, what convention was adopted), and possibly one `concepts/` page on the project-vs-target distinction if the sources warrant it.

**Connector:** sharepoint
**Access level:** all_fte

- [x] sharepoint_protein-science-documents-delphi-project-target-harmonization-09102023-chemcart-project-and-targets-xlsx
- [x] sharepoint_protein-science-documents-delphi-project-target-harmonization-20220301-delphi-project-target-name-harmonization-updated-xlsx
- [x] sharepoint_protein-science-documents-delphi-project-target-harmonization-20230910-delphi-project-target-name-harmonization-updated-xlsx
- [x] sharepoint_protein-science-documents-delphi-project-target-harmonization-chemreg-project-target-contract-data-xlsx
- [x] sharepoint_protein-science-documents-delphi-project-target-harmonization-chemreg-project-xlsx
- [x] sharepoint_protein-science-documents-delphi-project-target-harmonization-delph-dnatag-project-target-list-20230511-jose-annotated09102023-xlsx
- [x] sharepoint_protein-science-documents-delphi-project-target-harmonization-delph-dnatag-project-target-list-20230511-xlsx
- [x] sharepoint_protein-science-documents-delphi-project-target-harmonization-delph-dnatag-project-target-list-20230912-xlsx
- [x] sharepoint_protein-science-documents-delphi-20240924-chad-del-protein-info-export-from-delphi-example-xlsx
- [x] sharepoint_protein-science-documents-delphi-vectors-not-on-genscript-page-xlsx

---

## Batch 10 — Delphi financials and SOW history

**Theme:** The budget / SOW trail from Delphi's ACS proposal through the Q4 revised project budgets and the maintenance-budget snapshot. Money-flow is distinct enough from UAT mechanics that it deserves its own `decisions/` page rather than being scattered into the ACS batch's pages.

**Connector:** sharepoint
**Access level:** all_fte

- [x] sharepoint_protein-science-documents-delphi-financials-2020-10-20-advanced-construct-support-estimation-financials-xlsx
- [x] sharepoint_protein-science-documents-delphi-financials-2020-11-06-advanced-construct-support-estimation-financials-prioritized-xlsx
- [x] sharepoint_protein-science-documents-delphi-financials-2020-11-06-advanced-construct-support-estimation-prioritized-xlsx
- [x] sharepoint_protein-science-documents-delphi-financials-campaign-planning-2021-sow---financials-jose-xlsx
- [x] sharepoint_protein-science-documents-delphi-financials-campaign-planning-2021-sow---financials-xlsx
- [x] sharepoint_protein-science-documents-delphi-financials-delphi-maintenance-budget-xlsx
- [x] sharepoint_protein-science-documents-delphi-financials-revised-nurix-project-budgets---q4-xlsx
- [x] sharepoint_protein-science-documents-delphi-financials-revised-nurix-project-budgets---q4--updated-xlsx
- [x] sharepoint_protein-science-documents-delphi-campaign-planning-uat-feedback---estimation-sheet---mon-nov-23-2020-pdf
- [x] sharepoint_protein-science-documents-delphi-campaign-planning-uat-feedback-financial-sow-thu-feb-25-2021-pdf

---

## Batch 11 — DSA early-discovery group meetings (2022) + DEL tech-dev

**Theme:** Closes out the non-Delphi DEL screening story started by Batch 1. The 2022 DSA (Discovery Screening Assay?) updates to the Early Discovery group are a continuous chronological thread; plus the all-DEL tech-dev meeting and the Stat6 DSP table (a specific target-aware DSA artifact). Expected outputs: one or two `decisions/` pages on the DSA project cadence and a possible `targets/stat6.md` anchor. Pairs well with Batch 1's outputs for cross-linking.

**Connector:** sharepoint
**Access level:** all_fte

- [x] sharepoint_protein-science-documents-all-del-meetings-20231113-20231113-all-del-mtg-techdev-pptx
- [x] sharepoint_protein-science-documents-del-screen-plans-dsa-projects--gantt-xlsx
- [x] sharepoint_protein-science-documents-del-screen-plans-dsa-projects-new-gantt-xlsx
- [x] sharepoint_protein-science-documents-del-screen-plans-dsa-projects-update-early-discovery-20220818-xlsx
- [x] sharepoint_protein-science-documents-del-screen-plans-dsa-update---early-discovery-group-meeting-20220915-pptx
- [x] sharepoint_protein-science-documents-del-screen-plans-dsa-update---early-discovery-group-meeting-20220929-pptx
- [x] sharepoint_protein-science-documents-del-screen-plans-dsa-update---early-discovery-group-meeting-20221013-pptx
- [x] sharepoint_protein-science-documents-del-screen-plans-dsa-update---early-discovery-group-meeting-20221027-pptx
- [x] sharepoint_protein-science-documents-del-screen-plans-dsa-update---early-discovery-group-meeting-20221110-pptx
- [x] sharepoint_protein-science-documents-del-screen-plans-stat6-dsp-tables-jss-xlsx

---

## Batch 12 — Protein request / checkout UX redesign

**Theme:** The protein-request and checkout form has been redesigned at least three times over four years — 2022's detail-page redesign and checkout deck, 2024's homepage redesign, 2025's inventory check-out proposal and purification export request, plus the figma reviews and workflow checklist that fed into them. Cohesive "how the request UX evolved" story. Expected outputs: a `decisions/protein-request-ux-redesign.md` page synthesizing the arc (what changed, why, from / to), possibly a `protocols/protein-request-submission.md` page if the sources together give a clean picture of the current submission flow.

**Connector:** sharepoint
**Access level:** all_fte

- [x] sharepoint_protein-science-documents-delphi-20220905-protein-request-detail-page-redesign-pptx
- [x] sharepoint_protein-science-documents-delphi-20221123-protein-request-checkout-pptx
- [x] sharepoint_protein-science-documents-delphi-20240308-delphi-proteinproductionrequests-homepage-redesign-xlsx
- [x] sharepoint_protein-science-documents-delphi-20250312-proposed-changes-to-delphi-inventory-check-out-ppt-pptx
- [x] sharepoint_protein-science-documents-delphi-20250513-protein-purification-export-request-pptx
- [x] sharepoint_protein-science-documents-delphi-revised-protein-request-workflow--jose-comments-pptx
- [x] sharepoint_protein-science-documents-delphi-revised-protein-request-workflow-1-pptx
- [x] sharepoint_protein-science-documents-delphi-figma-review-01052023-pptx
- [x] sharepoint_protein-science-documents-delphi-figma-review-112022-pptx
- [x] sharepoint_protein-science-documents-delphi-work-flow-check-list-pptx

---

## Batch 13 — DS399 QA testing saga

**Theme:** DS399 was one Delphi ticket that took six rounds of QA testing to close out between September and December 2024. A single `decisions/ds399-qa-testing.md` page captures what DS399 changed and why it needed six review passes; the DS725 test doc from December is a close cousin (another long-tail QA case from the same era) and fits the same narrative. Trailing batch — seven entries is the right size given how focused the cluster is.

**Connector:** sharepoint
**Access level:** all_fte

- [x] sharepoint_protein-science-documents-delphi-20240919-ds399-qa-testing-docx
- [x] sharepoint_protein-science-documents-delphi-20241023-ds399-qa-testing-docx
- [x] sharepoint_protein-science-documents-delphi-20241114-delphi-ds399-testing-docx
- [x] sharepoint_protein-science-documents-delphi-20241127-qatesting-ds399-docx
- [x] sharepoint_protein-science-documents-delphi-20241205-delphi-ds399-testing-docx
- [x] sharepoint_protein-science-documents-delphi-20241212-delphi-ds399-testing-docx
- [x] sharepoint_protein-science-documents-delphi-20241218-delphi-ds725testing-derek-docx

---

## Batch 14 — Delphi triage / QA reviews / Jira workflow

**Theme:** How bugs and issues get filed, triaged, and resolved in Delphi — the 2022 Delphi-cases status deck, QA review sessions (2022 ACS issues triage, the Feb 2024 SSEPT QA check), the 2023 Delphi-challenges issue log, jira ticket filing guidelines, and the automatic-status-changes rollout that replaced manual triage in late 2024. Expected outputs: a `methods/delphi-bug-triage.md` page on the bug-filing and triage process, a `decisions/delphi-automatic-status-changes.md` page on the 2024 rollout.

**Connector:** sharepoint
**Access level:** all_fte

- [x] sharepoint_protein-science-documents-delphi-20221101-proteinsciences-delphi-cases-pptx
- [x] sharepoint_protein-science-documents-delphi-20230821-delphi-challenges-xlsx
- [x] sharepoint_protein-science-documents-delphi-delphi-qa-reviews-20220810-delphi-qa-review-jose-emily-hugo-docx
- [x] sharepoint_protein-science-documents-delphi-delphi-qa-reviews-09022022-delphi-acs-issues-august-xlsx  <!-- near-duplicate: entries 4&5 both August 2022 ACS Jira filter, second marked "sent" -->
- [x] sharepoint_protein-science-documents-delphi-delphi-qa-reviews-09022022-delphi-acs-issues-august-sent-xlsx  <!-- duplicate-of-entry-4 -->
- [x] sharepoint_protein-science-documents-delphi-delphi-qa-reviews-test-ssept-020924-docx
- [x] sharepoint_protein-science-documents-delphi-20241015-jira-ticket-filing-guidelines-pptx
- [x] sharepoint_protein-science-documents-delphi-20241021-automatic-status-changes-pptx
- [x] sharepoint_protein-science-documents-delphi-automatic-status-changes-09-06-2024-pptx
- [x] sharepoint_protein-science-documents-delphi-automatic-status-changes-10-21-2024-pptx

---

## Batch 15 — SSEPT round 2 (import tables, tickets, small-scale task proposal)

**Theme:** Second pass on SSEPT material — the original 2023 small-scale-task proposal that pitched the feature, the SSEPT tickets log from April 2024, the Feb 2024 ssepttable snapshot, the Sep 2025 import-documents exports, and the late-2025 one-off SSEPT exports feeding downstream tools (protein sequence export for Boltz, info6484 examples). Extends the methods/protocols page produced by Batch 7 with ticket-level history and downstream integration patterns; likely warrants a `protocols/ssept-export-integration.md` sub-page.

**Connector:** sharepoint
**Access level:** all_fte

- [x] sharepoint_protein-science-documents-delphi-2023-07-14-delphi-small-scale-task-proposal-pptx
- [x] sharepoint_protein-science-documents-delphi-20240201-delphi-ssepttable-xlsx
- [x] sharepoint_protein-science-documents-delphi-20250224-delphi-sseptimporttable-xlsx
- [x] sharepoint_protein-science-documents-delphi-20250730-delphi-sseptimporttable-xlsx
- [x] sharepoint_protein-science-documents-delphi-copy-of-ssept-tickets---april-2024-xlsx
- [x] sharepoint_protein-science-documents-delphi-ssept-import-documents-am-complete-expression-task-list-wed-sep-03-2025-xlsx
- [x] sharepoint_protein-science-documents-delphi-ssept-import-documents-am-expression-task-list-wed-sep-03-2025-xlsx
- [x] sharepoint_protein-science-documents-delphi-20250519-proteinsequenceexport-pp-info6484-ssept-example-from-rob-20250519-xlsx
- [x] sharepoint_protein-science-documents-delphi-20250916-pp-info6484-onetimesseptexport-proteinseq-xlsx
- [x] sharepoint_protein-science-documents-delphi-20251001-proteinexportsforboltz-ssept-xlsx

---

## Batch 16 — Representative sample across snapshot clusters (DDT / roles / QC-reports)

**Theme:** The three big near-duplicate snapshot clusters flagged in the earlier backlog collapse into one session: three DDT protein-clone-database snapshots (2020-11 earliest, 2021-05 middle, 2022-05 latest), three user-roles snapshots (2022-07 earliest, 2023-03 middle, 2024-08 latest), three QC-reports-redesign variants (2023-04 Option1, 2023-10 mid-iteration, 2023-11 final design), and the CP-DS old-to-new roles crosswalk that ties the role evolution together. Three output pages expected — `protocols/delphi-ddt-clone-database.md`, `decisions/delphi-user-role-model.md`, `decisions/delphi-qc-report-redesign.md` — each synthesizing what the artifact is and what changed across the snapshots. Remaining snapshots in each cluster are pruned at Phase 6 per CLAUDE.md Principle 3.

**Connector:** sharepoint
**Access level:** all_fte

- [x] sharepoint_protein-science-documents-delphi-11-09-2020-ddt-protein-clone-database-for-christophe-xlsx
- [x] sharepoint_protein-science-documents-delphi-05-13-2021-ddt-protein-clone-database-for-amy-xlsx
- [x] sharepoint_protein-science-documents-delphi-05-13-2022-ddt-protein-clone-database-for-lf-xlsx
- [x] sharepoint_protein-science-documents-delphi-delphi-user-roles-20220725-xlsx
- [x] sharepoint_protein-science-documents-delphi-delphi-roles-definition-delphi-user-roles-20230314-xlsx
- [x] sharepoint_protein-science-documents-delphi-delphi-roles-definition-delphi-user-roles-20240829-xlsx
- [x] sharepoint_protein-science-documents-delphi-delphi-qc-reports-redesign-qc-report-pptx-2023-04-27-19-38-56-832661-option1-pptx
- [x] sharepoint_protein-science-documents-delphi-delphi-qc-reports-redesign-qc-report-pptx-2023-10-27-18-30-02-806343-pptx
- [x] sharepoint_protein-science-documents-delphi-delphi-qc-reports-redesign-qc-report-pptx-2023-11-07-19-53-12-221873-1b-pptx
- [x] sharepoint_protein-science-documents-delphi-delphi-roles-definition-delphi-cp-ds-old-roles-to-new-roles-map-wks-xlsx

---

## Batch 17 — Early Delphi history (2020-2021 + early 2022)

**Theme:** The pre-ACS era — the 2020 campaign-planning project plan for 2021, the early tags-fusion-cleavage-linkers table (before Batch 8's consolidated version), 2021 inventory-pathways and PP/CP screenshot review, late-2021 project renaming changes, the ACS2022-September release notes (the `campaign-planning-release-notes-july-september-prod-v2-4-0.pdf` that pre-dates the ACS2024.1 release-notes cluster in Batch 4), the 2022-08 Delphi lascex/lascpu tutorial, the June 2022 production-release-feedback prioritization deck, and an undated "jose notes on review" doc. Expected output: a `decisions/delphi-pre-acs-timeline.md` page that establishes "where Delphi was before the ACS epic" as the baseline anchor for Batches 3-5 citations.

**Connector:** sharepoint
**Access level:** all_fte

- [x] sharepoint_protein-science-documents-delphi-12-22-2020-campaign-planning-project-plan-2021-xlsx
- [x] sharepoint_protein-science-documents-delphi-11-17-2020-tags-fusion-cleavage-linkers-xlsx
- [x] sharepoint_protein-science-documents-delphi-09-22-2021-inventory-pathways-xlsx
- [x] sharepoint_protein-science-documents-delphi-10-08-2021-pp-and-cp-review-of-screen-shots-pptx
- [x] sharepoint_protein-science-documents-delphi-10-08-2021-pp-and-cp-review-of-screen-shots-kl-pptx
- [x] sharepoint_protein-science-documents-delphi-12-07-2021-delphi-project-renaming-changes-xlsx
- [x] sharepoint_protein-science-documents-delphi-release-notes-acs2022-sept-release-campaign-planning-release-notes-july-september-prod-v2-4-0-pdf
- [x] sharepoint_protein-science-documents-delphi-2022-production-release-feedback-prioritization-06212022-xlsx
- [x] sharepoint_protein-science-documents-delphi-delphi-tutorial-lascex-lascpu-08022222-docx
- [x] sharepoint_protein-science-documents-delphi-jose-notes-on-review-docx

---

## Batch 18 — Protein-production inventory + data-integrity events

**Theme:** Inventory-side changes to Delphi — the August 2022 inventory columns schema change, the April 2023 protein-inventory updates, three Aug/Sep 2023 protein-production-inventory data samples (representative snapshots of the inventory table), the September 2023 invalid→corrected barcodes event (a discrete data-integrity fix), the October 2023 DS869 manual-updates sweep, and a November 2023 flasks snapshot tail that followed the DS841 rollout (Batch 6). Expected outputs: a `decisions/delphi-inventory-schema.md` page for the 2022-08 columns change and the downstream 2023-04 update, plus a `decisions/barcode-correction-2023-09.md` anchor for the invalid→corrected event if the sources warrant it.

**Connector:** sharepoint
**Access level:** all_fte

- [x] sharepoint_protein-science-documents-delphi-delphi-inventory-columns-changes-080922-pptx
- [x] sharepoint_protein-science-documents-delphi-20230418-delphi-proteininventory-updates-xlsx
- [x] sharepoint_protein-science-documents-delphi-20230810-protein-production-inventory-data-sample-xlsx
- [x] sharepoint_protein-science-documents-delphi-20230822-protein-production-inventory-data-sample-xlsx
- [x] sharepoint_protein-science-documents-delphi-20230907-protein-production-inventory-data-sample-xlsx
- [x] sharepoint_protein-science-documents-delphi-protein-production-inventory-data-sample-xlsx
- [x] sharepoint_protein-science-documents-delphi-20230925-invalidbarcodes-xlsx
- [x] sharepoint_protein-science-documents-delphi-20230927-correctedbarcodes-xlsx
- [x] sharepoint_protein-science-documents-delphi-20231023-manual-updates-for-ds869-xlsx
- [x] sharepoint_protein-science-documents-delphi-20231109-copy-of-flasks-updated-xlsx

---

## Batch 19 — Delphi ACS2026.2 release cycle + ACS2025.3 testing tail

**Theme:** The ACS2026.2 release-notes deck (March 2026) plus the four UAT testing snapshots that validated it (Feb through April 2026, including an early ACS2026.3 testing snapshot), plus the two orphan ACS2025.3 testing snapshots from July 2025 that never got release-notes companions, plus two September 2025 `delphi-uat` decks likely in the ACS2025.3 tail. Same pattern as Batches 4-5 — one `decisions/acs2026-2-release.md` page anchored to the Delphi platform page from Batch 2, one `decisions/acs2025-3-release.md` page (looser, given the missing release notes). If the two September 2025 decks turn out to be a different release, promote them out at Phase 6.

**Connector:** sharepoint
**Access level:** all_fte

- [x] sharepoint_protein-science-documents-delphi-release-notes-acs2026-2-20260311-delphi-2026-2-1-release-notes-pptx
- [x] sharepoint_protein-science-documents-delphi-delphi-uat-reviews-acs2026-2-uat-testing-20260217-uat-snapshots-pptx
- [x] sharepoint_protein-science-documents-delphi-delphi-uat-reviews-acs2026-2-uat-testing-20260305-2026-2-1-uat-testing-pptx
- [x] sharepoint_protein-science-documents-delphi-delphi-uat-reviews-acs2026-2-uat-testing-20260320-2026-2-2-uat-snapshots-pptx
- [x] sharepoint_protein-science-documents-delphi-delphi-uat-reviews-acs2026-3-uat-testing-20260406-uat-snapshots-pptx
- [x] sharepoint_protein-science-documents-delphi-delphi-uat-reviews-acs2025-3-testing-20250730-delphi-sseptimporttable-xlsx
- [x] sharepoint_protein-science-documents-delphi-delphi-uat-reviews-acs2025-3-testing-20250731-expression-task-list-thu-jul-31-2025-emily-export-xlsx
- [x] sharepoint_protein-science-documents-delphi-20250923-delphi-uat-pptx
- [x] sharepoint_protein-science-documents-delphi-20250925-delphi-uat-pptx

---

## Batch 20 — Delphi ACS2025.2 second-wave UAT testing

**Theme:** The second wave of ACS2025.2 UAT testing that landed after the release-notes deck (already in Batch 5). Batch 5 anchored the release with one representative DS-1392/1423 testing pair; this batch covers the rest of the ticket-level UAT trail — DS-1393, DS-1394, DS-1396, the three DS-1423 iterations (April 17, 22, plus the DS-1423 EmptyMWPicklist error log that bracketed them), DS-1439, and the three DS-1476 large-scale-expression task-list cases. Cohesive ACS2025.2 long-tail story; same `decisions/acs2025-2-release.md` page produced by Batch 5 should absorb this batch's findings rather than producing a parallel page. Closes the SharePoint coverage gap from the manifest survey done 2026-04-24.

**Connector:** sharepoint
**Access level:** all_fte

- [x] sharepoint_protein-science-documents-delphi-delphi-uat-reviews-acs2025-2-uat-testing-20250416-ds-1393-docx
- [x] sharepoint_protein-science-documents-delphi-delphi-uat-reviews-acs2025-2-uat-testing-20250416-ds-1394-docx
- [x] sharepoint_protein-science-documents-delphi-delphi-uat-reviews-acs2025-2-uat-testing-20250416-ds-1396-docx
- [x] sharepoint_protein-science-documents-delphi-delphi-uat-reviews-acs2025-2-uat-testing-20250417-ds-1423-docx
- [x] sharepoint_protein-science-documents-delphi-delphi-uat-reviews-acs2025-2-uat-testing-20250418-ds-1423-emptymwpicklist-error-txt
- [x] sharepoint_protein-science-documents-delphi-delphi-uat-reviews-acs2025-2-uat-testing-20250418-ds-1439-docx
- [x] sharepoint_protein-science-documents-delphi-delphi-uat-reviews-acs2025-2-uat-testing-20250422-ds-1423-docx
- [x] sharepoint_protein-science-documents-delphi-delphi-uat-reviews-acs2025-2-uat-testing-ds-1476-large-scale-expression-task-list-fri-apr-18-2025-case1-xlsx
- [x] sharepoint_protein-science-documents-delphi-delphi-uat-reviews-acs2025-2-uat-testing-ds-1476-large-scale-expression-task-list-fri-apr-18-2025-case2-xlsx
- [x] sharepoint_protein-science-documents-delphi-delphi-uat-reviews-acs2025-2-uat-testing-ds-1476-large-scale-expression-task-list-fri-apr-18-2025-case3-xlsx

---

## Batch 21 — Phase 6 prune coverage (truthful-index dump)

**Theme:** Not an absorb batch — a coverage-only batch that enumerates every SharePoint manifest entry the human-readable Backlog already classified as Phase 6 prune-pool, so the queue index is mechanically complete. Each line is pre-ticked with `<!-- skip: <reason> -->`. The compile worker should treat these as already-handled (do not absorb); Phase 6 lint pulls any cross-snapshot signal back into the canonical Batch 3-19 pages. Generated 2026-04-24 from `manifest.json` minus `queue.md` strict-batched IDs (118 entries across 27 clusters).

**Connector:** sharepoint
**Access level:** all_fte

### 'Copy of' working-file variants — one-off scratch  (3)

- [x] sharepoint_protein-science-documents-delphi-20240419-copy-of-jiraissues-testing-el-hb-xlsx  <!-- skip: copy_of_variants -->
- [x] sharepoint_protein-science-documents-delphi-20241021-copy-of-invalidaa-xlsx  <!-- skip: copy_of_variants -->
- [x] sharepoint_protein-science-documents-delphi-20250129-copy-of-pathdifs-xlsx  <!-- skip: copy_of_variants -->

### Informal Delphi review docs — undated scope; Phase 6 prune  (2)

- [x] sharepoint_protein-science-documents-delphi-20250812-delphi-review-docx  <!-- skip: delphi_review -->
- [x] sharepoint_protein-science-documents-delphi-20250820-delphi-review-docx  <!-- skip: delphi_review -->

### Delphi error-log dumps — bug-report evidence, not knowledge; Phase 6 pattern-analysis only  (14)

- [x] sharepoint_protein-science-documents-delphi-20240314-el-delphi-error-txt  <!-- skip: error_txt -->
- [x] sharepoint_protein-science-documents-delphi-20240314-kl-delphi-error-txt  <!-- skip: error_txt -->
- [x] sharepoint_protein-science-documents-delphi-20240529-el-delphi-biomass-reg-error-txt  <!-- skip: error_txt -->
- [x] sharepoint_protein-science-documents-delphi-20240607-biomass-dotmatics-error-txt  <!-- skip: error_txt -->
- [x] sharepoint_protein-science-documents-delphi-20240614-clone-persistenceerror-txt  <!-- skip: error_txt -->
- [x] sharepoint_protein-science-documents-delphi-20240909-ssept-5moiconditions-error-txt  <!-- skip: error_txt -->
- [x] sharepoint_protein-science-documents-delphi-20241009-ds1252error-txt  <!-- skip: error_txt -->
- [x] sharepoint_protein-science-documents-delphi-20250528-lset4595-error-javax-persistence-persistenceexcept-txt  <!-- skip: error_txt -->
- [x] sharepoint_protein-science-documents-delphi-20250613-qcreportexporterror-txt  <!-- skip: error_txt -->
- [x] sharepoint_protein-science-documents-delphi-20260112-lset-console-error-1-txt  <!-- skip: error_txt -->
- [x] sharepoint_protein-science-documents-delphi-20260112-lset-error-stack-trace-txt  <!-- skip: error_txt -->
- [x] sharepoint_protein-science-documents-delphi-20260324-delphi-del-screening-error-txt  <!-- skip: error_txt -->
- [x] sharepoint_protein-science-documents-delphi-20260325-delphi-pp-error-lspt-table-txt  <!-- skip: error_txt -->
- [x] sharepoint_protein-science-documents-delphi-20260403-uat-cloneregerror-txt  <!-- skip: error_txt -->

### Single-ticket evidence dumps — Phase 6 prune unless a pattern emerges  (4)

- [x] sharepoint_protein-science-documents-delphi-20231107-ds882-necc-n21333-001a-xlsx  <!-- skip: evidence_dump -->
- [x] sharepoint_protein-science-documents-delphi-20250403-blankfields-docx  <!-- skip: evidence_dump -->
- [x] sharepoint_protein-science-documents-delphi-20260211-differences-target-forms-not-correctly-assigned-to-project-txt  <!-- skip: evidence_dump -->
- [x] sharepoint_protein-science-documents-delphi-20260211-differences-target-forms-not-correctly-assigned-to-project-xlsx  <!-- skip: evidence_dump -->

### Herman/John protein-id match snapshots — two iterations of the same artifact  (2)

- [x] sharepoint_protein-science-documents-delphi-20260225-herman-john-protein-id-his-avi-matches-xlsx  <!-- skip: herman_john -->
- [x] sharepoint_protein-science-documents-delphi-20260410-herman-john-protein-id-his-avi-matches-copy-xlsx  <!-- skip: herman_john -->

### 2024-01-29 meeting-with-Rob scratch — no standalone wiki signal  (3)

- [x] sharepoint_protein-science-documents-delphi-20240129-meetingwithrob-copy-of-testresultsallenv-xlsx  <!-- skip: meetingwithrob -->
- [x] sharepoint_protein-science-documents-delphi-20240129-meetingwithrob-copy-of-updatedsamples-xlsx  <!-- skip: meetingwithrob -->
- [x] sharepoint_protein-science-documents-delphi-20240129-meetingwithrob-ppmeeting26jan2024-pptx  <!-- skip: meetingwithrob -->

### Standalone non-Delphi singletons — Coupa, Cyrus, laptop-copy of DSA project list  (4)

- [x] sharepoint_protein-science-documents-coupa-coupa-project-coding-updates-pptx  <!-- skip: non_delphi_singletons -->
- [x] sharepoint_protein-science-documents-coupa-split-billing-functionality-in-coupa-docx  <!-- skip: non_delphi_singletons -->
- [x] sharepoint_protein-science-documents-cyrus-hm-and-cad-training-pptx  <!-- skip: non_delphi_singletons -->
- [x] sharepoint_protein-science-documents-del-screen-plans-dsa-projects-jsantos04-t480-xlsx  <!-- skip: non_delphi_singletons -->

### Performance benchmarks — revisit at Phase 6 (may deserve `decisions/delphi-performance-characterization.md`)  (1)

- [x] sharepoint_protein-science-documents-delphi-20251118-performance-benchmarks-xlsx  <!-- skip: perf_bench -->

### Picklist-bug investigation snapshots — promote when a fix lands  (2)

- [x] sharepoint_protein-science-documents-delphi-20260309-picklist-bug-pptx  <!-- skip: picklist_bug -->
- [x] sharepoint_protein-science-documents-delphi-20260325-picklist-bug-pptx  <!-- skip: picklist_bug -->

### PP-INFO6484 export iterations — same artifact evolving June 2025; collapse at Phase 6  (4)

- [x] sharepoint_protein-science-documents-delphi-20250603-elresponse-copy-of-pp-info6484-lsptmay27-xlsx  <!-- skip: pp_info6484 -->
- [x] sharepoint_protein-science-documents-delphi-20250605-pp-info6484-lspt-04jun-prod-elcomments-xlsx  <!-- skip: pp_info6484 -->
- [x] sharepoint_protein-science-documents-delphi-20250606-pp-info6484-lspt-05jun-prod-exportfromrob-xlsx  <!-- skip: pp_info6484 -->
- [x] sharepoint_protein-science-documents-delphi-20250613-pp-info6484-lspt-12jun-prod-proteinsequenceexport-final-xlsx  <!-- skip: pp_info6484 -->

### Test-environment scratch exports — PPTestsProd  (2)

- [x] sharepoint_protein-science-documents-delphi-20230914-pptestsprod-el-edits-xlsx  <!-- skip: pptestsprod -->
- [x] sharepoint_protein-science-documents-delphi-20230928-pptestsprod3-xlsx  <!-- skip: pptestsprod -->

### Loose QC report export PPTX — one-off, not part of redesign cluster  (1)

- [x] sharepoint_protein-science-documents-delphi-20231011-qcreportexport-qc-report-pptx-2023-10-11-17-18-59-191389-pptx  <!-- skip: qcreportexport_loose -->

### One-off reconcile/audit artifacts  (2)

- [x] sharepoint_protein-science-documents-delphi-03052023-protein-production-missing-antibiotic-resistance-for-existing-clones-xlsx  <!-- skip: reconcile -->
- [x] sharepoint_protein-science-documents-delphi-20221111-protein-production-reconcile-clone-dna-sequence-xlsx  <!-- skip: reconcile -->

### 2021-05-27 ACS UAT reviewer variants — masters in Batch 3; reviewer commentary folded in at Phase 6 lint  (13)

- [x] sharepoint_protein-science-documents-delphi-delphi-uat-reviews-05-27-2021-uat-reviews-01-advanced-construct-support-uat-plan-campaign-planning-milestone-2-changes-eledits-pdf  <!-- skip: review_2021_05_27 -->
- [x] sharepoint_protein-science-documents-delphi-delphi-uat-reviews-05-27-2021-uat-reviews-01-advanced-construct-support-uat-plan-campaign-planning-milestone-2-changes-jose-pdf  <!-- skip: review_2021_05_27 -->
- [x] sharepoint_protein-science-documents-delphi-delphi-uat-reviews-05-27-2021-uat-reviews-01-advanced-construct-support-uat-plan-campaign-planning-milestone-2-changes-kl-pdf  <!-- skip: review_2021_05_27 -->
- [x] sharepoint_protein-science-documents-delphi-delphi-uat-reviews-05-27-2021-uat-reviews-01-advanced-construct-support-uat-plan-protein-production-requests-eledits-pdf  <!-- skip: review_2021_05_27 -->
- [x] sharepoint_protein-science-documents-delphi-delphi-uat-reviews-05-27-2021-uat-reviews-01-advanced-construct-support-uat-plan-protein-production-requests-jose-pdf  <!-- skip: review_2021_05_27 -->
- [x] sharepoint_protein-science-documents-delphi-delphi-uat-reviews-05-27-2021-uat-reviews-01-advanced-construct-support-uat-plan-protein-production-requests-kl-pdf  <!-- skip: review_2021_05_27 -->
- [x] sharepoint_protein-science-documents-delphi-delphi-uat-reviews-05-27-2021-uat-reviews-02-advanced-construct-support-uat-plan-clone-tasks-eledits-pdf  <!-- skip: review_2021_05_27 -->
- [x] sharepoint_protein-science-documents-delphi-delphi-uat-reviews-05-27-2021-uat-reviews-02-advanced-construct-support-uat-plan-clone-tasks-jose-docx-pdf  <!-- skip: review_2021_05_27 -->
- [x] sharepoint_protein-science-documents-delphi-delphi-uat-reviews-05-27-2021-uat-reviews-02-advanced-construct-support-uat-plan-clone-tasks-kl-pdf  <!-- skip: review_2021_05_27 -->
- [x] sharepoint_protein-science-documents-delphi-delphi-uat-reviews-05-27-2021-uat-reviews-02-advanced-construct-support-uat-plan-target-form-eledits-pdf  <!-- skip: review_2021_05_27 -->
- [x] sharepoint_protein-science-documents-delphi-delphi-uat-reviews-05-27-2021-uat-reviews-02-advanced-construct-support-uat-plan-target-form-kl-pdf  <!-- skip: review_2021_05_27 -->
- [x] sharepoint_protein-science-documents-delphi-delphi-uat-reviews-05-27-2021-uat-reviews-03-advanced-construct-support-uat-plan-sequence-and-structure-eledits-pdf  <!-- skip: review_2021_05_27 -->
- [x] sharepoint_protein-science-documents-delphi-delphi-uat-reviews-05-27-2021-uat-reviews-03-advanced-construct-support-uat-plan-sequence-and-structure-kl-pdf  <!-- skip: review_2021_05_27 -->

### 2021-08-29 UAT reviewer copies — same Batch 3 lineage  (2)

- [x] sharepoint_protein-science-documents-delphi-delphi-uat-reviews-08-29-2021-uat-reviews-copy-of-0-2-advanced-construct-support-uat-plan-protein-production---jose-pdf  <!-- skip: review_2021_08_29 -->
- [x] sharepoint_protein-science-documents-delphi-delphi-uat-reviews-08-29-2021-uat-reviews-copy-of-04-advanced-construct-support-uat-plan--jose-pdf  <!-- skip: review_2021_08_29 -->

### 2024-05-28 SSEPT UAT testing artifacts — collapse into Batch 7 SSEPT page  (2)

- [x] sharepoint_protein-science-documents-delphi-delphi-uat-reviews-05-28-2024-uat-reviews-delphi-ssept-testing-checklist-xlsx  <!-- skip: review_2024_05_28 -->
- [x] sharepoint_protein-science-documents-delphi-delphi-uat-reviews-05-28-2024-uat-reviews-test-case-1-pptx  <!-- skip: review_2024_05_28 -->

### ACS2024.1 extended UAT tickets — Batch 4 has six representatives; this is the long tail  (6)

- [x] sharepoint_protein-science-documents-delphi-delphi-uat-reviews-acs2024-1-uat-testing-20241220-ds-1362-docx  <!-- skip: review_acs2024_1 -->
- [x] sharepoint_protein-science-documents-delphi-delphi-uat-reviews-acs2024-1-uat-testing-20250102-ds-1124-docx  <!-- skip: review_acs2024_1 -->
- [x] sharepoint_protein-science-documents-delphi-delphi-uat-reviews-acs2024-1-uat-testing-20250102-ds-725-docx  <!-- skip: review_acs2024_1 -->
- [x] sharepoint_protein-science-documents-delphi-delphi-uat-reviews-acs2024-1-uat-testing-20250103-ds-1284-testing-results-xlsx  <!-- skip: review_acs2024_1 -->
- [x] sharepoint_protein-science-documents-delphi-delphi-uat-reviews-acs2024-1-uat-testing-20250214-ds-1283-docx  <!-- skip: review_acs2024_1 -->
- [x] sharepoint_protein-science-documents-delphi-delphi-uat-reviews-acs2024-1-uat-testing-ds-1284-docx  <!-- skip: review_acs2024_1 -->

### ACS2025.1 extended UAT tickets — Batch 5 covers the release; this is the long tail  (4)

- [x] sharepoint_protein-science-documents-delphi-delphi-uat-reviews-acs2025-1-uat-testing-ds-1298-20250219-ds-1298-uat-testing-docx  <!-- skip: review_acs2025_1 -->
- [x] sharepoint_protein-science-documents-delphi-delphi-uat-reviews-acs2025-1-uat-testing-ds-1300-02192025-irf5-emilylow-1-picklist-xlsx  <!-- skip: review_acs2025_1 -->
- [x] sharepoint_protein-science-documents-delphi-delphi-uat-reviews-acs2025-1-uat-testing-ds-1300-02272024-irf5-emilylow-1-picklist-xlsx  <!-- skip: review_acs2025_1 -->
- [x] sharepoint_protein-science-documents-delphi-delphi-uat-reviews-acs2025-1-uat-testing-ds-1300-20250219-uat-testing-picklist-export-error-docx  <!-- skip: review_acs2025_1 -->

### Annotation/Q&A scratch — Phase 6 prune  (2)

- [x] sharepoint_protein-science-documents-delphi-06072023-df-selections-domains-jose-xlsx  <!-- skip: scratch -->
- [x] sharepoint_protein-science-documents-delphi-20250527-delphi-clone-task-cp-and-pp-questions-pptx  <!-- skip: scratch -->

### One-off sequence-exports xlsx — Phase 6  (1)

- [x] sharepoint_protein-science-documents-delphi-20250922-sequence-exports-xlsx  <!-- skip: sequence_exports -->

### DDT clone-database snapshots — Batch 16 sampled 3; rest pruned at Phase 6 (Principle 3)  (15)

- [x] sharepoint_protein-science-documents-delphi-03-01-2022-ddt-protein-clone-database-for-lf-xlsx  <!-- skip: snap_ddt -->
- [x] sharepoint_protein-science-documents-delphi-03-26-2021-ddt-protein-clone-database-amy-xlsx  <!-- skip: snap_ddt -->
- [x] sharepoint_protein-science-documents-delphi-05-10-2022-ddt-protein-clone-database-for-fl-xlsx  <!-- skip: snap_ddt -->
- [x] sharepoint_protein-science-documents-delphi-05-11-2022-ddt-protein-clone-database-xlsx  <!-- skip: snap_ddt -->
- [x] sharepoint_protein-science-documents-delphi-05-12-2022-ddt-protein-clone-database-forlf-xlsx  <!-- skip: snap_ddt -->
- [x] sharepoint_protein-science-documents-delphi-06-13-2021-ddt-protein-clone-database-forlf-xlsx  <!-- skip: snap_ddt -->
- [x] sharepoint_protein-science-documents-delphi-07-07-2021-ddt-protein-clone-database-for-lf-xlsx  <!-- skip: snap_ddt -->
- [x] sharepoint_protein-science-documents-delphi-07-20-2021-ddt-protein-clone-database-for-lf-xlsx  <!-- skip: snap_ddt -->
- [x] sharepoint_protein-science-documents-delphi-07-22-2021-ddt-protein-clone-database-for-lf-xlsx  <!-- skip: snap_ddt -->
- [x] sharepoint_protein-science-documents-delphi-07-23-2021-ddt-protein-clone-database-for-lf-xlsx  <!-- skip: snap_ddt -->
- [x] sharepoint_protein-science-documents-delphi-08-02-2021-ddt-protein-clone-database-for-lf-xlsx  <!-- skip: snap_ddt -->
- [x] sharepoint_protein-science-documents-delphi-09-10-2021-ddt-protein-clone-database-forlf-xlsx  <!-- skip: snap_ddt -->
- [x] sharepoint_protein-science-documents-delphi-10-27-2021-ddt-protein-clone-database-for-lf-xlsx  <!-- skip: snap_ddt -->
- [x] sharepoint_protein-science-documents-delphi-11-14-2021-ddt-protein-clone-database-forlf-xlsx  <!-- skip: snap_ddt -->
- [x] sharepoint_protein-science-documents-delphi-11-8-2021-ddt-protein-clone-database-for-john-lin-xlsx  <!-- skip: snap_ddt -->

### QC reports redesign variants — Batch 16 sampled 3; rest pruned at Phase 6  (8)

- [x] sharepoint_protein-science-documents-delphi-delphi-qc-reports-redesign-qc-report-pptx-2023-04-27-19-38-56-832661-option2-pptx  <!-- skip: snap_qc_redesign -->
- [x] sharepoint_protein-science-documents-delphi-delphi-qc-reports-redesign-qc-report-pptx-2023-04-27-19-38-56-832661-option3-pptx  <!-- skip: snap_qc_redesign -->
- [x] sharepoint_protein-science-documents-delphi-delphi-qc-reports-redesign-qc-report-pptx-2023-04-27-19-38-56-832661-original-pptx  <!-- skip: snap_qc_redesign -->
- [x] sharepoint_protein-science-documents-delphi-delphi-qc-reports-redesign-qc-report-pptx-2023-10-26-17-03-23-124907-pptx  <!-- skip: snap_qc_redesign -->
- [x] sharepoint_protein-science-documents-delphi-delphi-qc-reports-redesign-qc-report-pptx-2023-10-27-16-15-17-91159-pptx  <!-- skip: snap_qc_redesign -->
- [x] sharepoint_protein-science-documents-delphi-delphi-qc-reports-redesign-qc-report-pptx-2023-10-27-16-16-42-201345-pptx  <!-- skip: snap_qc_redesign -->
- [x] sharepoint_protein-science-documents-delphi-delphi-qc-reports-redesign-qc-report-pptx-2023-10-27-16-20-18-159905-pptx  <!-- skip: snap_qc_redesign -->
- [x] sharepoint_protein-science-documents-delphi-delphi-qc-reports-redesign-qc-report-pptx-2023-11-07-19-44-27-341239-1a-pptx  <!-- skip: snap_qc_redesign -->

### Delphi User Roles snapshots — Batch 16 sampled 3; rest pruned at Phase 6  (12)

- [x] sharepoint_protein-science-documents-delphi-delphi-roles-definition-delphi-user-roles-20220725-xlsx  <!-- skip: snap_user_roles -->
- [x] sharepoint_protein-science-documents-delphi-delphi-roles-definition-delphi-user-roles-20220831-xlsx  <!-- skip: snap_user_roles -->
- [x] sharepoint_protein-science-documents-delphi-delphi-roles-definition-delphi-user-roles-20221010-xlsx  <!-- skip: snap_user_roles -->
- [x] sharepoint_protein-science-documents-delphi-delphi-roles-definition-delphi-user-roles-20221018-xlsx  <!-- skip: snap_user_roles -->
- [x] sharepoint_protein-science-documents-delphi-delphi-roles-definition-delphi-user-roles-20221021-xlsx  <!-- skip: snap_user_roles -->
- [x] sharepoint_protein-science-documents-delphi-delphi-roles-definition-delphi-user-roles-20230105-minimal-xlsx  <!-- skip: snap_user_roles -->
- [x] sharepoint_protein-science-documents-delphi-delphi-roles-definition-delphi-user-roles-20230105-xlsx  <!-- skip: snap_user_roles -->
- [x] sharepoint_protein-science-documents-delphi-delphi-roles-definition-delphi-user-roles-20230316-xlsx  <!-- skip: snap_user_roles -->
- [x] sharepoint_protein-science-documents-delphi-delphi-roles-definition-delphi-user-roles-20230502-jose-xlsx  <!-- skip: snap_user_roles -->
- [x] sharepoint_protein-science-documents-delphi-delphi-roles-definition-delphi-user-roles-20230502-xlsx  <!-- skip: snap_user_roles -->
- [x] sharepoint_protein-science-documents-delphi-delphi-roles-definition-delphi-user-roles-20231103-xlsx  <!-- skip: snap_user_roles -->
- [x] sharepoint_protein-science-documents-delphi-delphi-roles-definition-delphi-user-roles-20231108-xlsx  <!-- skip: snap_user_roles -->

### Delphi roles-definition extras (cp-pp AD roles, investigators table, alternate-path cp-ds map)  (4)

- [x] sharepoint_protein-science-documents-delphi-delphi-cp-ds-old-roles-to-new-roles-map-wks-xlsx  <!-- skip: snap_user_roles_extra -->
- [x] sharepoint_protein-science-documents-delphi-delphi-roles-definition-20220927-delphi-investigators-xlsx  <!-- skip: snap_user_roles_extra -->
- [x] sharepoint_protein-science-documents-delphi-delphi-roles-definition-20230112-delph-cp-pp-ad-roles-xlsx  <!-- skip: snap_user_roles_extra -->
- [x] sharepoint_protein-science-documents-delphi-delphi-roles-definition-20230205-delphi-cp-pp-ad-roles-xlsx  <!-- skip: snap_user_roles_extra -->

### Search-result exports — textsearchcIAP2/12; Phase 6 prune  (2)

- [x] sharepoint_protein-science-documents-delphi-20250812-textsearchciap2-xlsx  <!-- skip: textsearch -->
- [x] sharepoint_protein-science-documents-delphi-20250814-textsearchciap12-xlsx  <!-- skip: textsearch -->

### Orphan timeline deck — one-off meeting visualization  (1)

- [x] sharepoint_protein-science-documents-delphi-timeline-04192024-pptx  <!-- skip: timeline_orphan -->

### Delphi vendor-info proposal snapshots — promote when a decision lands  (2)

- [x] sharepoint_protein-science-documents-delphi-20260226-delphi-vendorinfo-proposal-pptx  <!-- skip: vendor_info -->
- [x] sharepoint_protein-science-documents-delphi-20260311-delphi-vendorinfo-proposal-v2-pptx  <!-- skip: vendor_info -->

---

## Batch 22 — Long-tail SharePoint coverage

**Theme:** Sweep of every SharePoint manifest entry not previously batched (Batches 1-21). Splits cleanly along absorb-vs-skip lines: ~79 entries with real wiki signal (the Early Discovery Research Day 2023 corpus, DEL triage internal-project meetings, ligandability-assay meetings, the lone 2021 Keystone TPD review deck, and the Loka ML 2024-09-09 PS bulk-info handoff) get absorbed; ~1,231 entries are bulk evidence or ephemeral artifacts skip-pooled with `<!-- skip: <reason> -->` annotations.

**Connector:** sharepoint  
**Access level:** all_fte

### Early Discovery Research Day 2023 — posters, rapid-fire decks, sign-ups  (68)

- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-edrd-2023-poster-talk-signup-xlsx
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-edrd-2023-sign-up-for-brainstorming-topics-xlsx
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-edrd-poster-presentation-session-for-chemistry-group-10-triazine-library-build-design-development-and-synthesis-pdf
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-edrd-poster-presentation-session-for-chemistry-group-12--advancing-global-proteomics-at-nurix-pdf
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-edrd-poster-presentation-session-for-chemistry-group-14-hit-validation-in-cellular-lysates-pdf
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-edrd-poster-presentation-session-for-chemistry-group-17--augmenting-lead-id-at-nurix-pdf
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-edrd-poster-presentation-session-for-chemistry-group-20-high-throughput-ligand-discovery-at-nurix-pdf
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-edrd-poster-presentation-session-for-chemistry-group-21--evolution-of-on-dna-click-reactions-pdf
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-edrd-poster-presentation-session-for-chemistry-group-22--ternary-complex-and-ubiquitylation-assays-pdf
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-edrd-poster-presentation-session-for-chemistry-group-5-development-of-a-solid-phase-asms-assay-for-del-hit-validation-pdf
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-edrd-poster-presentation-session-for-chemistry-group-7-measurement-of-ternary-complex-formation-by-spr-pdf
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-edrd-poster-presentation-session-for-chemistry-group-9--discovering-and-validating-ppil2-harness-pdf
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-poster-deposit-assay-poster-shipragupta-pdf
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-poster-deposit-bli-poster-mg-pdf
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-poster-deposit-cellscreening-finalppt-sst-dv-1-pdf
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-poster-deposit-chemicalspaceposter-researchday-tkennedy-pdf
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-poster-deposit-cl-research-day-2023-final-poster-pdf
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-poster-deposit-crispr-poster-2-sst-dv-pdf
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-poster-deposit-delml-poster---ec-hg-pdf
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-poster-deposit-dpcr-poster-2023-ia-pdf
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-poster-deposit-dsf-assay-development-biophysics-jf-resizing-pdf
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-poster-deposit-global-proteomics-jaipalreddy-panga-pdf
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-poster-deposit-isp-poster-sh-pdf
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-poster-deposit-ligandability-ppil2-poster-pdf
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-poster-deposit-poster-4-biochemistry-screening-platform-pdf
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-poster-deposit-poster-spotfire-mark-bingener-20230920e-pdf
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-poster-deposit-poster-triazine-library-build-design-development-and-synthesis-pdf
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-poster-deposit-ratul-tcf-poster-final-pdf
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-poster-deposit-sanchez-morgado-techdev-lyaste-final-pdf
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-poster-deposit-santos22-ligandabilitystatusposter-pdf
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-poster-deposit-sent-to-printer-santos1-assay-poster-shipragupta-pdf
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-poster-deposit-sent-to-printer-santos10-ligandability-ppil2-poster-pdf
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-poster-deposit-sent-to-printer-santos11-poster-4-biochemistry-screening-platform-pdf
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-poster-deposit-sent-to-printer-santos12-poster-triazine-library-build-design-development-and-synthesis-pdf
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-poster-deposit-sent-to-printer-santos13-poster-spotfire-mark-bingener-20230920e-pdf
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-poster-deposit-sent-to-printer-santos14-snf04-tcf-ub-poster-092023-final-pdf
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-poster-deposit-sent-to-printer-santos15-ssdels-as-tool-for-mitigating-del-binding-v2-pdf
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-poster-deposit-sent-to-printer-santos16-uncle-dsf-assay-dev-biophysics-jf-pdf
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-poster-deposit-sent-to-printer-santos17-2023-edrd-poster-htms-final-pdf
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-poster-deposit-sent-to-printer-santos18-ratul-tcf-poster-final-pdf
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-poster-deposit-sent-to-printer-santos19-global-proteomics-jaipalreddy-panga-pdf
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-poster-deposit-sent-to-printer-santos2-bli-poster-mg-pdf
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-poster-deposit-sent-to-printer-santos20-sanchez-morgado-techdev-lyaste-final-pdf
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-poster-deposit-sent-to-printer-santos21-dsf-assay-development-biophysics-jf-resizing-pdf
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-poster-deposit-sent-to-printer-santos22-ligandabilitystatusposter-pdf
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-poster-deposit-sent-to-printer-santos3-chemicalspaceposter-researchday-tkennedy-pdf
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-poster-deposit-sent-to-printer-santos4-cl-research-day-2023-final-poster-pdf
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-poster-deposit-sent-to-printer-santos5-crispr-poster-2-sst-dv-pdf
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-poster-deposit-sent-to-printer-santos6-delml-poster---ec-hg-pdf
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-poster-deposit-sent-to-printer-santos7-srk-development-of-high-throughput-cellular-degradation-assays-to-enable-direct-to-biology-workflows-pdf
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-poster-deposit-sent-to-printer-santos8-dpcr-poster-2023-ia-pdf
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-poster-deposit-sent-to-printer-santos9-isp-poster-sh-pdf
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-poster-deposit-snf04-tcf-ub-poster-092023-final-pdf
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-poster-deposit-srk-development-of-high-throughput-cellular-degradation-assays-to-enable-direct-to-biology-workflows-pdf
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-poster-deposit-srkold-pdf
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-poster-deposit-ssdels-as-tool-for-mitigating-del-binding-v2-pdf
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-poster-deposit-uncle-dsf-assay-dev-biophysics-jf-pdf
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-poster-template-examples-aacr-2023-nx-5948-poster-pptx
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-poster-template-examples-nurix-poster-hy-pptx
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-poster-template-examples-poster-template-optional-pptx
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-poster-template-examples-poster-template-optional-v2-pptx
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-rapid-fire-presentations-deposit-1ed-edrd-pptx
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-rapid-fire-presentations-deposit-early-discovery-research---targeted-proteomics-pptx
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-rapid-fire-presentations-deposit-early-discovery-research-day-20230920-pptx
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-rapid-fire-presentations-deposit-edrd-2023-ml-automation-and-infrastructure-at-the-nurix-scale-pptx
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-rapid-fire-presentations-deposit-intein-presentation-for-edrd-pptx
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-rapid-fire-presentations-deposit-ji-research-day-2023-tcf-ub-pptx
- [x] sharepoint_protein-science-documents-early-discovery-research-day-2023-rapid-fire-presentations-deposit-small-angle-x-ray-scattering-saxs-in-ternary-complex-guided-ctm-design-edrd-2023-09-20-pptx

### Internal seed projects — DEL triage monthly umbrella meetings  (5)

- [x] sharepoint_protein-science-documents-internal-seed-projects-monthly-umbrella-meetings-20240117-del-triage-internal-project-meeting-pptx
- [x] sharepoint_protein-science-documents-internal-seed-projects-monthly-umbrella-meetings-20240221-del-triage-internal-project-meeting-pptx
- [x] sharepoint_protein-science-documents-internal-seed-projects-monthly-umbrella-meetings-20240320-del-triage-internal-project-meeting-pptx
- [x] sharepoint_protein-science-documents-internal-seed-projects-monthly-umbrella-meetings-20240417-del-triage-internal-project-meeting-pptx
- [x] sharepoint_protein-science-documents-internal-seed-projects-monthly-umbrella-meetings-20240515-del-triage-internal-project-meeting-pptx

### Ligandability assay meetings  (4)

- [x] sharepoint_protein-science-documents-ligandability-assay-03092023-lucid-chard-ligandability-leadid-mod-pdf
- [x] sharepoint_protein-science-documents-ligandability-assay-ligandability---early-discovery-meeting-04062023-pptx
- [x] sharepoint_protein-science-documents-ligandability-assay-meetings-03102023-03102023-ligandability-team-meeting-pptx
- [x] sharepoint_protein-science-documents-ligandability-assay-meetings-03222023-03222023-ligandability-team-meeting-pptx

### External presentations — 2021 Keystone TPD review  (1)

- [x] sharepoint_protein-science-documents-external-presentations-2021-keystone-targeted-protein-degradation-keystone-review-kl-pptx

### Loka ML 2024-09-09 PS bulk-info handoff  (1)

- [x] sharepoint_protein-science-documents-loka-ml-20240909-bulk-info-for-ps-xlsx

### LC/MS QC per-clone reports — bulk evidence dump, Phase 6 sampling only  (1225)

Per-clone LC/MS intact-protein QC reports (2018-2023). Same shape as the Batch 21 error-log dumps — bulk evidence, not knowledge per se. A small representative sample may be lifted into `methods/lcms-qc-reports.md` at Phase 6 lint time, anchoring the QC pipeline; absorbing 1,225 individually would not improve wiki signal. Year coverage: 2018 (25), 2019 (78), 2020 (249), 2021 (252), 2022 (421), 2023 (200).

- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2018-reports-2018-09-16-nbvc-n19-1b-mass-pptx  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2018-reports-2018-09-16-necc-n6-1a-mass-pptx  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2018-reports-2018-09-16-necc-n6-1b-mass-pptx  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2018-reports-2018-09-18-nbvc-n4-1c-mass-pptx  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2018-reports-2018-09-21-necc-n5-1a-mass-pptx  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2018-reports-2018-09-28-necc-n12-1a-mass-pptx  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2018-reports-2018-09-28-necc-n12-7a-mass-pptx  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2018-reports-2018-10-11-ms-of-co-elute-zap70-pptx  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2018-reports-2018-10-11-ms-of-sec-peak-of-ccbl-pgl-pptx  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2018-reports-2018-10-12-ms-mb204-sec-r1-c12-pptx  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2018-reports-2018-10-12-ms-mb204-sec-r1andr2-pptx  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2018-reports-2018-10-13-cblb-delta-ring-steffan-pptx  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2018-reports-2018-10-13-e2-miki-pptx  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2018-reports-2018-10-13-e2-ubi-miki-impurity-pptx  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2018-reports-2018-10-13-e2-ubi-miki-pptx  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2018-reports-2018-10-13-zap70-d461n-miki-pptx  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2018-reports-2018-10-15-necc-n39-1a-pptx  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2018-reports-2018-10-24-crbn-ddb1-js-mass-pptx  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2018-reports-2018-10-31-crbn-ddb1-js-72h-25deg-mass-peak1-pptx  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2018-reports-2018-10-31-crbn-ddb1-js-72h-25deg-mass-peak2-pptx  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2018-reports-2018-10-31-crbn-ddb1-js-72h-25deg-mass-pptx  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2018-reports-2018-10-31-crbn-ddb1-n19-ea-72h-25deg-mass-peak1-pptx  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2018-reports-2018-10-31-mb204-eileen-pptx  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2018-reports-2018-12-16-necc-n45-1a-stefan-pptx  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2018-reports-ccbl-in-vitro-biotinylated-pptx  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-081220-qc-ne-n338-2a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-081519-qc-n114-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-081519-qc-n115-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-081519-qc-n43-2a-1-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-081519-qc-n43-2a-2-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-082319-qc-n114-2a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-082319-qc-n114-3a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-082319-qc-n115-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-082319-qc-n119-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-082619-qc-mb204-8-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-083019-protein-qc-n114-n117-n119-v2-pptx  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-083019-protein-qc-n117-pptx  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-090419-largescalepurif-n131-1a-pptx  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-090619-qc-126-pt-pptx  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-090619-qc-n120-1a-pptx  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-091019-qc-n120-1a-01-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-091019-qc-n120-1a-02-intactproteinreport-1-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-091019-qc-n120-1a-02-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-091019-qc-n120-1a-03-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-091119-qc-n131-1a-1-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-091119-qc-n131-1a-2-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-091119-qc-n131-1a-3-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-092319-qc-kras-apo-necc-n49-5a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-092319-qc-nc121-1c-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-092319-qc-nc121-1d-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-092319-qc-nc126-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-092319-qc-nc126-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-092319-qc-nc135-1c-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-092319-qc-nc135-1d-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-092319-qc-nc136-1c-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-092319-qc-nc136-1d-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-092319-qc-nc137-1c-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-092319-qc-nc137-1d-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-092319-qc-nc138-1c-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-092319-qc-nc138-1d-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-092319-qc-nc139-1c-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-092319-qc-nc139-1d-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-092519-qc-n144-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-092519-qc-n30-atp-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-092519-qc-n30-ms-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-092519-qc-n30-pcp-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-092519-qc-n42-atp-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-092519-qc-n42-ms-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-092519-qc-n42-pcp-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-093019-qc-n120-1a-phospho-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-093019-qc-n145-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-093019-qc-n145-intactproteinreport-v2-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-100419-qc-n140-4-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-100419-qc-n143-5-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-100419-qc-n149-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-100719-qc-n115-2a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-100719-qc-n149-1a-2-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-100819-zap70-atp1h-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-100819-zap70-atp3h-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-100819-zap70-atpon-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-100819-zap70-pnp1h-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-100819-zap70-pnp3h-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-100819-zap70-pnpon-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-110119-qc-ipa-n55-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-110119-qc-ipa-n55-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-110119-qc-ipa-n61-1a-intactproteinreport-1-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-110119-qc-ipa-n61-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-110119-qc-ipa-n61-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-111109-qc-n140-3a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-111109-qc-n142-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-112219-qc-n102-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-112219-qc-n98-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-120519-qc-n145-1b-intactproteinreport-2-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-120519-qc-n145-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-120519-qc-n145-2a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-120619-loadqc-kras-n136-1c-10ug-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-120619-loadqc-kras-n138-1c-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-121619-qc-n60-1e-eh-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-121619-qc-n60-1e-pf-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-121619-qc-n71-2b-eh-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-121619-qc-n71-2b-pf-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-121619-qc-n72-1d-eh-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2019-reports-121619-qc-n72-1d-pf-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-010620-qc-n101-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-010620-qc-n102-3a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-010620-qc-n86-3a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-010620-qc-n96-2a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-010720-n98-1a-endoh-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-011520-n115-4a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-011520-n145-3a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-011520-n148-2a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-012920-qc-n118-2a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-012920-qc-n120-1d-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-012920-qc-n189-a1-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-012920-qc-n189-a2-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-012920-qc-n418-1a-manual-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-012920-qc-n427-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-020420-native-newcol-n136-1d-5ug-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-020420-native-newcol-n136-1e-5ug-v2-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-020420-native-newcol-n138-1d-5ug-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-020420-native-newcol-n138-1e-5ug-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-020420-qc-n136-1d-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-020420-qc-n136-1e-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-020420-qc-n138-1d-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-020420-qc-n138-1e-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-020620-qc-n117-1-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-020620-qc-n117-2-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-020620-qc-n189-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-020720-n102-4a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-020720-n102-4b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-020720-n96-3b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-021020-blk09-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-021020-n112-6a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-021020-qc-n189-1b-2-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-021220-qc-n189-1b-3-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-021920-qc-n102-4c-intactproteinreport-1-1-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-021920-qc-n102-4c-intactproteinreport-1-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-021920-qc-n102-4c-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-021920-qc-n102-5a-intactproteinreport-1-1-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-021920-qc-n102-5a-intactproteinreport-1-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-021920-qc-n102-5a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-021920-qc-n71-3a-endoh-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-021920-qc-n71-3a-pngf-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-021920-qc-n98-3a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-022520-qc-n112-2a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-022520-qc-n117-2a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-022520-qc-n98-3a-intactproteinreport-1-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-022520-qc-n98-3a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-022520-qc-n98-3b-intactproteinreport-1-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-022520-qc-n98-3b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-022520-qc-n98-3c-intactproteinreport-1-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-022520-qc-n98-3c-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-030920-qc-n86-5a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-030920-qc-n96-4a-intactproteinreport-1-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-030920-qc-n96-4a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-030920-qc-n96-4b-intactproteinreport-1-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-030920-qc-n96-4b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-030920-qc-n98-3e-intactproteinreport-1-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-030920-qc-n98-3e-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-041320-irak4-np-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-041320-irak4-np-pm-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-041320-irak4-p-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-041320-irak4-p-pm-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-041320-kras-load-check-041320-kras-121-gdp-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-041320-kras-load-check-041320-kras-121-pcp-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-041320-kras-load-check-041320-kras-135-gdp-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-041320-kras-load-check-041320-kras-135-pcp-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-041320-kras-load-check-041320-kras-136-gdp-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-041320-kras-load-check-041320-kras-136-pcp-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-041320-kras-load-check-041320-kras-137-gdp-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-041320-kras-load-check-041320-kras-137-pcp-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-041320-kras-load-check-041320-kras-138-gdp-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-041320-kras-load-check-041320-kras-138-pcp-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-041320-kras-load-check-041320-kras-139-gdp-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-041320-kras-load-check-041320-kras-139-pcp-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-041320-nb-119-1b-dp-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-041320-nb-119-1b-dp-pm-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-041320-nb-119-1b-np-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-041320-nb-119-1b-np-pm-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-041320-nb-119-1b-p-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-041320-nb-119-1b-p-pm-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-041320-nb-12-8a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-041320-nb-131-2a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-041320-nb-200-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-041320-nb-201-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-041320-ne-117-3a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-042320-n209-1a-high-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-042320-n209-1a-low-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-042720-n210-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-042720-n252-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-042820-n209-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-050420-necc-n216-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-050420-necc-n255-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-050420-necc-n255-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-050620-nbvc-n37-7a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-051320-nbvc-n131-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-051320-nbvc-n132-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-051320-nbvc-n30-6a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-051320-necc-n216-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-051320-necc-n216-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-051320-necc-n255-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-051320-necc-n255-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-051920-necc-n042-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-051920-necc-n131-1a-intactproteinreport-1-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-051920-necc-n131-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-051920-necc-n132-1a-intactproteinreport-1-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-051920-necc-n132-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-051920-necc-n133-1a-intactproteinreport-1-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-051920-necc-n133-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-051920-necc-n216-1a-10ug-intactproteinreport-1-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-051920-necc-n216-1a-10ug-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-051920-necc-n216-1b-10ug-intactproteinreport-1-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-051920-necc-n216-1b-10ug-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-051920-necc-n255-1a-10ug-intactproteinreport-1-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-051920-necc-n255-1a-10ug-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-051920-necc-n255-1b-10ug-intactproteinreport-1-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-051920-necc-n255-1b-10ug-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-060120-necc-n247-3a-intactproteinreport-1-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-060120-necc-n247-3a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-060120-necc-n261-1a-intactproteinreport-1-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-060120-necc-n261-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-061020-n174-1g-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-061020-n247-3a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-061020-n261-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-061020-n261-1c-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-061220-n131-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-061220-n132-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-061220-n133-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-061220-n216-2a-intactproteinreport-1-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-061220-n216-2a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-061220-n288-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-061720-ne-268-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-061720-ne-271-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-061720-ne-272-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-061720-ne-273-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-061720-ne-278-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-062320-ne-n279-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-062320-ne-n279-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-063020-nb139-2b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-063020-ne-n277-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-063020-ne-n277-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-063020-ne280-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-070620-craf-kd-abcam-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-070620-ne-n261-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-071420-qc-ne-n101-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-071420-qc-ne-n132-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-071420-qc-ne-n133-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-071420-qc-ne-n247-3b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-071420-qc-ne-n291-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-072720-nb164-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-072720-nb164-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-072720-ne132-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-072720-ne208-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-072720-ne257-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-072720-ne259-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-072720-ne259-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-072720-ne273-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-072720-ne291-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-072720-ne309-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-072720-ne310-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-073120-nb-n164-1c-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-073120-nb-n164-1d-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-073120-nb-n165-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-073120-ne-n210-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-073120-ne-n302-1a-3ug-native-v3-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-073120-ne-n302-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-073120-ne-n38-2a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-073120-ne-n38-2b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-073120-ne-n38-2c-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-081220-qc-nb-n165-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-081720-nb-n124-10a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-081720-nb-n124-10b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-081920-ne-n313-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-081920-ne-n343-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-081920-ne-n343-2a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-082720-nb163-2a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-082720-ne115-5a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-082720-ne145-4a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-090320-nb-n85-2b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-090320-nb-n85-2c-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-090320-nb-n85-2c-maxent-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-090320-ne-n115-2b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-090320-ne-n115-5a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-090820-ne-n291-1b-rpt-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-090820-ne-n291-2a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-091720-nb-n098-3h-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-091720-nb-n214-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-092120-nativeqc-ne-n172-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-092120-nativeqc-ne-n172-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-092120-nativeqc-ne-n303-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-092120-nativeqc-ne-n303-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-092120-nb-n225-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-092120-ne-n172-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-092120-ne-n172-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-092120-ne303-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-092120-ne303-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-100220-nb-n115-6a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-100220-nb-n145-5a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-100220-nb-n212-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-100220-nb-n212-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-101320-adar1cat-sanofi-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-101320-ne-n273-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-101320-ne-n346-3a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-101320-ne-n38-3a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-101320-ne-n38-3b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-101920-nb-n247-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-101920-ne-n288-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-101920-ne-n294-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-102920-321h-gnhcl-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-102920-321h-organic-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-102920-craf-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-102920-nb-n102-5b-endoh-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-102920-nb-n102-5b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-102920-nb-n86-5b-endoh-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-102920-nb-n86-5b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-102920-ne-344-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-102920-ne-n216-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-110620-nb-n86-5c-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-110620-nb-n92-3b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-110620-nb-n96-3a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-110620-ne-n163-4a-intactproteinreport-new-quantitation-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-110620-ne-n163-4a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-110620-ne-n291-2b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-110620-ne-n399-2a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-111320-adar-catalytic-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-111320-n284-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-111320-n286-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-111320-nbvc-n005-n025-3a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-111320-nbvc-n131-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-111320-nbvc-n163-3a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-111320-necc-n48-5a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-111320-necc-n48-5a-native-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-111320-necc-n48-5b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-111320-necc-n48-5b-native-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-111320-nxxc-n266-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-112320-nbvc-n163-3b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-112320-nbvc-n238-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-112320-nbvc-n238-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-112420-nbvc-n00131-1c-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-112420-nbvc-n00131-1d-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-112420-nbvc-n00131-1e-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-112420-necc-n115-2c-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-120420-ne-n50-5a-native-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-12042020-btk-jak1-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-12042020-nbvc-n00131-1d-new-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-12042020-nbvc-n00131-1e-new-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-12042020-necc-n00050-5a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-12112020-necc-n00216-2b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-12112020-necc-n284-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-12182020-nbvc-n00209-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-12182020-necc-n00266-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2020-reports-12182020-necc-n00286-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-01132021-nbvc-n225-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-01132021-necc-n292-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-01132021-necc-n293-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-012121-qc-adar-cat-viva-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-012121-qc-ne-n198-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-012121-qc-ne-n284-3a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-012121-qc-ne-n420-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-012121-qc-ne-n421-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-012121-qc-ne-n422-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-012121-qc-ne-n423-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-01292021-ne-n198-1b-native02-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-02012021-nbvc-n098-4b-acn-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-02102021-adar1-p110-sino-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-02102021-adar2-fl-sino-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-02102021-nbvc-n225-3a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-02122021-nbvc-n163-5a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-02222021-nbvc-n163-9a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-02222021-necc-n147-1a-intactproteinreport-2-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-02222021-necc-n147-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-02222021-necc-n286-2a-intactproteinreport-4-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-02222021-necc-n286-2a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-030521-n147-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-030521-n432-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-030521-n435-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-031021-fbw7-skp1-check-df20-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-031021-necc-n00429-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-031221-ne-n478-1a-gdp-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-031221-ne-n478-1a-gmppnp-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-031221-ne-n478-2a-gdp-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-031221-ne-n478-2a-gmppnp-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-031921-nbvc-n251-soluble-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-031921-necc-n313-1b-intactproteinreport-1-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-031921-necc-n344-3a-intactproteinreport-1-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-031921-necc-n443-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-031921-necc-n450-1a-intactproteinreport-1-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-031921-necc-n450-1b-intactproteinreport-1-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-031921-necc-n450-1c-intactproteinreport-1-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-031921-necc-n493-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-031921necc-n443-1b-intactproteinreport-1-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-033121-n344-met-v2-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-033121-necc-n273-4a-v2-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210226-dtl-ae-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210226-dtl-cl-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210226-dtl-eg-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210226-dtl-el-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210226-nbvc-n00365-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210401-necc-n005-n025-regq-3200-intactproteinreport-1-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210402-necc-n413-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210402-necc-n414-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210402-necc-n453-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210402-necc-n453-2a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210402-necc-n466-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210402-necc-n466-2a-intactproteinreport-1-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210405-necc-n273-4b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210405-necc-n273-4c-intactproteinreport-1-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210405-necc-n273-4d-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210405-necc-n273-4e-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210408-nbvc-n360-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210409-necc-273-4f-intactproteinreport-1-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210416-necc-n115-6b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210416-necc-n115-6c-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210423-nbvc-n360-1a-endoh-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210423-nbvc-n360-1a-pp-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210423-necc-n174-2a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210423-necc-n412-elution-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210423-necc-n412-truncated-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210423-necc-n413-elution-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210423-necc-n414-truncated-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210427-nbvc-n366-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210427-nbvc-n366-1a-pp-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210427-necc-n268-3a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210427-necc-n273-5a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210427-necc-n273-5b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210430-nbvc-n005-7a-nbvc-n025-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210430-nbvc-n367-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210430-nbvc-n368-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210430-necc-n446-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210430-necc-n447-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210506-nbvc-n353-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210506-nbvc-n354-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210506-necc-n5-6b-n25-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210513-nbvc-n368-2a-ce00-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210517-nbvc-n366-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210521-necc-n257-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210521-necc-n257-1c-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210521-necc-n257-1d-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210521-necc-n493-2a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210524-necc-n466-3a-new-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210604-nbvc-n366-5a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210604-necc-n346-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210604-necc-n502-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210611-nbvc-n98-5a-acn50-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210611-necc-n366-6a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210617-nbvc-n225-4a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210617-necc-n360-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210617-necc-n422-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210617-necc-n533-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210702-nbvc-n366-6c-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210702-necc-n450-1c-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210709-nbvc-n366-6d-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210709-nbvc-n370-endoh-intactproteinreport-new-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210709-nbvc-n370-endoh-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210709-nbvc-n370-intactproteinreport-new-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210709-nbvc-n370-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210709-nbvc-n370-pngasef-intactproteinreport-new-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210709-nbvc-n370-pngasef-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210709-nbvc-n371-endoh-intactproteinreport-new-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210709-nbvc-n371-endoh-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210709-nbvc-n371-intactproteinreport-new-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210709-nbvc-n371-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210709-nbvc-n371-pngasef-intactproteinreport-new-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210709-nbvc-n371-pngasef-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210709-nbvc-n372-endoh-intactproteinreport-new-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210709-nbvc-n372-endoh-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210709-nbvc-n372-intactproteinreport-new-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210709-nbvc-n372-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210709-nbvc-n372-pngasef-intactproteinreport-new-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210709-nbvc-n372-pngasef-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210709-necc-n225-4b-intactproteinreport-1-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210709-necc-n248-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210709-necc-n248-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210709-necc-n252-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210709-necc-n544-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210709-necc-n548-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210715-necc-n536-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210726-nbvc-n071-9b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210726-nbvc-n371-1a-intactproteinreport-1-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210726-nbvc-n384-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210726-necc-n209-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210726-necc-n209-2a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210726-necc-n210-2a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210726-necc-n539-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210726-necc-n539-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210726-viva-adar1-cd-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210730-nbvc-n071-9b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210730-nbvc-n384-1a-fa-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210730-nbvc-n384-1b-fa-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210730-nbvc-n388-1a-fa-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210730-necc-n182-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210730-necc-n426-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210730-viva-adar1-cd-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210813-nb-n397-1a-irf6-analysis-uv-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210813-nb-n397-1a-irf6-intactproteinreport-1-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210813-ne-n348-1a-tet2-intactproteinreport-1-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210813-ne-n348-1b-tet2-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210813-ne-n352-1a-cish-elobc-intactproteinreport-1-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210813-ne-n544-1b-smarca2b-intactproteinreport-1-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210813-ne-n554-1a-smarca4-intactproteinreport-1-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210813-ne-n556-1a-mcrbn-analysis-uv-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210813-ne-n556-1a-mcrbn-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210820-adar1-p110-mf15ap2811-intactproteinreport-1-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210820-adar1-p110-mf15my1811-intactproteinreport-1-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210827-dtl-el-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210827-itch-eg-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210827-itch-el-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210827-itch-pk-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210827-itch-tr-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210827-nbvc-n285-1a-intactproteinreport-1-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210827-nbvc-n394-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210827-nbvc-n394-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210827-nbvc-n398-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210827-nbvc-n398-1a-intactproteinreport-uv-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210827-nbvc-n399-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210827-nbvc-n399-1a-intactproteinreport-uv-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210827-necc-n216-4a-intactproteinreport-1-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210827-necc-n542-1a-intactproteinreport-1-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210830-dcaf1-el-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210830-dcaf1-pa-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210903-chip-eg-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210903-chip-el-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210903-chip-pa-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210903-chip-tr-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210903-nbvc-n366-7a-intactproteinreport-1-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210913-adar1-cat-proteros-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210913-necc-n443-2a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210913-necc-n443-2b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210913-necc-n450-2a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210913-necc-n484-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210913-necc-n573-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210913-necc-n573-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210913-necc-n577-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210913-necc-n577-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210917-nbvc-n379-3a-intactproteinreport-1-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210917-nbvc-n379-3a-intactproteinreport-3-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210917-nbvc-n428-2a-c12-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210917-nbvc-n428-2a-c4-ni-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210917-nbvc-n428-2a-c5-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210917-nbvc-n428-2a-d5-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210924-adar1-his-cat-proteros-1-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210924-adar1-his-cat-proteros-2-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210924-adar1-p110-1231-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210924-adar1-p110-1233-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210924-nbvc-n349-n351-3a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210924-necc-n257-2a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20210924-necc-n443-2b-rerun-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20211001-nbvc-n214-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20211001-necc-n038-2b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20211001-necc-n555-1a-1-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20211001-necc-n555-1a-2-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20211008-nbvc-n379-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20211008-necc-n453-5a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20211008-necc-n554-2a-cut-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20211008-necc-n554-2a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20211008-necc-n578-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20211008-necc-n578-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20211008-necc-n582-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20211008-necc-n582-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20211008-nmac-n026-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20211015-nbvc-n055-2a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20211015-nbvc-n061-2a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20211015-nbvc-n384-2a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20211015-necc-n549-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20211021-necc-n133-1b-auto-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20211021-necc-n549-1a-rerun-auto-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20211021-necc-n549-2a-auto-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20211021-necc-n554-3a-auto-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20211029-ews-fli1-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20211029-necc-n544-2a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20211029-necc-n562-2a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20211029-necc-n611-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20211029-necc-n613-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20211029-necc-n614-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20211112-nbvc-n00349-nbvc-n00351-3b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20211112-necc-n00544-2a8-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20211112-necc-n00544-2b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20211112-necc-n00614-1b-intactproteinreport-1-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20211112-necc-n00614-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20211124-nbvc-n00384-3a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20211124-nbvc-n00385-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20211124-necc-n00257-3a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20211124-necc-n00257-3b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20211124-necc-n00646-1c-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20211124-necc-n00646-1d-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20211124-necc-n00646-1e-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20211124-necc-n00652-1c-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20211124-necc-n00652-1d-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20211124-necc-n00652-1e-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20211124-necc-n00652-1f-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20211124-necc-n643-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20211124-necc-n657-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20211206-necc-n00453-6a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20211206-necc-n00670-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20211206-necc-n00670-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20211206-necc-n00671-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20211206-necc-n428-4a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20211206-nmac-n00026-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20211206-nmac-n00027-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20211210-necc-n00163-intactproteinreport-new-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20211210-necc-n00344-4a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20211210-necc-n00443-2c-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20211210-necc-n00633-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2021-reports-20211210-necc-n00645-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-202201104-nbvc-n20844-1b-intactproteinreport-v2-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-202201104-nbvc-n20844-1b2-intactproteinreport-v2-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-202201104-necc-n20579-intactproteinreport-v2-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-202201104-necc-n20580-intactproteinreport-v2-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-202201104-necc-n20581-intactproteinreport-v2-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-202201104-necc-n21285-intactproteinreport-v2-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-202201104-necc-n21286-intactproteinreport-v2-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-202201104-necc-n21307-intactproteinreport-v2-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-202201104-necc-n21308-intactproteinreport-v2-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-202201104-necc-n21309-intactproteinreport-v2-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-202201104-necc-n21313-intactproteinreport-v2-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220113-necc-n00163-6a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220113-necc-n00422-2b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220113-necc-n00426-2a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220113-necc-n00442-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220113-necc-n00450-3a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220113-necc-n00453-7a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220113-necc-n00680-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220113-necc-n00681-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220113-nmac-n00024-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220120-nb366-8a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220120-nb366-8b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220120-nb366-8c-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220120-nb368-3b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220120-nb368-3c-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220120-ne257-3c-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220120-ne450-3b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220121-ne662-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220121-ne662-2a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220121-ne688-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220121-ne698-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220128-nbvc-n00071-10a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220128-nbvc-n00448-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220128-nbvc-n428-4b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220128-necc-n00358-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220128-necc-n00553-2a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220128-necc-n00553-2b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220128-necc-n00619-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220128-necc-n00619-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220128-necc-n00620-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220128-necc-n00687-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220128-necc-n643-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220207-nb428-4c-b2-e-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220207-nb428-4c-b2-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220207-nb428-4c-b2-l-intactproteinreport-45kda-55kda-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220207-nb428-4c-b2-l-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220207-nb428-4c-s1-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220207-nb428-4c-w-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220207-ne671-2a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220207-ne715-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220211-nbvc-n00485-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220211-nbvc-n00485-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220211-necc-n00453-7b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220211-necc-n00453-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220211-necc-n00700-0a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220211-necc-n00700-0b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220215-adar1-1a-rerun-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220215-adar1-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220215-adar1-1c-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220218-cish-aviva-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220218-nbvc-n00497-0a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220218-nbvc-n00499-0a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220218-necc-n00451-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220218-necc-n00672-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220225-nbvc-n00497-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220225-nbvc-n00499-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220225-necc-n715-1b-0-2-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220225-necc-n715-1b-0-4-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220228-necc-n00422-1c-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220304-nbvc-n00448-2a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220304-nbvc-n00448-2b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220304-necc-n00015-41-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220304-necc-n00257-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220304-necc-n00422-1c-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220304-necc-n00700-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220304-necc-n716-1a-1-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220304-necc-n716-1a-2-2-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220311-necc-n00014-16-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220311-necc-n00715-1c-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220311-necc-n00721-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220311-necc-n00722-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220328-nbvc-n0002-btk-ref-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220328-nbvc-n0011-1a-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220328-necc-n00442-1a-20-80b-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220328-necc-n00687-2a-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220328necc-n00442-1b-20-80b-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220411-nbvc-n00485-2a-html-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220411-nbvc-n00485-2b-html-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220411-nbvc-n00504-1a-html-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220411-necc-n00257-3b-1-html-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220411-necc-n00257-3b-2-html-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220411-necc-n00257-3b-3-html-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220411-necc-n00473-1a-html-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220411-necc-n00637-1a-html-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220411-necc-n00637-1b-html-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220411-necc-n00744-html-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220411-necc-n717-1a-b5-html-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220418-nbvc-n00007-1a-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220418-nbvc-n00505-1a-html-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220418-nbvc-n00529-0a-html-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220418-nbvc-n00530-0a-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220418-necc-n00694-1a-html-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220418-necc-n00695-1a-html-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220418-necc-n00696-1a-html-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220418-trip12---ctrl-re-html-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220418-trip12---el-re-html-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220418-trip12---tr-re-html-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220418-uhrf1---ctrl-re-html-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220418-uhrf1---pk-re-html-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220419-del-1-html-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220419-del-2-html-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220419-del-3-html-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220419-lit-1-html-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220419-lit-2-html-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220419-lit-3-html-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220419-nbvc-n00506-1a-html-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220419-necc-n00133-bcat-html-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220419-necc-n00553-siah-html-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220419-necc-n00616-2a-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220419-necc-n00717-aa-html-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220427-nbvc-n00530-0a-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220427-necc-n00453-8a-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220427-necc-n00525-1a-necc-n00722-2a-html-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220427-necc-n366-9a-html-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220506-nbvc-n00503-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220506-nbvc-n00504-2a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220506-necc-n00145-5b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220506-necc-n00182-4a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220506-necc-n00182-4b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220506-necc-n00544-1c-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220506-necc-n00645-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220506-necc-n00645-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220506-necc-n714-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220506-trip12-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220513-nbvc-n503-1a-rerun-intactproteinreport-2-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220513-necc-n645-1a-rerun-ce05-intactproteinreport-1-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220513-necc-n645-1a-rerun-ce10-intactproteinreport-1-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220513-necc-n645-1b-rerun-ce05-intactproteinreport-1-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220513-necc-n645-1b-rerun-ce10-intactproteinreport-1-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220513-necc-n657-2a-4-intactproteinreport-2-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220513-necc-n657-2a-6-intactproteinreport-1-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220520-nativeqc-desi-nras-ccr1-9ug-slow-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220523-nbvc-n00366-8d-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220523-nbvc-n00366-8e-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220527-nbvc-n00005-nbvc-n00025-7b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220527-necc-n00038-2e-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220527-necc-n00689-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220527-necc-n00807-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220527-necc-n00807-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220527-necc-n00807-1c-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220527-rnf4-5000-ng-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220603-nbvc-n00329-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220603-nbvc-n00503-1b-guan-hcl-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220603-nbvc-n414-2a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220603-necc-n00524-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220603-necc-n804-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220603-necc-n805-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220613-nbvc-n504-4a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220613-nbvc-n667-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220613-necc-n714-2a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220620-necc-n00627-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220620-necc-n00827-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220624-nbvc-n00351-n00348-6a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220624-necc-n00807-3a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220624-necc-n00807-3b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220630-nbvc-n00383-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220630-nbvc-n00383-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220630-nbvc-n20913-3a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220630-nbvc-n20916-3a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220708-nbvc-n00131-7a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220708-nbvc-n00131-7b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220708-nbvc-n00132-3a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220708-nbvc-n00132-3b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220708-nbvc-n406-2a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220708-nbvc-n627-2a-intactproteinreport-1-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220708-nbvc-n627-2a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220708-necc-n21146-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220708-necc-n21147-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220708-necc-n714-2b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220708-nemo-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220715-nbvc-n00585-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220715-necc-n21144-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220715-necc-n21145-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220715-necc-n21165-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220715-necc-n714-3a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220715-necc-n833-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220715-necc-n839-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220715-necc-n840-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220715-necc-n841-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220715-necc-n842-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220715-necc-n844-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220715-necc-n845-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220715-necc-n846-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220715-necc-n849-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220722-nbvc-n00351-n00348-7a-intactproteinreport-1-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220722-nbvc-n00625-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220722-nbvc-n00625-1c-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220722-nbvc-n20822-2a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220722-nbvc-n20825-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220722-nbvc-n20826-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220722-nbvc-n20832-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220722-necc-n00835-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220722-necc-n00836-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220722-necc-n714-4a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220729-nbvc-n00504-4a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220729-necc-n00216-5a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220729-necc-n00216-5b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220729-necc-n00687-3a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220729-necc-n21179-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220729-necc-n21180-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220729-necc-n21181-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220729-necc-n21182-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220729-necc-n853-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220729-necc-n854-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220729-necc-n855-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220805-nbvc-n00005-n00025-7c-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220805-nbvc-n00585-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220805-nbvc-n00585-1c-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220805-nbvc-n00585-1d-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220805-nbvc-n00585-1e-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220805-necc-n00808-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220805-necc-n00808-1c-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220805-necc-n7142a-mycn-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220815-necc-n000011-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220815-necc-n00006-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220815-necc-n00007-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220815-necc-n00802-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220815-necc-n00802-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220815-necc-n21170-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220815-necc-n21171-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220819-nbvc-n20572-3a-intactproteinreport-p-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220819-nbvc-n20572-3a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220819-nbvc-n20833-2a-intactproteinreport-p-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220819-nbvc-n20833-2a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220819-nbvc-n20834-2a-intactproteinreport-p-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220819-nbvc-n20834-2a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220819-nbvc-n20835-2a-intactproteinreport-p-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220819-nbvc-n20835-2a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220819-nbvc-n20840-2a-intactproteinreport-p-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220819-nbvc-n20840-2a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220819-nbvc-n20841-1a-intactproteinreport-p-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220819-nbvc-n20841-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220819-nbvc-n20842-1a-intactproteinreport-p-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220819-nbvc-n20842-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220819-necc-n00595-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220819-necc-n00682-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220819-necc-n00846-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220819-necc-n00846-1a-intactproteinreport-rev1-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220819-necc-n00846-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220819-necc-n00846-1b-intactproteinreport-rev1-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220819-necc-n00856-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220819-necc-n21184-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220819-necc-n21185-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220819-necc-n21191-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220819-necc-n21193-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220819-necc-n21195-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220819-necc-n21196-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220819-necc-n21197-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220819-necc-n21198-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220819-necc-n21199-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220819-necc-n21200-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220819-necc-n21201-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220819-necc-n21202-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220822-nbvc-n20841-1a-intactproteinreport-p-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220822-nbvc-n20841-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220822-nbvc-n20842-1a-intactproteinreport-p-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220822-nbvc-n20842-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220826-nbvc-n00397-5a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220826-nbvc-n20559-9a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220826-necc-n00846-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220826-necc-n00846-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220826-necc-n21187-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220826-necc-n21210-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220826-necc-n21213-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220901-nbvc-n00383-2b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220901-nbvc-n20818-002a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220901-nbvc-n20821-003a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220901-necc-n00857-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220901-necc-n745-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220901-necc-n757-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220906-anx-bavi-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220906-anx-nobavi-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220906-aurka-kd-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220909-necc-n20559-1c-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220915-nbvc-n00366-9a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220915-nbvc-n00368-4a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220923-nbvc-n00469-001a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220923-nbvc-n20849-001a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220923-necc-n21191-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220923-necc-n21193-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220923-necc-n21195-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220923-necc-n21199-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220923-necc-n21235-001a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220923-necc-n747-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220923-necc-n775-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220929-nbvc-n00636-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20220929-necc-n21290-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221003-nbvc-n00585-1f-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221003-nbvc-n00585-1g-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221003-nbvc-n00585-1h-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221003-nbvc-n00585-1i-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221003-nbvc-n00585-1j-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221003-necc-n00827-2a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221003-necc-n21258-001a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221003-necc-n21259-001a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221005-nbvc-n00636-2-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221005-nbvc-n00636-3-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221005-nbvc-n20381-001a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221007-nbvc-n00658-1-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221007-necc-n00038-2f-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221007-necc-n00827-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221007-necc-n21284-001a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221014-nbvc-n20816-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221014-nbvc-n20817-1k-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221014-nbvc-n20817-1l-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221018-nbvc-n20725-002a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221018-nbvc-n20816-1c-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221018-necc-n21187-001a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221021-necc-n21169-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221021-necc-n21209-001a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221021-necc-n21209-001b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221021-necc-n858-a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221021-necc-n858-b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221031-nbvc-n20844-001a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221031-necc-n21219-001a-intactproteinreport-v2-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221031-necc-n21242-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221031-necc-n21249-001a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221031-necc-n21255-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221111-nbvc-n20437-intactproteinreport-v2-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221111-nbvc-n20865-1a-intactproteinreport-v2-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221111-nbvc-n20866-1a-intactproteinreport-v2-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221111-ncmp-n20030-001a-intactproteinreport-v2-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221111-necc-n20472-001a-intactproteinreport-v2-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221111-necc-n20472-001b-intactproteinreport-v2-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221111-necc-n21305-001a-intactproteinreport-v2-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221111-necc-n21306-001a-intactproteinreport-v2-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221111-necc-n21314-intactproteinreport-v2-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221118-n71-8a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221118-n71-8a-lb-ph-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221118-nbvc-n00384-5a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221118-nbvc-n20816-1d-intactproteinreport-v2-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221118-nbvc-n20816-1e-intactproteinreport-v2-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221118-nbvc-n20816-1f-intactproteinreport-v2-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221118-nbvc-n20816-1g-intactproteinreport-v2-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221118-nbvc-n20817-1m-intactproteinreport-v2-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221118-nbvc-n20817-1n-intactproteinreport-v2-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221118-nbvc-n20817-1o-intactproteinreport-v2-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221118-nbvc-n20817-1p-intactproteinreport-v2-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221118-necc-n20569-n00564-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221118-necc-n20570-n00565-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221118-necc-n20575-n00570-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221118-necc-n20577-n00572-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221118-necc-n21260-1a-intactproteinreport-v2-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221118-necc-n21261-1a-intactproteinreport-v2-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221118-necc-n21308-1a-intactproteinreport-v2-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221122-nbvc-n00469-2a-intactproteinreport-v2-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221122-nbvc-n00469-2b-intactproteinreport-v2-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221122-nbvc-n20676-1a-intactproteinreport-v2-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221122-necc-21300-mes-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221122-necc-21300-pa-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221122-necc-21311-mes-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221122-necc-21311-pa-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221202-nbvc-n20816-1h-intactproteinreport-v2-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221202-nbvc-n20816-1i-intactproteinreport-v2-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221202-nbvc-n20816-1j-intactproteinreport-v2-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221202-nbvc-n20816-1k-intactproteinreport-v2-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221202-nbvc-n20817-1q-intactproteinreport-v2-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221202-nbvc-n20817-1r-intactproteinreport-v2-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221202-nbvc-n20817-1s-intactproteinreport-v2-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221202-nbvc-n20817-1t-intactproteinreport-v2-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221202-nbvc-n20839-001a-intactproteinreport-v2-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221202-nbvc-n20941-8a-intactproteinreport-v2-1-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221202-nbvc-n20942-3a-intactproteinreport-v2-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221202-nbvc-n20943-2a-intactproteinreport-v2-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221202-nbvc-n20944-2a-intactproteinreport-v2-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221202-nbvc-n20945-7a-intactproteinreport-v2-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221202-necc-n20465-001a-intactproteinreport-v2-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221214-anx-n534-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221214-anx-n534-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221214-nbvc-n534-1b-sec-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221216-nbvc-n20725-001a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221216-ncmp-n20031-001a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221216-necc-n21317-001a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221216-necc-n21317-001b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221216-necc-n21317-001c-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221216-necc-n21317-001d-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221216-necc-n21327-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221216-necc-n21327-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20221216-necc-n21327-1c-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20230310-klhdc3-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20230310-nbvc-n20879-2a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20230310-necc-n00554-2b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20230310-necc-n21311-pa-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20230310-necc-n21317-2b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20230310-necc-n21317-2c-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20230310-necc-n21319-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20230310-necc-n21368-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20230310-necc-n21392-mesna-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20230310-usp18-isg15-ctd-pa-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20230310-wdr26-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20230811-nbvc-n20776-002a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20230811-ncmp-n20044-3a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20230811-necc-n21449-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20230811-necc-n21495-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20230811-necc-n21496-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20240112-n15-41-2b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20240112-nbvc-n20879-5a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-20240112-necc-n21635-001a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-nbvc-n20412-001a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-nbvc-n20601-4b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-nbvc-n20816-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-nbvc-n534-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-nbvc-n534-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-necc-n21308-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-necc-n21316-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-necc-n21317-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-necc-n21318-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-necc-n21319-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-necc-n21327-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-necc-n21332-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2022-reports-necc-n21333-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230106-dcaf15-ddb1-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230106-fbxw5-ft-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230106-fbxw5-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230106-nbvc-n00005-6c-nbvc-n00025-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230106-nbvc-n20817-1u-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230106-nbvc-n20817-1v-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230106-nbvc-n20817-1w-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230106-nbvc-n20817-1x-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230106-ubr1-ft-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230106-ubr1-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230109-nbvc-n20816-1l-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230109-nbvc-n20816-1m-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230109-nbvc-n20816-1n-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230109-nbvc-n20816-1o-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230109-nbvc-n20879-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230113-nbvc-n20408-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230113-nbvc-n20879-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230113-necc-n00584-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230113-necc-n20481-001a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230113-necc-n20749-002a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230120-nbvc-n20870-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230120-necc-n21328-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230120-necc-n21328-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230120-necc-n21329-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230127-3-d-10-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230127-3-e-1-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230127-4-f-2-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230127-4-f-4-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230127-n21364-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230127-n21368-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230127-n21369-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230127-n21373-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230127-n21375-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230127-necc-n21329-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230127-necc-n21352-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230127-necc-n21353-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230127-necc-n21354-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230127-necc-n21355-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230127-necc-n21357-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230127-necc-n542-2a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230127-necc-n544-3a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230127-necc-n544-3b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230127-necc-n657-2a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230203-nbvc-n20381-001b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230203-nbvc-n20879-002a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230203-necc-n00532-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230203-necc-n20855-001a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230206-nbvc-n485-4a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230206-nbvc-n485-4b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230206-nbvc-n485-4c-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230206-necc-n21337-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230206-necc-n21342-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230210-nbvc-n495-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230210-ncmp-n20035-001a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230210-ncmp-n20035-001b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230210-necc-n20855-001c-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230210-necc-n21361-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230210-necc-n21372-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230210-nmac-n20088-001a-intactproteinreport-1-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230210-nmac-n20089-001a-intactproteinreport-1-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230210-nmac-n20096-001a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230210-nmac-n20098-001a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230217-nbvc-n20863-001a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230217-necc-n00763-necc-n21030-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230217-necc-n00764-necc-n21031-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230217-necc-n21348-001a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230217-necc-n21348-002a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230217-necc-n21349-001a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230217-necc-n21349-002a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230217-necc-n21364-001a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230217-necc-n21367-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230217-necc-n21373-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230217-necc-n21374-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230227-dcaf-16-1-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230227-dcaf-16-2-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230227-nbvc-n20392-001a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230227-nbvc-n20392-001b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230227-nbvc-n20858-001a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230227-nbvc-n20879-003a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230227-ncmp-n20037-001a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230227-necc-n20621-001a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230227-necc-n21348-001a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230227-necc-n21349-001a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230303-nbvc-n20393-1a-intactproteinreport-v2-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230303-nbvc-n20858-1b-intactproteinreport-v2-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230303-necc-n21317-2a-intactproteinreport-v2-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230310-klhdc3-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230310-nbvc-n20879-2a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230310-necc-n00554-2b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230310-necc-n21311-pa-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230310-necc-n21317-2b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230310-necc-n21317-2c-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230310-necc-n21319-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230310-necc-n21368-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230310-necc-n21392-mesna-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230310-usp18-isg15-ctd-pa-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230310-wdr26-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230315-nbvc-n20174-001a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230321-nbvc-n20875-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230321-ncmp-n20035-001b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230321-necc-n20374-002a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230321-necc-n21284-002a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230321-necc-n21355-001a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230321-necc-n21395-001a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230324-nbvc-n00495-002a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230324-nbvc-n00495-002b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230324-nbvc-n20816-1p-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230324-nbvc-n20816-1q-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230324-nbvc-n20816-1r-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230324-nbvc-n20816-1s-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230324-nbvc-n20816-1t-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230324-nbvc-n20817-1aa-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230324-nbvc-n20817-1bb-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230324-nbvc-n20817-1cc-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230324-nbvc-n20817-1y-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230324-nbvc-n20817-1z-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230324-nbvc-n20893-001a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230324-nbvc-n20893-001b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230324-nbvc-n20894-001a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230324-necc-n20954-2a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230324-necc-n21369-001a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230324-necc-n21402-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230403-nbvc-n20816-1u-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230403-nbvc-n20816-1v-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230403-nbvc-n20816-1w-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230403-nbvc-n20816-1x-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230403-nbvc-n20816-1y-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230403-nbvc-n20816-1z-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230403-nbvc-n20817-1dd-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230403-nbvc-n20817-1ee-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230403-nbvc-n20817-1ff-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230403-nbvc-n20817-1gg-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230403-nbvc-n20817-1hh-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230403-nbvc-n20817-1ii-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230403-ncmp-n20008-006a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230403-ncmp-n20039-001a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230403-necc-n21353-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230403-necc-n21354-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230403-necc-n21392-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230407-nbvc-n20817-1aa-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230407-nbvc-n20817-1bb-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230407-nbvc-n20817-1cc-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230407-nbvc-n20817-1dd-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230407-nbvc-n20817-1ee-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230407-nbvc-n20817-1jj-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230407-nbvc-n20817-1kk-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230407-nbvc-n20817-1ll-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230407-nbvc-n20817-1mm-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230407-nbvc-n20817-1nn-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230407-necc-n21030-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230407-necc-n21031-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230407-necc-n21338-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230407-necc-n21353-1b6-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230407-necc-n21354-1h10-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230407-necc-n21359-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230407-necc-n21408-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230407-necc-n21412-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230407-necc-n21413-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230407-necc-n21415-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230407-necc-n21416-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230407-necc-n21417-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230407-necc-n21418-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230417-cdk2-proteros-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230417-nbvc-n20842-1b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230417-nbvc-n20876-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230417-ncmp-n20032-2a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230417-necc-n21378-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230417-necc-n21381-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230421-n2-8a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230421-n20942-3a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230421-nbvc-n20816-1ff-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230421-nbvc-n20816-1gg-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230421-nbvc-n20816-1hh-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230421-nbvc-n20817-1oo-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230421-nbvc-n20822-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230421-ncmp-n20008-005a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230421-ncmp-n20035-001c-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230421-ncmp-n20042-001b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230421-necc-n21362-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230421-necc-n21363-1a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230428-nbvc-20820-2a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230428-nbvc-n20830-001a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230428-nbvc-n20830-001b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230428-ncmp-n20039-001b-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230428-ncmp-n20042-001a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230428-necc-n20958-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230428-necc-n21031-2a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230428-necc-n21416-001a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230428-necc-n21417-001a-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230428-necc-n21425-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230428-necc-n21426-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230428-necc-n21429-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230428-necc-n21430-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230428-necc-n21431-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230428-necc-n21432-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230428-necc-n21433-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230428-necc-n21434-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230428-necc-n21435-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230505-nbvc-n20993-001-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->
- [x] sharepoint_protein-science-documents-ms-lcms-qc-reports-2023-reports-20230505-ncmp-n20039-001c-intactproteinreport-pdf  <!-- skip: bulk_qc_evidence -->

### Lab IT move — PC ipconfig text dumps  (3)

Three `ipconfig` text outputs captured during a Protein Sciences computer move (Akta-A, Nanodrop, Kingfisher). IT operational artifact, no wiki signal.

- [x] sharepoint_protein-science-documents-move-pc-pictures-protein-science-computers-complete-akta-a---di-jsant-0j89yj-di-jsant-0j89yj-ip-config-txt  <!-- skip: it_move_logs -->
- [x] sharepoint_protein-science-documents-move-pc-pictures-protein-science-computers-complete-nanodrop-pc-kingfisher-pc-scientist-computer-kl---elow-m720q-elow-m720q-ip-config-txt  <!-- skip: it_move_logs -->
- [x] sharepoint_protein-science-documents-move-pc-pictures-protein-science-computers-complete-nanodrop-pc-scientist-computer-am---jsantos-m720q-jsantos-m720q-ip-config-txt  <!-- skip: it_move_logs -->

### "Lunches with Chris" — calendar artifacts  (2)

Two scheduling spreadsheets (December 2022, October-November 2022) for informal lunches. Calendar metadata, no decision/method content.

- [x] sharepoint_protein-science-documents-lunches-with-chris-december-2022-xlsx  <!-- skip: ephemeral_calendar -->
- [x] sharepoint_protein-science-documents-lunches-with-chris-october-november-2022-xlsx  <!-- skip: ephemeral_calendar -->

### Superseded DEL-PS goals draft  (1)

A 2025 DEL-PS goals draft explicitly stamped `-old`. The current `del-ps-goals-2025-research-goals-final-docx` (absorbed in Batch 1) supersedes this.

- [x] sharepoint_protein-science-documents-documents-2025-del-ps-goals-old-docx  <!-- skip: superseded_by_2025_research_goals_final -->


---

## OneDrive — pending laptop-side triage

**Why this section exists.** The Cowork session that maintains this queue lives on a Linux container that cannot see Mateo's local OneDrive sync — the OneDrive manifest entries land in `ask_jojo_raw/manifest.json` on the laptop, not in this checked-in copy. Until OneDrive entries either (a) get committed back to the repo or (b) get surveyed and pasted into this file, the OneDrive section is structural placeholder, not real batches.

**One-time triage one-liner (run on the laptop, repo root, venv active):**

```powershell
python -c "import json, collections, pathlib; m=json.loads(pathlib.Path('ask_jojo_raw/manifest.json').read_text()); od=[e for e in m['entries'].values() if e['source_type']=='onedrive']; tops=collections.Counter(e['source_id'].split('/',1)[0] for e in od); print(f'OneDrive entries: {len(od)}'); [print(f'  {n:>5}  {top}') for top, n in tops.most_common()]"
```

That prints `<count> <top-folder-name>` lines sorted by document count. Decide which top-folders are wiki-worthy; surface those folders' files into Batches 23+ (one batch per coherent topic, ~10 entries each). Folders that are clearly ephemeral (Downloads, Pictures, Personal-anything) can go straight to Batch N+1 below as `[x]` with a `<!-- skip: ephemeral_onedrive -->` note.

### Batch 23 — OneDrive top-folder coverage  *(placeholder)*

**Theme:** TBD after the triage one-liner runs. Plan: one ~10-entry batch per most-active OneDrive top-folder (project-coded folders, role-coded folders, etc.). Aim for the same topical-cohesion bar Batches 1-19 use — files within a batch should converge on a few strong wiki pages, not sprawl.

**Connector:** onedrive
**Access level:** owner_only  *(default for OneDrive — adjust per file at absorb time)*

- [ ] *(populate after running the survey one-liner above)*

### Batch 24 — OneDrive misc / small-folder cleanup  *(placeholder)*

**Theme:** OneDrive entries that don't slot cleanly into a Batch 23 top-folder cluster — single-file folders, root-level loose files, cross-folder one-offs. Treat the same way Batch 21 treats SharePoint long-tail — enumerate, skip-tag, surface only what has wiki signal.

**Connector:** onedrive
**Access level:** owner_only

- [ ] *(populate after running the survey one-liner above; expected: ~10-30 entries with mixed `[x]`/`[ ]` ticks)*


---

## Backlog — not yet batched

Loose pool of entries the absorb prompt has flagged but that haven't been grouped into a batch. When writing a new batch heading above, pull from this list and delete the lines you pull. Not every raw entry belongs here — low-signal files (outdated drafts, copy-of-copy variants, meeting no-shows) are absorbed by the lint pipeline's retention pass in Phase 6, not by hand now.

### Scope note (as of 2026-04-24)

The batches above cover sharepoint entries only. `ask_jojo_raw/` also holds ~18k onedrive entries and whatever publicdrive eventually produces, but those live on Mateo's laptop filesystem, not this session's workspace. When running absorb sessions from the laptop, the absorb pipeline sees the full corpus and the queue can point at onedrive / publicdrive entries directly — those batches should be appended here once identified. OneDrive at ~18k entries needs a triage pass first (walk the top-level folders, classify wiki-worthy vs. ephemeral vs. sharepoint-duplicate); only the wiki-worthy folders become batch targets. Publicdrive is likely small enough to survey-then-batch directly.

### Near-duplicate snapshot clusters (representative sample in Batch 16; remainder prunes at Phase 6)

Batch 16 pulls three representatives from each of the three big snapshot clusters. All remaining snapshots in each cluster are pruned at Phase 6 per CLAUDE.md Principle 3 ("pages are knowledge, not records"). If a specific snapshot ever looks load-bearing for a citation, lift it out at absorb time — but don't batch the whole cluster.

- **DDT protein clone database.** 15 additional `delphi-*-ddt-protein-clone-database-*.xlsx` snapshots beyond the three in Batch 16.
- **Delphi user roles.** 16 additional `delphi-roles-definition-delphi-user-roles-YYYYMMDD-xlsx` snapshots beyond the three in Batch 16.
- **Delphi QC reports redesign.** 8 additional `delphi-qc-reports-redesign-*.pptx` variants beyond the three in Batch 16 (Option2/3/original from 2023-04-27 plus five October/November iterations).

### UAT reviewer variants (Phase 6 prune pool — do not batch individually)

Each file listed here is a reviewer-specific annotated copy of a source document already absorbed in Batches 3/4/5. Principle 3 says one page per artifact, not one per reviewer; pull unique reviewer commentary into the corresponding Batch 3/4/5 pages at Phase 6 lint time, don't absorb separately.

- **2021-05-27 ACS UAT reviewer variants (14 files).** The `-eledits-pdf`, `-kl-pdf`, and (additional) `-jose-pdf` copies of the four 2021-05-27 UAT plan docs whose `-jose-docx` masters are in Batch 3.
- **2021-08-29 UAT reviewer copies (2 files).** `copy-of-0-2-advanced-construct-support-*-jose-pdf` and `copy-of-04-advanced-construct-support-*-jose-pdf`.
- **ACS2024.1 extended UAT tickets (6 files).** `20241220-ds-1362`, `20250102-ds-1124`, `20250102-ds-725`, `20250103-ds-1284-testing-results`, `20250214-ds-1283`, `ds-1284-docx` — additional ticket-level UAT docs beyond the six in Batch 4; same release cycle.
- **ACS2025.1 / ACS2025.2 extended UAT tickets (~11 files).** `ds-1298`, two `ds-1300-*` picklist variants, `ds-1300-20250219-uat-testing-picklist-export-error-docx`, `ds-1393`, `ds-1394`, `ds-1396`, `ds-1423`, `ds-1423-emptymwpicklist-error-txt`, `ds-1439`, `ds-1476` case1/2/3 — additional ticket-level UAT beyond Batch 5.
- **2024-05-28 SSEPT UAT testing artifacts (2 files).** `delphi-ssept-testing-checklist-xlsx` and `test-case-1-pptx`.

### Standalone low-signal entries (Phase 6 prune pool)

Ephemeral working files that don't produce wiki knowledge on their own. Listed here so the queue stays truthful but skip for hand-absorb — Phase 6 lint will prune unless a pattern surfaces that the wiki otherwise captures.

- **Annotation / Q&A scratch:** `06072023-df-selections-domains-jose-xlsx`, `20250527-delphi-clone-task-cp-and-pp-questions-pptx`.
- **One-off reconcile / audit artifacts:** `20221111-protein-production-reconcile-clone-dna-sequence-xlsx`, `03052023-protein-production-missing-antibiotic-resistance-for-existing-clones-xlsx`.
- **Test-environment / scratch exports:** `20230914-pptestsprod-el-edits-xlsx`, `20230928-pptestsprod3-xlsx`, `20231011-qcreportexport-qc-report-pptx-2023-10-11-17-18-59-191389-pptx`.
- **Single-ticket evidence dumps:** `20231107-ds882-necc-n21333-001a-xlsx`, `20250403-blankfields-docx`, `20260211-differences-target-forms-not-correctly-assigned-to-project-xlsx` (both `-txt` and `-xlsx` variants).
- **Meeting scratch:** `20240129-meetingwithrob-copy-of-testresultsallenv-xlsx`, `20240129-meetingwithrob-copy-of-updatedsamples-xlsx`, `20240129-meetingwithrob-ppmeeting26jan2024-pptx`.
- **"copy-of" variants of working files:** `20240419-copy-of-jiraissues-testing-el-hb-xlsx`, `20241021-copy-of-invalidaa-xlsx`, `20250129-copy-of-pathdifs-xlsx`.
- **PP-INFO6484 export iteration snapshots (same artifact evolving over 10 days in June 2025).** `20250603-elresponse-copy-of-pp-info6484-lsptmay27`, `20250605-pp-info6484-lspt-04jun-prod-elcomments`, `20250606-pp-info6484-lspt-05jun-prod-exportfromrob`, `20250613-pp-info6484-lspt-12jun-prod-proteinsequenceexport-final`. Collapse at Phase 6 if signal warrants.
- **Informal review docs (undated scope):** `20250812-delphi-review-docx`, `20250820-delphi-review-docx`.
- **Search-result / export artifacts:** `20250812-textsearchciap2-xlsx`, `20250814-textsearchciap12-xlsx`, `20250922-sequence-exports-xlsx`.
- **Herman/John protein-id match snapshots (two snapshots of same artifact, 2026-02 + 2026-04).** `20260225-herman-john-protein-id-his-avi-matches-xlsx`, `20260410-herman-john-protein-id-his-avi-matches-copy-xlsx`.
- **Performance benchmarks (revisit at Phase 6).** `20251118-performance-benchmarks-xlsx` — may deserve its own `decisions/delphi-performance-characterization.md` if a broader perf story exists in OneDrive.
- **Vendor-info proposal (two snapshots).** `20260226-delphi-vendorinfo-proposal-pptx`, `20260311-delphi-vendorinfo-proposal-v2-pptx` — promote to a batch if/when a decision on vendor-info lands.
- **Picklist bug investigation (two snapshots).** `20260309-picklist-bug-pptx`, `20260325-picklist-bug-pptx` — promote if a fix lands and produces a `decisions/` entry.
- **Orphan timeline deck.** `timeline-04192024-pptx` — unclear scope, likely a one-off visualization for a meeting.

### Standalone non-Delphi entries

- `sharepoint_protein-science-documents-coupa-coupa-project-coding-updates-pptx` + `sharepoint_protein-science-documents-coupa-split-billing-functionality-in-coupa-docx` — Coupa (procurement) usage notes. Not worth a batch on their own; may merge into a broader `platforms/coupa.md` page if OneDrive surfaces more Coupa material.
- `sharepoint_protein-science-documents-cyrus-hm-and-cad-training-pptx` — Cyrus homology modeling / CAD training. Pair with computational-biology training material from OneDrive when in scope.
- `sharepoint_protein-science-documents-del-screen-plans-dsa-projects-jsantos04-t480-xlsx` — laptop copy of the DSA projects master list already absorbed in Batch 1; skip unless the diff against the master is meaningful.

### Delphi error-log files

17 `-txt` error-log dumps across 2024-03 through 2026-04 (persistence errors, biomass registration errors, import errors, picklist bugs, etc.). These are bug-report evidence, not knowledge — each one individually is low signal. If there's a systemic pattern (repeated failure mode, specific subsystem fragility), the pattern belongs on a `decisions/` or `runbooks/` page at Phase 6 lint time, not as individual absorb targets now. Skip for Phase 2 first-pass absorb.
