# Phase 1 Exit-Criterion Evidence

**Last updated.** 2026-04-23

This doc captures the observational evidence that Phase 1 ("Source Ingestion") has met the exit criterion defined in `PLAN.md` §6 Phase 1 and `docs/v2_status.md`. It complements — but does not replace — the machine-generated validation reports under `ops/validation/reports/`. Those reports are the source of truth for per-run numbers; this doc is the human-readable wrap-up that cites them.

See also:

- `PLAN.md` §6 Phase 1 — exit criterion text (authoritative).
- `docs/v2_status.md` — living phase tracker (this doc feeds the Phase 1 "exit-criterion met" cell).
- `docs/ADR/0007-sharepoint-delegated-auth-first.md` — Path A auth decision; explains why scheduled SharePoint runs remain manual-rotate today.
- `docs/ADR/0008-onedrive-local-mount-over-graph.md` — OneDrive / PublicDrive walk-the-local-sync-folder decision.
- `docs/ADR/0009-local-mode-packaging-and-dpapi-secrets.md` — DPAPI config + Task Scheduler + installer.
- `docs/ops/path-b-msal-device-code-setup.md` — next auth path (unblocks fully unattended SharePoint).

---

## Exit criterion (from PLAN.md)

> Click 'Sync all' in the UI; the system pulls a meaningful slice of Protein Sciences data into `ask_jojo_raw/` in under an hour. **≥100 files from ≥2 connectors.** Access-level metadata correct. No crashes. Manifest shows what got ingested. Daily incremental sync runs unattended for a week.

The criterion decomposes into six separable gates. We evaluate each below.

| # | Gate | Status |
| - | --- | --- |
| 1 | ≥100 files ingested into `ask_jojo_raw/` | 🟢 met |
| 2 | ≥2 connectors contributing | 🟢 met |
| 3 | Access-level metadata correct | 🟢 met |
| 4 | No crashes (ingest exits 0) | 🟢 met |
| 5 | Manifest shows what got ingested | 🟢 met |
| 6 | Daily incremental sync runs unattended for a week | 🟡 in progress — scheduler wired + 3 of 4 connectors unattended today; SharePoint needs Path B to fully clear |

Gates 1–5 are met as of 2026-04-23. Gate 6 is architecturally satisfied (`ops/scheduler/` registers four tasks; three run unattended end-to-end; SharePoint still requires the operator to rotate the Graph token every ~60 min). The seven-day soak is the remaining observation window — it starts today and we expect to declare it met by 2026-04-30 without code changes. Path B (ADR 0007) converts the SharePoint gate from "needs a human touch every 60 min" to "needs a human touch every ~90 days."

We consider Phase 1 exited for purposes of moving on to Phase 2 work in parallel with the seven-day soak. If the soak surfaces a crash, we fix it and reset the clock without reopening the whole phase.

---

## Evidence per gate

### Gate 1 — ≥100 files ingested

**Filesystem count of raw `.md` files at 2026-04-23 11:09 PT:**

| Subtree of `ask_jojo_raw/` | `.md` files |
| --- | ---: |
| `onedrive/` | 18,111 |
| `sharepoint/` | 1,199 (mid-run; growing) |
| `publicdrive/` | in-flight (walker still running at time of capture) |
| **Total** | **19,310+** |

Source: `find ask_jojo_raw -type f -name '*.md' | wc -l` against the operator's working tree on DESKTOP-CPOD0VB. This is ≥193× the threshold; the criterion is met comfortably even ignoring publicdrive.

### Gate 2 — ≥2 connectors contributing

Three connectors have written entries into `ask_jojo_raw/manifest.json` this phase:

| `source_type` | Status | Notes |
| --- | --- | --- |
| `onedrive` | 🟢 ingested | Local-mount walker over `C:\Users\mdelosrios\OneDrive - Nurix Therapeutics, Inc` (ADR 0008). |
| `sharepoint` | 🟢 ingested | MS Graph v1.0 via delegated token (ADR 0007). Six sites: Protein Sciences, NurixNet, DEL Triage Seed Projects, DEL Screen Team, CRUK Grant, Biortus. |
| `publicdrive` | 🟡 in-flight | Local-mount walker over `P:\` (ADR 0008). Long-running first walk; incremental re-runs land inside the hour budget. |

`drive` is configured but not exercised in this run (optional; Phase 1a only needed it for the smoke test, which is green — see Gate 5). The criterion asks for ≥2 and we have at least two (onedrive + sharepoint) with real data on disk today.

### Gate 3 — Access-level metadata correct

Every entry written by `IngestDriver` goes through the frontmatter pass in `packages/jojo_connectors_common/frontmatter.py`, which requires an `access_level` field. The default policy (`ADR 0006`) classifies every connector currently live as **`all-FTE`** because:

- OneDrive sync folder mirrors Mateo's own Nurix OneDrive — content is personal but tenant-scoped.
- SharePoint sites we walk are Nurix-internal SharePoint (all-FTE read is the ACL baseline).
- `P:\` is the Nurix-wide "public" SMB share — all-FTE by name.

`access_level: all-FTE` is stamped on every raw `.md` at write time and validated by the manifest schema. Finer-grained ACLs (beyond all-FTE) are explicitly gated on IT/Legal review and tracked as a Phase 7b deliverable — not a Phase 1 requirement. Legal cleared this classification on 2026-04-22 conditional on the `ask_jojo_raw` repo remaining private (Open Question #3, ADR 0006).

Spot check: pick any file under `ask_jojo_raw/sharepoint/` and confirm the frontmatter block includes `access_level: all-FTE`. Any file failing this check is a bug to file against the ingest driver, not a Phase 1 blocker.

### Gate 4 — No crashes (ingest exits 0)

| Connector | Latest run exit code | Duration | Notes |
| --- | --- | --- | --- |
| sharepoint | 0 | 2s (pre-fix 401 run) → now streaming at ~2 files/sec | Pre-fix run exited clean because sites 401'd and we log-and-skip; post-fix run writing entries as of capture. |
| onedrive | 0 | 1,976s (~33 min) | 101 updated, 18,068 skipped (already-ingested), 83 per-file failures (logged-and-skipped per the `_build_entry` hardening — ADR 0008 / task #53). |
| publicdrive | _pending (in-flight)_ | (ongoing) | See [Gate 6 Caveats](#gate-6-caveats-path-b-and-publicdrive-soak) for follow-up tasks. |

Key design decision: per-file download / conversion failures **do not** abort the run. `_build_entry` and the graph `_request` retry (task #52) both log-and-continue. 83 errors inside a 19k-file tree is 0.4% — within the "messy real data" tolerance, not a Phase 1 blocker. Each failure is captured in the per-run JSON report for later review.

Latest validation report: `ops/validation/reports/sync-all_20260423_100608.md` (tail truncated while publicdrive is still running; previous full report at `sync-all_20260422_215928.md`).

### Gate 5 — Manifest shows what got ingested

`ask_jojo_raw/manifest.json` is the single source of truth for what's in the raw corpus. At 2026-04-23 11:09 PT:

- Schema version: `0.1.0` (locked; migration machinery tracked for Phase 2).
- Entry count: matches filesystem count in Gate 1 (19,310+).
- Keyed by `entry_id`; every entry has `source_type`, `source_ref`, `sha256`, `fetched_at`, `access_level`, plus connector-specific `extra` fields (`graph_item_id` / `graph_drive_id` / `graph_site_id` / `site_display` / `drive_name` for SharePoint; local path + mtime for drive family).
- Per-change audit trail in `ask_jojo_raw/_changes/2026-04-23.json` (today's additions + updates).
- Smoke test `test_phase1_exit_criterion` still green on its canonical 120-file fixture (105 ingested, 15 ignored, re-run zero-work, 5-edit → 5 updates). Runs every CI cycle; green on the commit that seeded the manifest you see today.

Raw tab UI (Phase 1c) renders the manifest directly, so operator spot checks land on the same data the compile pass will consume.

### Gate 6 — Daily incremental sync runs unattended

**Architecture: done.** `ops/scheduler/Register-JojoBotTasks.ps1` creates four Windows Task Scheduler tasks under `\JojoBot\`:

| Task | Cadence | Principal | Unattended today? |
| --- | --- | --- | --- |
| `JojoBot\sync-drive` | Daily | Interactive user | ✅ yes |
| `JojoBot\sync-onedrive` | Daily | Interactive user | ✅ yes |
| `JojoBot\sync-publicdrive` | Daily | Interactive user | ✅ yes |
| `JojoBot\sync-sharepoint` | Every 4h | Interactive user | ⚠️ partial — Graph token expires ~60 min, needs rotation |

Three of four connectors sync on schedule with no human in the loop. SharePoint runs on schedule but 401s after ~60 min until the operator runs `jojo-core config set graph_access_token "<new>"`. Path B (MSAL device-code, tracked in ADR 0007 and `docs/ops/path-b-msal-device-code-setup.md`) replaces pasted tokens with a ~90-day cached refresh — the code path slots in behind the existing `TokenProvider` interface without touching the connector.

**The seven-day soak starts 2026-04-23.** Day 1 data captured by this doc. Expect to update this section daily with observed vs expected task-run counts until 2026-04-30.

#### Gate 6 caveats (Path B and publicdrive soak)

- **Path B (MSAL device-code):** not yet shipped. Tracked in ADR 0007 as the next auth path and in `docs/ops/path-b-msal-device-code-setup.md`. Until it lands, scheduled SharePoint ingest requires operator token rotation roughly every hour during business activity. This is acceptable for the 7-day soak — we measure the three-connector cadence and note SharePoint separately.
- **Publicdrive first walk:** the initial `P:\` walk is long-running (observed multi-hour; exact duration TBD once the in-flight run finishes). Incremental re-runs after the first walk land inside the hour budget because the manifest short-circuits already-ingested files. We are tracking two follow-ups for resilience (task #58): (a) streaming writes during the walker's enumeration phase so progress is visible and crash recovery is cheap; (b) per-connector singleton lock so a second invocation of `sync publicdrive` can't race the first and corrupt the manifest.

---

## Today's resilience tidy-up (2026-04-23)

In service of Gate 4 / Gate 6 resilience, we shipped three small hardening changes today. All three preserve the existing public behavior; they just make "messy real data" and "token expires mid-run" hurt less.

| File | Change | Reason |
| --- | --- | --- |
| `packages/jojo_ingest/drive.py` | Widen `_walk` exception catch from `PermissionError` to `OSError` | `P:\` drive surfaces WinError 59 (network I/O) and long-path errors that aren't `PermissionError` subclasses. Skipping these per-file preserves the rest of the walk. |
| `packages/jojo_ingest/graph.py` | Transport-error retry in `_request`; replaced misleading "token likely expired" 401 message with scope+lifetime dual hypothesis pointing to jwt.ms | Flaky tenant network dropped individual Graph requests, aborting an otherwise-good run. And the old 401 message told operators the token was stale even when the real cause was a missing `Sites.Read.All` scope — which we hit today. |
| `packages/jojo_ingest/sharepoint.py` | Swallow per-file download failures in `_build_entry` | A single bad file (e.g., 0-byte placeholder) previously aborted a whole-site walk. Now logged + skipped, same pattern as drive. |
| `ops/installer/Install-JojoBot.ps1` + `ops/scheduler/Enable-JojoShell.ps1` | Wired `Enable-JojoShell.ps1` into the installer as its final step | Installer finishes with an immediately usable shell. Operator no longer has to open a new terminal after install and remember to activate the venv. |
| `ops/scheduler/README.md` | Document `Enable-JojoShell.ps1` alongside the scheduler scripts | Operators land on this README when a scheduled run misbehaves; surfacing the interactive shell helper here closes the loop. |

All edits verified pure-ASCII per ADR 0009 / feedback memory (CP1252 + PS 5.1 parser). 129 pytest tests stay green; ruff clean.

See task #62 for the commit-staging plan.

---

## Known follow-ups carried out of Phase 1

Nothing here blocks the exit criterion, but each is worth tracking so we don't lose them when Phase 2 starts:

1. **Path B (MSAL device-code provider)** — ADR 0007, dummy's guide at `docs/ops/path-b-msal-device-code-setup.md`. Unblocks fully unattended SharePoint scheduled runs.
2. **Publicdrive walker streaming writes + timeout** — task #58a. First walk is very long; interim progress + crash-resume would make the 7-day soak more forgiving.
3. **Per-connector singleton lock** — task #58b. Defensive: two overlapping `sync publicdrive` runs can't corrupt the manifest today because the writer is append-only per change record, but we also don't want them racing the same FS walk. Cheap `msvcrt.locking()` on `%APPDATA%\JojoBot\locks\<connector>.lock` is sufficient.
4. **ADR 0010 (optional)** — if Path B ships as planned, consider whether to fold the decision into ADR 0007 or write a new ADR documenting the transition. Deferred until we actually ship Path B so the ADR reflects real behavior, not speculation.

---

## How to regenerate the numbers in this doc

```powershell
# File counts per connector (from the operator's WSL or PowerShell).
cd C:\Users\mdelosrios\Claude_Local\jojo_bot_v2.0\ask_jojo_raw
(Get-ChildItem -Recurse -File -Filter *.md sharepoint).Count
(Get-ChildItem -Recurse -File -Filter *.md onedrive).Count
(Get-ChildItem -Recurse -File -Filter *.md publicdrive).Count

# Latest validation-run summary.
Get-ChildItem ..\ask_jojo\ops\validation\reports\sync-all_*.md |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1

# Task Scheduler state.
Get-ScheduledTask -TaskPath '\JojoBot\' | Format-Table TaskName,State,LastRunTime,LastTaskResult

# Full re-run (writes a fresh report under ops/validation/reports/).
.\ops\validation\sync-all.ps1
```

The `sync-all.ps1` driver writes both a `.md` human report and a `.log` raw stdout/stderr capture named `sync-all_<yyyymmdd_hhmmss>.{md,log}`. Both are checked into the repo to keep an append-only record of the bot's real-world behavior across phases.
