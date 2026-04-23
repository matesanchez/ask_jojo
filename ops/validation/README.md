# Phase 1 Validation Runs

Scripts + reports for end-to-end validation against real Nurix data. These are
*not* scheduled jobs — they're deliberate, noisy, one-shot runs that produce a
timestamped Markdown report you can paste into `docs/v2_status.md`.

## The exit-criterion run

`Run-ValidationSyncAll.ps1` drives `jojo-ingest sync-all` across all four
walking connectors (drive + sharepoint + onedrive + publicdrive) and writes a
report to `ops/validation/reports/sync-all_<timestamp>.md`.

### First-time use (Path A — paste a token)

```powershell
cd C:\Users\mdelosrios\Claude_Local\jojo_bot_v2.0\ask_jojo\ops\validation
.\Run-ValidationSyncAll.ps1
# When prompted, paste a fresh Graph Explorer bearer token (Access token tab).
```

The script will:

1. Preflight each connector (checks the OneDrive + public-drive paths exist).
2. Run each connector in sequence, printing the CLI output live.
3. Pipe the full output into a `.log` file alongside the report.
4. At the end, call `jojo-ingest status` and test the exit criterion
   (≥100 files, ≥2 connectors) against the manifest totals.

Expected runtime on a cold raw repo: ~5–15 minutes for a typical Protein
Sciences corpus (dominated by SharePoint PDFs and OneDrive docx). Re-runs
are near-zero-work thanks to manifest-based idempotency.

### Flags worth knowing

| Flag | Why you'd use it |
| --- | --- |
| `-DryRun` | Print what would be run without executing. Use to sanity-check paths and site URLs first. |
| `-SkipConnector "publicdrive"` | Skip a connector — e.g. if P:\ isn't mounted on the box you're running from, or OneDrive isn't signed in. |
| `-DrivePath "D:\SomeSnapshot"` | Include the *local* drive connector too (it's disabled by default because there's no canonical "drive" folder). |
| `-GraphToken "eyJ..."` | Pass the token on the command line instead of the prompt. Don't do this in shell history you care about keeping clean. |
| `-RawRoot "D:\alt\raw"` | Point at a different raw repo (e.g. a throwaway one for a dry test). |
| `-SharePointSites "https://...,https://..."` | Override the six-site default. |

### Re-running — what should happen

After a successful first run:

- `jojo-ingest status --raw ...\ask_jojo_raw` should report `total_entries ≥100`
  and multiple entries under `by_source`.
- A second invocation of the script should finish far faster and report
  `added: 0` / `updated: 0` / mostly `skipped` across every connector —
  that's the idempotency invariant at work.
- Editing a handful of source files should produce exactly that number of
  `updated` entries on the next run.

## Path B — after MSAL device-code is set up

Once `docs/ops/path-b-msal-device-code-setup.md` has been followed, the
validation run no longer needs a pasted token:

```powershell
$env:JOJO_MSAL_CLIENT_ID = "<client-id>"
$env:JOJO_MSAL_TENANT_ID = "1c966021-d551-45e4-89a5-849f81b69208"
# GraphToken left empty — the script passes the -GraphToken "" prompt path,
# but the SharePoint connector will pick up Path B from the env vars instead.
.\Run-ValidationSyncAll.ps1 -GraphToken "(path-b)"
```

(We keep the prompt flow for Path A specifically because it's the "you have to
think about this every ~60 minutes" case — Path B should just work silently
from the token cache.)

## Reading a report

Every report has four sections:

1. **Configuration** — what we pointed at. Sanity-check this first; wrong URLs
   or paths produce the most common false-negative failures.
2. **Connector results** — one section per connector, with duration, exit code,
   and the JSON summary `jojo-ingest` prints at the end.
3. **Final manifest state** — output of `jojo-ingest status`, including
   `total_entries` and `by_source` breakdown.
4. **Exit-criterion check** — pass/fail table keyed to the Phase 1 exit
   criterion. This is the table to copy into `docs/v2_status.md` Phase 1
   amendment log if the run passes.

## Reports directory

`reports/` is in the raw repo's `.gitignore`-style exclusion list (i.e.
don't commit it). Reports can contain Protein Sciences file names, which
we treat as privileged per ADR 0006. If you need to share a report
externally, paste the redacted summary into a fresh file first.

## Troubleshooting

### "SharePoint connector cannot start: JOJO_GRAPH_ACCESS_TOKEN is not set"

Either the token prompt was skipped with an empty Enter, or the token is
empty string. Re-run without skipping, or pass `-GraphToken "eyJ..."`.

### "OneDrive path 'C:\Users\…\OneDrive - Nurix Therapeutics' does not exist"

OneDrive desktop client isn't signed in on this machine, or the tenant
name in the folder is different. `dir $env:USERPROFILE` and look for the
`OneDrive - ...` folder; pass its actual name via `-OneDrivePath`.

### "Public drive path 'P:\' does not exist"

The SMB mount to the Nurix public drive isn't connected. `net use P: \\...`
to remount, or pass `-SkipConnector publicdrive` to run without it.

### SharePoint ingest runs but `added: 0` across all sites

- Confirm the site URLs in `-SharePointSites` actually exist and you have
  read access — visit each in a browser first.
- The token may lack `Sites.Read.All`. Decode the JWT at https://jwt.ms
  and confirm the `scp` claim.
- If the sites exist but are genuinely empty (brand new), this is expected
  and not a bug — but the exit criterion needs ≥100 files, so cast a wider
  net before the formal run.

### Long runs (hours) on SharePoint

Graph throttling. Our client honors `Retry-After`, so long durations are
usually real rate-limit pushback, not a bug. Run during low-traffic hours
(early morning Pacific) or narrow `-SharePointSites` to a subset per run.
