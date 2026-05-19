# Run-DeviceCodeLogin.ps1
#
# One-shot helper that walks the operator through the MSAL device-code login
# for Microsoft Graph (SharePoint / OneDrive). After this runs successfully a
# token is cached at %APPDATA%\JojoBot\tokencache.bin (~90 day lifetime with
# silent refresh), and scheduled SharePoint ingest tasks stop needing manual
# token rotation.
#
# REQUIREMENTS
#   - Phase 4 of the /goal run must have shipped the `jojo-ingest auth
#     device-code` subcommand. If you run this before that ships, you will
#     see "No module named jojo_ingest.auth" or similar -- wait for the
#     first Path B commit to land.
#   - JoJo Bot venv at <repo-root>\ask_jojo\.venv (default; override via
#     -VenvPath).
#   - Network access to login.microsoftonline.com.
#
# USAGE
#   .\Run-DeviceCodeLogin.ps1
#   .\Run-DeviceCodeLogin.ps1 -VenvPath "C:\Custom\Path\.venv"
#   .\Run-DeviceCodeLogin.ps1 -Force            # ignore existing cache
#   .\Run-DeviceCodeLogin.ps1 -ClearCache       # delete cache and exit
#
# DESIGN NOTES
#   - Pure ASCII (codepoints <= 127). Windows PowerShell 5.1 reads .ps1 as
#     CP1252 without BOM; em-dashes break the parser. Verified via
#     [System.Text.Encoding]::ASCII roundtrip; do NOT add smart quotes.
#   - Tees output to ops\scheduler\logs\device-code\<date>.log so a failed
#     login leaves a breadcrumb.
#   - Writes a Windows Application event-log entry on success/failure under
#     source "JojoBot" (silently no-ops if the source has not been
#     registered with admin rights -- not fatal).
#   - Idempotent: re-running with a valid cache exits 0 immediately unless
#     -Force is passed.

[CmdletBinding()]
param(
    [string] $VenvPath,
    [switch] $Force,
    [switch] $ClearCache
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot  = Split-Path -Parent (Split-Path -Parent $ScriptDir)   # ...\ask_jojo
$LogDir    = Join-Path $ScriptDir "logs\device-code"
$null = New-Item -ItemType Directory -Path $LogDir -Force
$LogFile   = Join-Path $LogDir ("{0:yyyy-MM-dd}.log" -f (Get-Date))

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $stamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    $line  = "$stamp [$Level] $Message"
    Write-Host $line
    Add-Content -Path $LogFile -Value $line
}

function Write-EventSafe {
    param([string]$Message, [string]$Level)
    try {
        Write-EventLog -LogName Application -Source "JojoBot" `
            -EventId 4100 -EntryType $Level -Message $Message
    } catch {
        # Source not registered (needs admin to register). Not fatal.
    }
}

Write-Log "Starting MSAL device-code login helper"

# --- Resolve venv Python ----------------------------------------------------
if (-not $VenvPath) {
    $VenvPath = Join-Path $RepoRoot ".venv"
}
$VenvPython = Join-Path $VenvPath "Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    Write-Log "Venv Python not found at $VenvPython" "ERROR"
    Write-Log "Pass -VenvPath or activate the venv before running" "ERROR"
    Write-EventSafe "Run-DeviceCodeLogin: venv missing at $VenvPython" "Error"
    exit 2
}
Write-Log "Using Python: $VenvPython"

# --- Preflight: jojo_ingest installed --------------------------------------
$preflight = & $VenvPython -c "import jojo_ingest; print('ok')" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Log "jojo_ingest is not importable from this venv: $preflight" "ERROR"
    Write-Log "Run: pip install -e `".[ingest,backend,cloud]`" from $RepoRoot" "ERROR"
    Write-EventSafe "Run-DeviceCodeLogin: jojo_ingest not importable" "Error"
    exit 2
}

# --- Clear cache mode -------------------------------------------------------
$CacheFile = Join-Path $env:APPDATA "JojoBot\tokencache.bin"
if ($ClearCache) {
    if (Test-Path $CacheFile) {
        Remove-Item $CacheFile -Force
        Write-Log "Cleared token cache at $CacheFile"
    } else {
        Write-Log "No token cache to clear (looked at $CacheFile)"
    }
    exit 0
}

# --- Skip if cache is valid (unless -Force) --------------------------------
if (-not $Force) {
    $status = & $VenvPython -m jojo_ingest auth status 2>&1
    if ($LASTEXITCODE -eq 0 -and $status -match "valid") {
        Write-Log "Existing cached token is valid; nothing to do. Pass -Force to re-login."
        Write-Log $status
        exit 0
    }
}

# --- Run device-code flow ---------------------------------------------------
Write-Log "Launching device-code flow. Follow the on-screen instructions:"
Write-Log "  1. A short code (e.g. ABC123) will be printed below."
Write-Log "  2. Open https://microsoft.com/devicelogin in any browser."
Write-Log "  3. Enter the code and sign in with your Nurix account."
Write-Log "  4. This script waits up to 15 minutes for the sign-in to complete."
Write-Log ""

$proc = Start-Process -FilePath $VenvPython `
    -ArgumentList @("-m", "jojo_ingest", "auth", "device-code") `
    -NoNewWindow -PassThru -Wait

if ($proc.ExitCode -ne 0) {
    Write-Log "Device-code login failed with exit code $($proc.ExitCode)" "ERROR"
    Write-EventSafe "Run-DeviceCodeLogin: failed with exit $($proc.ExitCode)" "Error"
    exit $proc.ExitCode
}

# --- Verify cache landed ----------------------------------------------------
if (-not (Test-Path $CacheFile)) {
    Write-Log "Login reported success but no cache file at $CacheFile" "ERROR"
    Write-EventSafe "Run-DeviceCodeLogin: success reported but no cache file" "Error"
    exit 3
}

$cacheInfo = Get-Item $CacheFile
Write-Log "Token cache written: $($cacheInfo.FullName) ($($cacheInfo.Length) bytes)"
Write-Log "Cached at: $($cacheInfo.LastWriteTime)"
Write-Log ""
Write-Log "Device-code login complete. Scheduled SharePoint sync tasks can now"
Write-Log "run unattended for approximately 90 days. Re-run this script if"
Write-Log "the cache is cleared or the refresh window expires."

Write-EventSafe "Run-DeviceCodeLogin: success, cache at $CacheFile" "Information"
exit 0
