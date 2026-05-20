# Run-LintNightly.ps1
#
# Phase 6 nightly lint run. Mirrors Run-GraphifyRebuild.ps1's pattern:
# tees stdout+stderr to a dated log file, mirrors success/failure to the
# Windows Application event log under source 'JojoBot'.
#
# The nightly task runs at 02:00 local time (same wall-clock slot as
# JojoBot-Drive -- they are independent processes with distinct work, so
# no conflict, but note it if the machine is memory-constrained).
#
# Usage:
#   Run-LintNightly.ps1 [-WikiRoot PATH] [-LogRoot PATH] [-MaxRuntimeMinutes N]
#
# Pure ASCII per ops convention (Windows PowerShell 5.1 reads .ps1 files as
# CP1252 without BOM; em-dashes and smart quotes break the parser).

param(
    [string]$WikiRoot,
    [string]$LogRoot,
    [int]$MaxRuntimeMinutes = 30
)

$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)

if (-not $LogRoot) {
    $LogRoot = Join-Path $ProjectRoot "ops\scheduler\logs"
}

if (-not $WikiRoot) {
    if ($env:JOJO_WIKI_ROOT) {
        $WikiRoot = $env:JOJO_WIKI_ROOT
    } else {
        $WikiRoot = Join-Path $ProjectRoot "..\ask_jojo_wiki"
    }
}

$LogDir = Join-Path $LogRoot "lint-nightly"
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

$LogFile = Join-Path $LogDir ("lint-nightly-" + (Get-Date -Format 'yyyy-MM-dd') + ".log")

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

# Resolve jojo-lint: prefer the venv console-script, fall back to PATH.
$LintExe = $null
$VenvLint = Join-Path $ProjectRoot ".venv\Scripts\jojo-lint.exe"
if (Test-Path $VenvLint) {
    $LintExe = $VenvLint
} else {
    if (Get-Command 'jojo-lint' -ErrorAction SilentlyContinue) {
        $LintExe = 'jojo-lint'
    }
}
if (-not $LintExe) {
    $msg = "jojo-lint not found. Checked $VenvLint and PATH. Install with: pip install -e '.[lint]'"
    Write-LogLine ("[{0}] ERROR {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $msg)
    Write-EventSafe -Message $msg -EventId 7201 -EntryType Error
    exit 1
}

Write-LogLine ("[{0}] lint-nightly starting" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'))
Write-LogLine ("  wiki    = {0}" -f $WikiRoot)
Write-LogLine ("  log     = {0}" -f $LogFile)
Write-LogLine ("  cap     = {0} minutes" -f $MaxRuntimeMinutes)
Write-LogLine ("  lintexe = {0}" -f $LintExe)

$startTime = Get-Date

try {
    $cmdArgs = @('nightly', '--wiki', $WikiRoot)
    $output = & $LintExe @cmdArgs 2>&1 | Out-String
    Write-LogLine $output

    $duration = (Get-Date) - $startTime
    $msg = ("lint-nightly completed in {0:F1} minutes" -f $duration.TotalMinutes)
    Write-LogLine ("[{0}] INFO {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $msg)
    Write-EventSafe -Message $msg -EventId 7200 -EntryType Information
    exit 0
} catch {
    $duration = (Get-Date) - $startTime
    $msg = ("lint-nightly FAILED after {0:F1} minutes: {1}" -f $duration.TotalMinutes, $_.Exception.Message)
    Write-LogLine ("[{0}] ERROR {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $msg)
    Write-EventSafe -Message $msg -EventId 7201 -EntryType Error
    exit 1
}
