<#
.SYNOPSIS
    One-shot fix for the "jojo-core / jojo-ingest not recognized" PATH
    problem. Adds the Python Scripts directory (where pip drops the .exe
    shims) to your persistent user PATH, so every new shell resolves the
    entry points without needing a venv activation or manual PATH hacking.

.DESCRIPTION
    The problem this solves:
      When pip installs jojo_core and jojo_ingest with their console_scripts
      entry points, it drops jojo-core.exe and jojo-ingest.exe into whatever
      Scripts directory the active Python uses. On the Microsoft Store build
      of Python 3.14 that's typically
        C:\Users\<you>\AppData\Local\Python\pythoncore-3.14-64\Scripts
      Windows does NOT auto-add this to PATH, so until you do (or until you
      activate a venv), bare command names fail with CommandNotFoundException.

    This script:
      1. Resolves the correct Scripts directory by asking Python itself
         (sysconfig.get_path('scripts')). Works for system Python and venvs.
      2. Prepends it to the persistent User-scope PATH via
         [Environment]::SetEnvironmentVariable. No admin required.
      3. Also prepends it to the current session's $env:Path so the fix
         takes effect immediately, without needing to reopen the shell.
      4. Verifies jojo-core / jojo-ingest resolve.

    Idempotent: re-running is safe. If the directory is already on User PATH
    the script says so and moves on.

.PARAMETER UseVenv
    Prefer the repo's .venv Scripts directory instead of the system Python
    one. Auto-detected: if .venv\Scripts\python.exe exists, we default to it.
    Pass this flag explicitly to require the venv be present (fails loudly
    if not, rather than silently falling back to system Python).

.EXAMPLE
    # First time (system Python):
    .\Enable-JojoShell.ps1

.EXAMPLE
    # After Install-JojoBot.ps1 -UseVenv:
    .\Enable-JojoShell.ps1 -UseVenv

.NOTES
    Why user-scope PATH and not HKLM: writing to User PATH doesn't need
    admin and doesn't affect other users of the machine. The one tradeoff
    is it won't show up for scheduled tasks that run under a different
    account -- but JoJo's scheduled tasks run under your interactive
    account anyway (ADR 0004), and they invoke python.exe directly via
    full paths, not the Scripts-dir shims.
#>

[CmdletBinding()]
param(
    [switch]$UseVenv
)

$ErrorActionPreference = "Stop"

# ---- resolve repo root + candidate Pythons ------------------------------
$RepoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$VenvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"

$PythonExe = $null
if ($UseVenv) {
    if (-not (Test-Path $VenvPython)) {
        Write-Error "-UseVenv was specified but no venv found at $VenvPython. Run Install-JojoBot.ps1 -UseVenv first."
        exit 2
    }
    $PythonExe = $VenvPython
    Write-Host "Using venv Python: $PythonExe"
} elseif (Test-Path $VenvPython) {
    $PythonExe = $VenvPython
    Write-Host "Detected .venv; using venv Python: $PythonExe"
} else {
    $pyCmd = Get-Command python -ErrorAction SilentlyContinue
    if ($pyCmd) {
        $PythonExe = $pyCmd.Source
    } else {
        $pyCmd = Get-Command py -ErrorAction SilentlyContinue
        if ($pyCmd) { $PythonExe = $pyCmd.Source }
    }
    if (-not $PythonExe) {
        Write-Error "No Python interpreter found on PATH. Install Python 3.11+ or run Install-JojoBot.ps1 first."
        exit 2
    }
    Write-Host "Using system Python: $PythonExe"
}

# ---- ask Python where its Scripts dir is -------------------------------
# sysconfig.get_path('scripts') returns the right answer for both venvs
# and system installs, including Microsoft Store pythoncore builds.
$ScriptsDir = (& $PythonExe -c "import sysconfig; print(sysconfig.get_path('scripts'))") 2>&1
$ScriptsDir = ($ScriptsDir | Out-String).Trim()
if (-not $ScriptsDir -or -not (Test-Path $ScriptsDir)) {
    Write-Error "Could not resolve Python Scripts dir from $PythonExe. Got: '$ScriptsDir'"
    exit 2
}

Write-Host ""
Write-Host "Scripts directory: $ScriptsDir"
Write-Host ""

# ---- add to persistent user-scope PATH ---------------------------------
$currentUserPath = [Environment]::GetEnvironmentVariable("Path", "User")
$userPathParts = @()
if ($currentUserPath) {
    $userPathParts = @($currentUserPath -split ';' | Where-Object { $_ -ne '' })
}

# Case-insensitive containment check -- Windows paths are not case sensitive.
$alreadyThere = $false
foreach ($p in $userPathParts) {
    if ($p.TrimEnd('\') -ieq $ScriptsDir.TrimEnd('\')) {
        $alreadyThere = $true
        break
    }
}

if ($alreadyThere) {
    Write-Host "[skip] Scripts dir already in persistent user PATH." -ForegroundColor Yellow
} else {
    $newUserPath = (@($ScriptsDir) + $userPathParts) -join ';'
    [Environment]::SetEnvironmentVariable("Path", $newUserPath, "User")
    Write-Host "[ok]  Prepended to persistent user PATH. New terminals will see it." -ForegroundColor Green
}

# ---- also update the current session so the fix is immediate -----------
$sessionParts = @($env:Path -split ';' | Where-Object { $_ -ne '' })
$inSession = $false
foreach ($p in $sessionParts) {
    if ($p.TrimEnd('\') -ieq $ScriptsDir.TrimEnd('\')) {
        $inSession = $true
        break
    }
}
if (-not $inSession) {
    $env:Path = "$ScriptsDir;$env:Path"
    Write-Host "[ok]  Also prepended to current session PATH (no need to reopen the shell)." -ForegroundColor Green
} else {
    Write-Host "[skip] Already on current session PATH." -ForegroundColor Yellow
}

# ---- verify ------------------------------------------------------------
Write-Host ""
Write-Host "Verifying entry points resolve..." -ForegroundColor Cyan

$allGood = $true
foreach ($cmd in @("jojo-core", "jojo-ingest")) {
    $found = Get-Command $cmd -ErrorAction SilentlyContinue
    if ($found) {
        Write-Host ("  [ok]   {0,-12} -> {1}" -f $cmd, $found.Source) -ForegroundColor Green
    } else {
        Write-Host ("  [miss] {0,-12} not found on PATH." -f $cmd) -ForegroundColor Yellow
        $allGood = $false
    }
}

Write-Host ""
if ($allGood) {
    Write-Host "Done. Every new PowerShell window will now have jojo-core and jojo-ingest on PATH." -ForegroundColor Green
} else {
    Write-Host "PATH is configured, but one or more entry points is not installed yet." -ForegroundColor Yellow
    Write-Host "Run:  .\ops\installer\Install-JojoBot.ps1 -SkipConfig -SkipScheduler"
    Write-Host "then re-run this script to verify."
}
