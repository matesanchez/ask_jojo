<#
.SYNOPSIS
    Wrapper script invoked by Windows Task Scheduler for each JoJo Bot
    connector. Runs `python -m jojo_ingest sync <connector>` with a
    max-runtime watchdog, singleton lock, environment preflight, and
    buffered logging.

.DESCRIPTION
    Scheduled tasks don't inherit an interactive shell's environment, so
    this script:
      1. Resolves python/py on PATH (fails loudly if neither is present).
      2. Confirms the jojo_ingest package is importable.
      3. Acquires a per-connector singleton lock (FU-10) so two scheduled
         runs can't race the same manifest.json.
      4. Runs preflight checks: source path reachable, free disk space,
         NIC selective-suspend posture (root cause of 2026-04-23 stall),
         OneDrive client running (Files-On-Demand needs it).
      5. Runs the sync via System.Diagnostics.Process with a max-runtime
         watchdog and periodic heartbeat. Tees stdout + stderr to a
         dated log file under ops\scheduler\logs\<connector>\<yyyy-MM-dd>.log
         using a buffered StreamWriter (per-line Add-Content was O(n)
         on 18k-file walks).
      6. Reports a rollup line to the Windows Application event log under
         source "JojoBot" -- informational on success, error on non-zero
         exit. If the event source doesn't exist, it's skipped silently
         (creation requires admin and happens at registration time).
      7. Exits with the underlying jojo-ingest exit code, or 2 for
         preflight failure, or 124 for watchdog timeout, so Task
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

.PARAMETER MaxRuntimeMinutes
    Watchdog deadline. If the python child runs longer than this, the
    wrapper kills it and exits 124. Per-connector defaults: publicdrive
    1440 (24h, the 18k-file P-drive walk), onedrive 720 (12h), drive 360
    (6h), sharepoint 120 (2h). Pass 0 to disable.

.PARAMETER MinDiskFreeGB
    Minimum free space (GB) on the volume holding ask_jojo_raw before the
    sync is allowed to start. Default 2. Pass 0 to disable.

.PARAMETER IgnoreLock
    Bypass the singleton lock check. For emergency manual reruns when
    you know the previous run is dead but its lock file is stale.

.EXAMPLE
    # Invoked by Task Scheduler:
    powershell -ExecutionPolicy Bypass -File Run-ScheduledSync.ps1 -Connector drive -Source "C:\Users\mdelosrios\Documents"

.EXAMPLE
    # Manual rerun after a confirmed-dead previous attempt:
    .\Run-ScheduledSync.ps1 -Connector publicdrive -Raw .\ask_jojo_raw -IgnoreLock

.NOTES
    Exit codes:
      0    success
      2    preflight failure (no python, package not importable, lock held,
           source missing, disk too full)
      124  watchdog timeout (max runtime exceeded)
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
    [string]$LogRoot,
    [int]$MaxRuntimeMinutes = -1,
    [int]$MinDiskFreeGB = 2,
    [switch]$IgnoreLock
)

$ErrorActionPreference = "Stop"

# ---- per-connector defaults for new params -------------------------------
if ($MaxRuntimeMinutes -lt 0) {
    $MaxRuntimeMinutes = switch ($Connector) {
        "publicdrive" { 1440 }
        "onedrive"    { 720 }
        "drive"       { 360 }
        "sharepoint"  { 120 }
        default       { 360 }
    }
}

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

# ---- buffered log writer (replaces per-line Add-Content) -----------------
# Add-Content opened-and-closed the file for every line, which on PS 5.1 is
# one syscall round-trip per line. For an 18k-file publicdrive walk that's
# enough I/O in the wrapper to noticeably affect throughput. A StreamWriter
# held open for the whole run is the standard fix; we Flush() periodically
# so external `Get-Content -Wait` tail-watchers still see live output.
$Script:LogStream = [System.IO.StreamWriter]::new($LogFile, $true, [System.Text.Encoding]::UTF8)
$Script:LogStream.AutoFlush = $false
$Script:LogLock = New-Object Object

function Write-LogLineRaw([string]$Line) {
    [System.Threading.Monitor]::Enter($Script:LogLock)
    try {
        $Script:LogStream.WriteLine($Line)
    } finally {
        [System.Threading.Monitor]::Exit($Script:LogLock)
    }
    Write-Host $Line
}

function Write-Log([string]$Level, [string]$Message) {
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-LogLineRaw "[$ts] [$Level] [$Connector] $Message"
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

function Close-LogStream {
    if ($Script:LogStream) {
        try {
            $Script:LogStream.Flush()
            $Script:LogStream.Dispose()
        } catch {}
        $Script:LogStream = $null
    }
}

# ---- singleton lock (FU-10) ---------------------------------------------
# Task Scheduler will happily fire a second copy of a task if the first run
# exceeds its expected duration. Two simultaneous runs racing the same
# manifest.json corrupts it. Use a PID-stamped lock file in %TEMP%; if the
# file exists and the recorded PID is still alive, refuse to start.
$LockFile = Join-Path $env:TEMP "JojoBot-$Connector.lock"
$lockAcquired = $false

function Test-LockHolderAlive([int]$HolderPid) {
    if ($HolderPid -le 0) { return $false }
    try {
        Get-Process -Id $HolderPid -ErrorAction Stop | Out-Null
        return $true
    } catch {
        return $false
    }
}

if (Test-Path $LockFile) {
    $existingPid = 0
    try { $existingPid = [int](Get-Content $LockFile -ErrorAction Stop -TotalCount 1) } catch {}
    if ((Test-LockHolderAlive $existingPid) -and -not $IgnoreLock) {
        Write-Log "ERROR" "another $Connector sync is already running (PID $existingPid). Lock: $LockFile. Use -IgnoreLock to override."
        Write-EventLogSafe -EntryType Error -EventId 1003 `
            -Message "JojoBot $Connector sync refused: lock held by PID $existingPid."
        Close-LogStream
        exit 2
    }
    if ($IgnoreLock) {
        Write-Log "WARN" "ignoring existing lock for PID $existingPid (-IgnoreLock set)"
    } else {
        Write-Log "WARN" "removing stale lock from PID $existingPid"
    }
    Remove-Item $LockFile -Force -ErrorAction SilentlyContinue
}
$PID | Out-File -FilePath $LockFile -Encoding ASCII -Force
$lockAcquired = $true

$exit = $null

try {

    # ---- preflight: python + jojo_ingest importable ----------------------
    # Resolution order:
    #   1. <repo>\.venv\Scripts\python.exe (pinned per-repo)
    #   2. `python` on PATH
    #   3. `py` (Windows Python launcher)
    # Scheduled tasks run with a stripped environment -- no interactive
    # PATH, no venv auto-activation -- so we resolve the venv path explicitly
    # against $ProjectRoot rather than relying on PATH inheriting anything.
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
        $exit = 2
        exit $exit
    }
    Write-Log "INFO" "using python: $PythonExe"

    # Tight preflight: import every connector module, not just the top-level
    # package. jojo_ingest/__init__.py is trivial, so a bare `import
    # jojo_ingest` misses third-party deps like httpx. We want the preflight
    # to fail here with a readable message rather than letting the actual
    # sync crash at import time.
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
        $exit = 2
        exit $exit
    }

    # ---- preflight: source path reachable --------------------------------
    # Run-ValidationSyncAll.ps1 has had this preflight; the scheduled
    # wrapper didn't. For publicdrive this is the difference between "fail
    # fast in 3s" and "burn 4 hours discovering the SMB mount dropped".
    function Resolve-DefaultSource([string]$Conn) {
        switch ($Conn) {
            "publicdrive" {
                if ($env:JOJO_PUBLIC_DRIVE_PATH) { return $env:JOJO_PUBLIC_DRIVE_PATH }
                return "P:\"
            }
            "onedrive" {
                if ($env:JOJO_ONEDRIVE_PATH) { return $env:JOJO_ONEDRIVE_PATH }
                return (Join-Path $env:USERPROFILE "OneDrive - Nurix Therapeutics, Inc")
            }
            default { return $null }
        }
    }

    $resolvedSource = $Source
    if (-not $resolvedSource) {
        $resolvedSource = Resolve-DefaultSource $Connector
    }
    if ($resolvedSource -and ($Connector -ne "sharepoint")) {
        if (-not (Test-Path -LiteralPath $resolvedSource)) {
            Write-Log "ERROR" "source path not reachable: $resolvedSource (connector $Connector). Mapped drive dropped or OneDrive folder missing."
            Write-EventLogSafe -EntryType Error -EventId 1004 `
                -Message "JojoBot $Connector sync failed: source path '$resolvedSource' not reachable."
            $exit = 2
            exit $exit
        }
        Write-Log "INFO" "source path reachable: $resolvedSource"
    }

    # ---- preflight: free disk space --------------------------------------
    if ($MinDiskFreeGB -gt 0) {
        $rawForCheck = $Raw
        if (-not $rawForCheck) { $rawForCheck = Join-Path $ProjectRoot "ask_jojo_raw" }
        $checkPath = $rawForCheck
        if (-not (Test-Path -LiteralPath $checkPath)) { $checkPath = $ProjectRoot }
        try {
            $qual = (Split-Path -Qualifier (Resolve-Path -LiteralPath $checkPath -ErrorAction Stop))
            $driveLetter = $qual.TrimEnd(':')
            $psd = Get-PSDrive -Name $driveLetter -ErrorAction Stop
            $freeGB = [math]::Floor($psd.Free / 1GB)
            if ($freeGB -lt $MinDiskFreeGB) {
                Write-Log "ERROR" "low disk space on ${qual}: ${freeGB}GB free, ${MinDiskFreeGB}GB required."
                Write-EventLogSafe -EntryType Error -EventId 1005 `
                    -Message "JojoBot $Connector sync refused: only ${freeGB}GB free on ${qual}."
                $exit = 2
                exit $exit
            }
            Write-Log "INFO" "disk free on ${qual}: ${freeGB}GB"
        } catch {
            Write-Log "WARN" "disk-space check failed (non-fatal): $($_.Exception.Message)"
        }
    }

    # ---- preflight: NIC selective-suspend (warn only) --------------------
    # Selective Suspend on a laptop NIC is the suspected root cause of the
    # 2026-04-23 17h zero-CPU publicdrive stall. The kernel suspends the
    # NIC mid-walk and SMB calls block in the driver indefinitely, with no
    # syscall return that the OSError catch can rescue. The Python-layer
    # watchdog (FU-9) is now the backstop for this; this check is the
    # operational nudge to stop the bug from being possible in the first
    # place. Warn loud, don't block: a desktop without the issue should
    # still run.
    try {
        $offending = Get-NetAdapter -ErrorAction Stop |
            Where-Object { $_.Status -eq 'Up' } |
            ForEach-Object {
                $pm = Get-NetAdapterPowerManagement -Name $_.Name -ErrorAction SilentlyContinue
                if ($pm -and ($pm.SelectiveSuspend -eq 'Enabled' -or $pm.AllowComputerToTurnOffDevice -eq 'Enabled')) { $pm }
            }
        if ($offending) {
            $names = ($offending | ForEach-Object { $_.Name }) -join ', '
            Write-Log "WARN" "NIC selective-suspend / device-power-down enabled on: $names. Recommended (elevated): Set-NetAdapterPowerManagement -SelectiveSuspend Disabled -AllowComputerToTurnOffDevice Disabled. Suspected root cause of 2026-04-23 publicdrive stall."
        } else {
            Write-Log "INFO" "NIC power-management posture clean"
        }
    } catch {
        Write-Log "DEBUG" "NIC power-management check skipped: $($_.Exception.Message)"
    }

    # ---- preflight: OneDrive client state (onedrive only) ----------------
    if ($Connector -eq "onedrive") {
        $odProc = Get-Process -Name OneDrive -ErrorAction SilentlyContinue
        if (-not $odProc) {
            Write-Log "WARN" "OneDrive client not running. Files-On-Demand placeholders will not hydrate; cloud-only files may be skipped or fail to read."
        } else {
            Write-Log "INFO" "OneDrive client running (PID $($odProc[0].Id))"
        }
    }

    # ---- build + run the sync invocation ---------------------------------
    $syncArgs = @("-m", "jojo_ingest", "sync", $Connector)
    if ($Raw)    { $syncArgs += @("--raw", $Raw) }
    if ($Source) { $syncArgs += @("--source", $Source) }
    if ($Since)  { $syncArgs += @("--since", $Since) }

    Write-Log "INFO" "starting: $PythonExe $($syncArgs -join ' ') (max ${MaxRuntimeMinutes}m)"
    $start = Get-Date

    # Use System.Diagnostics.Process directly so we can:
    #   - tee stdout + stderr line-by-line into the buffered StreamWriter
    #   - enforce a max-runtime watchdog that actually kills a hung child
    #   - emit periodic heartbeats so external tail-watchers can tell the
    #     run is alive even when Python is silent during a deep walk
    #
    # PS 5.1 gotcha: ProcessStartInfo.ArgumentList (the array form) is
    # .NET 5+ and not available here, so we build a single Arguments string
    # and escape any whitespace ourselves. The connector arg values we
    # accept are paths and ISO timestamps; quote anything with spaces.
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $PythonExe
    $psi.Arguments = ($syncArgs | ForEach-Object {
        if ($_ -match '\s') { '"' + ($_ -replace '"','\"') + '"' } else { $_ }
    }) -join ' '
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.UseShellExecute = $false
    $psi.CreateNoWindow = $true
    $psi.WorkingDirectory = $ProjectRoot

    $childProc = New-Object System.Diagnostics.Process
    $childProc.StartInfo = $psi
    $childProc.EnableRaisingEvents = $true

    # Bridge child stdout/stderr into a thread-safe queue. Event handlers
    # fire on .NET threadpool threads; PowerShell scriptblocks attached via
    # Register-ObjectEvent run in their own runspace and can't see
    # $Script: variables, so we pass the queue in through -MessageData.
    $lineQueue = [System.Collections.Concurrent.ConcurrentQueue[string]]::new()
    $stdoutSub = Register-ObjectEvent -InputObject $childProc -EventName OutputDataReceived `
        -MessageData $lineQueue -Action {
            if ($null -ne $EventArgs.Data) { $Event.MessageData.Enqueue($EventArgs.Data) }
        }
    $stderrSub = Register-ObjectEvent -InputObject $childProc -EventName ErrorDataReceived `
        -MessageData $lineQueue -Action {
            if ($null -ne $EventArgs.Data) { $Event.MessageData.Enqueue("[stderr] " + $EventArgs.Data) }
        }

    $childProc.Start() | Out-Null
    $childProc.BeginOutputReadLine()
    $childProc.BeginErrorReadLine()

    if ($MaxRuntimeMinutes -gt 0) {
        $watchdogDeadline = (Get-Date).AddMinutes($MaxRuntimeMinutes)
    } else {
        $watchdogDeadline = [DateTime]::MaxValue
    }
    $lastHeartbeat = Get-Date
    $heartbeatInterval = [TimeSpan]::FromMinutes(15)
    $watchdogFired = $false

    try {
        while (-not $childProc.HasExited) {
            $line = $null
            $drained = 0
            while ($lineQueue.TryDequeue([ref]$line)) {
                Write-LogLineRaw $line
                $drained++
                if ($drained -ge 200) { break }  # yield to watchdog check
            }
            if ($drained -gt 0) {
                $Script:LogStream.Flush()
            }
            if ((Get-Date) -gt $watchdogDeadline) {
                Write-Log "ERROR" "watchdog: max runtime ${MaxRuntimeMinutes}m exceeded; killing PID $($childProc.Id)"
                try { $childProc.Kill() } catch { Write-Log "WARN" "Kill() failed: $($_.Exception.Message)" }
                $watchdogFired = $true
                break
            }
            if ((Get-Date) - $lastHeartbeat -gt $heartbeatInterval) {
                $running = [int]((Get-Date) - $start).TotalSeconds
                $wsMb = 0
                try { $wsMb = [math]::Round($childProc.WorkingSet64 / 1MB) } catch {}
                Write-Log "INFO" "heartbeat: alive ${running}s (PID $($childProc.Id), workingset ${wsMb}MB)"
                $Script:LogStream.Flush()
                $lastHeartbeat = Get-Date
            }
            Start-Sleep -Milliseconds 500
        }

        # Wait for full exit, then drain any output buffered after HasExited
        # flipped but before the event handlers fired.
        $childProc.WaitForExit(10000) | Out-Null
        $line = $null
        while ($lineQueue.TryDequeue([ref]$line)) {
            Write-LogLineRaw $line
        }
        $Script:LogStream.Flush()

        if ($watchdogFired) {
            $exit = 124
        } else {
            $exit = $childProc.ExitCode
        }
    } finally {
        try { Unregister-Event -SubscriptionId $stdoutSub.Id -ErrorAction SilentlyContinue } catch {}
        try { Unregister-Event -SubscriptionId $stderrSub.Id -ErrorAction SilentlyContinue } catch {}
        try { $childProc.Dispose() } catch {}
    }

    $duration = [int]((Get-Date) - $start).TotalSeconds

    if ($exit -eq 0) {
        Write-Log "INFO" "completed in ${duration}s"
        Write-EventLogSafe -EntryType Information -EventId 100 `
            -Message "JojoBot $Connector sync completed in ${duration}s. Log: $LogFile"
    } elseif ($exit -eq 124) {
        Write-Log "ERROR" "watchdog timeout after ${duration}s (limit ${MaxRuntimeMinutes}m)"
        Write-EventLogSafe -EntryType Error -EventId 1006 `
            -Message "JojoBot $Connector sync KILLED by watchdog after ${duration}s (limit ${MaxRuntimeMinutes}m). Log: $LogFile"
    } else {
        Write-Log "ERROR" "failed with exit $exit after ${duration}s"
        Write-EventLogSafe -EntryType Error -EventId 1000 `
            -Message "JojoBot $Connector sync FAILED (exit $exit) after ${duration}s. Log: $LogFile"
    }

} finally {
    if ($lockAcquired) {
        Remove-Item $LockFile -Force -ErrorAction SilentlyContinue
    }
    Close-LogStream
}

if ($null -eq $exit) { $exit = 1 }
exit $exit
