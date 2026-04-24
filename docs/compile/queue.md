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

- [ ] sharepoint_protein-science-documents-delphi-20240112-ssept-moi-redesign-pptx
- [ ] sharepoint_protein-science-documents-delphi-20240222-ssept-moi-redesign-pptx
- [ ] sharepoint_protein-science-documents-delphi-20240229-ssept-moi-redesign-pptx
- [ ] sharepoint_protein-science-documents-delphi-20240311-moi-section-pptx
- [ ] sharepoint_protein-science-documents-delphi-20240702-ssept-exceltable-export-import-xlsx
- [ ] sharepoint_protein-science-documents-delphi-20241203-delphi-sseptimporttable-xlsx
- [ ] sharepoint_protein-science-documents-delphi-20241203-ssept-resultsimport-pptx
- [ ] sharepoint_protein-science-documents-delphi-20250114-delphi-sseptimporttable-xlsx
- [ ] sharepoint_protein-science-documents-delphi-20250114-ssept-resultsimport-pptx
- [ ] sharepoint_protein-science-documents-delphi-20250625-delphi-sseptimporttable-updated-xlsx

---

## Batch 8 — Delphi clone / GenScript / Dotmatics integration

**Theme:** The clone-side data flow: how cloned constructs get from GenScript (external DNA vendor) into Delphi, how metadata is tagged (fusion tags, cleavage linkers), how bulk clone imports work, and how Delphi reconciles against Dotmatics inventory. Cohesive "external-systems integration" story. Expected outputs: a `methods/` or `protocols/` page on the GenScript-to-Delphi workflow and a `concepts/` page on protein tagging / cleavage-linker conventions.

**Connector:** sharepoint
**Access level:** all_fte

- [ ] sharepoint_protein-science-documents-delphi-clone-information-to-be-uploaded-from-genscript-pptx
- [ ] sharepoint_protein-science-documents-delphi-com-workflow-tutorial-genscript-usages-pptx
- [ ] sharepoint_protein-science-documents-delphi-com-workflow-tutorial-genscript-usages-2-pptx
- [ ] sharepoint_protein-science-documents-delphi-clone-order-management-clone-order-management-release-notes-v1-1-0-pdf
- [ ] sharepoint_protein-science-documents-delphi-20231120-ds889-cloneidduplications-xlsx
- [ ] sharepoint_protein-science-documents-delphi-20230620-dotmaticsinventory-missingdescriptions-xlsx
- [ ] sharepoint_protein-science-documents-delphi-20250408-clone-import-xlsx
- [ ] sharepoint_protein-science-documents-delphi-20250604-delphi-clone-bulk-import-example-xlsx
- [ ] sharepoint_protein-science-documents-delphi-20250604-delphi-clone-bulk-import-pptx
- [ ] sharepoint_protein-science-documents-delphi-tags-fusion-cleavage-linkers-xlsx

---

## Batch 9 — Delphi project / target harmonization (Chemcart ↔ ChemReg ↔ DNAtag)

**Theme:** A running effort to reconcile project and target naming across Delphi, Chemcart, ChemReg, and the DNAtag system. Spans 2022 through late 2023. Expected outputs: a `decisions/` page on the naming-harmonization decision (why the cross-system mapping was needed, what convention was adopted), and possibly one `concepts/` page on the project-vs-target distinction if the sources warrant it.

**Connector:** sharepoint
**Access level:** all_fte

- [ ] sharepoint_protein-science-documents-delphi-project-target-harmonization-09102023-chemcart-project-and-targets-xlsx
- [ ] sharepoint_protein-science-documents-delphi-project-target-harmonization-20220301-delphi-project-target-name-harmonization-updated-xlsx
- [ ] sharepoint_protein-science-documents-delphi-project-target-harmonization-20230910-delphi-project-target-name-harmonization-updated-xlsx
- [ ] sharepoint_protein-science-documents-delphi-project-target-harmonization-chemreg-project-target-contract-data-xlsx
- [ ] sharepoint_protein-science-documents-delphi-project-target-harmonization-chemreg-project-xlsx
- [ ] sharepoint_protein-science-documents-delphi-project-target-harmonization-delph-dnatag-project-target-list-20230511-jose-annotated09102023-xlsx
- [ ] sharepoint_protein-science-documents-delphi-project-target-harmonization-delph-dnatag-project-target-list-20230511-xlsx
- [ ] sharepoint_protein-science-documents-delphi-project-target-harmonization-delph-dnatag-project-target-list-20230912-xlsx
- [ ] sharepoint_protein-science-documents-delphi-20240924-chad-del-protein-info-export-from-delphi-example-xlsx
- [ ] sharepoint_protein-science-documents-delphi-vectors-not-on-genscript-page-xlsx

---

## Batch 10 — Delphi financials and SOW history

**Theme:** The budget / SOW trail from Delphi's ACS proposal through the Q4 revised project budgets and the maintenance-budget snapshot. Money-flow is distinct enough from UAT mechanics that it deserves its own `decisions/` page rather than being scattered into the ACS batch's pages.

**Connector:** sharepoint
**Access level:** all_fte

- [ ] sharepoint_protein-science-documents-delphi-financials-2020-10-20-advanced-construct-support-estimation-financials-xlsx
- [ ] sharepoint_protein-science-documents-delphi-financials-2020-11-06-advanced-construct-support-estimation-financials-prioritized-xlsx
- [ ] sharepoint_protein-science-documents-delphi-financials-2020-11-06-advanced-construct-support-estimation-prioritized-xlsx
- [ ] sharepoint_protein-science-documents-delphi-financials-campaign-planning-2021-sow---financials-jose-xlsx
- [ ] sharepoint_protein-science-documents-delphi-financials-campaign-planning-2021-sow---financials-xlsx
- [ ] sharepoint_protein-science-documents-delphi-financials-delphi-maintenance-budget-xlsx
- [ ] sharepoint_protein-science-documents-delphi-financials-revised-nurix-project-budgets---q4-xlsx
- [ ] sharepoint_protein-science-documents-delphi-financials-revised-nurix-project-budgets---q4--updated-xlsx
- [ ] sharepoint_protein-science-documents-delphi-campaign-planning-uat-feedback---estimation-sheet---mon-nov-23-2020-pdf
- [ ] sharepoint_protein-science-documents-delphi-campaign-planning-uat-feedback-financial-sow-thu-feb-25-2021-pdf

---

## Batch 11 — DSA early-discovery group meetings (2022) + DEL tech-dev

**Theme:** Closes out the non-Delphi DEL screening story started by Batch 1. The 2022 DSA (Discovery Screening Assay?) updates to the Early Discovery group are a continuous chronological thread; plus the all-DEL tech-dev meeting and the Stat6 DSP table (a specific target-aware DSA artifact). Expected outputs: one or two `decisions/` pages on the DSA project cadence and a possible `targets/stat6.md` anchor. Pairs well with Batch 1's outputs for cross-linking.

**Connector:** sharepoint
**Access level:** all_fte

- [ ] sharepoint_protein-science-documents-all-del-meetings-20231113-20231113-all-del-mtg-techdev-pptx
- [ ] sharepoint_protein-science-documents-del-screen-plans-dsa-projects--gantt-xlsx
- [ ] sharepoint_protein-science-documents-del-screen-plans-dsa-projects-new-gantt-xlsx
- [ ] sharepoint_protein-science-documents-del-screen-plans-dsa-projects-update-early-discovery-20220818-xlsx
- [ ] sharepoint_protein-science-documents-del-screen-plans-dsa-update---early-discovery-group-meeting-20220915-pptx
- [ ] sharepoint_protein-science-documents-del-screen-plans-dsa-update---early-discovery-group-meeting-20220929-pptx
- [ ] sharepoint_protein-science-documents-del-screen-plans-dsa-update---early-discovery-group-meeting-20221013-pptx
- [ ] sharepoint_protein-science-documents-del-screen-plans-dsa-update---early-discovery-group-meeting-20221027-pptx
- [ ] sharepoint_protein-science-documents-del-screen-plans-dsa-update---early-discovery-group-meeting-20221110-pptx
- [ ] sharepoint_protein-science-documents-del-screen-plans-stat6-dsp-tables-jss-xlsx

---

## Backlog — not yet batched

Loose pool of entries the absorb prompt has flagged as worth processing but that haven't been grouped into a batch yet. When writing a new batch heading above, pull from this list (and delete the lines you pull). Not every raw entry belongs here — low-signal files (outdated drafts, copy-of-copy variants, meeting no-shows) are absorbed by the lint pipeline's retention pass in Phase 6, not by hand now.

### Scope note (as of 2026-04-24)

The batches above cover sharepoint entries only. `ask_jojo_raw/` also holds ~18k onedrive entries and whatever publicdrive eventually produces, but those are on Mateo's laptop filesystem, not this session's workspace. When running absorb sessions from the laptop, the absorb pipeline can see the full corpus and the queue can point at onedrive / publicdrive entries directly — those batches should be added here as they're identified.

### Low-signal near-duplicate clusters (absorb a representative sample only)

These clusters are intentionally *not* fully batched because the files are evolutionary snapshots of the same underlying artifact. The CLAUDE.md rule "pages are knowledge, not records" (Principle 3) says the wiki gets one page per artifact synthesizing current state and notable evolution, not one page per snapshot. When batching, pull the earliest + latest + one representative middle snapshot (three to five files max) and let the rest be pruned by the Phase 6 retention pass.

- **DDT protein clone database snapshots (2020-2021).** ~14 `delphi-*-ddt-protein-clone-database-*.xlsx` files from 2020-11 through 2021-11. Produces one `protocols/delphi-ddt-clone-database.md` page describing what the table is and how it's maintained, plus notable schema shifts.
- **Delphi user-roles snapshots.** ~15 `delphi-delphi-roles-definition-delphi-user-roles-YYYYMMDD-xlsx` files from 2022-07 through 2024-08. Produces one `decisions/delphi-user-role-model.md` page describing the role model and how it shifted (CP / PP / AD / DS).
- **Delphi QC reports redesign iterations (Apr-Nov 2023).** ~10 `delphi-delphi-qc-reports-redesign-*.pptx` files — four Option1/2/3/original variants from the 2023-04-27 session plus six follow-up redesigns. Produces one `decisions/delphi-qc-report-redesign.md` page on the final chosen design and why.
- **ACS2025-3 / ACS2026 UAT snapshots.** ~6 `delphi-delphi-uat-reviews-acs2025-3-*` and `acs2026-*` files. Not yet matched to release notes (those release notes may not have surfaced in the corpus yet). Wait until the next sync picks up the corresponding release notes, then batch together.

### Standalone low-priority entries (single-page absorb candidates)

- `sharepoint_protein-science-documents-coupa-coupa-project-coding-updates-pptx` + `sharepoint_protein-science-documents-coupa-split-billing-functionality-in-coupa-docx` — Coupa (procurement software) usage notes. Unlikely to warrant wiki pages on their own; may end up as sections on a broader `platforms/coupa.md` page if more Coupa content surfaces in OneDrive / other corpora.
- `sharepoint_protein-science-documents-cyrus-hm-and-cad-training-pptx` — Cyrus homology modeling / CAD training. Likely `equipment/cyrus-hm.md` or `methods/cyrus-homology-modeling.md`; could pair with more computational-biology training material from OneDrive when that's in scope.
- `sharepoint_protein-science-documents-del-screen-plans-ds-projects-jss-xlsx` + `sharepoint_protein-science-documents-del-screen-plans-dsa-projects-xlsx` + `sharepoint_protein-science-documents-del-screen-plans-dsa-projects-jsantos04-t480-xlsx` — DSA project master lists. Three of the four go in Batch 1; this fourth ("jsantos04-t480") looks like an individual laptop copy — skip unless the diff against the master is meaningful.

### Delphi error-log files

Dozens of `-txt` error-log dumps across 2024-03 through 2026-04 (persistence errors, biomass registration errors, import errors, picklist bugs, etc.). These are bug-report evidence, not knowledge — each one individually is low signal. If there's a systemic pattern (repeated failure mode, specific subsystem fragility), the pattern belongs on a `decisions/` or `runbooks/` page at Phase 6 lint time, not as individual absorb targets now. Skip for Phase 2 first-pass absorb.
