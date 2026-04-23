<#
.SYNOPSIS
    All-in-one bootstrap: takes a fresh checkout of ask_jojo to a running,
    scheduled JoJo Bot install on a Windows workstation.

.DESCRIPTION
    Walks the operator through:

      1. Preflight   -- Python, pip, git on PATH.
      2. Venv        -- (optional, -UseVenv) create .venv\ at repo root and
                        use its python for every subsequent step. Auto-
                        detected on re-run: if .venv\ exists, it's used
                        without the flag.
      3. Package     -- pip install -e ".[ingest,backend,cloud]" into the
                        active interpreter (venv if present, else system).
      4. Config      -- prompts for the handful of values the scheduler
                        needs (onedrive_path, public_drive_path,
                        sharepoint_sites, and optionally graph_access_token)
                        and writes them via `jojo-core config set`. DPAPI
                        encryption happens transparently on first write.
      5. Scheduler   -- calls Register-JojoBotTasks.ps1 with the answers
                        collected above, unless the operator opts out.
      6. PATH setup  -- calls Enable-JojoShell.ps1 to add the interpreter's
                        Scripts directory to persistent user PATH, so
                        `jojo-core` and `jojo-ingest` resolve in every new
                        PowerShell without a venv activation step. Opt out
                        with -SkipPathSetup.
      7. Smoke       -- runs `jojo-ingest --help` + `jojo-core config show`
                        to prove the end-to-end path works before the
                        script returns.

    Safe to re-run. Steps detect existing state and ask before overwriting:

      * venv creation is a no-op if .venv\ already exists.
      * pip install is always re-run (editable installs are cheap and
        refresh metadata).
      * existing config keys are left in place unless -Reconfigure is set.
      * scheduled tasks only re-register if -Force is set (otherwise you
        get the same "skip" warning Register-JojoBotTasks emits on its own).

.PARAMETER RepoRoot
    Path to the ask_jojo directory (the one that contains pyproject.toml).
    Defaults to two levels up from this script
    (ops\installer\.. \.. == ask_jojo root).

.PARAMETER DriveSource
    Passed through to Register-JojoBotTasks.ps1 for the JojoBot-Drive task.
    Optional; skip the drive task if not provided.

.PARAMETER UseVenv
    Create (or reuse) a project-local virtual environment at <RepoRoot>\.venv
    and install every package into it. All subsequent pip / jojo-core /
    jojo-ingest invocations in this script use the venv's python. Strongly
    recommended: it pins the interpreter so scheduled tasks, the validation
    runner, and the backend all see the same site-packages.

    If .venv\ already exists, the flag is effectively implied -- the script
    picks up the existing venv automatically. Use -RecreateVenv to wipe and
    rebuild a bad one.

.PARAMETER RecreateVenv
    Delete the existing .venv\ before creating a new one. Use only when the
    venv is corrupted (pip broken, wrong Python version baked in). Has no
    effect without -UseVenv or an existing .venv\.

.PARAMETER SkipPackage
    Don't run pip. Useful if the venv is already set up and you just want
    to redo config + tasks.

.PARAMETER SkipConfig
    Don't prompt for config values. Useful for re-running just the task
    registration step on a box that is already configured.

.PARAMETER SkipScheduler
    Don't call Register-JojoBotTasks.ps1. Useful when setting up a
    no-scheduler dev box.

.PARAMETER SkipPathSetup
    Don't call Enable-JojoShell.ps1 to add the Python Scripts directory
    to persistent user PATH. Useful on machines where PATH is managed
    externally (group policy, dotfiles, a profile script, etc.).

.PARAMETER Reconfigure
    Re-prompt for every config key even if it's already set. Old values
    are shown as the default so you can hit Enter to keep them (secrets
    are shown masked and Enter keeps the existing value).

.PARAMETER Force
    Pass -Force through to Register-JojoBotTasks.ps1 so existing
    JojoBot-* tasks are overwritten rather than skipped.

.EXAMPLE
    # first-time install with venv (recommended)
    .\Install-JojoBot.ps1 -UseVenv -DriveSource "C:\Users\mdelosrios\Documents"

.EXAMPLE
    # move an existing install from system-Python to a venv without redoing
    # config or tasks
    .\Install-JojoBot.ps1 -UseVenv -SkipConfig -SkipScheduler

.EXAMPLE
    # reconfigure an existing install (e.g. after the OneDrive path moved)
    .\Install-JojoBot.ps1 -Reconfigure -SkipPackage

.EXAMPLE
    # re-run just the task registration step (e.g. fixing a bad cadence)
    .\Install-JojoBot.ps1 -SkipPackage -SkipConfig -Force -DriveSource "C:\Work"

.NOTES
    Elevated PowerShell is NOT required, but recommended on the first
    run so Register-JojoBotTasks.ps1 can register the "JojoBot" event-log
    source. Non-elevated runs still work; event-log integration just
    stays off.

    All scripts involved are ASCII-only for Windows PowerShell 5.1
    compatibility (see ops/scheduler/README.md "Design notes").
#>

[CmdletBinding()]
param(
    [string]$RepoRoot,
    [string]$DriveSource,
    [switch]$UseVenv,
    [switch]$RecreateVenv,
    [switch]$SkipPackage,
    [switch]$SkipConfig,
    [switch]$SkipScheduler,
    [switch]$SkipPathSetup,
    [switch]$Reconfigure,
    [switch]$Force
)

$ErrorActionPreference = "Stop"

# ---- resolve repo root ---------------------------------------------------
if (-not $RepoRoot) {
    # ops\installer\.. -> ops; ops\.. -> ask_jojo
    $RepoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
}
$RepoRoot = (Resolve-Path $RepoRoot).Path
if (-not (Test-Path (Join-Path $RepoRoot "pyproject.toml"))) {
    Write-Host "[error] $RepoRoot does not look like the ask_jojo root (no pyproject.toml)." -ForegroundColor Red
    exit 1
}

$SchedulerDir = Join-Path $RepoRoot "ops\scheduler"
$RegisterScript = Join-Path $SchedulerDir "Register-JojoBotTasks.ps1"
$EnableScript = Join-Path $RepoRoot "ops\installer\Enable-JojoShell.ps1"
$VenvDir = Join-Path $RepoRoot ".venv"
$VenvPython = Join-Path $VenvDir "Scripts\python.exe"

# If a venv already exists, flip -UseVenv on so the rest of the script goes
# through it automatically. Explicit -UseVenv still works and is documented;
# this branch just prevents "forgot the flag" from silently using system
# python against an existing venv install.
if ((Test-Path $VenvPython) -and -not $UseVenv) {
    Write-Host "[info] .venv\ detected at $VenvDir; treating run as -UseVenv." -ForegroundColor Cyan
    $UseVenv = $true
}

Write-Host ""
Write-Host "=== JoJo Bot installer ===" -ForegroundColor Cyan
Write-Host "Repo:       $RepoRoot"
Write-Host "Scheduler:  $SchedulerDir"
Write-Host "Venv:       $(if ($UseVenv) { $VenvDir } else { '(not using a venv; system python)' })"
Write-Host ""

# ---- helpers -------------------------------------------------------------
# $script:ActivePython is whichever interpreter subsequent steps should use.
# Set by step 1 to the bootstrap (system) python, possibly re-pointed by
# step 2 to the venv python after we create one. Everything after step 2
# (config, scheduler invocation, smoke test) uses ActivePython so one
# installer run stays consistent.
$script:ActivePython = $null

function Get-SystemPython {
    # Bootstrap python -- used to *create* the venv, or used for everything
    # if -UseVenv is off.
    foreach ($candidate in @("python", "py")) {
        if (Get-Command $candidate -ErrorAction SilentlyContinue) { return $candidate }
    }
    return $null
}

function Get-Python {
    # The interpreter subsequent steps should use. Points at the venv once
    # step 2 has created it, otherwise at the system python.
    if ($script:ActivePython) { return $script:ActivePython }
    return (Get-SystemPython)
}

function Read-WithDefault {
    param(
        [string]$Prompt,
        [string]$Default,
        [switch]$Masked
    )
    if ($Default) {
        if ($Masked) {
            $shown = if ($Default.Length -le 4) { "****" } else { $Default.Substring(0,2) + "***" + $Default.Substring($Default.Length-2) }
            $display = "$Prompt [$shown] (Enter to keep)"
        } else {
            $display = "$Prompt [$Default] (Enter to keep)"
        }
    } else {
        $display = "$Prompt (blank to skip)"
    }
    $answer = Read-Host $display
    if ([string]::IsNullOrWhiteSpace($answer)) { return $Default }
    return $answer
}

function Invoke-JojoCore {
    param([string[]]$CoreArgs)
    $py = Get-Python
    & $py -m jojo_core @CoreArgs
    if ($LASTEXITCODE -ne 0) {
        # Redact the value for `config set <key> <value>` so a failure
        # never echoes a secret (e.g. graph_access_token) into the terminal
        # or the shell history. Same shape for any future SECRET_KEYS key.
        $safe = @($CoreArgs)
        if ($safe.Count -ge 4 -and $safe[0] -eq "config" -and $safe[1] -eq "set") {
            $safe[3] = "<redacted>"
        }
        throw "jojo-core $($safe -join ' ') exited with $LASTEXITCODE"
    }
}

function Get-ConfigValue([string]$Key) {
    # Returns the current value or $null if unset. --no-env so we don't
    # confuse ourselves by echoing back an env var we never persisted.
    $py = Get-Python
    $raw = & $py -m jojo_core config get $Key --no-env 2>$null
    if ($LASTEXITCODE -ne 0) { return $null }
    $raw = ($raw | Out-String).Trim()
    if ([string]::IsNullOrWhiteSpace($raw)) { return $null }
    return $raw
}

function Set-ConfigValue {
    param([string]$Key, [string]$Value)
    if ([string]::IsNullOrWhiteSpace($Value)) { return }
    # jojo-core config set treats everything after the key as the value,
    # which is what we want (spaces / special chars preserved).
    Invoke-JojoCore @("config", "set", $Key, $Value)
}

# ---- 1. preflight --------------------------------------------------------
Write-Host "[1/7] Preflight" -ForegroundColor Cyan
$sysPy = Get-SystemPython
if (-not $sysPy) {
    Write-Host "[error] Neither 'python' nor 'py' is on PATH." -ForegroundColor Red
    Write-Host "        Install Python 3.11+ from python.org, check 'Add to PATH', and re-run."
    exit 2
}
$pyVersion = (& $sysPy --version 2>&1 | Out-String).Trim()
Write-Host "  python:  $sysPy ($pyVersion)"

try {
    $null = & $sysPy -m pip --version 2>&1
    if ($LASTEXITCODE -ne 0) { throw "pip not available" }
} catch {
    Write-Host "[error] pip not available for $sysPy. Try: $sysPy -m ensurepip" -ForegroundColor Red
    exit 2
}
Write-Host "  pip:     ok"

if (Get-Command git -ErrorAction SilentlyContinue) {
    Write-Host "  git:     ok"
} else {
    Write-Host "  git:     [warn] not on PATH (fine for run-time; needed only to pull updates)" -ForegroundColor Yellow
}

# Default ActivePython to the system interpreter; step 2 may re-point it.
$script:ActivePython = $sysPy
Write-Host ""

# ---- 2. venv (optional) --------------------------------------------------
Write-Host "[2/7] Virtual environment" -ForegroundColor Cyan
if (-not $UseVenv) {
    Write-Host "  skipped (-UseVenv not set; using system python $sysPy)."
    Write-Host "  Tip: next run, add -UseVenv to pin jojo_bot to its own interpreter."
} else {
    if ((Test-Path $VenvDir) -and $RecreateVenv) {
        Write-Host "  -RecreateVenv set; removing existing $VenvDir ..."
        Remove-Item -Recurse -Force $VenvDir
    }
    if (-not (Test-Path $VenvPython)) {
        Write-Host "  creating venv at $VenvDir (using $sysPy) ..."
        & $sysPy -m venv $VenvDir
        if ($LASTEXITCODE -ne 0 -or -not (Test-Path $VenvPython)) {
            Write-Host "[error] venv creation failed." -ForegroundColor Red
            Write-Host "        $sysPy -m venv $VenvDir returned $LASTEXITCODE."
            Write-Host "        Check the output above, delete any half-created .venv\, and retry."
            exit 2
        }
        Write-Host "  [ok] venv created."
    } else {
        Write-Host "  [ok] existing venv at $VenvDir reused."
    }

    # Upgrade pip inside the venv. Fresh venvs ship with whatever pip was
    # bundled with the Python that created them -- often old enough to bork
    # on newer pyproject.toml build-backends. One cheap upgrade avoids a
    # whole class of mysterious install errors later.
    Write-Host "  upgrading pip inside the venv ..."
    & $VenvPython -m pip install --upgrade pip 2>&1 | Select-Object -Last 1 | ForEach-Object { Write-Host "    $_" }
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[warn] pip self-upgrade returned $LASTEXITCODE. Continuing; retry manually if installs misbehave." -ForegroundColor Yellow
    }

    $script:ActivePython = $VenvPython
    Write-Host "  [ok] active interpreter: $VenvPython"
}
Write-Host ""

# ---- 3. package install --------------------------------------------------
Write-Host "[3/7] Package install" -ForegroundColor Cyan
$py = Get-Python  # refresh: points at venv now if step 2 created one
if ($SkipPackage) {
    Write-Host "  skipped (-SkipPackage)."
} else {
    Push-Location $RepoRoot
    $pipExit = 0
    try {
        Write-Host "  running: $py -m pip install -e `".[ingest,backend,cloud]`""
        & $py -m pip install -e ".[ingest,backend,cloud]"
        $pipExit = $LASTEXITCODE
    } finally {
        Pop-Location
    }
    # `exit` inside try/finally skips finally in PowerShell, so we capture
    # the exit code inside the try and branch out here after Pop-Location ran.
    if ($pipExit -ne 0) {
        Write-Host "[error] pip install failed with exit $pipExit." -ForegroundColor Red
        exit $pipExit
    }
    # Smoke-test that both packages AND the third-party deps behind them
    # actually import now. httpx is the one that bit us last time -- it's
    # pulled in by jojo_ingest.graph but the plain `import jojo_ingest`
    # check passes without ever loading it. Probing the connector modules
    # catches missing-extra regressions at install time, not 15 minutes into
    # the first validation run.
    $probe = "import jojo_core, jojo_core.config, jojo_ingest, jojo_ingest.graph, jojo_ingest.sharepoint, jojo_ingest.onedrive, jojo_ingest.publicdrive"
    & $py -c $probe 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[error] install finished but a connector module failed to import:" -ForegroundColor Red
        & $py -c $probe  # re-run without /dev/null so the operator sees why
        exit 2
    }
    Write-Host "  import check: ok"
}
Write-Host ""

# ---- 4. configuration ----------------------------------------------------
Write-Host "[4/7] Configuration" -ForegroundColor Cyan
if ($SkipConfig) {
    Write-Host "  skipped (-SkipConfig)."
} else {
    $configPath = (& $py -m jojo_core config path | Out-String).Trim()
    Write-Host "  config file: $configPath"
    Write-Host ""

    # Keys to prompt for. Order matches the order operators think about them.
    $prompts = @(
        @{ Key = "raw_root";           Label = "ask_jojo_raw root (where ingested files land)"; Masked = $false },
        @{ Key = "onedrive_path";      Label = "OneDrive path (e.g. C:\Users\<you>\OneDrive - Nurix Therapeutics)"; Masked = $false },
        @{ Key = "public_drive_path";  Label = "Public drive root (e.g. P:\)"; Masked = $false },
        @{ Key = "sharepoint_sites";   Label = "SharePoint site names, comma-separated"; Masked = $false },
        @{ Key = "graph_access_token"; Label = "Microsoft Graph access token (paste one for today; rotate later)"; Masked = $true }
    )

    foreach ($p in $prompts) {
        $current = Get-ConfigValue $p.Key
        if ($current -and -not $Reconfigure) {
            Write-Host "  $($p.Key) already set; skipping (use -Reconfigure to re-prompt)."
            continue
        }
        $answer = Read-WithDefault -Prompt "    $($p.Label)" -Default $current -Masked:$p.Masked
        if ($answer -and ($answer -ne $current)) {
            Set-ConfigValue $p.Key $answer
            Write-Host "    [ok] saved."
        } elseif ($answer -and ($answer -eq $current)) {
            Write-Host "    [ok] kept existing."
        } else {
            Write-Host "    [skip] left unset."
        }
    }
}
Write-Host ""

# ---- 5. scheduled tasks --------------------------------------------------
Write-Host "[5/7] Scheduled tasks" -ForegroundColor Cyan
if ($SkipScheduler) {
    Write-Host "  skipped (-SkipScheduler)."
} elseif (-not (Test-Path $RegisterScript)) {
    Write-Host "[warn] $RegisterScript not found; skipping task registration." -ForegroundColor Yellow
} else {
    $regArgs = @()
    if ($DriveSource) { $regArgs += @("-DriveSource", $DriveSource) }
    if ($Force)       { $regArgs += @("-Force") }
    Write-Host "  invoking: $RegisterScript $($regArgs -join ' ')"
    & $RegisterScript @regArgs
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[warn] Register-JojoBotTasks.ps1 exited with $LASTEXITCODE." -ForegroundColor Yellow
        Write-Host "       Inspect above for details. Install continues."
    }
}
Write-Host ""

# ---- 6. PATH setup -------------------------------------------------------
# Add the active interpreter's Scripts directory to persistent user PATH so
# bare `jojo-core` / `jojo-ingest` resolve in every new PowerShell. This
# closes out the "Scripts dir not on PATH" class of support pings. For a
# venv install, we point PATH at <repo>\.venv\Scripts; for a system install,
# at the system Python's own Scripts dir -- Enable-JojoShell.ps1 handles
# the detection by asking Python itself (sysconfig.get_path('scripts')).
Write-Host "[6/7] Shell PATH" -ForegroundColor Cyan
if ($SkipPathSetup) {
    Write-Host "  skipped (-SkipPathSetup)."
} elseif (-not (Test-Path $EnableScript)) {
    Write-Host "[warn] $EnableScript not found; skipping PATH setup." -ForegroundColor Yellow
    Write-Host "       Add the Python Scripts directory to your user PATH manually if"
    Write-Host "       bare 'jojo-core' does not resolve in new shells."
} else {
    # Enable-JojoShell.ps1 auto-detects the venv on its own, but pass -UseVenv
    # through explicitly when this install ran with it so the intent is clear
    # in the script's console output.
    #
    # PS 5.1 splatting gotcha: `& $script @(-UseVenv)` passes "-UseVenv" as a
    # positional string arg rather than a named switch, which yields
    # "positional parameter cannot be found" from the callee. Call the script
    # directly with the switch to sidestep the quirk entirely.
    if ($UseVenv) {
        & $EnableScript -UseVenv
    } else {
        & $EnableScript
    }
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[warn] Enable-JojoShell.ps1 exited with $LASTEXITCODE." -ForegroundColor Yellow
        Write-Host "       Bare 'jojo-core' may not resolve in new shells; install continues."
    }
}
Write-Host ""

# ---- 7. end-to-end smoke -------------------------------------------------
Write-Host "[7/7] Smoke test" -ForegroundColor Cyan
$py = Get-Python  # refresh in case step 2 re-pointed at the venv
& $py -m jojo_ingest --help | Select-Object -First 5 | ForEach-Object { Write-Host "    $_" }
Write-Host ""
Write-Host "  current config (secrets masked):"
& $py -m jojo_core config show | ForEach-Object { Write-Host "    $_" }
Write-Host ""

Write-Host "=== Done ===" -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  * Confirm tasks:  Get-ScheduledTask -TaskPath '\JojoBot\*' | Format-Table"
Write-Host "  * Smoke one run:  Start-ScheduledTask -TaskPath '\JojoBot\' -TaskName 'JojoBot-Drive'"
Write-Host "  * Tail a log:     Get-Content -Wait -Tail 0 (Join-Path '$RepoRoot' 'ops\scheduler\logs\drive\<yyyy-MM-dd>.log')"
Write-Host "  * Rotate token:   jojo-core config set graph_access_token `"<fresh token>`""
Write-Host ""
Write-Host "See ops/scheduler/README.md for ongoing operations." -ForegroundColor Cyan
