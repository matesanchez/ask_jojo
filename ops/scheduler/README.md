# JoJo Bot - Windows Task Scheduler wrappers

Three PowerShell scripts that take JoJo Bot from "works when I run it" to
"syncs on its own overnight." Designed for Mateo's local-tier deploy
model (ADR 0004) where the tasks run under the operator's own Windows
account rather than a service account.

## Files in this directory

| File | Purpose |
| ---- | ------- |
| `Run-ScheduledSync.ps1`        | Generic wrapper. Task Scheduler invokes this with `-Connector <name>`; it runs `python -m jojo_ingest sync <name>` and tees output to a dated log file plus the Windows Application event log. |
| `Register-JojoBotTasks.ps1`    | One-shot registrar. Creates four scheduled tasks under `\JojoBot\` and (best-effort, needs admin) registers the `JojoBot` event-log source. |
| `Unregister-JojoBotTasks.ps1`  | Cleanup. Removes tasks, optionally purges log history. Leaves config.json and the event-log source alone. |
| `logs/<connector>/<date>.log`  | Per-connector dated log files the wrapper tees into. `logs/` is gitignored. |

## Prerequisites

1. **Python available.** The wrapper resolves its interpreter in this
   order:
     1. `<repo>\ask_jojo\.venv\Scripts\python.exe` -- preferred, pinned
        to this repo's install.
     2. `python` on PATH.
     3. `py` (the Windows Python launcher) on PATH.
   Install Python 3.11+ from python.org (check "Add to PATH") *or* let
   `Install-JojoBot.ps1 -UseVenv` create the project venv for you (see
   below). Exit code 2 if none of the three is found.
2. **Project venv (recommended).** Scheduled tasks run under a stripped
   environment: no interactive PATH, no venv auto-activation. Pinning the
   tasks to a project-local venv eliminates the "which Python got picked
   up overnight?" class of failure. One command sets it up:
   ```powershell
   cd <repo>\ask_jojo
   .\ops\installer\Install-JojoBot.ps1 -UseVenv
   ```
   This creates `<repo>\ask_jojo\.venv\`, runs `pip install -e
   ".[ingest,backend,cloud]"` *inside the venv*, and re-registers the
   tasks so they point at `.venv\Scripts\python.exe`. If you skip the
   venv, the wrapper falls back to system `python` -- works, but you're
   responsible for making sure every extra is installed in that
   interpreter.
3. **`jojo_ingest` and connectors importable.** The wrapper preflight now
   probes every connector module (not just `import jojo_ingest`), so a
   missing extra like `httpx` fails before the sync call rather than
   halfway through. If you see preflight exit 2, read the log -- it
   names the module that failed to import.
4. **Shell PATH set up** so bare `jojo-core` / `jojo-ingest` names
   resolve in interactive shells. `Install-JojoBot.ps1` wires this up
   automatically as step 6/7; if you skipped it or installed a different
   way, run the one-shot fix on its own:
   ```powershell
   .\ops\installer\Enable-JojoShell.ps1          # system Python
   .\ops\installer\Enable-JojoShell.ps1 -UseVenv # repo .venv
   ```
   It adds the right Scripts directory to persistent user PATH (no admin
   needed) and also patches the current session so the fix takes effect
   immediately. Idempotent -- safe to re-run when switching between
   system Python and a venv. Scheduled tasks do not use PATH (they
   invoke `python.exe` by absolute path), so this step is quality-of-
   life only; it doesn't affect overnight runs.
5. **`config.json` populated.** At minimum:
   ```powershell
   jojo-core config set onedrive_path    "C:\Users\mdelosrios\OneDrive - Nurix Therapeutics"
   jojo-core config set public_drive_path "P:\"
   jojo-core config set sharepoint_sites "ProteinScience,RegulatoryAffairs"
   jojo-core config set graph_access_token "<paste fresh token>"
   ```
   See `docs/ops/path-b-dummies-guide.md` for how to grab a token while
   Path B (MSAL device-code) is still pending IT.

## Quickstart

```powershell
cd <repo>\ask_jojo\ops\scheduler

# (optional) run from elevated PowerShell so the event log source registers
.\Register-JojoBotTasks.ps1 -DriveSource "C:\Users\mdelosrios\Documents"

# inspect
Get-ScheduledTask -TaskPath '\JojoBot\*' | Format-Table TaskName, State, LastRunTime

# tail today's log for the SharePoint task
Get-Content -Wait -Tail 0 .\logs\sharepoint\$((Get-Date).ToString('yyyy-MM-dd')).log
```

## Task cadence

| Task name            | Connector     | Trigger                                |
| -------------------- | ------------- | -------------------------------------- |
| `JojoBot-Drive`      | `drive`       | Daily at 02:00 (needs `-DriveSource`)  |
| `JojoBot-OneDrive`   | `onedrive`    | Daily at 02:15                         |
| `JojoBot-PublicDrive`| `publicdrive` | Daily at 02:30                         |
| `JojoBot-SharePoint` | `sharepoint`  | Every 4 hours starting at 03:00        |

Cadences are overridable via `-DriveTime`, `-OneDriveTime`,
`-PublicDriveTime`, `-SharePointStart` parameters on the registrar.
Each task can be individually skipped with `-SkipDrive`, `-SkipOneDrive`,
`-SkipPublicDrive`, `-SkipSharePoint`.

All tasks run with:

- **Principal:** current interactive user (no stored service-account creds).
- **Run level:** Limited (inherits your normal permissions).
- **Run only when user is logged on.** If the laptop is suspended or
  signed out, the task waits and runs when next available
  (`-StartWhenAvailable`), then skips any runs it missed.
- **Battery safe:** `-AllowStartIfOnBatteries` +
  `-DontStopIfGoingOnBatteries`.
- **Timeout:** 2 hours. Exceeds that and Task Scheduler terminates it.

## SharePoint token rotation

Until Path B (MSAL device-code) ships, the SharePoint task authenticates
with a pasted Graph token stored DPAPI-encrypted in
`%APPDATA%\JojoBot\config.json`. Tokens expire on the order of an hour,
so most scheduled SharePoint runs will fail with a 401.

**That is expected.** The task still logs the failure, the drive /
onedrive / publicdrive tasks keep working, and the operator rotates
when they notice:

```powershell
jojo-core config set graph_access_token "<fresh token>"
# next scheduled run (within 4h) picks it up; no restart needed
```

When Path B unblocks we'll swap this for a refresh-token flow and delete
the caveat. Tracked against ADR 0007.

## Operations

### Check task status

```powershell
# all four
Get-ScheduledTask -TaskPath '\JojoBot\*' | Format-Table TaskName, State, LastRunTime, LastTaskResult

# deeper inspection on one
Get-ScheduledTaskInfo -TaskPath '\JojoBot\' -TaskName 'JojoBot-SharePoint'
```

`LastTaskResult` reflects `jojo-ingest`'s exit code (0 = success, non-zero
= something went wrong - see log file for details).

### Tail a log

```powershell
Get-Content -Wait -Tail 50 .\logs\sharepoint\$((Get-Date).ToString('yyyy-MM-dd')).log
```

Logs rotate by day automatically (one file per connector per day). No
active cleanup - prune manually or with `Unregister-JojoBotTasks.ps1
-PurgeLogs`.

### Check the Windows event log

If you ran the registrar from elevated PowerShell, every run also
writes a one-line rollup to the Application event log under source
`JojoBot`:

```powershell
Get-EventLog -LogName Application -Source JojoBot -Newest 20 |
  Format-Table TimeGenerated, EntryType, EventId, Message -AutoSize
```

Event IDs:

- `100`  - sync completed successfully
- `1000` - sync failed (exit non-zero)
- `1001` - no Python interpreter on PATH (preflight failure)
- `1002` - `jojo_ingest` not importable

### Run a task on demand (without waiting for the trigger)

```powershell
Start-ScheduledTask -TaskPath '\JojoBot\' -TaskName 'JojoBot-Drive'
```

Use this to smoke-test after registration or after rotating the
SharePoint token.

## Troubleshooting

| Symptom                                     | Likely cause                                    | Fix |
| ------------------------------------------- | ----------------------------------------------- | --- |
| `LastTaskResult = 2`                        | `python`/`py` not on PATH, or `jojo_ingest` not installed | Open a new cmd, verify `python -c "import jojo_ingest"`. If it fails, re-run the workspace bootstrap. |
| `LastTaskResult = 3`                        | Wrapper invoked with unknown connector name     | Should not happen via the registrar. Check the task's Action tab in taskschd.msc. |
| SharePoint 401 in log                       | Graph token expired                             | `jojo-core config set graph_access_token "<new>"` |
| No event log entries appearing              | Source never registered (non-admin registrar run) | Re-run `Register-JojoBotTasks.ps1` from elevated PowerShell; tasks themselves do not need re-registering. |
| Task stays "Ready" and never fires          | Machine asleep at trigger time                  | `-StartWhenAvailable` catches next wake; or `Start-ScheduledTask` manually. |
| `JojoBot-Drive` was skipped during register | `-DriveSource` not supplied                     | Re-run with `-DriveSource "C:\Path\To\Walk"` and `-Force`. |

### "I need to stop the scheduler immediately"

```powershell
Get-ScheduledTask -TaskPath '\JojoBot\*' | Disable-ScheduledTask
```

Re-enable with `Enable-ScheduledTask`. Disabling preserves history and
lets you diagnose at leisure; use `Unregister-JojoBotTasks.ps1` only
when you want them gone for good.

## Teardown

```powershell
# remove tasks, keep logs + event source + config.json
.\Unregister-JojoBotTasks.ps1

# remove tasks AND log history
.\Unregister-JojoBotTasks.ps1 -PurgeLogs

# remove just one task (e.g. disabling SharePoint while Path B is still blocked)
.\Unregister-JojoBotTasks.ps1 -Name JojoBot-SharePoint
```

Event log source and `config.json` are intentionally left behind so a
re-registration doesn't lose rotation history or stored secrets.

## Design notes / why it looks this way

- **Run only when user is logged on** instead of a stored credential:
  keeps us inside the local-tier deploy model (ADR 0004). No secrets at
  rest outside `%APPDATA%\JojoBot\config.json` (DPAPI-encrypted per ADR
  0009).
- **`python -m jojo_ingest` rather than `jojo-ingest`**: sidesteps
  pip's Scripts-directory PATH issues inside the Task Scheduler
  environment, which does not inherit the interactive shell's PATH edits.
- **Logs tee stdout+stderr interleaved** (`2>&1 | ForEach-Object`)
  instead of `*>>` or two files: preserves the exact order Python
  emits them, which makes failure postmortems much easier.
- **Event log source creation is best-effort, not required.** Admin
  rights are a bigger ask than "please run this once"; the file log
  is the authoritative record either way.
- **ASCII-only source.** Windows PowerShell 5.1 reads `.ps1` as CP1252
  without BOM, so em-dashes / smart quotes would break parsing mid-file.
  Verified by `python3 -c '...ord(c) > 127...'` before every commit.

## Related

- ADR 0004 - Local-tier deploy model
- ADR 0007 - Delegated-token auth (Path B refresh flow target)
- ADR 0009 - Local-mode packaging + DPAPI secrets (this slice)
- `docs/ops/path-b-dummies-guide.md` - grabbing a SharePoint token manually
- `packages/jojo_core/cli.py` - `jojo-core config` subcommands
