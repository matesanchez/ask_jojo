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

- [ ] sharepoint_protein-science-documents-del-ps-goals-2025-research-goals-final-docx
- [ ] sharepoint_protein-science-documents-del-screen-plans-del-protein-screen-2022-pptx
- [ ] sharepoint_protein-science-documents-del-screen-plans-del-queue-2022-pptx
- [ ] sharepoint_protein-science-documents-del-screen-plans-03232022-del-screen-plan-proteins-xlsx
- [ ] sharepoint_protein-science-documents-del-buffer-screen-q42022-dsaprojects-remainingscreensandbudget-xlsx
- [ ] sharepoint_protein-science-documents-del-buffer-screen-siah1-nbvc-n00619-1a-n00620-1-buffer-stability-testing-pptx
- [ ] sharepoint_protein-science-documents-del-screen-plans-average-screen-plan-for-protein-estimates-20220412-wks-xlsx
- [ ] sharepoint_protein-science-documents-del-screen-plans-ds-projects-jss-xlsx
- [ ] sharepoint_protein-science-documents-del-screen-plans-dsa-projects-xlsx
- [ ] sharepoint_protein-science-documents-del-screen-plans-dsa-update---early-discovery-group-meeting-20220818-pptx

---

## Backlog — not yet batched

Loose pool of entries the absorb prompt has flagged as worth processing but that haven't been grouped into a batch yet. When writing a new batch heading above, pull from this list (and delete the lines you pull). Not every raw entry belongs here — low-signal files (outdated drafts, copy-of-copy variants, meeting no-shows) are absorbed by the lint pipeline's retention pass in Phase 6, not by hand now.

_None yet. Add candidates here as they surface during review._
