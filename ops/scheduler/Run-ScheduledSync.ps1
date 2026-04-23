<#
.SYNOPSIS
    Wrapper script invoked by Windows Task Scheduler for each JoJo Bot
    connector. Runs `python -m jojo_ingest sync <connector>` with logging
    to disk plus a Windows event-log entry on failure.

.DESCRIPTION
    Scheduled tasks don't inherit an interactive shell's environment, so
    this script:
      1. Resolves python/py on PATH (fails loudly if neither is present).
      2. Confirms the jojo_ingest package is importable.
      3. Runs the sync and tees stdout + stderr to a dated log file under
         ops\scheduler\logs\<connector>\<yyyy-MM-dd>.log.
      4. Reports a rollup line to the Windows Application event log under
         source "JojoBot" -- informational on success, error on non-zero
         exit. If the event source doesn't exist, it's skipped silently
         (creation requires admin and happens at registration time).
      5. Exits with the underlying jojo-ingest exit code so Task
         Scheduler's "Last Run Result" column reflects reality.

    The script reads no secrets itself. All credentials come from
    %APPDATA%\JojoBot\config.json (DPAPI-encrypted) via jojo_core.config.
    See ADR 0009 and docs/ops/scheduler-setup.md.

.PARAMETER Connector
    One of: drive, onedrive, publicdrive, sharepoint. Maps to the
    corresponding `jojo-ingest sync <name>` invocation.

.PARAMETER Raw
    ask_jojo_raw root. If omitted, reads JOJO_RAW_ROOT from config/env,
    else defaults to .\ask_jojo_raw relative to the project.

.PARAMETER Source
    Path to walk (drive/onedrive/publicdrive). Optional -- the per-connector
    factory reads config.json / env if omitted. Ignored for sharepoint.

.PARAMETER Since
    ISO-8601 datetime. Passed through as --since to enable incremental
    sync. Typical scheduled use leaves this empty and lets the connector's
    own incremental-state file drive the window.

.PARAMETER LogRoot
    Directory for dated log files. Defaults to ops\scheduler\logs\
    relative to the project root.

.EXAMPLE
    # Invoked by Task Scheduler:
    powershell -ExecutionPolicy Bypass -File Run-ScheduledSync.ps1 -Connector drive -Source "C:\Users\mdelosrios\Documents"

.NOTES
    Exit codes:
      0    success
      2    preflight failure (no python / package not importable)
      *    whatever jojo-ingest returned

    Unknown connector names are rejected by the -Connector parameter's
    ValidateSet before the script body runs; no dedicated exit code.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("drive", "onedrive", "publicdrive", "sharepoint")]
    [string]$Connector,

    [string]$Raw,
    [string]$Source,
    [string]$Since,
    [string]$LogRoot
)

$ErrorActionPreference = "Stop"

# ---- resolve project root + log dir --------------------------------------
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
if (-not $LogRoot) {
    $LogRoot = Join-Path $ProjectRoot "ops\scheduler\logs"
}
$LogDir = Join-Path $LogRoot $Connector
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}
$LogFile = Join-Path $LogDir ((Get-Date -Format "yyyy-MM-dd") + ".log")

function Write-Log([string]$Level, [string]$Message) {
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "[$ts] [$Level] [$Connector] $Message"
    Add-Content -Path $LogFile -Value $line -Encoding UTF8
    Write-Host $line
}

function Write-EventLogSafe([string]$EntryType, [int]$EventId, [string]$Message) {
    # Source must exist first; creating it requires admin and is done at
    # registration time. If it doesn't exist yet, skip quietly -- the log
    # file is the authoritative record.
    if (-not [System.Diagnostics.EventLog]::SourceExists("JojoBot")) { return }
    try {
        Write-EventLog -LogName Application -Source JojoBot `
            -EntryType $EntryType -EventId $EventId -Message $Message
    } catch {
        Write-Log "WARN" "Could not write event log: $($_.Exception.Message)"
    }
}

# ---- preflight: python + jojo_ingest importable --------------------------
# Resolution order:
#   1. <repo>\.venv\Scripts\python.exe (pinned per-repo)
#   2. `python` on PATH
#   3. `py` (Windows Python launcher)
# Scheduled tasks run with a stripped environment -- no interactive PATH, no
# venv auto-activation -- so we resolve the venv path explicitly against
# $ProjectRoot rather than relying on PATH inheriting anything. This is what
# makes `Install-JojoBot.ps1 -UseVenv` "just work" for the overnight tasks.
$PythonExe = $null
$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (Test-Path $VenvPython) {
    $PythonExe = $VenvPython
} else {
    foreach ($candidate in @("python", "py")) {
        if (Get-Command $candidate -ErrorAction SilentlyContinue) {
            $PythonExe = $candidate
            break
        }
    }
}
if (-not $PythonExe) {
    Write-Log "ERROR" "No Python interpreter found. Checked $VenvPython, then 'python' and 'py' on PATH."
    Write-EventLogSafe -EntryType Error -EventId 1001 `
        -Message "JojoBot $Connector sync failed: no Python interpreter available to the scheduled task."
    exit 2
}
Write-Log "INFO" "using python: $PythonExe"

# Tight preflight: import every connector module, not just the top-level
# package. jojo_ingest/__init__.py is trivial, so a bare `import jojo_ingest`
# misses third-party deps like httpx (pulled in by jojo_ingest.graph and then
# by sharepoint.py). We want the preflight to fail here with a readable
# message rather than letting the actual sync crash at import time.
$preflightProbe = "import jojo_core, jojo_core.config, jojo_ingest, jojo_ingest.drive, jojo_ingest.onedrive, jojo_ingest.publicdrive, jojo_ingest.graph, jojo_ingest.sharepoint, jojo_ingest.upload"
$prevEAP = $ErrorActionPreference
$ErrorActionPreference = "Continue"
try {
    $preflightOut = & $PythonExe -c $preflightProbe 2>&1 | Out-String
    $preflightExit = $LASTEXITCODE
} finally {
    $ErrorActionPreference = $prevEAP
}
if ($preflightExit -ne 0) {
    $msg = "connector modules not importable by '$PythonExe'. $($preflightOut.Trim())"
    Write-Log "ERROR" $msg
    Write-Log "ERROR" "Fix: pip install -e `".[ingest,backend,cloud]`" from the project root."
    Write-EventLogSafe -EntryType Error -EventId 1002 `
        -Message "JojoBot $Connector sync failed: $msg"
    exit 2
}

# ---- build + run the sync invocation -------------------------------------
$syncArgs = @("-m", "jojo_ingest", "sync", $Connector)
if ($Raw)    { $syncArgs += @("--raw", $Raw) }
if ($Source) { $syncArgs += @("--source", $Source) }
if ($Since)  { $syncArgs += @("--since", $Since) }

Write-Log "INFO" "starting: $PythonExe $($syncArgs -join ' ')"
$start = Get-Date

# Tee both stdout and stderr into the same log file. 2>&1 merges the streams
# *as the child emits them*, preserving the interleaving, which makes
# failure postmortems much easier than reading two separate files.
#
# PowerShell 5.1 gotcha: under $ErrorActionPreference = "Stop" (set at the top
# of this script), every stderr line from a native command merged via 2>&1
# becomes an ErrorRecord, and the pipeline terminates on the first one. That
# turns a Python traceback into a single useless "NativeCommandError" with
# only line 1 ("Traceback (most recent call last):") captured. Relax the
# preference locally so the full traceback actually makes it into the log.
$prevEAP = $ErrorActionPreference
$ErrorActionPreference = "Continue"
try {
    & $PythonExe @syncArgs 2>&1 | ForEach-Object {
        $line = $_.ToString()
        Add-Content -Path $LogFile -Value $line -Encoding UTF8
        Write-Host $line
    }
    $exit = $LASTEXITCODE
} finally {
    $ErrorActionPreference = $prevEAP
}
$duration = [int]((Get-Date) - $start).TotalSeconds

if ($exit -eq 0) {
    Write-Log "INFO" "completed in ${duration}s"
    Write-EventLogSafe -EntryType Information -EventId 100 `
        -Message "JojoBot $Connector sync completed in ${duration}s. Log: $LogFile"
} else {
    Write-Log "ERROR" "failed with exit $exit after ${duration}s"
    Write-EventLogSafe -EntryType Error -EventId 1000 `
        -Message "JojoBot $Connector sync FAILED (exit $exit) after ${duration}s. Log: $LogFile"
}

exit $exit
