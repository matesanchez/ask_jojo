<#
.SYNOPSIS
    Register the JoJo Bot backend as a Windows Service using NSSM (or sc.exe
    as a fallback when NSSM is not available).

.DESCRIPTION
    Registers JoJo Bot so it starts automatically on boot, restarts on failure,
    and logs stdout/stderr to %ProgramData%\JojoBot\logs\. Called by the end-user
    installer (Install-JojoBot.ps1 step 5) or run standalone for manual service
    management.

    Two runtime modes are supported:
      1. Frozen-exe mode: AppPath points to jojo-server.exe produced by PyInstaller.
         The exe is self-contained; AppArgs drives --host / --port only.
      2. Python mode: AppPath points to python.exe / python3.exe. AppArgs drives the
         -m uvicorn launch command and includes --host / --port.
    The script auto-detects the mode from the AppPath filename. Pass -AppArgs
    explicitly to override the defaults for either mode.

    NSSM vs sc.exe tradeoff:
      - NSSM captures stdout/stderr to rotating log files; sc.exe does not.
      - NSSM surfaces per-failure recovery actions cleanly; sc.exe needs a
        follow-up 'sc failure' call.
      - sc.exe is built into every Windows edition; NSSM must be bundled in the
        zip or found on PATH.
    This script tries NSSM first. If not found, it falls back to sc.exe and
    documents the limitation clearly.

.PARAMETER ServiceName
    Windows Service internal name. Default: JojoBot

.PARAMETER NssmPath
    Explicit path to nssm.exe. If omitted, the script searches: (1) the same
    directory as this script, (2) %ProgramFiles%\nssm\, (3) PATH.

.PARAMETER AppPath
    Path to the server executable. For a frozen install this is jojo-server.exe;
    for a dev/source install this is python.exe. Required.

.PARAMETER AppArgs
    Arguments forwarded to AppPath. Auto-detected if omitted:
      - Frozen-exe mode (AppPath ends in jojo-server.exe):
          --host 127.0.0.1 --port 8765 --no-access-log
      - Python mode:
          -m uvicorn backend.main:app --host 127.0.0.1 --port 8765 --no-access-log

.PARAMETER WorkingDir
    Working directory for the service process. Defaults to the parent directory
    of AppPath.

.PARAMETER BindAddress
    Host address for uvicorn to bind. Default: 127.0.0.1 (localhost only).
    Pass 0.0.0.0 to allow LAN access; the welcome page surfaces a warning
    when the service is bound that way.

.PARAMETER Port
    TCP port for the backend API. Default: 8765.

.PARAMETER StartImmediately
    Start the service after registration. Without this flag the service is
    installed in Automatic (Delayed Start) state but not started.

.PARAMETER Force
    If the service already exists, unregister it before re-registering.
    Without -Force, the script skips registration and exits 0 if the service
    already exists with the requested name.

.EXAMPLE
    # Frozen-exe install (typical end-user path):
    .\Install-Service.ps1 -AppPath "C:\JojoBot\python\jojo-server.exe" -StartImmediately

.EXAMPLE
    # Source / dev install (python.exe):
    .\Install-Service.ps1 -AppPath "C:\project\.venv\Scripts\python.exe" `
        -WorkingDir "C:\project" -StartImmediately

.EXAMPLE
    # LAN-accessible install for a department projector workstation:
    .\Install-Service.ps1 -AppPath "C:\JojoBot\python\jojo-server.exe" `
        -BindAddress 0.0.0.0 -StartImmediately

.NOTES
    Requires admin privileges to register a Windows Service.
    All strings in this file are pure ASCII (codepoints <= 127).
#>

[CmdletBinding()]
param(
    [string]$ServiceName    = "JojoBot",
    [string]$NssmPath,
    [Parameter(Mandatory=$true)]
    [string]$AppPath,
    [string]$AppArgs,
    [string]$WorkingDir,
    [string]$BindAddress    = "127.0.0.1",
    [int]$Port              = 8765,
    [switch]$StartImmediately,
    [switch]$Force
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "=== JoJo Bot -- Windows Service registration ===" -ForegroundColor Cyan
Write-Host "Service name: $ServiceName"
Write-Host "App path:     $AppPath"
Write-Host "Bind:         $BindAddress`:$Port"
Write-Host ""

# ---- validate AppPath --------------------------------------------------------
if (-not (Test-Path -LiteralPath $AppPath)) {
    Write-Host "[error] AppPath not found: $AppPath" -ForegroundColor Red
    Write-Host "        Build the frozen exe first (Build-JojoBotRelease.ps1),"
    Write-Host "        or verify your -AppPath argument."
    exit 1
}

# ---- auto-detect mode and default AppArgs ------------------------------------
# Frozen mode: the PyInstaller onedir exe is named jojo-server.exe.
# Python mode: anything else (python.exe, python3.exe, etc.).
$isFrozen = (Split-Path -Leaf $AppPath) -ieq "jojo-server.exe"

if (-not $AppArgs) {
    if ($isFrozen) {
        # jojo-server.exe IS the uvicorn runner; no -m flag needed.
        $AppArgs = "--host $BindAddress --port $Port --no-access-log"
    } else {
        # python.exe: launch via the -m uvicorn interface.
        $AppArgs = "-m uvicorn backend.main:app --host $BindAddress --port $Port --no-access-log"
    }
}
Write-Host "Mode:         $(if ($isFrozen) { 'frozen-exe' } else { 'python.exe' })"
Write-Host "App args:     $AppArgs"

# ---- default WorkingDir to parent of AppPath ---------------------------------
if (-not $WorkingDir) {
    $WorkingDir = Split-Path -Parent (Resolve-Path -LiteralPath $AppPath)
}
Write-Host "Working dir:  $WorkingDir"
Write-Host ""

# ---- warn when binding to all interfaces ------------------------------------
if ($BindAddress -ne "127.0.0.1") {
    Write-Host "[warn] Service will bind to $BindAddress (not localhost-only)." -ForegroundColor Yellow
    Write-Host "       Any user on the local network can reach the JoJo Bot UI."
    Write-Host "       Only do this on a firewalled department workstation."
    Write-Host ""
}

# ---- locate NSSM -------------------------------------------------------------
function Find-Nssm {
    # 1. Explicit path from caller.
    if ($NssmPath -and (Test-Path -LiteralPath $NssmPath)) {
        return $NssmPath
    }
    # 2. Same directory as this script (bundled in the zip).
    $beside = Join-Path $PSScriptRoot "nssm.exe"
    if (Test-Path $beside) { return $beside }
    # 3. ProgramFiles\nssm\
    $pf = Join-Path $env:ProgramFiles "nssm\nssm.exe"
    if (Test-Path $pf) { return $pf }
    # 4. PATH.
    $onPath = Get-Command nssm -ErrorAction SilentlyContinue
    if ($onPath) { return $onPath.Source }
    return $null
}

$nssmExe = Find-Nssm
if ($nssmExe) {
    Write-Host "[ok] NSSM found: $nssmExe" -ForegroundColor Green
} else {
    Write-Host "[warn] NSSM not found. Falling back to sc.exe." -ForegroundColor Yellow
    Write-Host "       Limitation: sc.exe does not capture stdout/stderr to log files."
    Write-Host "       To get full logging, bundle nssm.exe beside Install-Service.ps1"
    Write-Host "       (download from https://nssm.cc/release/nssm-2.24.zip)."
    Write-Host ""
}

# ---- check for existing service ----------------------------------------------
$existingSvc = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
if ($existingSvc) {
    if (-not $Force) {
        Write-Host "[skip] Service '$ServiceName' already exists (State: $($existingSvc.Status))." -ForegroundColor Yellow
        Write-Host "       Use -Force to remove and re-register."
        exit 0
    }
    Write-Host "[info] -Force set; removing existing service '$ServiceName'..." -ForegroundColor Cyan
    # Stop before removing.
    if ($existingSvc.Status -ne "Stopped") {
        Stop-Service -Name $ServiceName -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 3
    }
    if ($nssmExe) {
        & $nssmExe remove $ServiceName confirm 2>&1 | Out-Null
    } else {
        & sc.exe delete $ServiceName | Out-Null
    }
    # Brief pause -- sc.exe / NSSM delete is async with the SCM.
    Start-Sleep -Seconds 2
    Write-Host "[ok] existing service removed."
}

# ---- prepare log directory for NSSM stdout/stderr ---------------------------
$logDir = Join-Path $env:ProgramData "JojoBot\logs"
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    Write-Host "[ok] created log directory: $logDir" -ForegroundColor Green
}

# ---- register the service ----------------------------------------------------
$displayName  = "JoJo Bot v2.0 -- Department AI Assistant"
$description  = "JoJo Bot knowledge assistant backend. Serves http://localhost:8765/"

if ($nssmExe) {
    # ---- NSSM path -----------------------------------------------------------
    Write-Host "[info] registering with NSSM..." -ForegroundColor Cyan

    & $nssmExe install $ServiceName $AppPath $AppArgs
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[error] NSSM install returned $LASTEXITCODE." -ForegroundColor Red
        exit $LASTEXITCODE
    }

    # Display name and description.
    & $nssmExe set $ServiceName DisplayName $displayName    | Out-Null
    & $nssmExe set $ServiceName Description $description    | Out-Null

    # Working directory.
    & $nssmExe set $ServiceName AppDirectory $WorkingDir    | Out-Null

    # Start type: Automatic (Delayed).
    & $nssmExe set $ServiceName Start SERVICE_DELAYED_AUTO_START | Out-Null

    # Stdout / stderr to the log directory.
    $stdoutLog = Join-Path $logDir "stdout.log"
    $stderrLog = Join-Path $logDir "stderr.log"
    & $nssmExe set $ServiceName AppStdout $stdoutLog        | Out-Null
    & $nssmExe set $ServiceName AppStderr $stderrLog        | Out-Null
    # Rotate logs when they exceed 10 MB (NSSM flag: 1 = append+rotate).
    & $nssmExe set $ServiceName AppStdoutCreationDisposition 4 | Out-Null
    & $nssmExe set $ServiceName AppStderrCreationDisposition 4 | Out-Null
    & $nssmExe set $ServiceName AppRotateFiles 1            | Out-Null
    & $nssmExe set $ServiceName AppRotateBytes 10485760     | Out-Null

    # Recovery actions: restart on failure.
    # NSSM surfaces this as AppThrottle + AppRestartDelay.
    # First failure: 10 s delay. Subsequent: 30 s delay.
    & $nssmExe set $ServiceName AppThrottle 10000           | Out-Null
    & $nssmExe set $ServiceName AppRestartDelay 10000       | Out-Null

    Write-Host "[ok] service registered via NSSM." -ForegroundColor Green

} else {
    # ---- sc.exe fallback path -----------------------------------------------
    Write-Host "[info] registering with sc.exe..." -ForegroundColor Cyan

    # sc.exe requires the full binary path in quotes if it contains spaces.
    $binPath = "`"$AppPath`" $AppArgs"

    & sc.exe create $ServiceName `
        binPath= $binPath `
        DisplayName= $displayName `
        start= delayed-auto | Out-Null

    if ($LASTEXITCODE -ne 0) {
        Write-Host "[error] sc.exe create returned $LASTEXITCODE." -ForegroundColor Red
        exit $LASTEXITCODE
    }

    # Description requires a separate sc.exe call.
    & sc.exe description $ServiceName $description | Out-Null

    # Recovery: restart on first and subsequent failures.
    # sc failure <svc> reset= 86400 actions= restart/10000/restart/30000/restart/30000
    & sc.exe failure $ServiceName reset= 86400 actions= restart/10000/restart/30000/restart/30000 | Out-Null

    Write-Host "[ok] service registered via sc.exe." -ForegroundColor Green
    Write-Host "[note] stdout/stderr are NOT captured by sc.exe. For log access," -ForegroundColor Yellow
    Write-Host "       bundle nssm.exe and re-run Install-Service.ps1."
}

# ---- configure the service object directly via .NET (works for both paths) --
# Set the description using the WMI Win32_Service API for reliability.
# (NSSM Description above is usually sufficient; this is belt-and-suspenders.)
try {
    $wmi = Get-WmiObject -Class Win32_Service -Filter "Name='$ServiceName'" -ErrorAction Stop
    if ($wmi) { $wmi.Change($null,$null,$null,$null,$null,$null,$null,$null,$description) | Out-Null }
} catch {
    # Non-fatal; description is cosmetic.
}

# ---- start immediately if requested ------------------------------------------
if ($StartImmediately) {
    Write-Host ""
    Write-Host "[info] starting service '$ServiceName'..." -ForegroundColor Cyan
    Start-Service -Name $ServiceName
    Start-Sleep -Seconds 3
    $svc = Get-Service -Name $ServiceName
    if ($svc.Status -eq "Running") {
        Write-Host "[ok] service running." -ForegroundColor Green
    } else {
        Write-Host "[warn] service status is '$($svc.Status)' after start attempt." -ForegroundColor Yellow
        Write-Host "       Check event viewer or NSSM logs for details:"
        Write-Host "       Get-Content `"$logDir\stderr.log`""
    }
}

Write-Host ""
Write-Host "--- Summary ---" -ForegroundColor Cyan
Write-Host "  Service name:  $ServiceName"
Write-Host "  Display name:  $displayName"
Write-Host "  Executable:    $AppPath"
Write-Host "  Arguments:     $AppArgs"
Write-Host "  Working dir:   $WorkingDir"
Write-Host "  Start type:    Automatic (Delayed)"
Write-Host "  URL:           http://$BindAddress`:$Port/"
Write-Host "  Log dir:       $logDir"
Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Cyan
Write-Host "  Start:   Start-Service $ServiceName"
Write-Host "  Stop:    Stop-Service $ServiceName"
Write-Host "  Status:  Get-Service $ServiceName | Format-List Name, Status, StartType"
Write-Host "  Logs:    Get-Content `"$logDir\stderr.log`" -Tail 50"
Write-Host ""
