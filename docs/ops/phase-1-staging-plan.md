# Phase 1 wrap-up commits — staging plan

**Last updated.** 2026-04-23

Working directory: `C:\Users\mdelosrios\Claude_Local\jojo_bot_v2.0\ask_jojo\`.

The uncommitted Phase 1 work splits cleanly into three commits. They should land **in this order** so bisects stay sane: A (ships the packaging pass), then B (hardens runtime against messy real data), then C (documents that Phase 1 is done).

Nothing here is destructive. If you want to collapse B into A or A into B for tidier history, that's fine — the split below is about bisect hygiene, not ceremony. `git log --oneline -5` before starting so you can confirm `c763b71 feat(core): DPAPI-encrypted config.json + jojo-core config CLI (Track 2 pt. 1)` is the immediate parent.

Smoke-test gate between every commit: `pytest -q` must stay green. Do not split-push — push all three at once when the suite is green on the tip.

---

## Commit A — Track 2 pt. 2: Task Scheduler + installer + ADR 0009

**Scope.** Ship the second half of the local-mode packaging pass so `c763b71` is no longer a half-merge on main. Adds the PowerShell wrappers operators actually run plus the decision record that covers both halves.

**Files (all currently untracked):**

```powershell
git add `
  ops/scheduler/Run-ScheduledSync.ps1 `
  ops/scheduler/Register-JojoBotTasks.ps1 `
  ops/scheduler/Unregister-JojoBotTasks.ps1 `
  ops/scheduler/README.md `
  ops/installer/Install-JojoBot.ps1 `
  ops/installer/Enable-JojoShell.ps1 `
  docs/ADR/0009-local-mode-packaging-and-dpapi-secrets.md
```

Intentionally excluded: `ops/scheduler/logs/` (runtime log dir; `.gitkeep` only if you want it), `package-lock.json` (belongs to a separate frontend pin commit if needed).

**Pre-commit sweep.** Every `.ps1` must be pure ASCII — see feedback memory + ADR 0009. PowerShell 5.1 reads `.ps1` as CP1252 without BOM; any curly quote / em-dash / non-breaking-space will parse-error with `TerminatorExpectedAtEndOfString` or similar. Run before committing:

```powershell
Get-ChildItem ops/scheduler, ops/installer -Filter *.ps1 -Recurse |
  ForEach-Object {
    $bad = Select-String -Path $_.FullName -Pattern '[^\x00-\x7F]' -AllMatches
    if ($bad) { Write-Host "NON-ASCII in $($_.Name): $($bad.Matches.Count)" -ForegroundColor Red }
  }
```

No output = green. If something bleeps, fix the offender before staging.

**Suggested message:**

```
feat(ops): Task Scheduler wrappers + all-in-one installer (Track 2 pt. 2)

Completes the local-mode packaging pass. Pairs with c763b71 which shipped
DPAPI config.json and jojo-core config CLI as part 1.

Ships:
- ops/scheduler/Run-ScheduledSync.ps1 -- generic wrapper; tees stdout+stderr
  to dated log files and rolls success/failure to the Windows Application
  event log under source JojoBot.
- ops/scheduler/Register-JojoBotTasks.ps1 -- one-shot registrar under
  \JojoBot\, interactive-user principal per ADR 0004 (no stored creds),
  four tasks: drive / onedrive / publicdrive daily, sharepoint every 4h.
  -Skip* opt-outs + -Force overwrite.
- ops/scheduler/Unregister-JojoBotTasks.ps1 -- cleanup with -PurgeLogs and
  -Name <single>.
- ops/scheduler/README.md -- operator-facing walkthrough: prereqs,
  cadences, token rotation, event-log IDs, Enable-JojoShell, teardown.
- ops/installer/Install-JojoBot.ps1 -- five-step idempotent bootstrap
  (preflight -> pip install -e '.[ingest,backend,cloud]' -> interactive
  config prompts -> Register-JojoBotTasks -> smoke test).
  -Reconfigure / -SkipPackage / -SkipConfig / -SkipScheduler / -Force.
- ops/installer/Enable-JojoShell.ps1 -- final install step; wires the
  venv + PATH so 'jojo-core' and 'jojo-ingest' resolve in a fresh shell.
- docs/ADR/0009-local-mode-packaging-and-dpapi-secrets.md -- decision
  record covering both halves of Track 2 (local-tier deploy model,
  ctypes-over-pywin32/keyring, interactive-user vs service-account,
  python -m vs console script, idempotent five-step install).

All .ps1 verified pure-ASCII (CP1252-safe per PS 5.1 parser).
```

---

## Commit B — resilience tidy-up for messy real data

**Scope.** Three small hardening changes surfaced by the first real `sync-all` runs on Mateo's laptop against the real Protein Sciences corpus. Each preserves the public API; they just make "one bad file / one flaky connection / one missing scope" stop poisoning a 19k-file walk.

**Files:**

```powershell
git add `
  packages/jojo_ingest/drive.py `
  packages/jojo_ingest/graph.py `
  packages/jojo_ingest/sharepoint.py `
  ops/validation/Run-ValidationSyncAll.ps1
```

**Pre-commit smoke.** From the venv:

```powershell
pytest -q packages/jojo_ingest
ruff check packages/jojo_ingest
```

Both must be clean.

**Suggested message:**

```
fix(ingest): harden walkers against real-world I/O failures

Three small changes surfaced by today's first sync-all runs on the
operator's laptop against the real Protein Sciences corpus.

- drive.py: widen _walk's exception catch from PermissionError to OSError.
  P:\ surfaces WinError 59/64/67/1231 (transient SMB blips, long paths)
  that aren't PermissionError subclasses; one bad subtree should never
  abort an already-yielding walk.

- graph.py: transport-error retry in _request (TransportError wraps
  ConnectError, ReadTimeout, RemoteProtocolError -- the corporate network
  plus Graph's pre-signed CDN seems to drop idle TLS occasionally). Also
  rewrite the 401 error message to distinguish lifetime-expired (~60 min)
  vs missing-scope (e.g. Sites.Read.All for SharePoint) and point at
  jwt.ms for the scp claim; we tripped the scope case today and the old
  "token likely expired" text was misleading.

- sharepoint.py: swallow per-file download failures inside _build_entry
  after the Graph client has already exhausted its transport retries.
  One bad item (404 because it moved, 403 on a per-item permission we
  can't see, CDN surprise) should not abort the whole site walk; the
  driver already reports failure counts in the manifest.

- ops/validation/Run-ValidationSyncAll.ps1: per-connector result extraction
  + markdown report layout improvements surfaced while debugging today.

Test suite stays green (pytest packages/jojo_ingest, ruff clean).
No interface changes; no manifest schema changes; no ADR needed.
```

---

## Commit C — Phase 1 wrap-up docs

**Scope.** Ship the paper trail that says Phase 1 is done. No code.

**Files:**

```powershell
git add `
  docs/phase-1-exit-evidence.md `
  docs/phase-1-wrap-up-checklist.md `
  docs/ops/phase-1-staging-plan.md `
  docs/v2_status.md
```

(`docs/phase-1-wrap-up-checklist.md` and the updated `v2_status.md` land in tasks #59 and #61; list them here so you remember to include them on the same commit. `docs/ops/phase-1-staging-plan.md` is this file.)

**Suggested message:**

```
docs: Phase 1 exit evidence + wrap-up checklist; flip status to green

- docs/phase-1-exit-evidence.md -- observational evidence that Phase 1
  meets the exit criterion (>=100 files from >=2 connectors, access-level
  metadata correct, no crashes, manifest showing what got ingested).
  Includes per-gate tables and citations into ops/validation/reports/.
- docs/phase-1-wrap-up-checklist.md -- MUST-have + SHOULD-have gates
  checked off before moving on to Phase 2 work.
- docs/ops/phase-1-staging-plan.md -- this phase's commit-staging runbook
  (lives on so Phase 2 can model on it).
- docs/v2_status.md -- Phase 1 flipped from yellow to green with exit
  date 2026-04-23; Phase 2 row unchanged (still white/not started);
  dated note + amendment log entry added.

Phase 1 is done. Seven-day unattended-sync soak started today; SharePoint
stays on manual token rotation until Path B (MSAL device-code) lands --
tracked in ADR 0007 and docs/ops/path-b-msal-device-code-setup.md.
```

---

## Push

```powershell
# all three commits staged and green:
git log --oneline -4    # confirm order: Track2-pt2, resilience, docs-wrapup on top
pytest -q               # final green
git push origin main
```

The `ask_jojo_raw/` tree remains deliberately outside this plan — per ADR 0006 it's a separate private repo and gets committed on its own cadence inside `ask_jojo_raw/`.
