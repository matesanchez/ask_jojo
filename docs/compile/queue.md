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

## OneDrive — pending laptop-side triage

**Why this section exists.** The Cowork session that maintains this queue lives on a Linux container that cannot see Mateo's local OneDrive sync — the OneDrive manifest entries land in `ask_jojo_raw/manifest.json` on the laptop, not in this checked-in copy. Until OneDrive entries either (a) get committed back to the repo or (b) get surveyed and pasted into this file, the OneDrive section is structural placeholder, not real batches.

**One-time triage one-liner (run on the laptop, repo root, venv active):**

```powershell
python -c "import json, collections, pathlib; m=json.loads(pathlib.Path('ask_jojo_raw/manifest.json').read_text()); od=[e for e in m['entries'].values() if e['source_type']=='onedrive']; tops=collections.Counter(e['source_id'].split('/',1)[0] for e in od); print(f'OneDrive entries: {len(od)}'); [print(f'  {n:>5}  {top}') for top, n in tops.most_common()]"
```

That prints `<count> <top-folder-name>` lines sorted by document count. Decide which top-folders are wiki-worthy; surface those folders' files into Batches 22+ (one batch per coherent topic, ~10 entries each). Folders that are clearly ephemeral (Downloads, Pictures, Personal-anything) can go straight to Batch N+1 below as `[x]` with a `<!-- skip: ephemeral_onedrive -->` note.

### Batch 22 — OneDrive top-folder coverage  *(placeholder)*

**Theme:** TBD after the triage one-liner runs. Plan: one ~10-entry batch per most-active OneDrive top-folder (project-coded folders, role-coded folders, etc.). Aim for the same topical-cohesion bar Batches 1-19 use — files within a batch should converge on a few strong wiki pages, not sprawl.

**Connector:** onedrive
**Access level:** owner_only  *(default for OneDrive — adjust per file at absorb time)*

- [ ] *(populate after running the survey one-liner above)*

### Batch 23 — OneDrive misc / small-folder cleanup  *(placeholder)*

**Theme:** OneDrive entries that don't slot cleanly into a Batch 22 top-folder cluster — single-file folders, root-level loose files, cross-folder one-offs. Treat the same way Batch 21 treats SharePoint long-tail — enumerate, skip-tag, surface only what has wiki signal.

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
