# JoJo Bot v2.0 — Status Tracker

This is the **living** progress document for JoJo Bot v2.0. It tracks execution against the phases in `PLAN.md` (living) / `docs/ADR/0000-v2-roadmap.md` (frozen ratification snapshot, 2026-04-22).

**How to use this file.** Update it whenever a phase changes status, a deliverable lands, a risk materializes, or an open question gets answered. Keep prose in the "Notes" blocks; avoid restating what `PLAN.md` already says. If a change in this file would contradict the frozen ADR, that is a signal to write a new ADR (`docs/ADR/0001-…`) rather than silently drifting.

**Status legend.** 🟢 Complete · 🟡 In progress · ⚪ Not started · 🔴 Blocked · ⚫ Deferred / descoped

---

## Snapshot

| Field | Value |
| --- | --- |
| Last updated | 2026-04-22 |
| Current phase | Phase 1 — Source Ingestion (local tier complete; SharePoint via delegated auth; OneDrive + public drive via local mount; Raw tab UI shipped) |
| Overall status | 🟡 In progress |
| MVP target | Phases 0–6 (linting + rich outputs in scope) |
| Blocking risks | None yet |
| v1.0 in production | Yes — continues to answer ÄKTA / UNICORN questions; query router (Phase 4) will formalize the split |

---

## Phase Summary

| # | Phase | Status | Estimate | Started | Exit-criterion met |
| - | --- | --- | --- | --- | --- |
| 0 | Preparation and Scaffolding | 🟢 | 1–2 wk | 2026-04-22 | 2026-04-22 |
| 1 | Source Ingestion (`ask_jojo_raw/`) | 🟡 | 3–5 wk | 2026-04-22 | — |
| 2 | Wiki Compile (raw → `ask_jojo_wiki/`) | ⚪ | 6–8 wk | — | — |
| 3 | JoJo Bot IDE Tabs (Wiki / Raw / Ops) | ⚪ | 4–6 wk (parallel w/ 2) | — | — |
| 4 | Q&A over the Wiki + query router | ⚪ | 3–4 wk | — | — |
| 5 | Rich Outputs (Marp, matplotlib, docx/pptx/pdf) | ⚪ | 3–4 wk | — | — |
| 6 | Wiki Linting + Self-Maintenance | ⚪ | 3–4 wk | — | — |
| 7a | Graph Tab (graphify integration) | ⚪ | 1–2 wk | — | — |
| 7b | Shared Nurix-Internal Server | ⚫ post-MVP | 3–5 wk | — | — |
| 8 | Backlog (synthetic data, fine-tune, etc.) | ⚫ post-MVP | — | — | — |

---

## Phase 0 — Preparation and Scaffolding · 🟢

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
- [x] ADR 0006-raw-repo-privacy-invariant.md
- [x] `jojo-bot` service identity provisioned via git-identity overlay (ADR 0005 + `ops/service-account/`). Full GitHub App deferred to Phase 7b (`PHASE_7B_APP_SETUP.md`).
- [x] Legal / MSA review complete — cleared 2026-04-22 conditional on `ask_jojo_raw` remaining private. Invariant captured in ADR 0006; visible notice added to `ask_jojo_raw/README.md`.
- [~] Anthropic API keys — model access confirmed for all three tiers (Haiku 4.5 / Sonnet 4.6 / Opus 4.6); keys not yet provisioned. **Not blocking Phase 1** (ingest makes no Claude calls). Must be wired before Phase 2 absorb. Tracked as a Phase 2 prerequisite rather than a Phase 0 blocker.
- [x] `packages/` skeleton — 7 packages (`jojo_core`, `jojo_ingest`, `jojo_compile`, `jojo_qa`, `jojo_output`, `jojo_lint`, `jojo_graph`) each with `__init__.py`, `cli.py` stub returning exit code 1, `README.md`, and a smoke test. `pyproject.toml` wires hatchling + 7 console entry points + dev/backend extras + ruff + pytest config.
- [x] `.github/workflows/ci.yml` — ruff + pytest CI on push/PR (Python 3.11).
- [x] `src/backend/` — FastAPI app with `/health` plus 5 routers (`wiki`, `raw`, `viz`, `ops`, `ingest`), all endpoints returning HTTP 501 with phase-pointing messages. Smoke tests (health + parametrized 501 coverage across 12 endpoints) passing.
- [x] `src/frontend/` — Next.js 14 App Router scaffold with persistent header/nav and `(tabs)` route group for `/wiki`, `/raw`, `/viz`, `/ops` placeholder pages. `next.config.js` proxies `/api/*` → backend.
- [x] Redis + RQ infrastructure — `docker-compose.yml` for dev (redis:7-alpine, AOF + snapshot persistence), `docs/ops/redis-setup.md` documenting both dev (Docker) and prod (Memurai on Windows) paths per ADR 0004.
- [x] `docs/budget-model.xlsx` — 3-sheet Claude API budget model (Overview / Assumptions / Weekly_Spend) at three corpus scales (100 / 500 / 2000 docs). Zero formula errors across 36 formulas. Caveats: pricing is placeholder until API keys issued; nightly Sonnet lint dominates at Nurix-wide scale (~$113/wk of $155/wk total).

### Notes

_Add dated entries below as work progresses._

- **2026-04-22** — PLAN.md ratified. Frozen ADR-0000 and this status doc created. Three GitHub repos (`ask_jojo`, `ask_jojo_wiki`, `ask_jojo_raw`) created and pushed. `PLAN.md` moved from workspace root into `ask_jojo/`. Duplicate source files (`README_ask_jojo_*.md`, `SCHEMA.md`) removed from workspace root. Path references updated from `C:\dev\jojo-workspace\` to `C:\Users\mdelosrios\Claude_Local\jojo_bot_v2.0\` throughout PLAN.md, v2_status.md, and the workspace README (ADR 0000 intentionally left unchanged as a historical snapshot).

---

## Phase 1 — Source Ingestion · 🟡

**Exit criterion.** `jojo_ingest sync-all` pulls ≥100 files from ≥2 Protein Sciences connectors into `ask_jojo_raw/` in under an hour with correct `access_level` metadata; daily incremental sync runs unattended for a week without crashes.

**Phase 1a (local tier) — shipped 2026-04-22.** Drive (local filesystem) + upload endpoint, shared driver/converter/manifest machinery, backend wired, exit-criterion smoke test green on 105 files in under a second. Enough to start filing Protein Sciences SOPs manually today.

**Phase 1b (SharePoint via delegated auth) — shipped 2026-04-22.** SharePoint connector now runs against MS Graph using a Graph Explorer–issued delegated bearer token (Path A), pluggable behind a `TokenProvider` callable so MSAL device-code (Path B) and client-credentials (Path C) slot in later without touching the connector. Initial scope targets six sites Mateo explicitly named (Protein Sciences, NurixNet, DEL Triage / Screen Team, CRUK Grant, Biortus). See **ADR 0007** for the auth decision and revisit triggers. With SharePoint live, the "≥2 connectors" half of the exit criterion is now satisfied (drive + sharepoint); the daily-unattended-for-a-week half stays open until Path B ships (Path A's ~60 min token lifetime blocks scheduled runs).

**Phase 1b+ (OneDrive + public drive via local mount, NurixNet subsumed) — shipped 2026-04-22.** Delegated `Files.Read.All` turned out to be tenant-gated in a way the UI wouldn't let Mateo self-consent. Rather than open an IT ticket and wait, we're ingesting OneDrive and the Nurix public drive by walking their existing local sync / mount points — both are already on Mateo's laptop courtesy of the OneDrive desktop client and the Windows `P:\` drive mapping. `OneDriveConnector` and `PublicDriveConnector` are five-line subclasses of `DriveConnector` that only override `source_type`, so provenance in the manifest stays accurate. NurixNet, meanwhile, turned out to be a SharePoint site all along and is covered by the existing SharePoint connector — the Playwright-over-VPN stub was deleted. See **ADR 0008** for the full decision. Still open for daily-unattended operation: Path B (MSAL device-code) for SharePoint, Windows Task Scheduler wrappers, and DPAPI config.json.

**Phase 1c (Raw tab UI) — shipped 2026-04-22.** The human audit surface for `ask_jojo_raw/`. Backend `/api/raw/tree`, `/api/raw/file/{entry_id}`, `/api/raw/manifest` are now real (not 501). Frontend `/raw` route is a three-pane IDE-style view: left = manifest-driven tree grouped by `source_type` and path, center = `react-markdown` preview of the selected raw file, right = metadata panel (title, source badge, access badge, source URL, fetched time, SHA256, supersedence). Top bar shows per-connector readiness + re-sync buttons; bottom bar shows per-source file counts + last-fetched time + pending/failed job counts. The tab polls `/api/raw/manifest` + `/api/ingest/jobs` every 15s so scheduled syncs show up without a reload. Source of truth is the manifest — the tree deliberately never lists the filesystem directly, matching the "filesystem walks should never bypass the manifest" invariant. This was nominally a Phase 3 deliverable but landed in Phase 1 so the ingest work is actually usable by a human before compile lands.

### Deliverables checklist

- [x] `packages/jojo_connectors_common/` — base connector interface (`Connector` ABC, `SourceEntry` dataclass, `ConnectorResult`, `IngestError`), YAML frontmatter spec + parser, canonical SHA256, PII redaction pass (ssn / credit card / email / phone / patient-id / DOB), `.jojoignore` gitignore-style filter, `Manifest` with idempotent upsert + supersedence tracking. 18 unit tests green.
- [x] `packages/jojo_ingest/drive.py` — local filesystem / SMB connector. Walks directory trees, respects `.jojoignore`, filters unsupported types, honors `since` via mtime for incremental sync. 5 integration tests.
- [x] `packages/jojo_ingest/upload.py` — single-file connector for the UI upload endpoint. Rejects unsupported extensions upfront with an actionable error. 3 tests.
- [x] File-type converters under `packages/jojo_ingest/converters/` — `.docx` via mammoth, `.xlsx` via openpyxl (one `## <sheet>` per worksheet, markdown tables), `.pptx` via python-pptx (bullets + speaker notes), `.pdf` via PyMuPDF (`## Page N` sections, flags image-only pages), text with encoding fallback chain. 7 tests covering real generated files.
- [x] `packages/jojo_ingest/driver.py` — `IngestDriver` shared pipeline: redact → hash → manifest check → write raw `.md` with frontmatter → update manifest → append change record. Idempotent re-runs produce zero work; content changes produce updates; source renames produce supersedence chains.
- [x] ~~`packages/jojo_ingest/{sharepoint,onedrive,nurixnet}.py` stubs~~ — retired during Phase 1b / 1b+. SharePoint shipped against MS Graph (ADR 0007); OneDrive shipped as a local-mount walker (ADR 0008); NurixNet deleted — it's a SharePoint site, not a separate surface. The stub-era parametrized interface-conformance test was removed with them.
- [x] `jojo-ingest` CLI — argparse subcommands `sync-all`, `sync <connector>`, `upload <file>`, `resync <connector>`, `status`. Drive/upload tiers run inline; stubbed connectors surface a friendly "needs creds" message.
- [x] Backend `/api/ingest/*` wired up — `GET /connectors` (readiness), `POST /sync/{connector}` (RQ-enqueue with inproc fallback), `POST /resync/{connector}`, `POST /upload` (multipart), `GET /jobs`, `GET /jobs/{id}`, `GET /status`. 8 endpoint tests green. `/schedule` still 501, deferred to local-mode packaging pass.
- [x] `ask_jojo_raw/manifest.json` schema locked at `0.1.0` + seeded. `.jojoignore`, `_changes/` directory, and `DIRECTORY.md` (mechanical companion to the narrative README) added to the raw repo.
- [x] YAML frontmatter spec for raw files — see `packages/jojo_connectors_common/frontmatter.py` `RawFrontmatter` + `FRONTMATTER_FIELDS`. All required PLAN.md §6 Phase 1 fields covered.
- [x] End-to-end exit-criterion smoke test — `test_phase1_exit_criterion` seeds 120 files across 8 subdirectories, runs drive ingest, verifies 105 files land (15 `drafts/` ignored), checks frontmatter well-formedness on a random sample, verifies second run is zero-work, verifies a 5-file edit produces exactly 5 updates.
- [x] `packages/jojo_ingest/graph.py` — thin httpx-based MS Graph v1.0 wrapper with pluggable `TokenProvider`. Handles path-style site resolution (`/sites/{hostname}:{server-relative-path}`), `@odata.nextLink` paging, 429/503 backoff honoring `Retry-After`, and 302-to-CDN content downloads. `env_token_provider()` ships as Path A; Path B/C providers slot in as later work. 13 unit tests (`test_graph.py`).
- [x] `packages/jojo_ingest/sharepoint.py` — real MS Graph connector, replacing the stub. Walks `/sites/{id}/drives` → `/drives/{id}/root/children` recursively, prefers `@microsoft.graph.downloadUrl` for content fetch, skips Office lock files + SharePoint internal folders (`Forms`, `_private`, `_catalogs`), emits full `SourceEntry` with `graph_item_id` / `graph_drive_id` / `graph_site_id` / `site_display` / `drive_name` in `extra`. Bad-site failures log-and-skip rather than poisoning the run. `build_sharepoint_connector_from_env` reads `JOJO_SHAREPOINT_SITES` + `JOJO_GRAPH_ACCESS_TOKEN` with CLI override support. 11 unit tests (`test_sharepoint.py`) including an end-to-end IngestDriver round-trip, all credential-free via `pytest-httpx`. Auth strategy documented in **ADR 0007**.
- [x] `packages/jojo_ingest/onedrive.py` — `OneDriveConnector`, a thin `DriveConnector` subclass that walks the local OneDrive sync folder (typically `C:\Users\<user>\OneDrive - Nurix Therapeutics`). Env factory reads `JOJO_ONEDRIVE_PATH`; `OneDriveEnvError` maps to HTTP 400. `source_type = "onedrive"` keeps manifest provenance distinct from generic drive paths. 6 tests. A Graph-backed path remains possible via `TokenProvider` but isn't needed for V1 — see **ADR 0008**.
- [x] `packages/jojo_ingest/publicdrive.py` — `PublicDriveConnector` walking the `P:\` network share (the Nurix org-wide SMB drive). Same shape as OneDrive: env factory on `JOJO_PUBLIC_DRIVE_PATH`, Windows-only `P:\` default. `source_type = "publicdrive"`. 6 tests. Covered by ADR 0008 alongside OneDrive.
- [x] ~~`packages/jojo_ingest/nurixnet.py`~~ — deleted. NurixNet turned out to be a SharePoint site (`https://nurix.sharepoint.com/sites/NurixNet`) and is walked by the SharePoint connector via `JOJO_SHAREPOINT_SITES`. The prior "Playwright over VPN" plan assumed NurixNet was a separate intranet app, which it is not.
- [ ] **Path B (MSAL device-code provider)** — unblocks scheduled SharePoint ingest by lifting the ~60-min token ceiling to ~90 days per interactive login. Token cache at `%APPDATA%\JojoBot\tokencache.bin`. Slots into `graph.py` as `msal_device_code_provider()`; connector code unchanged. Tracked in ADR 0007 as the next path.
- [ ] **Path C (MSAL client-credentials provider)** — Phase 7b service-account endpoint. Requires a real Entra app registration with admin-consented `Files.Read.All` + `Sites.Read.All` app permissions and cert/secret storage (DPAPI locally per ADR 0004; Key Vault on the shared server). Tracked in ADR 0007.
- [ ] Windows Task Scheduler integration (SharePoint 4h · OneDrive 24h · NurixNet weekly · Drive 24h) — deferred to local-mode packaging pass at end of Phase 1 (Windows-only, best done alongside the installer).
- [ ] Secrets at `%APPDATA%\JojoBot\config.json` (DPAPI-encrypted) — deferred to local-mode packaging pass. Current env-var reads (`JOJO_RAW_ROOT`, `JOJO_UPLOAD_DIR`, `JOJO_REDIS_URL`) are sufficient for dev + the local tier.
- [x] **Raw tab UI** — `src/backend/routers/raw_router.py` implements `/tree`, `/file/{entry_id}`, `/manifest` over the manifest (no filesystem bypass). `src/frontend/app/(tabs)/raw/page.tsx` renders a three-pane IDE-style view (tree / markdown preview / metadata panel) with a top bar of connector badges + re-sync buttons and a bottom bar of per-source counts + last-fetched times + pending/failed job counts. 10 new backend tests (`test_raw_endpoints.py`), including a path-traversal guard and a supersedence-pointer assertion. 129 tests green, ruff clean. (Nominally a Phase 3 deliverable — pulled forward so the ingest work is usable by a human before compile lands.)

### Notes

- **2026-04-22** — Phase 1a (local tier, fully wired) complete. New `jojo_connectors_common` package ships the shared primitives; `jojo_ingest` has a real `IngestDriver` + drive + upload + stubs. Backend router is no longer a bag of 501s — drive + upload endpoints execute against an in-process fallback when Redis isn't reachable (so CI doesn't need a live broker). 83 tests green, ruff clean. `ask_jojo_raw/` seeded with `.jojoignore`, `_changes/`, `DIRECTORY.md`, and a fresh schema-0.1.0 manifest. Cloud tier (SharePoint/OneDrive/NurixNet) deliberately scoped out of this push — IT hasn't issued MS Graph app registration or VPN-scoped credentials for `jojo-bot[bot]`, and stubs return actionable `NotImplementedError` messages rather than rotting into silent no-ops.

- **2026-04-22** — Phase 1b (SharePoint via delegated auth) shipped. Pivot from the ADR 0005 "wait on IT for a service-account app registration" framing: inspecting a Graph Explorer bearer token revealed Mateo already has `Sites.Read.All` / `Sites.ReadWrite.All` / `Sites.FullControl.All` / `Application.ReadWrite.All` consented in the Nurix tenant, and his directory roles (JWT `wids` claim) suggest he can self-serve app registrations. Rather than burn a day on portal clicks before validating the pipeline, shipped the pasted-token path now and kept the service-account path as Phase 7b work behind the same `TokenProvider` interface. New `packages/jojo_ingest/graph.py` (~230 lines) is the shared Graph client for SharePoint + OneDrive; `packages/jojo_ingest/sharepoint.py` is now a real connector, not a stub. Backend `/api/ingest/connectors` reports SharePoint as "ready"/"needs-token" based on env-var presence; `/sync/sharepoint` returns 400 (config-fixable) rather than 501 (feature-missing) when env vars are absent. CLI grows `--sites` / `--access-token` overrides on `jojo-ingest sync sharepoint`. 108 tests green (up from 83), ruff clean, credential-free test suite via `pytest-httpx`. Scheduled-ingest remains blocked on Path B (MSAL device-code) because Path A tokens expire ~60 min. See **ADR 0007** for the full decision record.

- **2026-04-22** — Phase 1b+ (OneDrive + public drive via local mount, NurixNet subsumed) shipped. Delegated `Files.Read.All` turned out to be tenant-gated in a way the Graph Explorer UI wouldn't let Mateo self-consent, and the OneDrive desktop client already syncs the same content to a local folder — so we pivoted from "implement OneDrive over Graph next" to "walk the sync folder like any other drive." `OneDriveConnector` and `PublicDriveConnector` are one-class subclasses of `DriveConnector` that override `source_type` ("onedrive", "publicdrive"); env factories read `JOJO_ONEDRIVE_PATH` and `JOJO_PUBLIC_DRIVE_PATH` and map missing-env errors to HTTP 400. NurixNet was discovered to be a SharePoint site rather than a separate intranet, so `packages/jojo_ingest/nurixnet.py` and `tests/test_stubs.py` were deleted. 121 tests green (up from 108), ruff clean. With OneDrive and the public drive live, the remaining Phase 1 work for daily-unattended operation is Path B (MSAL device-code for SharePoint) + Windows Task Scheduler wrappers + DPAPI config.json — all deferred to the local-mode packaging pass. See **ADR 0008** for the full decision record.

- **2026-04-22** — Phase 1c (Raw tab UI) shipped. The human audit surface for `ask_jojo_raw/` that PLAN.md §6 Phase 1 listed as a Phase-1 deliverable (the Phase 3 checklist's "Raw tab" line is the same artifact — pulled forward because a validator needs eyes on the manifest before we start compiling it). Backend `raw_router.py` replaces three 501 stubs with real endpoints: `/tree` groups manifest entries by `source_type` then path segments and returns a `{dir|file}` nested structure, `/file/{entry_id}` returns split frontmatter + body + forward supersedence pointer (with 410 Gone for manifest/disk drift and a traversal guard for hand-edited `../` paths), `/manifest` returns a summary with per-source counts + latest-fetched-ISO. Frontend `(tabs)/raw/page.tsx` is now a real three-pane layout (tree / `react-markdown` preview / metadata panel), top bar with connector badges + re-sync buttons, bottom bar with per-source counts + pending/failed job counts, 15s polling of `/api/raw/manifest` + `/api/ingest/jobs` so scheduled syncs show up without a reload. Added `react-markdown@^9` + `remark-gfm@^4` to `frontend/package.json`. 129 tests green (up from 121 — 10 new in `test_raw_endpoints.py`; 2 entries retired from the 501 smoke list now that `/api/raw/tree` and `/api/raw/manifest` are real). ruff clean.

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
- [x] Raw tab (tree view, source preview, re-sync controls, permission badges) — shipped 2026-04-22 as Phase 1c (see Phase 1 notes)
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
| 3 | Legal / MSA confirmation on Protein Sciences data classes | Legal | Cleared — conditional on `ask_jojo_raw` remaining private (ADR 0006) | 2026-04-22 |
| 4 | Should the query router live in `ask_jojo/` or split into its own package? | Mateo | — | — |
| 5 | Wiki locale rules (Nurix-wide SOPs sometimes mix US / UK spellings) | Domain reviewer | — | — |

---

## Risk Watchlist

Live view into the risks in `PLAN.md` §11. Only the "hot" ones are listed here; promote or demote as reality unfolds.

| Risk | Likelihood | Impact | Status | Mitigation in flight |
| --- | --- | --- | --- | --- |
| Legal MSA gap on Protein Sciences data classes | Low | High | 🟢 cleared 2026-04-22 | Conditional on raw repo privacy; see ADR 0006 |
| Raw repo visibility accidentally flipped to public | Low | High | 🟢 on watch | ADR 0006 invariant + README banner; optional CI check deferred to `jojo_lint` in Phase 6 |
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
| 2026-04-22 | Legal/MSA review cleared for ingest, conditional on `ask_jojo_raw` remaining a private repo. ADR 0006 ratified as the privacy invariant. Visible banner added to `ask_jojo_raw/README.md`. Open Question #3 closed. Anthropic API keys still to be provisioned, but reclassified from Phase 0 blocker to Phase 2 prerequisite (Phase 1 ingest makes no Claude calls). | Mateo + Claude |
| 2026-04-22 | Phase 0 scaffolding push: 7-package Python skeleton under `packages/` (all with CLI stub + smoke tests), `pyproject.toml` with hatchling + dev/backend extras, CI workflow (ruff + pytest), FastAPI backend under `src/backend/` with 5 routers returning 501 placeholders, Next.js 14 frontend under `src/frontend/` with `(tabs)` route group, Redis dev compose + Memurai-on-Windows runbook, and `docs/budget-model.xlsx` (3 sheets, 36 formulas, 0 errors). Full test suite green; ready for Phase 1 ingest work. | Mateo + Claude |
| 2026-04-22 | Phase 1a (local tier) complete. Phase 0 marked 🟢; Phase 1 marked 🟡. Shipped: `jojo_connectors_common` (frontmatter / redaction / ignore / manifest / connector-base — 18 tests), `jojo_ingest` drive + upload connectors with shared `IngestDriver` (10 tests), file-type converters for docx/xlsx/pptx/pdf/text (7 tests), sharepoint/onedrive/nurixnet stubs (parametrized interface test), argparse-based `jojo-ingest` CLI, backend `/api/ingest/*` fully wired (RQ with inproc fallback, 8 endpoint tests), `ask_jojo_raw/` scaffolding (`.jojoignore`, `_changes/`, `DIRECTORY.md`, schema-0.1.0 manifest), Phase 1 dependency groups in `pyproject.toml` (`ingest`, `cloud`, `web`), and the `test_phase1_exit_criterion` end-to-end smoke test (120 files → 105 ingested, re-run zero-work, 5-edit → 5 updated). 83 tests green, ruff clean. Cloud tier deliberately deferred pending IT issuing MS Graph creds + VPN access; stubs raise actionable `NotImplementedError` with remediation pointers. | Mateo + Claude |
| 2026-04-22 | Phase 1b (SharePoint via delegated auth) shipped. ADR 0007 ratified: three-path `TokenProvider` strategy (delegated-token / MSAL device-code / service-account), Path A live today, Path B + C tracked as later work that slots into the same interface. New `packages/jojo_ingest/graph.py` (shared Graph v1.0 wrapper, 13 tests) + real `packages/jojo_ingest/sharepoint.py` (replacing the stub, 11 tests including an end-to-end `IngestDriver` round-trip via `pytest-httpx`). Backend `/api/ingest/connectors` reports env-driven readiness (`ready` / `needs-token`); `/sync/sharepoint` returns 400 (config-fixable) rather than 501 when env vars are absent. CLI gains `--sites` / `--access-token` overrides. 108 tests green, ruff clean, test suite stays credential-free. Scheduled ingest still blocked on Path B due to ~60 min token lifetime. | Mateo + Claude |
| 2026-04-22 | Phase 1b+ (OneDrive + public drive via local mount, NurixNet subsumed). ADR 0008 ratified: ingest OneDrive and the Nurix `P:\` share by walking their local sync / mount points instead of MS Graph — tenant blocks delegated `Files.Read.All`, OneDrive client already mirrors the same bytes to disk, and `DriveConnector` already knows how to walk a filesystem root. `OneDriveConnector` and `PublicDriveConnector` ship as one-line `DriveConnector` subclasses with distinct `source_type` values so manifest provenance stays honest. Env-driven factories (`JOJO_ONEDRIVE_PATH`, `JOJO_PUBLIC_DRIVE_PATH`, Windows default `P:\`) raise typed errors that map to HTTP 400. NurixNet is a SharePoint site (not a separate intranet app) — `nurixnet.py` stub + its test deleted; the sharepoint connector already walks it via `JOJO_SHAREPOINT_SITES`. All five connector endpoints now execute real code or return 400 with actionable messages (no stub-era 501s). 121 tests green, ruff clean. | Mateo + Claude |
