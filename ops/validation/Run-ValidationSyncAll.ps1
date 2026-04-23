<#
.SYNOPSIS
    End-to-end Phase 1 exit-criterion validation run against real Nurix data.

.DESCRIPTION
    Runs `jojo-ingest sync-all` across all four walking connectors
    (drive + sharepoint + onedrive + publicdrive) and captures file counts,
    per-source breakdown, duration, and failures into a timestamped report.

    This is the thing the Phase 1 exit criterion asks for:
      ">=100 files from >=2 Protein Sciences connectors into ask_jojo_raw/
       in under an hour with correct access_level metadata"

.PARAMETER RawRoot
    Where the ingest writes to. Default: the project's ask_jojo_raw/ clone.

.PARAMETER GraphToken
    Fresh bearer token from Graph Explorer (Access token tab). Paste at
    prompt or pass via -GraphToken. ~60 min lifetime, so run this script
    within an hour of copying the token.

.PARAMETER SharePointSites
    Comma-separated site URLs. Defaults to the six sites in the Phase 1b
    plan (Protein Sciences, NurixNet, DEL Triage, Screen Team, CRUK Grant,
    Biortus).

.PARAMETER OneDrivePath
    Local OneDrive sync root. Defaults to the standard Nurix mount.

.PARAMETER PublicDrivePath
    Public SMB drive root. Defaults to P:\.

.PARAMETER DrivePath
    Optional extra local folder to include (e.g. a Protein Sciences
    snapshot folder on disk). Leave empty to skip the drive connector.

.PARAMETER SkipConnector
    Comma-separated names of connectors to skip. Useful if e.g. P:\ isn't
    mounted on the workstation you're running from.

.EXAMPLE
    .\Run-ValidationSyncAll.ps1 -GraphToken "eyJ0eXAi..."

.EXAMPLE
    # Dry preview -- shows which connectors would run, doesn't hit the network
    .\Run-ValidationSyncAll.ps1 -DryRun

.NOTES
    This script is deliberately noisy. It's a validation run, not a silent
    scheduled task -- you want to see every step so surprises don't hide.
#>

[CmdletBinding()]
param(
    [string]$RawRoot = "C:\Users\mdelosrios\Claude_Local\jojo_bot_v2.0\ask_jojo_raw",

    [string]$GraphToken = "",

    [string]$SharePointSites = "https://nurix.sharepoint.com/sites/ProteinScience,https://nurix.sharepoint.com/sites/NurixNet,https://nurix.sharepoint.com/sites/DELTriage,https://nurix.sharepoint.com/sites/ScreenTeam,https://nurix.sharepoint.com/sites/CRUKGrant,https://nurix.sharepoint.com/sites/Biortus",

    [string]$OneDrivePath = "$env:USERPROFILE\OneDrive - Nurix Therapeutics, Inc",

    [string]$PublicDrivePath = "P:\",

    [string]$DrivePath = "",

    [string]$SkipConnector = "",

    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

# Resolve the project root from this script's location.
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)

# Resolve the Python interpreter. Order:
#   1. <repo>\.venv\Scripts\python.exe  -- pinned to this repo's install
#   2. `python` on PATH
#   3. `py` (the Windows Python launcher) on PATH
# The venv takes precedence so we never accidentally run against a system
# python that happens to be on PATH but doesn't have the [ingest,backend,
# cloud] extras installed (that's how we hit the httpx ModuleNotFoundError
# on 2026-04-22).
$PythonExe = $null
$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (Test-Path $VenvPython) {
    $PythonExe = $VenvPython
    Write-Host "[preflight] using project venv: $VenvPython"
} else {
    foreach ($candidate in @("python", "py")) {
        if (Get-Command $candidate -ErrorAction SilentlyContinue) {
            $PythonExe = $candidate
            break
        }
    }
}
if (-not $PythonExe) {
    Write-Host "[preflight] Neither a project venv nor 'python'/'py' on PATH was found." -ForegroundColor Red
    Write-Host "Install Python 3.11+ from python.org or the Microsoft Store, or run"
    Write-Host "ops\installer\Install-JojoBot.ps1 -UseVenv from the project root, and try again."
    exit 1
}

# Preflight: the jojo_ingest package AND every connector module must import
# cleanly. A bare ``import jojo_ingest`` only exercises __init__.py, which is
# trivial -- it misses third-party deps like ``httpx`` (pulled in by
# jojo_ingest.graph -> jojo_ingest.sharepoint). We instead import every
# connector module directly so a missing extra fails here, not 15 minutes
# into the run when the first ``sync`` call crashes at import time.
#
# We capture stderr and print it on failure so the operator sees the actual
# ModuleNotFoundError instead of a generic "preflight failed". Note the
# EAP="Continue" wrapper: PS 5.1 under EAP=Stop treats each stderr line from
# a 2>&1 merge as a terminating error, swallowing everything after line 1
# (see long comment near the per-connector run call below for full context).
$preflightProbe = @"
import jojo_core, jojo_core.config
import jojo_ingest
import jojo_ingest.drive
import jojo_ingest.onedrive
import jojo_ingest.publicdrive
import jojo_ingest.graph
import jojo_ingest.sharepoint
import jojo_ingest.upload
"@
$prevEAP = $ErrorActionPreference
$ErrorActionPreference = "Continue"
try {
    $preflightOut = & $PythonExe -c $preflightProbe 2>&1 | Out-String
    $preflightExit = $LASTEXITCODE
} finally {
    $ErrorActionPreference = $prevEAP
}
if ($preflightExit -ne 0) {
    Write-Host ""
    Write-Host "[preflight] Connector modules cannot import under '$PythonExe'." -ForegroundColor Red
    Write-Host ""
    Write-Host "Python reported:" -ForegroundColor Yellow
    Write-Host $preflightOut.Trim()
    Write-Host ""
    Write-Host "Most likely cause: the [ingest], [backend], or [cloud] extras haven't been" -ForegroundColor Yellow
    Write-Host "installed in this Python. httpx in particular is pulled in by the [cloud]" -ForegroundColor Yellow
    Write-Host "extra and is imported at module load time by jojo_ingest.graph." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Fix: from the project root, install the package in editable mode:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "    cd $ProjectRoot" -ForegroundColor Cyan
    Write-Host "    $PythonExe -m pip install -e `".[ingest,backend,cloud,dev]`"" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "If the install succeeded but preflight still fails, you may be running a" -ForegroundColor Yellow
    Write-Host "different Python than the one pip installed into. Check which Python pip" -ForegroundColor Yellow
    Write-Host "is bound to:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "    $PythonExe -m pip --version" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "If you use a venv, activate it before running this script:" -ForegroundColor Yellow
    Write-Host "    .\.venv\Scripts\Activate.ps1" -ForegroundColor Cyan
    Write-Host ""
    exit 1
}
$ReportDir = Join-Path $ProjectRoot "ops\validation\reports"
New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null
$ReportPath = Join-Path $ReportDir "sync-all_$timestamp.md"
$LogPath = Join-Path $ReportDir "sync-all_$timestamp.log"

$skip = @($SkipConnector -split "," | ForEach-Object { $_.Trim().ToLower() } | Where-Object { $_ })

function Write-Section($title) {
    Write-Host ""
    Write-Host ("=" * 70) -ForegroundColor Cyan
    Write-Host " $title" -ForegroundColor Cyan
    Write-Host ("=" * 70) -ForegroundColor Cyan
}

function Append-Report([string]$line) {
    Add-Content -Path $ReportPath -Value $line -Encoding UTF8
}

function Run-Connector([string]$Name, [scriptblock]$Preflight, [string[]]$CliArgs) {
    if ($skip -contains $Name.ToLower()) {
        Write-Host "[skip] $Name (per -SkipConnector)" -ForegroundColor Yellow
        Append-Report "### $Name -- skipped"
        Append-Report ""
        Append-Report "Skipped via ``-SkipConnector``. Re-run without the skip to include."
        Append-Report ""
        return
    }

    Write-Section "Connector: $Name"
    $preflightMsg = & $Preflight
    if ($preflightMsg) {
        Write-Host "[preflight] $preflightMsg" -ForegroundColor Yellow
        Append-Report "### $Name -- preflight failed"
        Append-Report ""
        Append-Report "$preflightMsg"
        Append-Report ""
        return
    }

    if ($DryRun) {
        Write-Host "[dry-run] would execute: $PythonExe -m jojo_ingest $($CliArgs -join ' ')" -ForegroundColor Yellow
        Append-Report "### $Name -- dry-run"
        Append-Report ""
        Append-Report "Would run: ``$PythonExe -m jojo_ingest $($CliArgs -join ' ')``"
        Append-Report ""
        return
    }

    $start = Get-Date
    Write-Host "[run] $PythonExe -m jojo_ingest $($CliArgs -join ' ')"
    # PS 5.1 under $ErrorActionPreference = "Stop" treats each native-command
    # stderr line (merged by 2>&1) as a terminating ErrorRecord, which hides the
    # real Python traceback behind a single "NativeCommandError" -- we only ever
    # see the first line. Relax the preference *locally* so stderr flows through
    # the pipeline as plain text and the full traceback lands in the log.
    $prevEAP = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        # Write the log via Add-Content -Encoding UTF8 instead of Tee-Object,
        # which in PS 5.1 defaults to UTF-16 LE and produces logs that look
        # spaced-out ("p y t h o n") and don't grep cleanly. Same pattern as
        # Run-ScheduledSync.ps1. Collect lines into $stdout for the JSON-blob
        # scraper below.
        $collected = New-Object System.Collections.Generic.List[string]
        & $PythonExe -m jojo_ingest @CliArgs 2>&1 | ForEach-Object {
            $line = $_.ToString()
            Add-Content -Path $LogPath -Value $line -Encoding UTF8
            Write-Host $line
            $collected.Add($line)
        }
        $exit = $LASTEXITCODE
        $stdout = $collected.ToArray()
    } finally {
        $ErrorActionPreference = $prevEAP
    }
    $end = Get-Date
    $duration = [int]($end - $start).TotalSeconds

    Append-Report "### $Name"
    Append-Report ""
    Append-Report "- Duration: ${duration}s"
    Append-Report "- Exit code: $exit"
    Append-Report "- Command: ``$PythonExe -m jojo_ingest $($CliArgs -join ' ')``"
    Append-Report ""
    Append-Report '```json'
    # jojo-ingest prints a JSON blob at the end; find and pull the last JSON object.
    $joined = $stdout -join "`n"
    $lastBrace = $joined.LastIndexOf('{')
    $lastClose = $joined.LastIndexOf('}')
    if ($lastBrace -ge 0 -and $lastClose -gt $lastBrace) {
        Append-Report $joined.Substring($lastBrace, $lastClose - $lastBrace + 1)
    } else {
        Append-Report "(no JSON block found in output -- see the .log file)"
    }
    Append-Report '```'
    Append-Report ""

    if ($exit -ne 0) {
        Write-Host "[fail] $Name exited $exit -- see $LogPath" -ForegroundColor Red
    } else {
        Write-Host "[ok]   $Name finished in ${duration}s" -ForegroundColor Green
    }
}

# ------------------------------------------------------------------ token prompt
if (-not $GraphToken -and -not ($skip -contains "sharepoint")) {
    Write-Host "Paste a fresh Graph Explorer bearer token (copy from Access token tab)." -ForegroundColor Yellow
    Write-Host "Or press Enter to skip SharePoint for this run." -ForegroundColor Yellow
    $GraphToken = Read-Host "Token"
}

# ------------------------------------------------------------------ env setup
$env:JOJO_RAW_ROOT = $RawRoot
if ($GraphToken) {
    $env:JOJO_GRAPH_ACCESS_TOKEN = $GraphToken
    $env:JOJO_SHAREPOINT_SITES = $SharePointSites
}
$env:JOJO_ONEDRIVE_PATH = $OneDrivePath
$env:JOJO_PUBLIC_DRIVE_PATH = $PublicDrivePath

# ------------------------------------------------------------------ report header
@"
# Phase 1 Exit-Criterion Validation -- sync-all

**Run:** $timestamp
**Raw root:** $RawRoot
**Machine:** $env:COMPUTERNAME ($env:USERNAME)
**Started:** $(Get-Date -Format o)

## Configuration

| Connector | Target | Status |
| --- | --- | --- |
| drive | $(if ($DrivePath) { $DrivePath } else { '_(not configured -- optional)_' }) | $(if ($skip -contains 'drive' -or -not $DrivePath) { 'skipped' } else { 'will run' }) |
| sharepoint | $SharePointSites | $(if ($skip -contains 'sharepoint' -or -not $GraphToken) { 'skipped' } else { 'will run' }) |
| onedrive | $OneDrivePath | $(if ($skip -contains 'onedrive') { 'skipped' } else { 'will run' }) |
| publicdrive | $PublicDrivePath | $(if ($skip -contains 'publicdrive') { 'skipped' } else { 'will run' }) |

---

## Connector results

"@ | Set-Content -Path $ReportPath -Encoding UTF8

# ------------------------------------------------------------------ connectors
Run-Connector -Name "drive" -CliArgs @("sync", "drive", "--raw", $RawRoot, "--source", $DrivePath) -Preflight {
    if (-not $DrivePath) { return "No -DrivePath passed. Drive connector is optional; pass -DrivePath <folder> to include." }
    if (-not (Test-Path $DrivePath)) { return "-DrivePath '$DrivePath' does not exist." }
    return $null
}

Run-Connector -Name "sharepoint" -CliArgs @("sync", "sharepoint", "--raw", $RawRoot) -Preflight {
    if (-not $GraphToken) { return "No Graph token provided; skipping SharePoint." }
    return $null
}

Run-Connector -Name "onedrive" -CliArgs @("sync", "onedrive", "--raw", $RawRoot) -Preflight {
    if (-not (Test-Path $OneDrivePath)) { return "OneDrive path '$OneDrivePath' does not exist. Is OneDrive signed in?" }
    return $null
}

Run-Connector -Name "publicdrive" -CliArgs @("sync", "publicdrive", "--raw", $RawRoot) -Preflight {
    if (-not (Test-Path $PublicDrivePath)) { return "Public drive path '$PublicDrivePath' does not exist. Is the SMB mount connected?" }
    return $null
}

# ------------------------------------------------------------------ final status
Write-Section "Manifest summary"
if (-not $DryRun) {
    # Same stderr-as-ErrorRecord trap as the per-connector runs above; if
    # `status` traces back, we want the full message in $status, not a PS
    # NativeCommandError that hides line 2+ of the traceback.
    $prevEAP = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        $status = & $PythonExe -m jojo_ingest status --raw $RawRoot 2>&1 | Out-String
    } finally {
        $ErrorActionPreference = $prevEAP
    }
    Write-Host $status
    Append-Report "## Final manifest state"
    Append-Report ""
    Append-Report '```json'
    Append-Report $status.Trim()
    Append-Report '```'
    Append-Report ""

    # Parse the JSON to check exit-criterion conditions.
    try {
        $parsed = $status | ConvertFrom-Json
        $total = [int]$parsed.total_entries
        $sourceCount = ($parsed.by_source.PSObject.Properties | Measure-Object).Count

        Append-Report "## Exit-criterion check"
        Append-Report ""
        Append-Report "| Criterion | Target | Actual | Pass |"
        Append-Report "| --- | --- | --- | --- |"
        Append-Report "| Total files ingested | >=100 | $total | $(if ($total -ge 100) {'YES'} else {'NO'}) |"
        Append-Report "| Connectors represented | >=2 | $sourceCount | $(if ($sourceCount -ge 2) {'YES'} else {'NO'}) |"
        Append-Report ""
        Append-Report "Run duration depended on file volume; see per-connector durations above."
        Append-Report ""

        Write-Host ""
        Write-Host "Exit-criterion check:" -ForegroundColor Cyan
        Write-Host "  total_entries = $total  (target >=100)  $(if ($total -ge 100) {'PASS'} else {'FAIL'})" -ForegroundColor $(if ($total -ge 100) {'Green'} else {'Red'})
        Write-Host "  by_source.Count = $sourceCount  (target >=2)  $(if ($sourceCount -ge 2) {'PASS'} else {'FAIL'})" -ForegroundColor $(if ($sourceCount -ge 2) {'Green'} else {'Red'})
    } catch {
        Write-Host "(couldn't parse jojo-ingest status JSON -- exit-criterion check skipped)" -ForegroundColor Yellow
    }
}

Append-Report ""
Append-Report "---"
Append-Report ""
Append-Report "_Generated $(Get-Date -Format o) by Run-ValidationSyncAll.ps1_"

Write-Section "Done"
Write-Host "Report: $ReportPath"
Write-Host "Log:    $LogPath"
Write-Host ""
Write-Host "Next: open the report, scan for failures, and paste the exit-criterion table into v2_status.md." -ForegroundColor Cyan
