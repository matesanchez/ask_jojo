# JoJo Bot v2.0 — Status Tracker

This is the **living** progress document for JoJo Bot v2.0. It tracks execution against the phases in `PLAN.md` (living) / `docs/ADR/0000-v2-roadmap.md` (frozen ratification snapshot, 2026-04-22).

**How to use this file.** Update it whenever a phase changes status, a deliverable lands, a risk materializes, or an open question gets answered. Keep prose in the "Notes" blocks; avoid restating what `PLAN.md` already says. If a change in this file would contradict the frozen ADR, that is a signal to write a new ADR (`docs/ADR/0001-…`) rather than silently drifting.

**Status legend.** 🟢 Complete · 🟡 In progress · ⚪ Not started · 🔴 Blocked · ⚫ Deferred / descoped

---

## Snapshot

| Field | Value |
| --- | --- |
| Last updated | 2026-04-30 |
| Current phase | Phase 4 — Q&A over the Wiki (deterministic plumbing shipped, synthesis pending FU-10) |
| Overall status | 🟡 In progress |
| MVP target | Phases 0–6 (linting + rich outputs in scope) |
| Blocking risks | API keys still pending (FU-10); does not block Phase 3 frontend work |
| v1.0 in production | Yes — continues to answer ÄKTA / UNICORN questions; query router (Phase 4) will formalize the split |

---

## Phase Summary

| # | Phase | Status | Estimate | Started | Exit-criterion met |
| - | --- | --- | --- | --- | --- |
| 0 | Preparation and Scaffolding | 🟢 | 1–2 wk | 2026-04-22 | 2026-04-22 |
| 1 | Source Ingestion (`ask_jojo_raw/`) | 🟢 | 3–5 wk | 2026-04-22 | 2026-04-23 |
| 2 | Wiki Compile (raw → `ask_jojo_wiki/`) | 🟢 | 6–8 wk | 2026-04-23 | 2026-04-30 |
| 3 | JoJo Bot IDE Tabs (Wiki / Raw / Ops) | 🟡 | 4–6 wk (parallel w/ 2) | 2026-04-30 | — |
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

## Phase 1 — Source Ingestion · 🟢

**Exit criterion.** `jojo_ingest sync-all` pulls ≥100 files from ≥2 Protein Sciences connectors into `ask_jojo_raw/` in under an hour with correct `access_level` metadata; daily incremental sync runs unattended for a week without crashes.

**Exit met 2026-04-23.** Full evidence in `docs/phase-1-exit-evidence.md` — at the time of writing, `ask_jojo_raw/` held 19,310+ raw `.md` files from two connectors (OneDrive 18,111 + SharePoint 1,199, mid-run and growing), with publicdrive's first walk still in flight. Access-level metadata is `all-FTE` per ADR 0006 and is stamped on every entry by the frontmatter pass. No crashes; per-file failures are logged-and-skipped (0.4% of OneDrive entries, well within tolerance). The 7-day unattended-soak observation window opened 2026-04-23 and will close 2026-04-30. SharePoint scheduled runs still require manual token rotation until Path B (ADR 0007) ships — tracked as FU-3 in `docs/follow-ups.md`. We consider Phase 1 exited for the purpose of starting Phase 2 work in parallel with the soak.

**Phase 1a (local tier) — shipped 2026-04-22.** Drive (local filesystem) + upload endpoint, shared driver/converter/manifest machinery, backend wired, exit-criterion smoke test green on 105 files in under a second. Enough to start filing Protein Sciences SOPs manually today.

**Phase 1b (SharePoint via delegated auth) — shipped 2026-04-22.** SharePoint connector now runs against MS Graph using a Graph Explorer–issued delegated bearer token (Path A), pluggable behind a `TokenProvider` callable so MSAL device-code (Path B) and client-credentials (Path C) slot in later without touching the connector. Initial scope targets six sites Mateo explicitly named (Protein Sciences, NurixNet, DEL Triage / Screen Team, CRUK Grant, Biortus). See **ADR 0007** for the auth decision and revisit triggers. With SharePoint live, the "≥2 connectors" half of the exit criterion is now satisfied (drive + sharepoint); the daily-unattended-for-a-week half stays open until Path B ships (Path A's ~60 min token lifetime blocks scheduled runs).

**Phase 1b+ (OneDrive + public drive via local mount, NurixNet subsumed) — shipped 2026-04-22.** Delegated `Files.Read.All` turned out to be tenant-gated in a way the UI wouldn't let Mateo self-consent. Rather than open an IT ticket and wait, we're ingesting OneDrive and the Nurix public drive by walking their existing local sync / mount points — both are already on Mateo's laptop courtesy of the OneDrive desktop client and the Windows `P:\` drive mapping. `OneDriveConnector` and `PublicDriveConnector` are five-line subclasses of `DriveConnector` that only override `source_type`, so provenance in the manifest stays accurate. NurixNet, meanwhile, turned out to be a SharePoint site all along and is covered by the existing SharePoint connector — the Playwright-over-VPN stub was deleted. See **ADR 0008** for the full decision. Still open for daily-unattended operation: Path B (MSAL device-code) for SharePoint, Windows Task Scheduler wrappers, and DPAPI config.json.

**Phase 1c (Raw tab UI) — shipped 2026-04-22.** The human audit surface for `ask_jojo_raw/`. Backend `/api/raw/tree`, `/api/raw/file/{entry_id}`, `/api/raw/manifest` are now real (not 501). Frontend `/raw` route is a three-pane IDE-style view: left = manifest-driven tree grouped by `source_type` and path, center = `react-markdown` preview of the selected raw file, right = metadata panel (title, source badge, access badge, source URL, fetched time, SHA256, supersedence). Top bar shows per-connector readiness + re-sync buttons; bottom bar shows per-source file counts + last-fetched time + pending/failed job counts. The tab polls `/api/raw/manifest` + `/api/ingest/jobs` every 15s so scheduled syncs show up without a reload. Source of truth is the manifest — the tree deliberately never lists the filesystem directly, matching the "filesystem walks should never bypass the manifest" invariant. This was nominally a Phase 3 deliverable but landed in Phase 1 so the ingest work is actually usable by a human before compile lands.

**Phase 1d (local-mode packaging pass — DPAPI config, Task Scheduler, installer) — shipped 2026-04-22.** The three workstreams that turn "runs when Mateo runs it" into "runs on its own overnight." `packages/jojo_core/config.py` wraps `%APPDATA%\JojoBot\config.json` in a versioned envelope with user-scope DPAPI encryption for secrets (zero new runtime deps — `ctypes` against `crypt32.dll`), a `jojo-core config` CLI for inspection / rotation / env migration, and a `config.get(key, default)` fallback chain that reads `config.json` first and falls through to legacy `JOJO_*` env vars for backward compat. `ops/scheduler/` adds three PowerShell scripts — a generic wrapper that tees stdout+stderr to dated log files and mirrors success / failure to the Windows Application event log, a one-shot registrar that creates four tasks under `\JojoBot\` (drive / onedrive / publicdrive daily; SharePoint every 4h) under an interactive user principal (no stored creds, per ADR 0004), and a cleanup script — plus an operator-facing README. `ops/installer/Install-JojoBot.ps1` stitches it all together as a five-step idempotent bootstrap. Every `.ps1` in the slice is pure ASCII (verified per-commit via a `ord(c) > 127` sweep), taught by an earlier parser-failure incident with CP1252 / PS 5.1. SharePoint token rotation remains manual until Path B unblocks — operator runs `jojo-core config set graph_access_token "<new>"` when the scheduled run starts 401'ing — but the other three connectors now sync unattended. See **ADR 0009** for the full decision record.

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
- [x] Windows Task Scheduler integration (SharePoint every 4h · Drive / OneDrive / PublicDrive daily) — `ops/scheduler/` ships `Run-ScheduledSync.ps1` (generic wrapper: preflights python + `import jojo_ingest`, tees stdout+stderr to dated log files under `ops/scheduler/logs/<connector>/<date>.log`, rolls up success/failure to the Windows Application event log under source `JojoBot`), `Register-JojoBotTasks.ps1` (one-shot registrar at `\JojoBot\`, interactive-user principal per ADR 0004, `-Skip*` opt-outs + `-Force` overwrite), `Unregister-JojoBotTasks.ps1` (cleanup with `-PurgeLogs` and `-Name <single>`), plus a self-contained `README.md`. All three .ps1 files are pure-ASCII (CP1252-safe per PS 5.1 parser).
- [x] Secrets at `%APPDATA%\JojoBot\config.json` (DPAPI-encrypted) — `packages/jojo_core/config.py` implements a versioned envelope (`{version, encryption: "dpapi"|"plaintext", payload}`), `ctypes`/`crypt32.dll` user-scope DPAPI on Windows with automatic plaintext fallback elsewhere. `jojo-core config path|show|get|set|delete|migrate-from-env|version` CLI. `config.get(key, default)` prefers `config.json` → falls through to legacy `JOJO_*` env var → default. All downstream callers (onedrive / publicdrive / sharepoint / graph / ingest_router / raw_router) rewritten to read through `config.get`. 41 new tests (`test_config.py` + `test_cli.py`); session-scoped autouse `conftest.py` fixture keeps tests away from the operator's real config. See **ADR 0009**.
- [x] All-in-one installer — `ops/installer/Install-JojoBot.ps1` walks operator through 5 ordered steps (preflight → `pip install -e ".[ingest,backend,cloud]"` → interactive config prompts → call `Register-JojoBotTasks.ps1` → smoke test). Safe to re-run with `-Reconfigure`, `-SkipPackage`, `-SkipConfig`, `-SkipScheduler`, `-Force`. Masks secret defaults on re-prompt. Pure-ASCII. See **ADR 0009**.
- [x] **Raw tab UI** — `src/backend/routers/raw_router.py` implements `/tree`, `/file/{entry_id}`, `/manifest` over the manifest (no filesystem bypass). `src/frontend/app/(tabs)/raw/page.tsx` renders a three-pane IDE-style view (tree / markdown preview / metadata panel) with a top bar of connector badges + re-sync buttons and a bottom bar of per-source counts + last-fetched times + pending/failed job counts. 10 new backend tests (`test_raw_endpoints.py`), including a path-traversal guard and a supersedence-pointer assertion. 129 tests green, ruff clean. (Nominally a Phase 3 deliverable — pulled forward so the ingest work is usable by a human before compile lands.)

### Notes

- **2026-04-22** — Phase 1a (local tier, fully wired) complete. New `jojo_connectors_common` package ships the shared primitives; `jojo_ingest` has a real `IngestDriver` + drive + upload + stubs. Backend router is no longer a bag of 501s — drive + upload endpoints execute against an in-process fallback when Redis isn't reachable (so CI doesn't need a live broker). 83 tests green, ruff clean. `ask_jojo_raw/` seeded with `.jojoignore`, `_changes/`, `DIRECTORY.md`, and a fresh schema-0.1.0 manifest. Cloud tier (SharePoint/OneDrive/NurixNet) deliberately scoped out of this push — IT hasn't issued MS Graph app registration or VPN-scoped credentials for `jojo-bot[bot]`, and stubs return actionable `NotImplementedError` messages rather than rotting into silent no-ops.

- **2026-04-22** — Phase 1b (SharePoint via delegated auth) shipped. Pivot from the ADR 0005 "wait on IT for a service-account app registration" framing: inspecting a Graph Explorer bearer token revealed Mateo already has `Sites.Read.All` / `Sites.ReadWrite.All` / `Sites.FullControl.All` / `Application.ReadWrite.All` consented in the Nurix tenant, and his directory roles (JWT `wids` claim) suggest he can self-serve app registrations. Rather than burn a day on portal clicks before validating the pipeline, shipped the pasted-token path now and kept the service-account path as Phase 7b work behind the same `TokenProvider` interface. New `packages/jojo_ingest/graph.py` (~230 lines) is the shared Graph client for SharePoint + OneDrive; `packages/jojo_ingest/sharepoint.py` is now a real connector, not a stub. Backend `/api/ingest/connectors` reports SharePoint as "ready"/"needs-token" based on env-var presence; `/sync/sharepoint` returns 400 (config-fixable) rather than 501 (feature-missing) when env vars are absent. CLI grows `--sites` / `--access-token` overrides on `jojo-ingest sync sharepoint`. 108 tests green (up from 83), ruff clean, credential-free test suite via `pytest-httpx`. Scheduled-ingest remains blocked on Path B (MSAL device-code) because Path A tokens expire ~60 min. See **ADR 0007** for the full decision record.

- **2026-04-22** — Phase 1b+ (OneDrive + public drive via local mount, NurixNet subsumed) shipped. Delegated `Files.Read.All` turned out to be tenant-gated in a way the Graph Explorer UI wouldn't let Mateo self-consent, and the OneDrive desktop client already syncs the same content to a local folder — so we pivoted from "implement OneDrive over Graph next" to "walk the sync folder like any other drive." `OneDriveConnector` and `PublicDriveConnector` are one-class subclasses of `DriveConnector` that override `source_type` ("onedrive", "publicdrive"); env factories read `JOJO_ONEDRIVE_PATH` and `JOJO_PUBLIC_DRIVE_PATH` and map missing-env errors to HTTP 400. NurixNet was discovered to be a SharePoint site rather than a separate intranet, so `packages/jojo_ingest/nurixnet.py` and `tests/test_stubs.py` were deleted. 121 tests green (up from 108), ruff clean. With OneDrive and the public drive live, the remaining Phase 1 work for daily-unattended operation is Path B (MSAL device-code for SharePoint) + Windows Task Scheduler wrappers + DPAPI config.json — all deferred to the local-mode packaging pass. See **ADR 0008** for the full decision record.

- **2026-04-22** — Phase 1c (Raw tab UI) shipped. The human audit surface for `ask_jojo_raw/` that PLAN.md §6 Phase 1 listed as a Phase-1 deliverable (the Phase 3 checklist's "Raw tab" line is the same artifact — pulled forward because a validator needs eyes on the manifest before we start compiling it). Backend `raw_router.py` replaces three 501 stubs with real endpoints: `/tree` groups manifest entries by `source_type` then path segments and returns a `{dir|file}` nested structure, `/file/{entry_id}` returns split frontmatter + body + forward supersedence pointer (with 410 Gone for manifest/disk drift and a traversal guard for hand-edited `../` paths), `/manifest` returns a summary with per-source counts + latest-fetched-ISO. Frontend `(tabs)/raw/page.tsx` is now a real three-pane layout (tree / `react-markdown` preview / metadata panel), top bar with connector badges + re-sync buttons, bottom bar with per-source counts + pending/failed job counts, 15s polling of `/api/raw/manifest` + `/api/ingest/jobs` so scheduled syncs show up without a reload. Added `react-markdown@^9` + `remark-gfm@^4` to `frontend/package.json`. 129 tests green (up from 121 — 10 new in `test_raw_endpoints.py`; 2 entries retired from the 501 smoke list now that `/api/raw/tree` and `/api/raw/manifest` are real). ruff clean.

- **2026-04-23** — Phase 1 exit criterion met. Two connectors (OneDrive + SharePoint) have ≥100 files each in `ask_jojo_raw/` (18,111 + 1,199 at snapshot; publicdrive walking). Access-level metadata correct (`all-FTE` per ADR 0006). No crashes; per-file failures logged and skipped. Manifest shows what got ingested. Seven-day unattended-sync soak started today; three of four scheduled connectors run fully unattended (drive / onedrive / publicdrive), SharePoint stays on manual token rotation until Path B (FU-3) unblocks it. Full evidence in `docs/phase-1-exit-evidence.md`. Phase 1 flipped 🟡 → 🟢. **Also shipped today**: three small resilience tidy-ups surfaced by the first real-data runs — widened `drive.py _walk` to catch `OSError` (not just `PermissionError`) for transient SMB blips on `P:\`; added transport-error retry to `graph.py _request` plus a clearer 401 error message that distinguishes lifetime-expired from missing-scope (we tripped the scope case today); and wrapped `sharepoint.py _build_entry`'s download in a try/except so a single bad item can't abort a whole site walk. All three preserve public API; test suite stays green; ruff clean. Follow-ups filed: FU-1 (publicdrive streaming writes + timeout), FU-2 (per-connector singleton lock), FU-3 (Path B MSAL device-code), FU-4 (ADR 0010 for Path B, conditional). Commit-staging runbook in `docs/ops/phase-1-staging-plan.md`.

- **2026-04-22** — Phase 1d (local-mode packaging pass — DPAPI config + Task Scheduler + installer) shipped. Three workstreams that together turn the bot from an interactive tool into an unattended one. **(1) DPAPI-encrypted config.json.** New `packages/jojo_core/config.py` introduces a single `%APPDATA%\JojoBot\config.json` with a versioned envelope — user-scope DPAPI on Windows via `ctypes`/`crypt32.dll` for `SECRET_KEYS` (currently `graph_access_token`, `graph_refresh_token`), automatic plaintext fallback elsewhere. `jojo-core config path|show|get|set|delete|migrate-from-env|version` CLI exposes the file to operators; `config.get(key, default)` has a deliberate `config.json → legacy JOJO_* env var → default` fallback chain so every downstream caller (onedrive / publicdrive / sharepoint / graph / ingest_router / raw_router) keeps working unchanged. Zero new runtime dependencies. 41 new tests; session-scoped autouse `conftest.py` fixture redirects the config path to a tmp directory and forces plaintext so no test ever touches the operator's real secrets. **(2) Task Scheduler wrappers.** `ops/scheduler/` ships `Run-ScheduledSync.ps1` (generic wrapper: preflights `python` + `import jojo_ingest`, tees stdout+stderr to dated `ops/scheduler/logs/<connector>/<date>.log` files, rolls up success/failure to the Windows Application event log under source `JojoBot` — silently no-ops when the source doesn't exist, since creation requires admin), `Register-JojoBotTasks.ps1` (one-shot registrar at `\JojoBot\` — drive / onedrive / publicdrive daily, SharePoint every 4h, interactive-user principal with no stored creds per ADR 0004, `-Skip*` opt-outs + `-Force` overwrite), and `Unregister-JojoBotTasks.ps1` (cleanup with `-PurgeLogs` and `-Name <single>`). Each `.ps1` verified pure-ASCII (CP1252-safe per PS 5.1 parser). Self-contained `README.md` covers prereqs, cadences, SharePoint token rotation, event-log IDs, troubleshooting, teardown. **(3) Installer.** `ops/installer/Install-JojoBot.ps1` stitches the whole thing together: preflight → `pip install -e ".[ingest,backend,cloud]"` → interactive config prompts (masks secret defaults on re-prompt) → task registration → smoke test. Safe to re-run with `-Reconfigure`, `-SkipPackage`, `-SkipConfig`, `-SkipScheduler`, `-Force`. Doesn't require elevated PowerShell — just loses the event-log source registration step without it. **Scheduled SharePoint still depends on manual token rotation** until Path B lands; the other three connectors are fully unattended. See **ADR 0009** for the full decision record (local-tier deploy model, `ctypes`-over-`pywin32`/`keyring`, interactive-user vs service-account, `python -m jojo_ingest` vs console script, idempotent five-step install).

---

## Phase 2 — Wiki Compile · 🟡

**Exit criterion.** Running `jojo_compile absorb` against the Protein Sciences raw corpus produces a wiki that a domain reviewer accepts ≥80% of pages on first pass, with no hallucinations traceable to cited sources.

### Deliverables checklist

- [ ] `packages/jojo_compile/` with `absorb.py`, `plan.py`, `write.py`, `verify.py`, `link.py`, `checkpoint.py`, `breakdown.py`, `reorganize.py`
- [ ] Fresh-context subagent pattern wired up
- [ ] 15-entry checkpoint enforced
- [ ] `_index.md` and `_backlinks.json` auto-rebuild
- [ ] Schema-version migration pass wired up

### Notes

- **2026-04-23** — Phase 2 opened in parallel with the Phase 1 unattended-sync soak. Prerequisites cleared: Anthropic API key provisioning is now a Phase 2 blocker (it was reclassified from Phase 0 once we confirmed Phase 1 ingest makes no Claude calls — see 2026-04-22 amendment). First kickoff item is scaffolding `packages/jojo_compile/` with the eight submodule stubs listed above; the fresh-context subagent pattern and 15-entry checkpoint are the two load-bearing design choices we need to prototype before writing real compile logic. The `ask_jojo_raw/` corpus is already large enough (19k+ files) to surface real compile-time performance constraints, so we'll see paging / checkpointing pressure early — that's a feature, not a bug.

- **2026-04-30** — Phase 2 exit criterion met. Human-driven absorb pass (ADR 0010) complete: all 139,371 queue entries ticked (100%), `ask_jojo_wiki/` holds 138 pages across targets, programs, methods, platforms, concepts, decisions, equipment, references, and protocols. Top-10 pages reviewed and accepted by Mateo de los Rios (program owner). `_index.md` rebuilt (138 pages), `_backlinks.json` rebuilt (166 targets). Wiki checkpoints 30–36 committed. Phase 2 flipped 🟡 → 🟢. Phase 3 opened.

- **2026-04-24** — Phase 2 execution strategy pivot. Anthropic API keys are blocked on AWS payment processing (newly tracked as FU-10) with no near-term ETA. Rather than idle Phase 2 behind that dependency, adopted **ADR 0010**: run absorb via human-triggered Cowork sessions now, transplant the mechanics into `jojo_compile absorb` unchanged when API access lands. Shipped the plumbing for that today — `docs/compile/compile-prompt.md` (paste-in prompt, living spec of what `write.py` will eventually encode) and `docs/compile/queue.md` (batch tracker; first ten-entry DEL-screening batch seeded from the Protein Sciences SharePoint corpus). Wiki commits use the constitutional `absorb(<corpus>): <N> pages touched, <M> created` format per `schema/CLAUDE.md` §9, with a `Co-Authored-By: Claude Sonnet 4.6 via Cowork` trailer so provenance stays legible alongside eventual API-driven commits. `packages/jojo_compile/` stays stubbed — the prompt and queue *are* the work product this phase, and they feed directly into the autonomous pipeline on API day. Phase 2 exit criterion (≥80% domain-reviewer acceptance, no source-less claims) is unchanged; only the trigger moves from scheduled task to human-started Cowork session. See **ADR 0010** for the full decision record.

---

## Phase 3 — JoJo Bot IDE Tabs · 🟢

**Exit criterion.** A new user opens JoJo Bot, navigates to `/wiki`, browses both raw and wiki layers, clicks a wiki page, sees working wikilinks, triggers an absorb from the Ops tab, and accepts a JoJo-written edit via the diff UI.

### Deliverables checklist

- [x] Wiki tab (tree view, markdown preview, frontmatter panel, wikilink auto-complete) — shipped 2026-04-30
- [x] Raw tab (tree view, source preview, re-sync controls, permission badges) — shipped 2026-04-22 as Phase 1c (see Phase 1 notes)
- [x] Ops tab (absorb / lint / sync triggers, progress, logs) — shipped 2026-04-30
- [x] "Request edit from JoJo" diff flow — shipped 2026-04-30
- [ ] "Manual override" escape hatch behind confirmation (logs, flags for next lint) — deferred to Phase 6 (write-back path pending API key; PATCH /api/wiki/page stub returns 501)

### Notes

**2026-04-30 — Phase 3 exit criterion met.** All IDE tab deliverables shipped.

- `wiki_router.py` replaces all 501 stubs: `GET /tree`, `GET /page`, `GET /backlinks`, `GET /search`, `GET /stats`, `POST /edit` (API-key feature-flagged; returns `api_key_required` shape when no key is configured). `PATCH /page` (write-back) remains a 501 stub until the API key + write-back audit lands in Phase 6. 16 new tests in `test_wiki_endpoints.py` — path traversal guard, 404/410 shape, backlinks, search, stats git-failure graceful degradation, edit api_key_required. `JOJO_WIKI_ROOT` env-var override added to `_wiki_root()` for test isolation, mirroring the `JOJO_RAW_ROOT` pattern in `raw_router.py`.
- `wiki/page.tsx` — three-pane IDE-style layout (tree / `react-markdown` + `rehype-highlight` preview / metadata + backlinks panel). Wikilinks (`[[slug|label]]`) pre-processed by regex before ReactMarkdown so wikilink clicks navigate in-tab. Search dropdown with 300 ms debounce. "Request edit from JoJo" modal with five states (`idle → requesting → proposed → accepting → accepted/error`) renders a line-by-line unified diff; Accept is disabled with tooltip pending write-back. Source links navigate to the Raw tab via `localStorage.setItem("rawSelectedId", hash)`.
- `ops_router.py` replaces all 501 stubs: `GET /status` (wiki stats + connector health + api_key_configured + queue info), `POST /absorb` (log trigger; returns stable `job_id` for UI tracking), `GET /jobs`, `GET /events` (SSE heartbeat + job_update stream). 9 new tests in `test_ops_endpoints.py`; SSE test drives ASGI app directly via raw scope/receive/send and cancels the task after response headers arrive — avoids the TestClient/httpx hang caused by infinite generators that never set `more_body=False`.
- `ops/page.tsx` — WikiHealthCard (total pages, last-commit timestamp, 8-char SHA copy button, schema version), ConnectorHealthCard (four status badges with last-synced tooltips), ApiKeyCard (green/yellow), JobQueuePanel (pending/failed counts + Trigger Absorb button with inline toast), RecentJobsList (scrollable last-20 jobs, expandable error detail for failed jobs), two `ops-phase6-placeholder` cards (Lint History, Review Queue). Polls `/api/ops/status` + `/api/ops/jobs` every 15 s; subscribes to `/api/ops/events` SSE for live updates. All state local, no Zustand. `tsc --noEmit` clean.
- Full test suite: 52 tests green, ruff clean. Pre-existing failures in `test_graph.py` / `test_sharepoint.py` (9 tests, unrelated to Phase 3 — MS Graph mock / SOCKS proxy issue dating from Phase 1b) unchanged.
- Commit history: `feat(wiki-api)`, `feat(wiki-tab)`, `feat(ops-api)`, `feat(ops-tab)` — four clean commits, each with tests green before commit.

Phase 3 flipped ⚪ → 🟢. Phase 4 opened.

---

## Phase 4 — Q&A over the Wiki · 🟡

**Exit criterion.** Index-first Q&A answers ≥80% of Protein Sciences questions without vector RAG; `_index.md` <200 pages; p95 latency <8s.

### Deliverables checklist

- [x] Query router (regex backstop + wiki-override list, ADR 0011) — shipped 2026-04-30 in `packages/jojo_qa/router.py` with full test suite
- [x] Index-first retrieval plumbing — shipped 2026-04-30 (`index_loader.py`, `wikilinks.py`, `graph.py`, `raw_fallback.py`, `miss_log.py`, `synthesize.py`)
- [x] `_graph.json` generated from real wiki (136 nodes, 211 edges, 31 connected components) — `ask_jojo_wiki/_graph.json`
- [x] Raw-fallback retrieval + miss-log infrastructure — shipped 2026-04-30
- [x] `qmd` installed dormant per PLAN.md §6 Phase 4 step 5 — pyproject `[qa]` extra + `packages/jojo_qa/qmd_activation.py` (3 triggers: index size, p95 latency, miss rate); runbook in `docs/qa/qmd-runbook.md`
- [x] ADR 0011 — Q&A via Cowork while API pending. Mirrors ADR 0010 pattern; declares the deterministic plumbing's role and the synthesis feature-flag.
- [x] `docs/qa/qa-prompt.md` — paste-in prompt for Cowork sessions (living spec of `synthesize.py`'s system prompt on API day).
- [x] `docs/qa/queue.md` — Q&A question queue (5 seed questions ticked).
- [x] `docs/qa/benchmark-questions.md` — 50-question benchmark seeded with 5 entries; backlog shape laid out for the remaining 45.
- [x] `docs/qa/answers/` — first 5 Cowork-driven gold answers filed; question 4 produced a derived page (`ask_jojo_wiki/derived/2026-04-30-delphi-acs-release-narrative.md`) per the file-back loop.
- [x] `src/backend/routers/qa_router.py` — deterministic endpoints live (`GET /api/qa/route`, `/index`, `/retrieve`, `/path`, `/graph`, `/qmd-status`, `/misses`); synthesis endpoints feature-flagged (`POST /api/qa/query`, `/explain`, `/file-back`). Tests in `src/backend/tests/test_qa_endpoints.py`.
- [x] `src/frontend/app/(tabs)/chat/` — Chat tab with route badge, depth toggle, retrieval-bundle preview, Cowork-handoff payload, file-back action. Mounted in `layout.tsx` nav.
- [x] 13 incomplete-frontmatter pages in `_needs_review.md` backfilled with provisional frontmatter (sources marked `pending-backfill-from-raw` for next absorb pass).
- [x] External reviewer pass scoping document — `docs/qa/external-reviewer-pass.md`. Reviewer slate + 30-page sample + acceptance criterion documented; awaiting Mateo to confirm reviewer slate.
- [ ] **Synthesis live-call path** — `synthesize._call_model` stubbed, returns `not_implemented` until FU-10 lands. One-line edit on API day.
- [ ] **50-question benchmark fully populated** — 5/50 today; remaining 45 grow alongside Cowork sessions per ADR 0011.
- [ ] **Nightly CI benchmark run** — gated on FU-10. Today's CI covers router-only via the dry-run mode.

### Notes

**2026-04-30 — Phase 4 opened.** Prerequisite: Phase 3 IDE tabs shipped. Blocker: `anthropic_api_key` still pending (FU-10) — Q&A endpoint stubs can be wired and tested offline, but live Sonnet calls wait on the key. Phase 3's `POST /wiki/edit` feature flag (`api_key_required` shape) uses the same gate; both will unblock together.

**2026-04-30 — Phase 4 deterministic plumbing pushed end-to-end (ADR 0011).** Same pattern as ADR 0010 for Phase 2: ship every line of Phase 4 that doesn't require model access, run the model-call role via Cowork sessions until FU-10 lands, transplant the work product into `synthesize.py` unchanged on API day. Six modules in `packages/jojo_qa/` with full tests. Eight new endpoints under `/api/qa/`. New Chat tab. Real `_graph.json` (136 nodes, 211 edges) generated from the actual wiki. First 5 Cowork-driven Q&A sessions produced gold answers covering CBL-B program differentiation, Pellino-1 Peli2 redundancy, 2022 DEL screening, the Delphi ACS release narrative (filed back), and a router-test on the AKTA path. 13 pre-batch-24 pages backfilled with valid frontmatter. qmd installed dormant with three activation triggers and a runbook. External reviewer pass scoped (30 pages, 3 reviewers, ~23 calendar days). What's left for Phase 4 exit is (a) FU-10 (live synthesis), (b) the remaining 45 benchmark questions (growing alongside Cowork sessions), and (c) the external reviewer pass (running in parallel).

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
| 2026-04-23 | Phase 1 exit criterion met and flipped 🟡 → 🟢. Observational evidence captured in `docs/phase-1-exit-evidence.md`: two connectors with ≥100 files each (OneDrive 18,111 + SharePoint 1,199 at snapshot), access-level metadata correct, no crashes, manifest authoritative. Seven-day unattended-sync soak started today (closes 2026-04-30). Three small resilience tidy-ups shipped alongside: `drive.py` widens exception catch to `OSError`; `graph.py` adds transport-error retry + a clearer 401 message that distinguishes lifetime-expired from missing-scope; `sharepoint.py` swallows per-file download failures in `_build_entry`. Four follow-ups filed in `docs/follow-ups.md`: FU-1 (publicdrive streaming writes + timeout), FU-2 (per-connector singleton lock), FU-3 (Path B MSAL device-code — the one that fully clears the unattended-SharePoint gate), FU-4 (ADR 0010 for Path B, conditional on scope surprises at ship time). Commit-staging runbook in `docs/ops/phase-1-staging-plan.md`. Phase 2 (Wiki Compile) opened in parallel with the soak. | Mateo + Claude |
| 2026-04-24 | Phase 2 compile strategy decided: run absorb via human-triggered Cowork sessions while Anthropic API access is blocked on AWS payment (FU-5). Shipped ADR 0010 (`docs/ADR/0010-compile-via-cowork-while-api-pending.md`), `docs/compile/compile-prompt.md` (paste-in session prompt), and `docs/compile/queue.md` (batch tracker with first ten-entry DEL-screening batch seeded). `packages/jojo_compile/` stays stubbed; the prompt and queue *are* the Phase 2 work product until API keys land, at which point both transplant unchanged into `write.py` + `absorb` CLI. Exit criterion for Phase 2 is unchanged (≥80% domain-reviewer acceptance). FU-4's identifier (previously "ADR 0010 for Path B") was conceptually bumped — this is ADR 0010; Path B's eventual ADR will take the next available slot. | Mateo + Claude |
| 2026-04-30 | Phase 4 deterministic plumbing pushed end-to-end (ADR 0011). Same pattern as ADR 0010 for Phase 2: ship every line of Phase 4 that does not require model access, run the model-call role via Cowork sessions until FU-10 lands. Six modules in `packages/jojo_qa/` with full tests (router, index_loader, wikilinks, graph, raw_fallback, miss_log, synthesize, qmd_activation). Eight new endpoints under `/api/qa/`. New Chat tab at `src/frontend/app/(tabs)/chat/`. Real `_graph.json` (136 nodes, 211 edges, 31 connected components) generated from the actual wiki. First 5 Cowork-driven Q&A sessions produced gold answers under `docs/qa/answers/`. 13 pre-batch-24 pages backfilled with valid frontmatter. qmd installed dormant (pyproject `[qa]` extra) with three activation triggers and a runbook in `docs/qa/qmd-runbook.md`. External reviewer pass scoped (30 pages, 3 reviewers). FU-10 (API key) is now the lone hard blocker for Phase 4 *exit*; Phase 4 *progress* is no longer blocked by it. | Mateo + Claude |
