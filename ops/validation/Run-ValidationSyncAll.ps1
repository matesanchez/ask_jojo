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

# Resolve the Python interpreter. We prefer `python`; fall back to `py` on
# systems where only the Windows Python launcher is on PATH.
$PythonExe = $null
foreach ($candidate in @("python", "py")) {
    if (Get-Command $candidate -ErrorAction SilentlyContinue) {
        $PythonExe = $candidate
        break
    }
}
if (-not $PythonExe) {
    Write-Host "[preflight] Neither 'python' nor 'py' is on PATH." -ForegroundColor Red
    Write-Host "Install Python 3.11+ from python.org or the Microsoft Store and re-run."
    exit 1
}

# Preflight: the jojo_ingest package must be importable. We invoke the CLI via
# `python -m jojo_ingest` rather than the `jojo-ingest` console entry point
# because the entry-point shim lives in Python's Scripts directory, which is
# often missing from Windows PATH when not inside a venv. `python -m` only
# needs `python` itself on PATH and the package importable -- more robust.
& $PythonExe -c "import jojo_ingest" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[preflight] Can't import jojo_ingest with '$PythonExe'." -ForegroundColor Red
    Write-Host ""
    Write-Host "Fix: from the project root, install the package in editable mode:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "    cd $ProjectRoot" -ForegroundColor Cyan
    Write-Host "    $PythonExe -m pip install -e `".[ingest,backend,cloud,dev]`"" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "If you use a venv, activate it first:" -ForegroundColor Yellow
    Write-Host "    .\.venv\Scripts\Activate.ps1" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Then re-run this script."
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
    $stdout = & $PythonExe -m jojo_ingest @CliArgs 2>&1 | Tee-Object -FilePath $LogPath -Append
    $exit = $LASTEXITCODE
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
    $status = & $PythonExe -m jojo_ingest status --raw $RawRoot 2>&1 | Out-String
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
