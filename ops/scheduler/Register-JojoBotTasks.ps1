<#
.SYNOPSIS
    Register Windows Scheduled Tasks for every JoJo Bot connector.

.DESCRIPTION
    Creates four tasks that invoke Run-ScheduledSync.ps1 for each
    connector, with cadences matching PLAN.md section 3.5:

      JojoBot-Drive         daily at 02:00
      JojoBot-OneDrive      daily at 02:15
      JojoBot-PublicDrive   daily at 02:30
      JojoBot-SharePoint    every 4 hours, starting 03:00

    All tasks run under the current Windows user ('Run only when user is
    logged on' -- safer than storing credentials, and sufficient for the
    local-tier deploy model per ADR 0004). Tasks are created with
    "Run with highest privileges = FALSE" so they inherit the user's
    normal access to OneDrive / the P:\ drive / SharePoint tokens in
    %APPDATA%\JojoBot\config.json.

    Also (best-effort, requires admin) creates the "JojoBot" event log
    source in the Application log so Run-ScheduledSync.ps1 can write
    success/failure events. Non-admin registration still works; the
    event-log integration just stays off.

.PARAMETER DriveSource
    Folder for the drive connector to walk. Typically the user's Documents
    or a project-specific folder. Required unless -SkipDrive is set.

.PARAMETER Raw
    ask_jojo_raw root. Passed through to every task's --raw argument.
    Defaults to the project's ask_jojo_raw (resolved relative to this script).

.PARAMETER DriveTime, OneDriveTime, PublicDriveTime, SharePointStart
    24-hour wall-clock time strings (HH:mm) for each task's trigger.
    SharePointStart is the first run; subsequent runs are every 4 hours.

.PARAMETER SkipDrive, SkipOneDrive, SkipPublicDrive, SkipSharePoint
    Opt-out switches, one per connector. Useful when a connector isn't
    configured yet (e.g., waiting on IT to issue the Entra app for Path B).

.PARAMETER Force
    Overwrite existing tasks with the same name. Without this, the script
    refuses to clobber an existing JojoBot-* task so you can't silently
    rewire someone else's schedule.

.EXAMPLE
    .\Register-JojoBotTasks.ps1 -DriveSource "C:\Users\mdelosrios\Documents" -SkipSharePoint

.EXAMPLE
    .\Register-JojoBotTasks.ps1 -DriveSource "C:\Work" -Force

.NOTES
    Run from an elevated PowerShell ONLY IF you want the event log source
    created. A non-elevated run still registers the tasks; the event log
    registration just fails quietly. All four tasks can be inspected in
    taskschd.msc afterward under the "JojoBot" folder.
#>

[CmdletBinding()]
param(
    [string]$DriveSource,
    [string]$Raw,

    [string]$DriveTime        = "02:00",
    [string]$OneDriveTime     = "02:15",
    [string]$PublicDriveTime  = "02:30",
    [string]$SharePointStart  = "03:00",

    [switch]$SkipDrive,
    [switch]$SkipOneDrive,
    [switch]$SkipPublicDrive,
    [switch]$SkipSharePoint,
    [switch]$Force,

    # Phase 6 lint tasks. Opt-in: pass -IncludeLint to also register the
    # nightly (02:00 daily) and weekly (03:00 Sunday) lint tasks.
    [switch]$IncludeLint,
    [string]$LintNightlyTime = "02:00",
    [string]$LintWeeklyTime  = "03:00"
)

$ErrorActionPreference = "Stop"

# ---- paths ---------------------------------------------------------------
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$Wrapper     = Join-Path $PSScriptRoot "Run-ScheduledSync.ps1"
if (-not (Test-Path $Wrapper)) {
    Write-Host "[error] wrapper not found: $Wrapper" -ForegroundColor Red
    exit 1
}
$LintNightlyWrapper = Join-Path $PSScriptRoot "Run-LintNightly.ps1"
$LintWeeklyWrapper  = Join-Path $PSScriptRoot "Run-LintWeekly.ps1"
if (-not $Raw) {
    $Raw = Join-Path $ProjectRoot "ask_jojo_raw"
}

# ---- best-effort event log source ----------------------------------------
# Creating a source requires admin. We try, and degrade gracefully if not.
# SourceExists() itself can throw SecurityException under a locked-down GPO
# (it has to enumerate all event-log registry keys to find the source), so
# the whole thing lives inside one try/catch -- we never want the registrar
# to abort just because we couldn't check event-log state.
function Ensure-EventSource {
    try {
        if ([System.Diagnostics.EventLog]::SourceExists("JojoBot")) {
            Write-Host "[ok] event log source 'JojoBot' already exists."
            return
        }
        New-EventLog -LogName Application -Source JojoBot
        Write-Host "[ok] created event log source 'JojoBot' in Application log." -ForegroundColor Green
    } catch {
        Write-Host "[warn] could not check/create event log source (not admin, or blocked by policy)." -ForegroundColor Yellow
        Write-Host "       Tasks will still run; event-log integration stays off."
        Write-Host "       Re-run from an elevated PowerShell to enable it."
    }
}

# ---- task helpers --------------------------------------------------------
$TaskFolder = "\JojoBot"

function Register-OneTask {
    param(
        [string]$Name,
        [string]$Connector,
        [string]$Source,
        [Microsoft.Management.Infrastructure.CimInstance]$Trigger,
        [string]$Description
    )
    $full = "$TaskFolder\$Name"
    $existing = Get-ScheduledTask -TaskPath "$TaskFolder\" -TaskName $Name -ErrorAction SilentlyContinue
    if ($existing -and -not $Force) {
        Write-Host "[skip] $Name already exists. Re-run with -Force to replace." -ForegroundColor Yellow
        return
    }
    if ($existing) {
        Unregister-ScheduledTask -TaskPath "$TaskFolder\" -TaskName $Name -Confirm:$false
    }

    $argList = @(
        "-NoProfile",
        "-ExecutionPolicy", "Bypass",
        "-File", "`"$Wrapper`"",
        "-Connector", $Connector,
        "-Raw", "`"$Raw`""
    )
    if ($Source) {
        $argList += @("-Source", "`"$Source`"")
    }
    $action = New-ScheduledTaskAction `
        -Execute "powershell.exe" `
        -Argument ($argList -join " ") `
        -WorkingDirectory $ProjectRoot

    # Run only when user is logged on. Local-tier deploy model (ADR 0004)
    # means we aren't storing service-account creds on this box.
    $principal = New-ScheduledTaskPrincipal `
        -UserId "$env:USERDOMAIN\$env:USERNAME" `
        -LogonType Interactive `
        -RunLevel Limited

    $settings = New-ScheduledTaskSettingsSet `
        -AllowStartIfOnBatteries `
        -DontStopIfGoingOnBatteries `
        -StartWhenAvailable `
        -ExecutionTimeLimit (New-TimeSpan -Hours 2)

    Register-ScheduledTask `
        -TaskPath $TaskFolder `
        -TaskName $Name `
        -Description $Description `
        -Action $action `
        -Trigger $Trigger `
        -Principal $principal `
        -Settings $settings | Out-Null

    Write-Host "[ok] registered $full ($Description)" -ForegroundColor Green
}

# ---- main ----------------------------------------------------------------
Write-Host "=== JoJo Bot -- Task Scheduler registration ===" -ForegroundColor Cyan
Write-Host "Project root: $ProjectRoot"
Write-Host "Wrapper:      $Wrapper"
Write-Host "Raw root:     $Raw"
Write-Host ""

Ensure-EventSource
Write-Host ""

if (-not $SkipDrive) {
    if (-not $DriveSource) {
        Write-Host "[skip] -DriveSource not provided; skipping JojoBot-Drive." -ForegroundColor Yellow
        Write-Host "       Rerun with -DriveSource 'C:\Path\To\Walk' to register it."
    } else {
        $trig = New-ScheduledTaskTrigger -Daily -At $DriveTime
        Register-OneTask -Name "JojoBot-Drive" -Connector "drive" -Source $DriveSource `
            -Trigger $trig -Description "JoJo Bot -- local drive sync daily at $DriveTime"
    }
}

if (-not $SkipOneDrive) {
    $trig = New-ScheduledTaskTrigger -Daily -At $OneDriveTime
    Register-OneTask -Name "JojoBot-OneDrive" -Connector "onedrive" -Source "" `
        -Trigger $trig -Description "JoJo Bot -- OneDrive sync daily at $OneDriveTime"
}

if (-not $SkipPublicDrive) {
    $trig = New-ScheduledTaskTrigger -Daily -At $PublicDriveTime
    Register-OneTask -Name "JojoBot-PublicDrive" -Connector "publicdrive" -Source "" `
        -Trigger $trig -Description "JoJo Bot -- public drive (P:\) sync daily at $PublicDriveTime"
}

if (-not $SkipSharePoint) {
    # Every 4 hours starting at $SharePointStart.
    $trig = New-ScheduledTaskTrigger -Once -At $SharePointStart `
        -RepetitionInterval (New-TimeSpan -Hours 4) `
        -RepetitionDuration ([TimeSpan]::FromDays(365*10))
    Register-OneTask -Name "JojoBot-SharePoint" -Connector "sharepoint" -Source "" `
        -Trigger $trig -Description "JoJo Bot -- SharePoint sync every 4h from $SharePointStart"
}

if ($IncludeLint) {
    Write-Host ""
    Write-Host "--- Phase 6 lint tasks ---" -ForegroundColor Cyan

    if (-not (Test-Path $LintNightlyWrapper)) {
        Write-Host "[warn] lint nightly wrapper not found: $LintNightlyWrapper" -ForegroundColor Yellow
    } else {
        # Idempotent: always unregister before registering (no -Force gate).
        Unregister-ScheduledTask -TaskPath "$TaskFolder\" -TaskName "lint-nightly" `
            -Confirm:$false -ErrorAction SilentlyContinue

        $lintNightlyAction = New-ScheduledTaskAction `
            -Execute "powershell.exe" `
            -Argument ("-NoProfile -ExecutionPolicy Bypass -File `"$LintNightlyWrapper`"") `
            -WorkingDirectory $ProjectRoot

        $lintNightlyPrincipal = New-ScheduledTaskPrincipal `
            -UserId "$env:USERDOMAIN\$env:USERNAME" `
            -LogonType Interactive `
            -RunLevel Limited

        $lintNightlySettings = New-ScheduledTaskSettingsSet `
            -AllowStartIfOnBatteries `
            -DontStopIfGoingOnBatteries `
            -StartWhenAvailable `
            -ExecutionTimeLimit (New-TimeSpan -Hours 1)

        $lintNightlyTrigger = New-ScheduledTaskTrigger -Daily -At $LintNightlyTime

        Register-ScheduledTask `
            -TaskPath $TaskFolder `
            -TaskName "lint-nightly" `
            -Description "JoJo Bot -- lint nightly checks daily at $LintNightlyTime" `
            -Action $lintNightlyAction `
            -Trigger $lintNightlyTrigger `
            -Principal $lintNightlyPrincipal `
            -Settings $lintNightlySettings | Out-Null

        Write-Host "[ok] registered $TaskFolder\lint-nightly (daily at $LintNightlyTime)" -ForegroundColor Green
    }

    if (-not (Test-Path $LintWeeklyWrapper)) {
        Write-Host "[warn] lint weekly wrapper not found: $LintWeeklyWrapper" -ForegroundColor Yellow
    } else {
        # Idempotent: always unregister before registering (no -Force gate).
        Unregister-ScheduledTask -TaskPath "$TaskFolder\" -TaskName "lint-weekly" `
            -Confirm:$false -ErrorAction SilentlyContinue

        $lintWeeklyAction = New-ScheduledTaskAction `
            -Execute "powershell.exe" `
            -Argument ("-NoProfile -ExecutionPolicy Bypass -File `"$LintWeeklyWrapper`"") `
            -WorkingDirectory $ProjectRoot

        $lintWeeklyPrincipal = New-ScheduledTaskPrincipal `
            -UserId "$env:USERDOMAIN\$env:USERNAME" `
            -LogonType Interactive `
            -RunLevel Limited

        $lintWeeklySettings = New-ScheduledTaskSettingsSet `
            -AllowStartIfOnBatteries `
            -DontStopIfGoingOnBatteries `
            -StartWhenAvailable `
            -ExecutionTimeLimit (New-TimeSpan -Hours 2)

        # Sunday = DayOfWeek 0 in .NET; New-ScheduledTaskTrigger -Weekly uses
        # the -DaysOfWeek parameter with the day name string.
        $lintWeeklyTrigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At $LintWeeklyTime

        Register-ScheduledTask `
            -TaskPath $TaskFolder `
            -TaskName "lint-weekly" `
            -Description "JoJo Bot -- lint weekly checks on Sunday at $LintWeeklyTime" `
            -Action $lintWeeklyAction `
            -Trigger $lintWeeklyTrigger `
            -Principal $lintWeeklyPrincipal `
            -Settings $lintWeeklySettings | Out-Null

        Write-Host "[ok] registered $TaskFolder\lint-weekly (weekly Sunday at $LintWeeklyTime)" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "Inspect tasks:" -ForegroundColor Cyan
Write-Host "  Get-ScheduledTask -TaskPath '\JojoBot\*' | Format-Table TaskName, State, LastRunTime"
Write-Host ""
Write-Host "Tail logs (per connector):" -ForegroundColor Cyan
Write-Host "  Get-Content -Wait -Tail 0 (Join-Path '$ProjectRoot' 'ops\scheduler\logs\<connector>\<yyyy-MM-dd>.log')"
Write-Host ""
Write-Host "To remove everything later:" -ForegroundColor Cyan
Write-Host "  .\Unregister-JojoBotTasks.ps1"
