# Run-GraphifyRebuild.ps1
#
# Phase 7a nightly graphify rebuild. Mirrors Run-ScheduledSync.ps1's pattern:
# tees stdout+stderr to a dated log file, mirrors success/failure to the
# Windows Application event log under source 'JojoBot'.
#
# Usage:
#   Run-GraphifyRebuild.ps1 [-Wiki PATH] [-LogRoot PATH] [-MaxRuntimeMinutes N]
#
# Pure ASCII per docs/follow-ups.md feedback memory (Windows PowerShell 5.1
# parser reads .ps1 files as CP1252 without BOM; em-dashes break parsing).

param(
    [string]$Wiki,
    [string]$LogRoot,
    [int]$MaxRuntimeMinutes = 30
)

$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)

if (-not $LogRoot) {
    $LogRoot = Join-Path $ProjectRoot "ops\scheduler\logs"
}

if (-not $Wiki) {
    if ($env:JOJO_WIKI_ROOT) {
        $Wiki = $env:JOJO_WIKI_ROOT
    } else {
        $Wiki = Join-Path $ProjectRoot "..\ask_jojo_wiki"
    }
}

$LogDir = Join-Path $LogRoot "graphify"
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

$Timestamp = Get-Date -Format 'yyyy-MM-dd_HHmm'
$LogFile = Join-Path $LogDir "$Timestamp.log"

# Always-on event-log target. Source creation requires admin; if the
# source doesn't exist yet, Write-EventLog silently fails -- that's OK.
$EventSource = 'JojoBot'

function Write-LogLine {
    param([string]$Line)
    Add-Content -Path $LogFile -Value $Line -Encoding ASCII
    Write-Host $Line
}

function Write-EventSafe {
    param([string]$Message, [int]$EventId, [string]$EntryType = 'Information')
    try {
        Write-EventLog -LogName Application -Source $EventSource `
            -EntryType $EntryType -EventId $EventId -Message $Message `
            -ErrorAction Stop
    } catch {
        # Source not registered (admin needed to create) -- non-fatal.
    }
}

Write-LogLine ("[{0}] graphify rebuild starting" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'))
Write-LogLine ("  wiki = {0}" -f $Wiki)
Write-LogLine ("  log  = {0}" -f $LogFile)
Write-LogLine ("  cap  = {0} minutes" -f $MaxRuntimeMinutes)

$startTime = Get-Date

try {
    # The jojo-graph CLI dispatches between graphify (when on PATH) and
    # the deterministic fallback (when not). Either way the call is the
    # same.
    $cmdArgs = @(
        '-m', 'jojo_graph', 'rebuild',
        '--wiki', $Wiki
    )

    $output = & python @cmdArgs 2>&1 | Out-String
    Write-LogLine $output

    $duration = (Get-Date) - $startTime
    $msg = ("graphify rebuild completed in {0:F1} minutes" -f $duration.TotalMinutes)
    Write-LogLine $msg
    Write-EventSafe -Message $msg -EventId 7100 -EntryType Information
    exit 0
} catch {
    $duration = (Get-Date) - $startTime
    $msg = ("graphify rebuild FAILED after {0:F1} minutes: {1}" -f $duration.TotalMinutes, $_.Exception.Message)
    Write-LogLine $msg
    Write-EventSafe -Message $msg -EventId 7101 -EntryType Error
    exit 1
}
