<#
.SYNOPSIS
    Uninstall JoJo Bot from a Windows workstation.

.DESCRIPTION
    Removes the Windows Service, all JoJo Bot scheduled tasks, and optionally
    the user configuration file and data directories. Safe to re-run; missing
    items are reported and skipped rather than causing errors.

    What is removed by default (no switches):
      - Windows Service (stopped and deleted via NSSM or sc.exe)
      - All scheduled tasks under the '\JojoBot\' task folder

    What is KEPT by default (opt-in deletion):
      - %APPDATA%\JojoBot\config.json  (API keys, connector paths, DPAPI secrets)
      - Wiki directory (ask_jojo_wiki\)
      - Raw-ingest directory (ask_jojo_raw\)

    Use -DeleteConfig / -DeleteWiki / -DeleteRaw to delete those items without
    prompting, or -Force to skip all prompts and delete everything except the
    binary install directory (which the caller manages by deleting the zip extract).
    Use -Purge to delete everything including config + data directories.

.PARAMETER ServiceName
    Windows Service name to stop and remove. Default: JojoBot

.PARAMETER DeleteConfig
    Delete %APPDATA%\JojoBot\config.json without prompting.

.PARAMETER DeleteWiki
    Delete the wiki directory without prompting. The directory path is read from
    config.json (wiki_root key) if present; otherwise defaults to a sibling
    directory named ask_jojo_wiki relative to the install root.

.PARAMETER DeleteRaw
    Delete the raw-ingest directory without prompting. Path read from config.json
    (raw_root key); defaults to ask_jojo_raw sibling.

.PARAMETER Purge
    Equivalent to -DeleteConfig -DeleteWiki -DeleteRaw. Removes ALL JoJo Bot
    state. Use to leave no traces on the machine.

.PARAMETER Force
    Skip all interactive confirmation prompts. Combines with -DeleteConfig /
    -DeleteWiki / -DeleteRaw / -Purge to suppress "are you sure?" questions.

.PARAMETER NssmPath
    Explicit path to nssm.exe. If omitted, the script searches the same locations
    as Install-Service.ps1 (script dir, ProgramFiles\nssm\, PATH).

.EXAMPLE
    # Standard uninstall: remove service + tasks, keep config and data.
    .\Uninstall-JojoBot.ps1

.EXAMPLE
    # Full wipe for re-imaging: no prompts, no traces.
    .\Uninstall-JojoBot.ps1 -Purge -Force

.EXAMPLE
    # Automated uninstall in a deployment script.
    .\Uninstall-JojoBot.ps1 -DeleteConfig -Force

.NOTES
    Stopping and deleting a Windows Service requires admin privileges.
    Removing scheduled tasks under \JojoBot\ requires the tasks to be owned by
    the current user or elevated privileges.
    All strings in this file are pure ASCII (codepoints <= 127).
#>

[CmdletBinding()]
param(
    [string]$ServiceName  = "JojoBot",
    [switch]$DeleteConfig,
    [switch]$DeleteWiki,
    [switch]$DeleteRaw,
    [switch]$Purge,
    [switch]$Force,
    [string]$NssmPath
)

$ErrorActionPreference = "Stop"

# -Purge implies -Delete* flags.
if ($Purge) {
    $DeleteConfig = $true
    $DeleteWiki   = $true
    $DeleteRaw    = $true
}

Write-Host ""
Write-Host "=== JoJo Bot -- Uninstaller ===" -ForegroundColor Cyan
Write-Host ""

# Track what was removed for the summary at the end.
$removed   = [System.Collections.Generic.List[string]]::new()
$skipped   = [System.Collections.Generic.List[string]]::new()
$warnings  = [System.Collections.Generic.List[string]]::new()

# ---- helpers -----------------------------------------------------------------
function Find-Nssm {
    if ($NssmPath -and (Test-Path -LiteralPath $NssmPath)) { return $NssmPath }
    $beside = Join-Path $PSScriptRoot "nssm.exe"
    if (Test-Path $beside) { return $beside }
    $pf = Join-Path $env:ProgramFiles "nssm\nssm.exe"
    if (Test-Path $pf) { return $pf }
    $onPath = Get-Command nssm -ErrorAction SilentlyContinue
    if ($onPath) { return $onPath.Source }
    return $null
}

function Confirm-Delete {
    param([string]$Target, [string]$Description)
    # Returns $true if the caller should proceed with deletion.
    if ($Force) { return $true }
    $answer = Read-Host "  Delete $Description`n  Path: $Target`n  [y/N]"
    return ($answer -imatch '^y')
}

# ---- 1. Stop and remove Windows Service --------------------------------------
Write-Host "[1/3] Windows Service '$ServiceName'" -ForegroundColor Cyan

$svc = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
if (-not $svc) {
    Write-Host "  [skip] Service '$ServiceName' not found." -ForegroundColor Yellow
    $skipped.Add("Windows Service: $ServiceName (not found)")
} else {
    Write-Host "  Status: $($svc.Status)"
    # Stop first.
    if ($svc.Status -ne "Stopped") {
        Write-Host "  Stopping service..."
        try {
            Stop-Service -Name $ServiceName -Force
            Start-Sleep -Seconds 4
            Write-Host "  [ok] stopped." -ForegroundColor Green
        } catch {
            $warnings.Add("Could not stop service '$ServiceName': $($_.Exception.Message)")
            Write-Host "  [warn] $($_.Exception.Message)" -ForegroundColor Yellow
        }
    }
    # Remove.
    $nssmExe = Find-Nssm
    $removeOk = $false
    if ($nssmExe) {
        Write-Host "  Removing via NSSM ($nssmExe)..."
        & $nssmExe remove $ServiceName confirm 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) { $removeOk = $true }
    }
    if (-not $removeOk) {
        Write-Host "  Removing via sc.exe..."
        & sc.exe delete $ServiceName | Out-Null
        if ($LASTEXITCODE -eq 0) { $removeOk = $true }
    }
    if ($removeOk) {
        $removed.Add("Windows Service: $ServiceName")
        Write-Host "  [ok] service removed." -ForegroundColor Green
    } else {
        $warnings.Add("Could not remove service '$ServiceName' via NSSM or sc.exe.")
        Write-Host "  [warn] manual removal may be needed: sc.exe delete $ServiceName" -ForegroundColor Yellow
    }
}

Write-Host ""

# ---- 2. Remove scheduled tasks -----------------------------------------------
Write-Host "[2/3] Scheduled tasks under \JojoBot\" -ForegroundColor Cyan

$taskFolder = "\JojoBot"
$tasks = @()
try {
    $tasks = @(Get-ScheduledTask -TaskPath "$taskFolder\*" -ErrorAction SilentlyContinue)
} catch {
    $warnings.Add("Could not enumerate scheduled tasks: $($_.Exception.Message)")
    Write-Host "  [warn] could not enumerate tasks: $($_.Exception.Message)" -ForegroundColor Yellow
}

if (-not $tasks -or $tasks.Count -eq 0) {
    Write-Host "  [skip] No tasks found under $taskFolder\." -ForegroundColor Yellow
    $skipped.Add("Scheduled tasks: none found under $taskFolder")
} else {
    foreach ($t in $tasks) {
        try {
            Unregister-ScheduledTask -TaskPath $t.TaskPath -TaskName $t.TaskName -Confirm:$false
            $removed.Add("Scheduled task: $($t.TaskPath)$($t.TaskName)")
            Write-Host "  [ok] removed $($t.TaskPath)$($t.TaskName)" -ForegroundColor Green
        } catch {
            $warnings.Add("Could not remove task $($t.TaskName): $($_.Exception.Message)")
            Write-Host "  [warn] $($t.TaskName): $($_.Exception.Message)" -ForegroundColor Yellow
        }
    }
    # Try to remove the now-empty \JojoBot folder via COM.
    try {
        $svcCom = New-Object -ComObject Schedule.Service
        $svcCom.Connect()
        $rootF = $svcCom.GetFolder("\")
        $folderList = @($rootF.GetFolders(0))
        foreach ($f in $folderList) {
            if ($f.Name -eq "JojoBot") {
                $leftovers = @($f.GetTasks(0))
                if ($leftovers.Count -eq 0) {
                    $rootF.DeleteFolder("JojoBot", 0)
                    $removed.Add("Task Scheduler folder: $taskFolder")
                    Write-Host "  [ok] removed empty task folder $taskFolder" -ForegroundColor Green
                }
            }
        }
    } catch {
        # Non-fatal; folder may not be removable without elevation.
        Write-Host "  [note] could not remove task folder (may need elevation)." -ForegroundColor DarkGray
    }
}

Write-Host ""

# ---- 3. Optional data removal ------------------------------------------------
Write-Host "[3/3] User data and configuration" -ForegroundColor Cyan

$configDir  = Join-Path $env:APPDATA "JojoBot"
$configFile = Join-Path $configDir "config.json"

# Read wiki_root and raw_root from config if it exists (best-effort).
$wikiRoot = $null
$rawRoot  = $null
if (Test-Path $configFile) {
    try {
        $cfg = Get-Content $configFile -Raw -ErrorAction Stop | ConvertFrom-Json -ErrorAction Stop
        if ($cfg.wiki_root) { $wikiRoot = $cfg.wiki_root }
        if ($cfg.raw_root)  { $rawRoot  = $cfg.raw_root  }
    } catch {
        # Non-fatal; fallback paths used below.
    }
}

# --- 3a. config.json ----------------------------------------------------------
if ($DeleteConfig) {
    if (Test-Path $configDir) {
        $doIt = Confirm-Delete -Target $configDir `
            -Description "JoJo Bot config directory (API keys, connector paths)"
        if ($doIt) {
            try {
                Remove-Item -Recurse -Force -LiteralPath $configDir
                $removed.Add("Config directory: $configDir")
                Write-Host "  [ok] removed $configDir" -ForegroundColor Green
            } catch {
                $warnings.Add("Could not remove config dir: $($_.Exception.Message)")
                Write-Host "  [warn] $($_.Exception.Message)" -ForegroundColor Yellow
            }
        } else {
            $skipped.Add("Config directory: $configDir (user declined)")
            Write-Host "  [skip] config kept." -ForegroundColor Yellow
        }
    } else {
        $skipped.Add("Config directory: $configDir (not found)")
        Write-Host "  [skip] config directory not found." -ForegroundColor Yellow
    }
} else {
    $skipped.Add("Config directory: $configDir (use -DeleteConfig or -Purge to remove)")
    Write-Host "  [kept] $configFile (-DeleteConfig not set)." -ForegroundColor DarkGray
}

# --- 3b. wiki directory -------------------------------------------------------
if ($DeleteWiki) {
    # Path from config preferred; prompt if unknown.
    if (-not $wikiRoot) {
        if (-not $Force) {
            $wikiRoot = Read-Host "  Wiki directory path (blank to skip)"
        }
    }
    if ($wikiRoot -and (Test-Path -LiteralPath $wikiRoot)) {
        $doIt = Confirm-Delete -Target $wikiRoot -Description "wiki directory (compiled knowledge pages)"
        if ($doIt) {
            try {
                Remove-Item -Recurse -Force -LiteralPath $wikiRoot
                $removed.Add("Wiki directory: $wikiRoot")
                Write-Host "  [ok] removed $wikiRoot" -ForegroundColor Green
            } catch {
                $warnings.Add("Could not remove wiki dir: $($_.Exception.Message)")
                Write-Host "  [warn] $($_.Exception.Message)" -ForegroundColor Yellow
            }
        } else {
            $skipped.Add("Wiki directory: $wikiRoot (user declined)")
            Write-Host "  [skip] wiki kept." -ForegroundColor Yellow
        }
    } else {
        $display = if ($wikiRoot) { $wikiRoot } else { "(unknown path)" }
        $skipped.Add("Wiki directory: $display (not found or path not provided)")
        Write-Host "  [skip] wiki directory not found or not specified." -ForegroundColor Yellow
    }
} else {
    Write-Host "  [kept] wiki directory (-DeleteWiki not set)." -ForegroundColor DarkGray
}

# --- 3c. raw-ingest directory -------------------------------------------------
if ($DeleteRaw) {
    if (-not $rawRoot) {
        if (-not $Force) {
            $rawRoot = Read-Host "  Raw-ingest directory path (blank to skip)"
        }
    }
    if ($rawRoot -and (Test-Path -LiteralPath $rawRoot)) {
        $doIt = Confirm-Delete -Target $rawRoot -Description "raw-ingest directory (ingested source files)"
        if ($doIt) {
            try {
                Remove-Item -Recurse -Force -LiteralPath $rawRoot
                $removed.Add("Raw-ingest directory: $rawRoot")
                Write-Host "  [ok] removed $rawRoot" -ForegroundColor Green
            } catch {
                $warnings.Add("Could not remove raw dir: $($_.Exception.Message)")
                Write-Host "  [warn] $($_.Exception.Message)" -ForegroundColor Yellow
            }
        } else {
            $skipped.Add("Raw-ingest directory: $rawRoot (user declined)")
            Write-Host "  [skip] raw directory kept." -ForegroundColor Yellow
        }
    } else {
        $display = if ($rawRoot) { $rawRoot } else { "(unknown path)" }
        $skipped.Add("Raw-ingest directory: $display (not found or path not provided)")
        Write-Host "  [skip] raw-ingest directory not found or not specified." -ForegroundColor Yellow
    }
} else {
    Write-Host "  [kept] raw-ingest directory (-DeleteRaw not set)." -ForegroundColor DarkGray
}

# ---- 4. Service log directory (inside ProgramData) ---------------------------
# Removed only when -Purge is set, since it is in ProgramData not the install dir.
if ($Purge) {
    $svcLogDir = Join-Path $env:ProgramData "JojoBot"
    if (Test-Path $svcLogDir) {
        $doIt = Confirm-Delete -Target $svcLogDir -Description "service log directory (%ProgramData%\JojoBot)"
        if ($doIt) {
            try {
                Remove-Item -Recurse -Force -LiteralPath $svcLogDir
                $removed.Add("Service log directory: $svcLogDir")
                Write-Host "  [ok] removed $svcLogDir" -ForegroundColor Green
            } catch {
                $warnings.Add("Could not remove service log dir: $($_.Exception.Message)")
                Write-Host "  [warn] $($_.Exception.Message)" -ForegroundColor Yellow
            }
        } else {
            $skipped.Add("Service log directory: $svcLogDir (user declined)")
        }
    }
}

# ---- Summary -----------------------------------------------------------------
Write-Host ""
Write-Host "=== Uninstall Summary ===" -ForegroundColor Cyan
Write-Host ""

if ($removed.Count -gt 0) {
    Write-Host "Removed:" -ForegroundColor Green
    foreach ($item in $removed) {
        Write-Host "  [x] $item"
    }
    Write-Host ""
}

if ($skipped.Count -gt 0) {
    Write-Host "Kept / skipped:" -ForegroundColor Yellow
    foreach ($item in $skipped) {
        Write-Host "  [ ] $item"
    }
    Write-Host ""
}

if ($warnings.Count -gt 0) {
    Write-Host "Warnings:" -ForegroundColor Red
    foreach ($item in $warnings) {
        Write-Host "  [!] $item"
    }
    Write-Host ""
}

if ($warnings.Count -eq 0) {
    Write-Host "Done. JoJo Bot has been uninstalled." -ForegroundColor Green
} else {
    Write-Host "Uninstall complete with warnings. Review items above." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Note: The event log source 'JojoBot' (if it was ever created) is left" -ForegroundColor DarkGray
Write-Host "in place. Remove it with (admin): Remove-EventLog -Source JojoBot" -ForegroundColor DarkGray
Write-Host ""
