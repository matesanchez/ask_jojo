<#
.SYNOPSIS
    Build a self-contained JoJo Bot release zip for department workstation install.

.DESCRIPTION
    Produces dist\JojoBot-v<version>.zip containing:

      JojoBot-v<version>\
        python\              <- frozen Python runtime (PyInstaller --onedir output,
                               or pip --target fallback when PyInstaller is absent)
        frontend\            <- Next.js static export (out\ directory after npm build)
        Install-JojoBot.ps1  <- end-user entry point: extracts, configures, registers service
        Uninstall-JojoBot.ps1
        Install-Service.ps1  <- NSSM service registration (called by Install-JojoBot.ps1)
        nssm.exe             <- bundled if found beside this script or in the nssm\ dir
        README.txt           <- one-screen quick-start guide

    The zip is self-contained for air-gapped Windows VMs: no internet required at
    install time. All Python wheels and the Next.js build are pre-bundled.

    === Python freeze strategy ===
    1. PRIMARY -- PyInstaller --onedir: produces python\jojo-server.exe plus a
       _internal\ tree of .dlls and .pyc files. The frozen exe IS the uvicorn
       runner; no python.exe needed at the install site.
       Invocation:
         pyinstaller --onedir --name jojo-server
           --add-data "src/backend:backend"
           src/backend/main.py
    2. FALLBACK -- pip --target: copies all packages into dist\python\ as plain
       Python files. The install site still needs a compatible Python 3.11+ on
       PATH; Install-Service.ps1 is called with -AppPath python.exe.
       Used when PyInstaller is absent or when -SkipPython is set.

    === Next.js build strategy ===
    'npm run build' then detects whether static export is configured. The existing
    next.config.js uses rewrites(), which is incompatible with Next.js static export
    (next export / output: 'export'). If the build does not produce an out\ directory,
    a note file is written explaining the manual step and the zip ships a placeholder
    frontend\. See docs\ops\distribution.md for the workaround.

    === Idempotency ===
    Re-running cleans the intermediate staging directory before building. Existing
    dist\ zip files from prior builds are left in place (named by version); only
    the current version's zip is overwritten.

.PARAMETER Version
    Version string embedded in the zip name and README. Default: 2.0.0

.PARAMETER RepoRoot
    Path to the ask_jojo directory (must contain pyproject.toml). Auto-detected
    as two levels up from ops\installer\ when omitted.

.PARAMETER OutDir
    Directory to write the final zip. Default: <RepoRoot>\dist

.PARAMETER DryRun
    Validate all prerequisites and print a summary of what would happen, but do
    not build anything. Exit 0 if all prerequisites are met; exit 1 with a clear
    error message for each unmet prerequisite.

.PARAMETER SkipFrontend
    Skip the Next.js build step. Use when the frontend has already been built
    (src\frontend\out\ exists) and you only want to freeze Python + assemble the zip.

.PARAMETER SkipPython
    Skip the Python freeze step entirely. The zip will ship a placeholder python\
    directory with a README explaining that the install site needs Python 3.11+ and
    the package installed separately. Use for debugging other build stages.

.PARAMETER KeepIntermediate
    Do not delete the staging directory (dist\JojoBot-v<version>\) after zipping.
    Useful for inspecting the staged contents before committing to a zip.

.EXAMPLE
    # Dry-run to check prerequisites:
    .\Build-JojoBotRelease.ps1 -DryRun

.EXAMPLE
    # Full build (typical CI / release manager invocation):
    .\Build-JojoBotRelease.ps1 -Version 2.0.1

.EXAMPLE
    # Rebuild only the zip assembly after manually fixing frontend out\:
    .\Build-JojoBotRelease.ps1 -SkipPython -SkipFrontend

.NOTES
    Compress-Archive (used for zip creation) has a practical size limit of ~2 GB
    on PowerShell 5.1. A PyInstaller --onedir build with FastAPI/uvicorn/click/
    Pydantic/all-deps typically runs 200-400 MB; the Next.js out\ dir 5-50 MB.
    If the archive approaches 1.5 GB (e.g. due to extra ML wheels), switch to
    the System.IO.Compression.ZipFile .NET API or 7z.exe.

    All strings in this file are pure ASCII (codepoints <= 127).
#>

[CmdletBinding()]
param(
    [string]$Version        = "2.0.0",
    [string]$RepoRoot,
    [string]$OutDir,
    [switch]$DryRun,
    [switch]$SkipFrontend,
    [switch]$SkipPython,
    [switch]$KeepIntermediate
)

$ErrorActionPreference = "Stop"

# ---- resolve repo root -------------------------------------------------------
if (-not $RepoRoot) {
    # ops\installer\.. -> ops; ops\.. -> ask_jojo
    $RepoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
}
# Resolve-Path throws if the path does not exist, which is the right behavior.
$RepoRoot = (Resolve-Path $RepoRoot).Path

if (-not (Test-Path (Join-Path $RepoRoot "pyproject.toml"))) {
    Write-Host "[error] $RepoRoot does not look like the ask_jojo root (no pyproject.toml)." -ForegroundColor Red
    exit 1
}

if (-not $OutDir) {
    $OutDir = Join-Path $RepoRoot "dist"
}

$StageName  = "JojoBot-v$Version"
$StageDir   = Join-Path $OutDir $StageName
$ZipPath    = Join-Path $OutDir "$StageName.zip"
$InstallerDir = $PSScriptRoot  # ops\installer\

Write-Host ""
Write-Host "=== JoJo Bot Release Builder ===" -ForegroundColor Cyan
Write-Host "Version:      $Version"
Write-Host "Repo root:    $RepoRoot"
Write-Host "Output dir:   $OutDir"
Write-Host "Staging dir:  $StageDir"
Write-Host "Zip path:     $ZipPath"
Write-Host "Dry run:      $(if ($DryRun) { 'YES' } else { 'no' })"
Write-Host ""

# ---- prerequisite helpers ---------------------------------------------------

$prereqOk    = $true
$prereqNotes = [System.Collections.Generic.List[string]]::new()

function Record-Prereq {
    param([bool]$Met, [string]$Label, [string]$Remedy)
    if ($Met) {
        Write-Host "  [ok]   $Label" -ForegroundColor Green
    } else {
        Write-Host "  [FAIL] $Label" -ForegroundColor Red
        Write-Host "         Remedy: $Remedy" -ForegroundColor Yellow
        $script:prereqOk = $false
        $script:prereqNotes.Add("FAIL: $Label -- $Remedy")
    }
}

function Record-Warn {
    param([string]$Label, [string]$Detail)
    Write-Host "  [warn] $Label" -ForegroundColor Yellow
    if ($Detail) { Write-Host "         $Detail" -ForegroundColor DarkGray }
    $script:prereqNotes.Add("WARN: $Label")
}

# ---- 1. Prerequisites check (always run, -DryRun exits here) ----------------
Write-Host "[1/5] Prerequisites" -ForegroundColor Cyan

# 1a. Python 3.11+
$pythonExe = $null
foreach ($candidate in @("python", "py")) {
    if (Get-Command $candidate -ErrorAction SilentlyContinue) {
        $pythonExe = $candidate
        break
    }
}
if (-not $SkipPython) {
    Record-Prereq -Met ($null -ne $pythonExe) `
        -Label "Python on PATH ($($pythonExe))" `
        -Remedy "Install Python 3.11+ from python.org and add to PATH."
    if ($pythonExe) {
        $pyVer = (& $pythonExe --version 2>&1 | Out-String).Trim()
        Write-Host "         Version: $pyVer" -ForegroundColor DarkGray
    }
}

# 1b. PyInstaller (optional -- fallback is pip --target)
# Use Continue to prevent the non-zero exit from a missing module raising a
# terminating error under $ErrorActionPreference = "Stop".
$hasPyInstaller = $false
if ($pythonExe -and -not $SkipPython) {
    $prevEAP = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $pyi = & $pythonExe -m PyInstaller --version 2>&1
    $pyiExit = $LASTEXITCODE
    $ErrorActionPreference = $prevEAP
    $hasPyInstaller = ($pyiExit -eq 0)
    if ($hasPyInstaller) {
        Write-Host "  [ok]   PyInstaller available ($($pyi | Out-String).Trim())" -ForegroundColor Green
    } else {
        Record-Warn -Label "PyInstaller not available -- will fall back to pip --target" `
            -Detail "To use frozen-exe mode: pip install pyinstaller"
    }
}

# 1c. Node / npm for frontend build
$hasNpm = $false
if (-not $SkipFrontend) {
    $hasNpm = $null -ne (Get-Command npm -ErrorAction SilentlyContinue)
    Record-Prereq -Met $hasNpm `
        -Label "npm on PATH" `
        -Remedy "Install Node.js 18+ from nodejs.org and add to PATH."
    if ($hasNpm) {
        $npmVer = (& npm --version 2>&1 | Out-String).Trim()
        Write-Host "         npm version: $npmVer" -ForegroundColor DarkGray
    }
}

# 1d. Frontend source directory exists
$frontendSrc = Join-Path $RepoRoot "src\frontend"
if (-not $SkipFrontend) {
    Record-Prereq -Met (Test-Path $frontendSrc) `
        -Label "Frontend source at src\frontend\" `
        -Remedy "Verify the repo is checked out completely."
}

# 1e. Backend source + pyproject.toml
$backendSrc = Join-Path $RepoRoot "src\backend"
if (-not $SkipPython) {
    Record-Prereq -Met (Test-Path $backendSrc) `
        -Label "Backend source at src\backend\" `
        -Remedy "Verify the repo is checked out completely."
}

# 1f. NSSM bundling (soft requirement -- warn if not found)
$nssmSource = $null
$nssmSearch = @(
    (Join-Path $InstallerDir "nssm.exe"),
    (Join-Path $InstallerDir "nssm\nssm.exe"),
    (Join-Path $RepoRoot "tools\nssm.exe")
)
foreach ($candidate in $nssmSearch) {
    if (Test-Path $candidate) { $nssmSource = $candidate; break }
}
if (-not $nssmSource) {
    $onPath = Get-Command nssm -ErrorAction SilentlyContinue
    if ($onPath) { $nssmSource = $onPath.Source }
}
if ($nssmSource) {
    Write-Host "  [ok]   NSSM bundleable from: $nssmSource" -ForegroundColor Green
} else {
    Record-Warn -Label "nssm.exe not found" `
        -Detail ("Install-Service.ps1 will fall back to sc.exe (no stdout/stderr capture). " +
                 "Place nssm.exe beside this script or in a nssm\ subdirectory to bundle it.")
}

# 1g. Installer scripts present
foreach ($script in @("Install-Service.ps1", "Uninstall-JojoBot.ps1")) {
    $p = Join-Path $InstallerDir $script
    Record-Prereq -Met (Test-Path $p) `
        -Label "Installer script: $script" `
        -Remedy "Run Build-JojoBotRelease.ps1 from ops\installer\ (all scripts must be co-located)."
}

# 1h. OutDir parent is writable (create it if needed -- dry-run only checks parent exists)
$outParent = Split-Path -Parent $OutDir
if ($outParent -and -not (Test-Path $outParent)) {
    Record-Prereq -Met $false `
        -Label "OutDir parent directory exists: $outParent" `
        -Remedy "Create the parent directory or specify a different -OutDir."
} else {
    Write-Host "  [ok]   OutDir parent writable: $(if ($outParent) { $outParent } else { $OutDir })" -ForegroundColor Green
}

Write-Host ""

# ---- Dry-run exit point ------------------------------------------------------
if ($DryRun) {
    Write-Host "=== Dry-run Summary ===" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Would build:  $ZipPath"
    Write-Host "Python mode:  $(if ($SkipPython) { 'skipped' } elseif ($hasPyInstaller) { 'PyInstaller --onedir' } else { 'pip --target (fallback)' })"
    Write-Host "Frontend:     $(if ($SkipFrontend) { 'skipped' } else { 'npm run build + export' })"
    Write-Host "NSSM bundle:  $(if ($nssmSource) { $nssmSource } else { 'not bundled (sc.exe fallback at install time)' })"
    Write-Host ""

    if ($prereqNotes.Count -gt 0) {
        Write-Host "Issues found:" -ForegroundColor Yellow
        foreach ($n in $prereqNotes) { Write-Host "  $n" }
        Write-Host ""
    }

    if ($prereqOk) {
        Write-Host "All prerequisites met. Build would proceed. (exit 0)" -ForegroundColor Green
        exit 0
    } else {
        Write-Host "One or more prerequisites are not met. Fix the FAIL items above. (exit 1)" -ForegroundColor Red
        exit 1
    }
}

# ---- Abort on hard prereq failures (non-dry-run) ----------------------------
if (-not $prereqOk) {
    Write-Host "[error] Prerequisites not met. Re-run with -DryRun for a full list." -ForegroundColor Red
    exit 1
}

# ---- 2. Stage directory setup ------------------------------------------------
Write-Host "[2/5] Staging directory" -ForegroundColor Cyan

if (-not (Test-Path $OutDir)) {
    New-Item -ItemType Directory -Path $OutDir -Force | Out-Null
    Write-Host "  [ok] created: $OutDir" -ForegroundColor Green
}

# Clean any previous staging from the same version.
if (Test-Path $StageDir) {
    Write-Host "  Removing previous staging dir: $StageDir"
    Remove-Item -Recurse -Force -LiteralPath $StageDir
}
New-Item -ItemType Directory -Path $StageDir -Force | Out-Null
Write-Host "  [ok] staging dir ready: $StageDir" -ForegroundColor Green
Write-Host ""

# ---- 3. Python freeze --------------------------------------------------------
Write-Host "[3/5] Python freeze" -ForegroundColor Cyan
$pythonStageDir = Join-Path $StageDir "python"

if ($SkipPython) {
    # Placeholder so the zip structure is consistent.
    New-Item -ItemType Directory -Path $pythonStageDir -Force | Out-Null
    $noteContent = @"
Python freeze was skipped (-SkipPython).

To run JoJo Bot, the install machine needs Python 3.11+ on PATH with the
following packages installed:

  pip install ".[ingest,backend,cloud]"

Then use Install-Service.ps1 -AppPath python.exe -WorkingDir <repo-root>.
"@
    $noteContent | Out-File -FilePath (Join-Path $pythonStageDir "README-no-freeze.txt") -Encoding ASCII
    Write-Host "  [skip] -SkipPython set; placeholder created." -ForegroundColor Yellow

} elseif ($hasPyInstaller) {
    # ---- PRIMARY: PyInstaller --onedir ----------------------------------------
    # This produces:
    #   dist\jojo-server\           <- PyInstaller staging (temporary)
    #     jojo-server.exe
    #     _internal\                <- all .dlls, .pyc, data files
    #
    # We move the entire jojo-server\ tree to our staging python\ directory.
    Write-Host "  Using PyInstaller --onedir mode." -ForegroundColor Cyan

    $pyiBuildSpec  = Join-Path $OutDir "jojo-server-build"
    $pyiDistDir    = Join-Path $OutDir "jojo-server-pyidist"

    # Clean previous PyInstaller artifacts.
    foreach ($p in @($pyiBuildSpec, $pyiDistDir)) {
        if (Test-Path $p) { Remove-Item -Recurse -Force -LiteralPath $p }
    }

    # The --add-data syntax differs between Windows (semicolon) and POSIX (colon).
    # We are on Windows, so use the semicolon form.
    $addDataArg = "src\backend;backend"

    Write-Host "  Running: pyinstaller --onedir --name jojo-server --add-data `"$addDataArg`" src\backend\main.py"
    Push-Location $RepoRoot
    try {
        & $pythonExe -m PyInstaller `
            --onedir `
            --name jojo-server `
            --add-data $addDataArg `
            --distpath $pyiDistDir `
            --workpath $pyiBuildSpec `
            --noconfirm `
            "src\backend\main.py"
        $pyiExit = $LASTEXITCODE
    } finally {
        Pop-Location
    }

    if ($pyiExit -ne 0) {
        Write-Host "[error] PyInstaller exited with $pyiExit." -ForegroundColor Red
        Write-Host "        Check output above. Common causes:"
        Write-Host "          - Missing hidden import: add --hidden-import <module>"
        Write-Host "          - Antivirus quarantine: exclude the dist\ directory"
        Write-Host "          - Encoding issues in a source file"
        exit $pyiExit
    }

    $pyiOutput = Join-Path $pyiDistDir "jojo-server"
    if (-not (Test-Path $pyiOutput)) {
        Write-Host "[error] PyInstaller produced no output at $pyiOutput." -ForegroundColor Red
        exit 1
    }

    # Move PyInstaller output into our staging python\ directory.
    Move-Item -LiteralPath $pyiOutput -Destination $pythonStageDir -Force

    Write-Host "  [ok] frozen exe staged at $pythonStageDir" -ForegroundColor Green

    # Clean PyInstaller temp dirs.
    foreach ($p in @($pyiBuildSpec, $pyiDistDir)) {
        if (Test-Path $p) { Remove-Item -Recurse -Force -LiteralPath $p -ErrorAction SilentlyContinue }
    }

} else {
    # ---- FALLBACK: pip --target -----------------------------------------------
    # Copies all packages as plain Python source into python\. The install site
    # needs Python 3.11+ on PATH. Install-Service.ps1 is called with
    # -AppPath python.exe and -WorkingDir pointing at this directory's parent.
    Write-Host "  PyInstaller not available. Falling back to pip --target." -ForegroundColor Yellow
    Write-Host "  Note: install machine requires Python 3.11+ on PATH." -ForegroundColor Yellow

    New-Item -ItemType Directory -Path $pythonStageDir -Force | Out-Null

    Push-Location $RepoRoot
    try {
        Write-Host "  Running: pip install -e `".[ingest,backend,cloud]`" --target $pythonStageDir"
        & $pythonExe -m pip install -e ".[ingest,backend,cloud]" --target $pythonStageDir
        $pipExit = $LASTEXITCODE
    } finally {
        Pop-Location
    }

    if ($pipExit -ne 0) {
        Write-Host "[error] pip install failed with exit $pipExit." -ForegroundColor Red
        exit $pipExit
    }

    # Leave a README explaining the fallback.
    $noteContent = @"
FALLBACK INSTALL MODE: pip --target (no frozen exe)
====================================================
PyInstaller was not available when this zip was built. The python\ directory
contains all Python packages as plain files, NOT a self-contained executable.

The install machine requires Python 3.11+ on PATH.

Install-Service.ps1 will detect this mode automatically when AppPath is set to
a python.exe (not jojo-server.exe) and will pass the correct -m uvicorn arguments.
"@
    $noteContent | Out-File -FilePath (Join-Path $pythonStageDir "README-fallback.txt") -Encoding ASCII
    Write-Host "  [ok] packages staged at $pythonStageDir (pip --target fallback)" -ForegroundColor Green
}

Write-Host ""

# ---- 4. Frontend build -------------------------------------------------------
Write-Host "[4/5] Frontend build" -ForegroundColor Cyan
$frontendStageDir = Join-Path $StageDir "frontend"

if ($SkipFrontend) {
    # Check for pre-existing out\ directory from a prior build.
    $frontendOut = Join-Path $frontendSrc "out"
    if (Test-Path $frontendOut) {
        Write-Host "  -SkipFrontend set; using existing out\ from $frontendOut" -ForegroundColor Yellow
        New-Item -ItemType Directory -Path $frontendStageDir -Force | Out-Null
        Copy-Item -Recurse -Force -LiteralPath $frontendOut -Destination $frontendStageDir
        Write-Host "  [ok] frontend staged from existing out\ directory." -ForegroundColor Green
    } else {
        New-Item -ItemType Directory -Path $frontendStageDir -Force | Out-Null
        "[skip] -SkipFrontend set and no out\ directory found. Frontend not included." |
            Out-File -FilePath (Join-Path $frontendStageDir "frontend-missing.txt") -Encoding ASCII
        Write-Host "  [skip] no out\ found; placeholder created." -ForegroundColor Yellow
    }
} else {
    # Run npm run build.
    $frontendOut = Join-Path $frontendSrc "out"
    Write-Host "  Running: npm run build (in $frontendSrc)"
    Push-Location $frontendSrc
    try {
        & npm run build
        $npmBuildExit = $LASTEXITCODE
    } finally {
        Pop-Location
    }

    if ($npmBuildExit -ne 0) {
        Write-Host "[error] npm run build exited with $npmBuildExit." -ForegroundColor Red
        Write-Host "        Fix the build errors above and retry, or use -SkipFrontend."
        exit $npmBuildExit
    }

    # Check if the build produced an out\ directory (requires output: 'export' in next.config.js).
    if (Test-Path $frontendOut) {
        New-Item -ItemType Directory -Path $frontendStageDir -Force | Out-Null
        Copy-Item -Recurse -Force -LiteralPath $frontendOut -Destination $frontendStageDir
        Write-Host "  [ok] frontend staged from $frontendOut" -ForegroundColor Green
    } else {
        # next.config.js uses rewrites(), which is incompatible with static export.
        # The frontend is currently a dev-server app, not a static export. Write a note.
        New-Item -ItemType Directory -Path $frontendStageDir -Force | Out-Null
        $noteFile = Join-Path $OutDir "frontend-build-note.txt"
        $buildNote = @"
FRONTEND STATIC EXPORT NOT CONFIGURED
======================================
Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm')
Version: $Version

'npm run build' succeeded, but no out\ directory was produced.

Root cause:
  src\frontend\next.config.js uses rewrites(), which disables static export in
  Next.js. The next export command (or output: 'export' config option) requires
  that no server-side features (rewrites, headers, API routes) are used.

Impact:
  The zip's frontend\ directory is empty. The JoJo Bot backend at
  http://localhost:8765/ will NOT serve the UI automatically.

Manual resolution (frontend agent task):
  1. Update src\frontend\next.config.js to add: output: 'export'
  2. Remove the rewrites() block (or gate it on process.env.NODE_ENV === 'development').
  3. Re-run Build-JojoBotRelease.ps1 or: npm run build (produces out\).
  4. Update the backend (src\backend\main.py) to mount the out\ directory at '/'
     using StaticFiles so the React app is served by FastAPI directly.
  5. The API rewrite in next.config.js assumes port 8000; the service runs on 8765.
     Update the port in next.config.js or the backend rewrites accordingly.

Until this is resolved, users can still access the backend API at
http://localhost:8765/api/ and the docs at http://localhost:8765/docs.
"@
        $buildNote | Out-File -FilePath $noteFile -Encoding ASCII
        $buildNote | Out-File -FilePath (Join-Path $frontendStageDir "frontend-build-note.txt") -Encoding ASCII
        Write-Host "  [warn] No out\ directory produced; static export not configured." -ForegroundColor Yellow
        Write-Host "         Note written to: $noteFile" -ForegroundColor Yellow
    }
}

Write-Host ""

# ---- 5. Assemble the zip staging directory -----------------------------------
Write-Host "[5/5] Assemble and zip" -ForegroundColor Cyan

# 5a. Copy installer scripts.
$scriptsToBundle = @(
    "Install-Service.ps1",
    "Uninstall-JojoBot.ps1"
)
foreach ($s in $scriptsToBundle) {
    $src = Join-Path $InstallerDir $s
    if (Test-Path $src) {
        Copy-Item -LiteralPath $src -Destination $StageDir -Force
        Write-Host "  [ok] bundled $s" -ForegroundColor Green
    } else {
        Write-Host "  [warn] $s not found at $src; skipping." -ForegroundColor Yellow
    }
}

# 5b. Bundle NSSM if found.
if ($nssmSource) {
    Copy-Item -LiteralPath $nssmSource -Destination $StageDir -Force
    Write-Host "  [ok] bundled nssm.exe from $nssmSource" -ForegroundColor Green
} else {
    Write-Host "  [note] nssm.exe not bundled; Install-Service.ps1 will use sc.exe fallback." -ForegroundColor DarkGray
}

# 5c. Generate the end-user Install-JojoBot.ps1 entry-point script.
# This is a thin wrapper: it finds the jojo-server.exe (or python.exe fallback)
# and calls Install-Service.ps1. It does NOT use the developer installer.
$endUserInstall = @'
#Requires -RunAsAdministrator
<#
.SYNOPSIS
    JoJo Bot end-user installer. Registers the service and opens the welcome page.

.DESCRIPTION
    Run this script after extracting the JoJo Bot zip to install the Windows
    Service and open http://localhost:8765/welcome in your browser.

    Steps performed:
      1. Locate jojo-server.exe (frozen) or detect Python mode (fallback zip).
      2. Ensure %APPDATA%\JojoBot\ config directory exists.
      3. Call Install-Service.ps1 to register the Windows Service.
      4. Start the service.
      5. Open http://localhost:8765/welcome in the default browser.

    Requires administrator privileges (service registration). The
    #Requires -RunAsAdministrator directive causes PowerShell to prompt for
    elevation automatically when the script is right-clicked and run.
    Safe to re-run; existing service is skipped unless -Force is passed.

.PARAMETER Force
    Pass -Force to Install-Service.ps1 (removes and re-registers the service).

.PARAMETER BindAddress
    Bind address for the backend. Default: 127.0.0.1 (localhost only).
    Use 0.0.0.0 for LAN access (department projector workstations only).

.PARAMETER Port
    Backend port. Default: 8765.

.NOTES
    All strings are pure ASCII (codepoints <= 127).
#>

[CmdletBinding()]
param(
    [switch]$Force,
    [string]$BindAddress = "127.0.0.1",
    [int]$Port = 8765
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "=== JoJo Bot v__VERSION__ Installer ===" -ForegroundColor Cyan
Write-Host ""

$InstallDir = $PSScriptRoot

# ---- locate the server executable ----------------------------------------
$frozenExe  = Join-Path $InstallDir "python\jojo-server.exe"
$fallbackPy = $null

if (Test-Path $frozenExe) {
    $AppPath = $frozenExe
    Write-Host "[ok] found frozen exe: $AppPath" -ForegroundColor Green
} else {
    Write-Host "[info] jojo-server.exe not found; checking for Python fallback..." -ForegroundColor Cyan
    foreach ($candidate in @("python", "py")) {
        if (Get-Command $candidate -ErrorAction SilentlyContinue) {
            $fallbackPy = (Get-Command $candidate).Source
            break
        }
    }
    if (-not $fallbackPy) {
        Write-Host "[error] Neither jojo-server.exe nor python.exe found." -ForegroundColor Red
        Write-Host "        Install Python 3.11+ from python.org and add it to PATH, then re-run."
        exit 1
    }
    $AppPath    = $fallbackPy
    $WorkingDir = $InstallDir
    Write-Host "[warn] Using Python fallback mode: $fallbackPy" -ForegroundColor Yellow
    Write-Host "       The python\ directory must have the JoJo Bot packages installed."
}

# ---- ensure config directory exists --------------------------------------
$configDir = Join-Path $env:APPDATA "JojoBot"
if (-not (Test-Path $configDir)) {
    New-Item -ItemType Directory -Path $configDir -Force | Out-Null
    Write-Host "[ok] created config directory: $configDir" -ForegroundColor Green
} else {
    Write-Host "[ok] config directory exists: $configDir" -ForegroundColor Green
}

# ---- call Install-Service.ps1 --------------------------------------------
$serviceScript = Join-Path $InstallDir "Install-Service.ps1"
if (-not (Test-Path $serviceScript)) {
    Write-Host "[error] Install-Service.ps1 not found at $serviceScript." -ForegroundColor Red
    exit 1
}

$svcArgs = @(
    "-AppPath", $AppPath,
    "-BindAddress", $BindAddress,
    "-Port", $Port,
    "-StartImmediately"
)
if ($WorkingDir) { $svcArgs += @("-WorkingDir", $WorkingDir) }
if ($Force)      { $svcArgs += @("-Force") }

Write-Host ""
Write-Host "[info] Registering Windows Service..." -ForegroundColor Cyan
& $serviceScript @svcArgs
if ($LASTEXITCODE -ne 0) {
    Write-Host "[error] Install-Service.ps1 failed with exit $LASTEXITCODE." -ForegroundColor Red
    exit $LASTEXITCODE
}

# ---- open the welcome page -----------------------------------------------
Write-Host ""
Write-Host "[info] Waiting for backend to start..." -ForegroundColor Cyan
Start-Sleep -Seconds 5

$welcomeUrl = "http://${BindAddress}:${Port}/welcome"
Write-Host "[ok] Opening $welcomeUrl in your default browser." -ForegroundColor Green
Start-Process $welcomeUrl

Write-Host ""
Write-Host "=== Installation complete ===" -ForegroundColor Green
Write-Host "JoJo Bot is running at http://$BindAddress`:$Port/"
Write-Host "Welcome page: $welcomeUrl"
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Paste your Anthropic API key in the Settings tab."
Write-Host "  2. Confirm connector paths (OneDrive, Public Drive) in Settings."
Write-Host "  3. Run your first ingest from the Ingest tab."
Write-Host ""
Write-Host "To stop the service:       Stop-Service JojoBot"
Write-Host "To uninstall:              Right-click Uninstall-JojoBot.ps1 -> Run with PowerShell"
Write-Host ""
'@

# Substitute the version placeholder.
$endUserInstall = $endUserInstall -replace '__VERSION__', $Version

$endUserInstallPath = Join-Path $StageDir "Install-JojoBot.ps1"
$endUserInstall | Out-File -FilePath $endUserInstallPath -Encoding ASCII
Write-Host "  [ok] generated Install-JojoBot.ps1 (end-user entry point)" -ForegroundColor Green

# 5d. Write README.txt.
$readmeContent = @"
JoJo Bot v$Version -- Quick Start
================================================

INSTALL
  1. Right-click Install-JojoBot.ps1 and select 'Run with PowerShell'.
     (If prompted about execution policy, click 'Open' or 'Run anyway'.)
  2. The script will:
       a. Register the JoJo Bot Windows Service (auto-starts on boot).
       b. Open http://localhost:8765/welcome in your browser.

  Admin privileges are required for service registration. The script will
  prompt for elevation if needed.

FIRST-TIME SETUP
  1. In the welcome page, paste your Anthropic API key into the Settings tab.
  2. Confirm the connector paths (OneDrive folder, P:\ drive) in Settings.
  3. Click 'Run Ingest' to build the knowledge base.

DAILY USE
  Open your browser to http://localhost:8765/
  The service starts automatically when Windows boots.

UNINSTALL
  Right-click Uninstall-JojoBot.ps1 and select 'Run with PowerShell'.
  Your config and knowledge base are kept unless you choose to delete them.

TROUBLESHOOTING
  Service not running:   Start-Service JojoBot
  Check logs:            Get-Content "$env:ProgramData\JojoBot\logs\stderr.log" -Tail 50
  Re-install service:    .\Install-Service.ps1 -AppPath .\python\jojo-server.exe -Force

SECURITY NOTE
  The config file at %APPDATA%\JojoBot\config.json is DPAPI-encrypted using the
  machine key. Anyone with local admin on this workstation can decrypt it.
  This is acceptable for a shared department workstation; do not store
  highly sensitive credentials beyond what the tool requires.

FOOTPRINT
  Service:   Windows Service 'JojoBot' (port 8765, localhost-only by default)
  Config:    %APPDATA%\JojoBot\config.json
  Logs:      %ProgramData%\JojoBot\logs\
  Build:     $Version ($(Get-Date -Format 'yyyy-MM-dd'))

SUPPORT
  docs\ops\distribution.md -- full operations guide
  https://nurix internal SharePoint -- submit a request to Mateo de los Rios
"@

$readmeContent | Out-File -FilePath (Join-Path $StageDir "README.txt") -Encoding ASCII
Write-Host "  [ok] README.txt written" -ForegroundColor Green

# ---- Create the zip ----------------------------------------------------------
Write-Host ""
Write-Host "  Compressing to: $ZipPath" -ForegroundColor Cyan

# Remove existing zip for this version if present.
if (Test-Path $ZipPath) {
    Remove-Item -LiteralPath $ZipPath -Force
}

Compress-Archive -LiteralPath $StageDir -DestinationPath $ZipPath -CompressionLevel Optimal
Write-Host "  [ok] zip created: $ZipPath" -ForegroundColor Green

# ---- Size report -------------------------------------------------------------
$zipInfo = Get-Item $ZipPath
$zipMB   = [math]::Round($zipInfo.Length / 1MB, 1)
Write-Host "  Zip size: $zipMB MB" -ForegroundColor DarkGray

# ---- Optional cleanup -------------------------------------------------------
if (-not $KeepIntermediate) {
    Remove-Item -Recurse -Force -LiteralPath $StageDir -ErrorAction SilentlyContinue
    Write-Host "  [ok] staging directory cleaned up." -ForegroundColor Green
} else {
    Write-Host "  [note] staging directory kept at: $StageDir (-KeepIntermediate)" -ForegroundColor DarkGray
}

Write-Host ""
Write-Host "=== Build complete ===" -ForegroundColor Green
Write-Host "  Artifact:  $ZipPath ($zipMB MB)"
Write-Host "  Version:   $Version"
Write-Host ""
Write-Host "Distribute $ZipPath to department staff." -ForegroundColor Cyan
Write-Host "See docs\ops\distribution.md for the full operations runbook." -ForegroundColor Cyan
Write-Host ""
