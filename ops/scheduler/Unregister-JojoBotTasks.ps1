<#
.SYNOPSIS
    Remove every Windows Scheduled Task registered by
    Register-JojoBotTasks.ps1.

.DESCRIPTION
    Deletes all tasks under the '\JojoBot\' task folder and, if empty
    afterwards, removes the folder itself. Safe to re-run; missing tasks
    are skipped quietly.

    Does NOT touch:
      * the 'JojoBot' event log source (needs admin to remove; harmless
        if left in place),
      * the on-disk log files under ops\scheduler\logs\,
      * %APPDATA%\JojoBot\config.json.

    Those are preserved so an operator can re-register later without
    losing history or secrets.

.PARAMETER Name
    Optional single task name (without the '\JojoBot\' prefix) to remove.
    If omitted, every JojoBot-* task is unregistered.

.PARAMETER PurgeLogs
    Also delete the ops\scheduler\logs directory tree. Off by default so
    postmortem data survives an accidental uninstall.

.EXAMPLE
    # remove all four JoJo Bot scheduled tasks
    .\Unregister-JojoBotTasks.ps1

.EXAMPLE
    # remove just the SharePoint task
    .\Unregister-JojoBotTasks.ps1 -Name JojoBot-SharePoint

.EXAMPLE
    # tear everything down, including log history
    .\Unregister-JojoBotTasks.ps1 -PurgeLogs
#>

[CmdletBinding()]
param(
    [string]$Name,
    [switch]$PurgeLogs
)

$ErrorActionPreference = "Stop"

$TaskFolder = "\JojoBot"
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)

Write-Host "=== JoJo Bot -- Task Scheduler cleanup ===" -ForegroundColor Cyan

# ---- enumerate tasks -----------------------------------------------------
$tasks = @()
try {
    if ($Name) {
        $tasks = @(Get-ScheduledTask -TaskPath "$TaskFolder\" -TaskName $Name -ErrorAction SilentlyContinue)
    } else {
        $tasks = @(Get-ScheduledTask -TaskPath "$TaskFolder\*" -ErrorAction SilentlyContinue)
    }
} catch {
    Write-Host "[warn] could not enumerate tasks: $($_.Exception.Message)" -ForegroundColor Yellow
}

if (-not $tasks -or $tasks.Count -eq 0) {
    Write-Host "[ok] no matching tasks found under $TaskFolder\."
} else {
    foreach ($t in $tasks) {
        try {
            Unregister-ScheduledTask -TaskPath $t.TaskPath -TaskName $t.TaskName -Confirm:$false
            Write-Host "[ok] removed $($t.TaskPath)$($t.TaskName)" -ForegroundColor Green
        } catch {
            Write-Host "[warn] failed to remove $($t.TaskName): $($_.Exception.Message)" -ForegroundColor Yellow
        }
    }
}

# ---- remove the empty \JojoBot folder if no siblings remain --------------
# Task Scheduler does not expose a direct 'remove folder' cmdlet; we fall
# back to the Schedule.Service COM object, which mirrors what taskschd.msc
# does when you right-click > Delete Folder. The folder refuses to delete
# if any task still lives inside it, so the call is safe to attempt
# unconditionally after the unregister loop above.
try {
    $svc = New-Object -ComObject Schedule.Service
    $svc.Connect()
    $root = $svc.GetFolder("\")
    $folders = @($root.GetFolders(0))
    foreach ($f in $folders) {
        if ($f.Name -eq "JojoBot") {
            $leftovers = @($f.GetTasks(0))
            if ($leftovers.Count -eq 0) {
                $root.DeleteFolder("JojoBot", 0)
                Write-Host "[ok] removed empty task folder $TaskFolder" -ForegroundColor Green
            } else {
                Write-Host "[skip] $TaskFolder still has $($leftovers.Count) task(s); leaving folder in place."
            }
        }
    }
} catch {
    Write-Host "[warn] could not tidy up task folder: $($_.Exception.Message)" -ForegroundColor Yellow
}

# ---- optional log purge --------------------------------------------------
if ($PurgeLogs) {
    $LogRoot = Join-Path $ProjectRoot "ops\scheduler\logs"
    if (Test-Path $LogRoot) {
        try {
            Remove-Item -Recurse -Force -Path $LogRoot
            Write-Host "[ok] purged $LogRoot" -ForegroundColor Green
        } catch {
            Write-Host "[warn] failed to purge logs: $($_.Exception.Message)" -ForegroundColor Yellow
        }
    } else {
        Write-Host "[ok] no log directory to purge."
    }
} else {
    Write-Host ""
    Write-Host "Log history preserved at ops\scheduler\logs\. Use -PurgeLogs to remove." -ForegroundColor DarkGray
}

Write-Host ""
Write-Host "Done. Event log source 'JojoBot' and config.json were left in place." -ForegroundColor Cyan
Write-Host "  * Remove source (admin):   Remove-EventLog -Source JojoBot"
Write-Host "  * Remove config.json:      Remove-Item `$env:APPDATA\JojoBot\config.json"
