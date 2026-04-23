# ADR 0009 — Local-Mode Packaging: DPAPI Config, Task Scheduler, All-in-One Installer

**Status:** Accepted
**Date:** 2026-04-22
**Deciders:** Mateo de los Rios
**Related:** `ADR 0004` (local-first deployment), `ADR 0007` (SharePoint delegated-auth first), `ADR 0008` (OneDrive local mount)

## Context

By the end of Phase 1b+, the bot could ingest drive, onedrive, publicdrive, and SharePoint — but only when Mateo was sitting in front of an interactive shell with the right env vars exported. Three problems had to be solved before V1 could be "running on its own":

1. **Secret storage.** The SharePoint connector needs a Microsoft Graph access token. Until Path B (MSAL device-code Entra app, `ADR 0007`) unblocks — it's sitting in the Nurix IT queue — the token is a short-lived string an operator pastes from Graph Explorer. We can't commit it to the repo, can't put it in a plaintext file that is liable to land in a screen-share, and pulling in the OS keyring via `pywin32` / `keyring` for one value is overkill.

2. **Unattended runs.** Ingest needs to happen overnight, not whenever the operator remembers to type `jojo-ingest sync-all`. That means Windows Task Scheduler, which runs tasks in a stripped environment that does not inherit the interactive shell's PATH, PowerShell profile, or exported variables. Every env-var assumption in the codebase becomes a silent failure there.

3. **Setup ergonomics.** Standing the system up on a new machine was a multi-page runbook (install Python, pip install extras, create env vars in System Properties, register scheduled tasks by hand). Every manual step is a future bug report.

A related constraint, learned the hard way in the validation run and captured in memory `feedback_powershell_ascii_only.md`: Windows PowerShell 5.1 reads `.ps1` files as CP1252 without a BOM. Any non-ASCII glyph (em-dash, smart quote, ≥, …) causes a parser error partway through the file. Every PowerShell file in this slice is pure ASCII and gets that property checked before commit.

## Decision

**Adopt a three-piece "local mode package" for V1:**

1. **`packages/jojo_core/config.py` — DPAPI-encrypted `%APPDATA%\JojoBot\config.json`.**
   - Single JSON file with a versioned envelope: `{"version": 1, "encryption": "dpapi"|"plaintext", "payload": ...}`.
   - On Windows, secrets (`graph_access_token`, `graph_refresh_token`, and any future key in `SECRET_KEYS`) are DPAPI-encrypted via `ctypes` against `crypt32.dll` — user-scoped, no per-secret dependency on `pywin32` or `keyring`.
   - Non-Windows (Linux CI, future macOS dev) falls back to plaintext automatically, same envelope with `encryption: "plaintext"`. Tests set `JOJO_CONFIG_FORCE_PLAINTEXT=1` so they never touch DPAPI.
   - `config.get(key, default)` has a deliberate fallback chain: config.json → legacy `JOJO_*` env var → default. Old callers work unchanged; new callers prefer the file. `env_fallback=False` disables the env step for tests and for `jojo-core config get --no-env`.
   - Every write is atomic (`os.replace`); corrupt or unknown-encryption files refuse to load rather than silently discarding data.

2. **`ops/scheduler/` — Windows Task Scheduler wrappers.**
   - `Run-ScheduledSync.ps1` — generic wrapper invoked by every task. Preflights Python and `import jojo_ingest`, runs `python -m jojo_ingest sync <connector>`, tees stdout+stderr to `ops/scheduler/logs/<connector>/<date>.log`, and writes a rollup line to the Windows Application event log under source `JojoBot` (skipped silently if the source doesn't exist — creating it requires admin).
   - `Register-JojoBotTasks.ps1` — one-shot registrar that creates four tasks under `\JojoBot\`: drive / onedrive / publicdrive daily; SharePoint every 4h. Interactive principal (`-LogonType Interactive`, `-RunLevel Limited`), no stored service-account credential. `-Skip*` opt-out flags per connector, `-Force` to replace existing tasks.
   - `Unregister-JojoBotTasks.ps1` — cleanup with `-PurgeLogs` and `-Name <single>` scoping. Leaves config.json and the event-log source in place so re-registration doesn't lose state.
   - `ops/scheduler/README.md` — self-contained operator doc covering prereqs, cadences, token rotation, event-log IDs, troubleshooting, and teardown.

3. **`ops/installer/Install-JojoBot.ps1` — all-in-one bootstrap.**
   - Five ordered steps: preflight (python/pip/git) → `pip install -e ".[ingest,backend,cloud]"` → interactive config prompts writing through `jojo-core config set` → task registration (reuses the scheduler scripts above) → smoke test (`jojo-ingest --help` + `jojo-core config show`).
   - Safe to re-run; `-Reconfigure`, `-SkipPackage`, `-SkipConfig`, `-SkipScheduler`, `-Force` let an operator re-execute any subset.
   - Existing config values are shown as defaults; secret defaults are masked (`"<first2>***<last2>"`) so a shoulder-peeker doesn't get the full token.
   - Does NOT require elevated PowerShell. Without elevation, Task Scheduler tasks still register; only the event-log source creation is skipped.

**The SharePoint token lives DPAPI-encrypted in `config.json` and rotates manually until Path B ships.** The token's ~60 min expiry means most scheduled SharePoint runs fail with 401 until the operator runs `jojo-core config set graph_access_token "<new>"`. That is documented; the other three connectors keep running. This is a known, tolerable gap for a single-operator V1.

## Rationale

Four reasons drove each of these shapes:

1. **`ctypes` + `crypt32.dll` instead of `pywin32` or `keyring`.** Zero new runtime dependencies. `pywin32` is a 15 MB install that pulls in compiled wheels for every Python version; `keyring` has a sprawling plugin ecosystem with its own backends. DPAPI via `ctypes` is 40 lines of code, user-scoped by default (which is what we want — the same Windows account that ingests should be the only one that can decrypt), and perfectly testable under a Linux CI using monkeypatched primitives. The encryption envelope is forward-compatible: if we ever need per-machine scope or a second encryption scheme, it's a `encryption:` string change plus a decode branch.

2. **"Run only when user is logged on" over stored credentials.** `ADR 0004` puts us on the local-tier deploy model: the bot runs on the operator's laptop, inherits the operator's permissions, and holds no tenant-wide secrets. Task Scheduler's "Run whether user is logged on or not" option requires stashing the user's Windows password in the task definition. That is both a security downgrade (one-step password exfiltration) and operationally brittle (breaks on every password rotation). Interactive-only tasks wake up when the laptop wakes up, skip gracefully when it doesn't (`-StartWhenAvailable`), and inherit the mapped `P:\` drive + OneDrive client's authenticated state without any additional credential plumbing. The per-task battery / timeout knobs are the same.

3. **`python -m jojo_ingest` instead of the `jojo-ingest` console script.** Task Scheduler launches its child process with the machine's default environment, not the operator's interactive PATH — any console script whose entry point is in a per-user `Scripts\` dir is reachable only because pip edited that shell's PATH. Using `python -m <package>` bypasses the problem entirely and matches the pattern `ops/validation/Invoke-SyncAll.ps1` already uses (same lesson, same fix). The wrapper auto-detects `python` vs `py` so it works on either a Microsoft Store or python.org install.

4. **One installer script, five ordered steps, all idempotent.** Splitting installer logic across multiple files (an `Install-Python.ps1`, a `Setup-Config.ps1`, etc.) produces more code without reducing the number of places a new operator has to look. One linear script with step headers is legible: each `[n/5]` line shows where it is in the flow; `-Skip*` flags let a returning operator re-run just the step they need. The install / reinstall / reconfigure paths collapse into one file.

## Consequences

### Positive

- Secrets off the command line and out of `~/.bashrc`-style exports. Screen-shared Graph Explorer tokens never land in plaintext on disk.
- Unattended runs. Four scheduled tasks cover drive / onedrive / publicdrive / SharePoint on overnight cadence, picking up automatically after reboots.
- New-machine install is one elevated `Install-JojoBot.ps1` from the repo root. Operator answers 3-5 prompts; no env-var dance.
- The `jojo-core config` CLI gives operators a first-class tool for rotating the Graph token — `jojo-core config set graph_access_token "<new>"` — without restarting the backend.
- Logs are dated per-connector and tee interleaved stdout+stderr; the event log gets a rollup for `LastTaskResult`-style visibility. Postmortems have two layers of evidence.
- Zero new runtime dependencies. Same wheelhouse, same CI image.

### Negative

- **DPAPI user-scope means config.json is not portable across Windows accounts.** If the operator changes their Windows login, they must re-run `jojo-core config set` for every key. Acceptable for V1 (one operator, one login). Phase 7b's shared-server deployment will have to revisit — machine-scope DPAPI + a tighter ACL, or a real secret manager.
- **SharePoint token rotation is manual until Path B ships.** 401s in the scheduled log are the expected signal. The UX is "operator notices red badge in UI, runs one command, moves on." Tolerable but not invisible; ADR 0007's MSAL refresh-token path will close this.
- **No centralized monitoring.** An operator only knows the scheduled task failed if they check Task Scheduler's `LastTaskResult`, skim the log, or notice the Raw tab's "latest fetched" is stale. Fine for one laptop, not fine for Phase 7b. A simple Prometheus exporter or even a daily "bot health" email is on the Phase 2+ watchlist.
- **ASCII-only constraint on `.ps1`** has to be guarded actively. Future scripts written in an editor that auto-smart-quotes ("Word mode") will break PS 5.1 parsing. Mitigation: the lesson is captured in the `ops/scheduler/README.md` "Design notes" section and in auto-memory (`feedback_powershell_ascii_only.md`); every new `.ps1` is checked via a tiny Python snippet before commit.
- **Install flow assumes a live internet connection.** `pip install -e ".[...]"` pulls wheels. For fully air-gapped installs we'd need a pre-built wheelhouse. Not a V1 concern, but worth noting when Phase 7b lands in a more locked-down environment.

## Revisit When

- Path B (Entra app + MSAL device-code) unblocks — the pasted Graph token and the rotation documentation both go away.
- Phase 7b begins — shared-server deployment makes user-scope DPAPI the wrong choice; we'll need a real secret manager (Azure Key Vault, HashiCorp Vault, or KMS) and a service principal instead of per-user interactive tasks.
- The scheduled-run latency starts mattering — the current 4h SharePoint cadence is chosen to balance token freshness with tenant throttling; if token rotation becomes invisible (post Path B), cadence could drop to 1h.
- Operators other than Mateo start using it — multi-user setup needs config.json provisioning automation, not interactive prompts.
