# JoJo Bot v2.0 — Status Tracker

This is the **living** progress document for JoJo Bot v2.0. It tracks execution against the phases in `PLAN.md` (living) / `docs/ADR/0000-v2-roadmap.md` (frozen ratification snapshot, 2026-04-22).

**How to use this file.** Update it whenever a phase changes status, a deliverable lands, a risk materializes, or an open question gets answered. Keep prose in the "Notes" blocks; avoid restating what `PLAN.md` already says. If a change in this file would contradict the frozen ADR, that is a signal to write a new ADR (`docs/ADR/0001-…`) rather than silently drifting.

**Status legend.** 🟢 Complete · 🟡 In progress · ⚪ Not started · 🔴 Blocked · ⚫ Deferred / descoped

---

## Snapshot

| Field | Value |
| --- | --- |
| Last updated | 2026-04-22 |
| Current phase | Phase 0 — Preparation and Scaffolding |
| Overall status | 🟡 In progress |
| MVP target | Phases 0–6 (linting + rich outputs in scope) |
| Blocking risks | None yet |
| v1.0 in production | Yes — continues to answer ÄKTA / UNICORN questions; query router (Phase 4) will formalize the split |

---

## Phase Summary

| # | Phase | Status | Estimate | Started | Exit-criterion met |
| - | --- | --- | --- | --- | --- |
| 0 | Preparation and Scaffolding | 🟡 | 1–2 wk | 2026-04-22 | — |
| 1 | Source Ingestion (`ask_jojo_raw/`) | ⚪ | 3–5 wk | — | — |
| 2 | Wiki Compile (raw → `ask_jojo_wiki/`) | ⚪ | 6–8 wk | — | — |
| 3 | JoJo Bot IDE Tabs (Wiki / Raw / Ops) | ⚪ | 4–6 wk (parallel w/ 2) | — | — |
| 4 | Q&A over the Wiki + query router | ⚪ | 3–4 wk | — | — |
| 5 | Rich Outputs (Marp, matplotlib, docx/pptx/pdf) | ⚪ | 3–4 wk | — | — |
| 6 | Wiki Linting + Self-Maintenance | ⚪ | 3–4 wk | — | — |
| 7a | Graph Tab (graphify integration) | ⚪ | 1–2 wk | — | — |
| 7b | Shared Nurix-Internal Server | ⚫ post-MVP | 3–5 wk | — | — |
| 8 | Backlog (synthetic data, fine-tune, etc.) | ⚫ post-MVP | — | — | — |

---

## Phase 0 — Preparation and Scaffolding · 🟡

**Goal.** Stand up the skeletal structure of v2.0 without changing any v1.0 behavior.

**Exit criterion.** All three repos exist on GitHub under the Nurix org (or Mateo's personal account, TBD), are cloned locally on disk at `C:\Users\mdelosrios\Claude_Local\jojo_bot_v2.0\` (not in any synced folder), `SCHEMA.md` v0.1.0 is committed to `ask_jojo_wiki/`, ADRs 0000–0004 are committed to `ask_jojo/docs/ADR/`, and the workspace `README.md` explains the layout.

### Deliverables checklist

- [x] `PLAN.md` merged from plans A + B and committed to `ask_jojo/`
- [x] `docs/ADR/0000-v2-roadmap.md` — frozen ratification copy of PLAN.md (2026-04-22)
- [x] `docs/v2_status.md` — living status doc (this file)
- [x] Three GitHub repos created: `ask_jojo`, `ask_jojo_wiki`, `ask_jojo_raw`
- [x] Local clones placed on local disk (`C:\Users\mdelosrios\Claude_Local\jojo_bot_v2.0\`) — **not** in OneDrive/Dropbox/iCloud
- [x] `.gitignore` committed to each repo (templates from `sample_git_ignore_*`)
- [x] `SCHEMA.md` v0.1.0 committed to `ask_jojo_wiki/`
- [x] `README.md` for `ask_jojo_wiki/` and `ask_jojo_raw/` committed to their respective repos
- [x] `ask_jojo/README.md` drafted (app-repo-specific entry point)
- [x] `ask_jojo/schema/CLAUDE.md` v0 drafted (constitution + absorb loop + writing rules)
- [x] `ask_jojo/schema/taxonomy.yaml` first-draft directory taxonomy (§4 D4 starter list)
- [x] ADR 0001-wiki-over-rag.md
- [x] ADR 0002-three-repo-split.md
- [x] ADR 0003-packages-layout.md
- [x] ADR 0004-local-first-deployment.md
- [x] ADR 0005-jojo-bot-service-account.md
- [x] `jojo-bot` service identity provisioned via git-identity overlay (ADR 0005 + `ops/service-account/`). Full GitHub App deferred to Phase 7b (`PHASE_7B_APP_SETUP.md`).
- [ ] Legal / MSA review kicked off (confirm Nurix↔Anthropic MSA covers Protein Sciences data classes)
- [ ] Anthropic API keys provisioned; Claude Haiku 4.5 / Sonnet 4.6 / Opus 4.6 routing verified

### Notes

_Add dated entries below as work progresses._

- **2026-04-22** — PLAN.md ratified. Frozen ADR-0000 and this status doc created. Three GitHub repos (`ask_jojo`, `ask_jojo_wiki`, `ask_jojo_raw`) created and pushed. `PLAN.md` moved from workspace root into `ask_jojo/`. Duplicate source files (`README_ask_jojo_*.md`, `SCHEMA.md`) removed from workspace root. Path references updated from `C:\dev\jojo-workspace\` to `C:\Users\mdelosrios\Claude_Local\jojo_bot_v2.0\` throughout PLAN.md, v2_status.md, and the workspace README (ADR 0000 intentionally left unchanged as a historical snapshot).

---

## Phase 1 — Source Ingestion · ⚪

**Exit criterion.** `jojo_ingest sync-all` pulls ≥100 files from ≥2 Protein Sciences connectors into `ask_jojo_raw/` in under an hour with correct `access_level` metadata; daily incremental sync runs unattended for a week without crashes.

### Deliverables checklist

- [ ] `packages/jojo_connectors_common/` — base connector interface
- [ ] `packages/jojo_ingest/sharepoint.py` — MS Graph SDK, `Files.Read.All` + `Sites.Read.All`
- [ ] `packages/jojo_ingest/onedrive.py`
- [ ] `packages/jojo_ingest/drive.py` — SMB + local path fallback
- [ ] `packages/jojo_ingest/nurixnet.py` — Playwright, selectors quarantined
- [ ] `packages/jojo_ingest/upload.py` — local-upload endpoint
- [ ] `ask_jojo_raw/manifest.json` schema locked + seeded
- [ ] YAML frontmatter spec for raw files (`id`, `source_type`, `source_url`, `sha256`, `access_level`, …)
- [ ] Windows Task Scheduler integration (SharePoint 4h · OneDrive 24h · NurixNet weekly · Drive 24h)
- [ ] Secrets at `%APPDATA%\JojoBot\config.json` (DPAPI-encrypted)

### Notes

_None yet._

---

## Phase 2 — Wiki Compile · ⚪

**Exit criterion.** Running `jojo_compile absorb` against the Protein Sciences raw corpus produces a wiki that a domain reviewer accepts ≥80% of pages on first pass, with no hallucinations traceable to cited sources.

### Deliverables checklist

- [ ] `packages/jojo_compile/` with `absorb.py`, `plan.py`, `write.py`, `verify.py`, `link.py`, `checkpoint.py`, `breakdown.py`, `reorganize.py`
- [ ] Fresh-context subagent pattern wired up
- [ ] 15-entry checkpoint enforced
- [ ] `_index.md` and `_backlinks.json` auto-rebuild
- [ ] Schema-version migration pass wired up

### Notes

_None yet._

---

## Phase 3 — JoJo Bot IDE Tabs · ⚪

**Exit criterion.** A new user opens JoJo Bot, navigates to `/wiki`, browses both raw and wiki layers, clicks a wiki page, sees working wikilinks, triggers an absorb from the Ops tab, and accepts a JoJo-written edit via the diff UI.

### Deliverables checklist

- [ ] Wiki tab (tree view, markdown preview, frontmatter panel, wikilink auto-complete)
- [ ] Raw tab (tree view, source preview, re-sync controls, permission badges)
- [ ] Ops tab (absorb / lint / sync triggers, progress, logs)
- [ ] "Request edit from JoJo" diff flow
- [ ] "Manual override" escape hatch behind confirmation (logs, flags for next lint)

### Notes

_None yet._

---

## Phase 4 — Q&A over the Wiki · ⚪

**Exit criterion.** Index-first Q&A answers ≥80% of Protein Sciences questions without vector RAG; `_index.md` <200 pages; p95 latency <8s.

### Deliverables checklist

- [ ] Query router (ÄKTA questions → v1.0 path; everything else → wiki path)
- [ ] Index-first retrieval (Sonnet reads `_index.md`, picks 3–8 pages, follows wikilinks 1–2 hops)
- [ ] Raw fallback when wiki coverage insufficient (miss logged → next absorb)
- [ ] `qmd` installed but dormant until threshold trips

### Notes

_None yet._

---

## Phase 5 — Rich Outputs · ⚪

**Exit criterion.** User asks "make me slides comparing TYK2 strategies for AR-V7 vs CRBN" and gets back a viewable Marp deck rendered inside JoJo Bot with one click to file-back into `wiki/outputs/`.

### Deliverables checklist

- [ ] Marp rendering via `@marp-team/marp-core` Web Worker
- [ ] matplotlib sandbox (resource limits, no network, allowlist imports)
- [ ] docx / pptx / pdf generation paths
- [ ] "File this" button wired up to `wiki/outputs/`

### Notes

_None yet._

---

## Phase 6 — Wiki Linting + Self-Maintenance · ⚪

**Exit criterion.** Nightly lint runs without human intervention for two weeks; weekly Opus pass surfaces contradictions with <10% false-positive rate on domain-reviewer sample.

### Deliverables checklist

- [ ] `packages/jojo_lint/` with pluggable check registry
- [ ] Schema / orphan / stub / broken-wikilink / bloat / quote-budget checks (nightly, Sonnet)
- [ ] Contradiction / staleness / missing-articles / suggested-questions checks (weekly, Opus)
- [ ] Scheduled-task integration (Windows Task Scheduler)
- [ ] Ops tab surfaces lint history + pending approvals
- [ ] Metrics trendlines (orphan count, avg confidence, staleness, contradiction density)

### Notes

_None yet._

---

## Phase 7a — Graph Tab · ⚪

**Exit criterion.** Graph tab embeds graphify's `graph.html`; Ops tab surfaces `GRAPH_REPORT.md`; nightly rebuild runs cleanly.

### Deliverables checklist

- [ ] graphify installed as CLI dependency
- [ ] Pointed at `ask_jojo_wiki/`; output to `ask_jojo_wiki/.graphify/` (in `.jojoignore`)
- [ ] Graph tab iframe wired up
- [ ] `GRAPH_REPORT.md` surfaced in Ops tab

### Notes

_None yet._

---

## Phase 7b — Shared Server · ⚫ post-MVP

**Exit criterion.** `jojo_server` on a Nurix-internal VM hosts authoritative `ask_jojo_raw/` + `ask_jojo_wiki/`; Azure AD / Nurix SSO gates every API call; per-article ACLs inherited from source-system permissions.

### Deliverables checklist

- [ ] `jojo_server` service on internal VM
- [ ] Azure AD / Nurix SSO integration
- [ ] Per-user scope checks on ingest (no one sees SharePoint content they can't already read)
- [ ] Migration path from local mode
- [ ] Finer-grained ACLs (beyond all-FTE) gated on IT/Legal review

### Notes

_None yet._

---

## Phase 8 — Backlog · ⚫ post-MVP

Parking lot for synthetic-data pipelines, fine-tune experiments, and other ideas that don't fit earlier phases. See §6 Phase 8 in `PLAN.md`.

---

## Open Questions

Carried forward from `PLAN.md` §13. Update as answers land.

| # | Question | Owner | Decision | Decided |
| - | --- | --- | --- | --- |
| 1 | GitHub org: `matesanchez` personal account vs. a Nurix org? | Mateo | — | — |
| 2 | `jojo-bot[bot]` service account provisioning path | Mateo + IT | Two-phase: git-identity overlay locally (Phases 0–6); GitHub App in Phase 7b | 2026-04-22 |
| 3 | Legal / MSA confirmation on Protein Sciences data classes | Legal | — | — |
| 4 | Should the query router live in `ask_jojo/` or split into its own package? | Mateo | — | — |
| 5 | Wiki locale rules (Nurix-wide SOPs sometimes mix US / UK spellings) | Domain reviewer | — | — |

---

## Risk Watchlist

Live view into the risks in `PLAN.md` §11. Only the "hot" ones are listed here; promote or demote as reality unfolds.

| Risk | Likelihood | Impact | Status | Mitigation in flight |
| --- | --- | --- | --- | --- |
| Legal MSA gap on Protein Sciences data classes | Low | High | ⚪ not yet raised | Phase 0 action item |
| NurixNet HTML changes break Playwright selectors | Medium | Medium | ⚪ pre-work | Quarantine selectors, raw-HTML fallback |
| Adoption fails (scientists don't use it) | Medium | High | ⚪ pre-work | Pilot beta group in Phase 4; dogfood real PS questions |
| Claude API cost blows past budget | Low | Medium | 🟢 on watch | Model tiering table in PLAN.md §4 D8; budget alerts on Anthropic console |

---

## Amendment Log

Non-trivial edits to this file. The frozen ADR (`docs/ADR/0000-v2-roadmap.md`) is never edited; changes to the plan itself require a new ADR.

| Date | Change | By |
| --- | --- | --- |
| 2026-04-22 | Initial creation of status tracker | Mateo + Claude |
| 2026-04-22 | Three GitHub repos created and pushed; PLAN.md relocated to `ask_jojo/`; workspace duplicates cleaned; paths updated to `C:\Users\mdelosrios\Claude_Local\jojo_bot_v2.0\` (ADR 0000 left untouched) | Mateo + Claude |
| 2026-04-22 | Phase 0 deep-work push: `ask_jojo/README.md`, `schema/CLAUDE.md` v0.1.0, `schema/taxonomy.yaml` v0.1.0, ADRs 0001–0004 all drafted. Remaining Phase 0 items are the human-only ones (service account, legal/MSA review, API key verification). | Mateo + Claude |
| 2026-04-22 | Service-account scaffolding: ADR 0005 ratified with two-phase strategy (git-identity overlay now, GitHub App in Phase 7b). `ops/service-account/` directory created with `bot-identity.ps1`, `bot-commit.ps1`, `test-bot-identity.ps1`, operational README, and `PHASE_7B_APP_SETUP.md` runbook. Phase 0 checkbox checked off; full GitHub App provisioning tracked for Phase 7b. | Mateo + Claude |
