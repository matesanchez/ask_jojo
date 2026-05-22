<#
.SYNOPSIS
    Build JoJo Bot as a standalone desktop application (double-click .exe).
    Output: dist\JojoBot\JojoBot.exe (+ _internal\, wiki\, raw\)

.DESCRIPTION
    Produces a self-contained desktop app. The user copies the JojoBot\ folder
    anywhere and double-clicks JojoBot.exe. No Python, Node, or browser needed.

    The app opens in a native Qt window (PySide6 QWebEngineView). It bundles
    the Next.js frontend, all Python packages, the ask_jojo_wiki knowledge base,
    and optionally the ask_jojo_raw source documents.

    Folder layout after build:
        dist\JojoBot\
            JojoBot.exe          <- double-click to launch
            _internal\           <- Python runtime + Qt DLLs (do not move)
            wiki\                <- ask_jojo_wiki snapshot (Q&A memory)
            raw\                 <- ask_jojo_raw source documents (omit -SkipRaw to include)
            README.txt

.PARAMETER SkipFrontend
    Skip npm run build (use existing src\frontend\out\).

.PARAMETER SkipRaw
    Omit the raw\ folder from the output (wiki is always included).
    Use this to produce a smaller package when recipients already have
    their own raw data or only need Q&A/chat features.

.PARAMETER WikiRoot
    Path to the ask_jojo_wiki directory. Defaults to ..\ask_jojo_wiki relative
    to the repo root.

.PARAMETER RawRoot
    Path to the ask_jojo_raw directory. Defaults to ..\ask_jojo_raw relative
    to the repo root.

.PARAMETER RepoRoot
    Path to the ask_jojo directory. Auto-detected from script location.

.EXAMPLE
    # Full build including raw files
    .\Build-JojoExe.ps1

    # Wiki only (smaller, faster copy)
    .\Build-JojoExe.ps1 -SkipRaw

    # Skip frontend rebuild if out\ already exists
    .\Build-JojoExe.ps1 -SkipFrontend -SkipRaw
#>
param(
    [switch]$SkipFrontend,
    [switch]$SkipRaw,
    [string]$WikiRoot,
    [string]$RawRoot,
    [string]$RepoRoot
)

$ErrorActionPreference = "Stop"

if (-not $RepoRoot) {
    $RepoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
}
$RepoRoot = (Resolve-Path $RepoRoot).Path

# Default wiki/raw paths are siblings of the repo root
if (-not $WikiRoot) { $WikiRoot = Join-Path $RepoRoot "..\ask_jojo_wiki" }
if (-not $RawRoot)  { $RawRoot  = Join-Path $RepoRoot "..\ask_jojo_raw" }

Write-Host ""
Write-Host "=== JoJo Bot Desktop App Builder ===" -ForegroundColor Cyan
Write-Host "Repo root:  $RepoRoot"
Write-Host "Wiki root:  $WikiRoot"
if (-not $SkipRaw) { Write-Host "Raw root:   $RawRoot" } else { Write-Host "Raw root:   (skipped)" -ForegroundColor DarkGray }
Write-Host ""

# ---- 1. Prerequisites --------------------------------------------------------
Write-Host "[1/4] Checking prerequisites..." -ForegroundColor Cyan

$python = $null
foreach ($c in @("python", "py")) {
    if (Get-Command $c -ErrorAction SilentlyContinue) { $python = $c; break }
}
if (-not $python) { Write-Host "[error] Python not found on PATH." -ForegroundColor Red; exit 1 }

$prevEAP = $ErrorActionPreference; $ErrorActionPreference = "Continue"
$pyiVer = & $python -m PyInstaller --version 2>&1
$pyiOk = ($LASTEXITCODE -eq 0)
$ErrorActionPreference = $prevEAP

if (-not $pyiOk) {
    Write-Host "[error] PyInstaller not installed. Run: pip install pyinstaller" -ForegroundColor Red
    exit 1
}
Write-Host "  [ok] PyInstaller $(($pyiVer | Out-String).Trim())" -ForegroundColor Green

# Verify PySide6 is installed (required for the Qt window)
$prevEAP = $ErrorActionPreference; $ErrorActionPreference = "Continue"
$pyside6Check = & $python -c "from PySide6.QtWebEngineWidgets import QWebEngineView; print('ok')" 2>&1
$ErrorActionPreference = $prevEAP
if ($pyside6Check -ne "ok") {
    Write-Host "[error] PySide6 not installed or QWebEngineView missing." -ForegroundColor Red
    Write-Host "        Run: pip install PySide6" -ForegroundColor Yellow
    exit 1
}
Write-Host "  [ok] PySide6 QWebEngineView available" -ForegroundColor Green

# ---- 2. Frontend build -------------------------------------------------------
Write-Host "[2/4] Frontend build..." -ForegroundColor Cyan
$frontendSrc = Join-Path $RepoRoot "src\frontend"
$frontendOut = Join-Path $frontendSrc "out"

if ($SkipFrontend -and (Test-Path $frontendOut)) {
    Write-Host "  [skip] Using existing out\ directory." -ForegroundColor Yellow
} else {
    if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
        Write-Host "[error] npm not found. Install Node.js 18+ from nodejs.org." -ForegroundColor Red
        exit 1
    }
    Write-Host "  Running: npm run build"
    Push-Location $frontendSrc
    try {
        & npm run build
        if ($LASTEXITCODE -ne 0) { throw "npm run build failed" }
    } finally {
        Pop-Location
    }
    if (-not (Test-Path $frontendOut)) {
        Write-Host "[error] npm build completed but out\ not produced." -ForegroundColor Red
        exit 1
    }
    Write-Host "  [ok] Frontend built: $frontendOut" -ForegroundColor Green
}

# ---- 3. PyInstaller ----------------------------------------------------------
Write-Host "[3/4] Running PyInstaller..." -ForegroundColor Cyan
$specFile = Join-Path $PSScriptRoot "JojoBot.spec"

Push-Location $RepoRoot
try {
    $prevEAP2 = $ErrorActionPreference; $ErrorActionPreference = "Continue"
    & $python -m PyInstaller $specFile --noconfirm
    $pyiExit = $LASTEXITCODE
    $ErrorActionPreference = $prevEAP2
    if ($pyiExit -ne 0) { throw "PyInstaller failed with exit $pyiExit" }
} finally {
    Pop-Location
}

$distExe = Join-Path $RepoRoot "dist\JojoBot\JojoBot.exe"
if (-not (Test-Path $distExe)) {
    Write-Host "[error] JojoBot.exe not found at $distExe." -ForegroundColor Red
    exit 1
}
Write-Host "  [ok] JojoBot.exe produced" -ForegroundColor Green

# ---- 4. Copy knowledge base (wiki + raw) ------------------------------------
Write-Host "[4/4] Copying knowledge base..." -ForegroundColor Cyan
$distDir = Join-Path $RepoRoot "dist\JojoBot"

# Wiki (always included — this IS the Q&A memory, ~1 MB)
$wikiResolved = $null
try { $wikiResolved = (Resolve-Path $WikiRoot -ErrorAction Stop).Path } catch {}
if ($wikiResolved -and (Test-Path $wikiResolved)) {
    $wikiDst = Join-Path $distDir "wiki"
    Write-Host "  Copying wiki ($wikiResolved) ..."
    if (Test-Path $wikiDst) { Remove-Item $wikiDst -Recurse -Force }
    Copy-Item $wikiResolved $wikiDst -Recurse
    $wikiMB = [math]::Round(
        (Get-ChildItem $wikiDst -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB, 1
    )
    Write-Host "  [ok] Wiki copied ($wikiMB MB) → $wikiDst" -ForegroundColor Green
} else {
    Write-Host "  [warn] ask_jojo_wiki not found at '$WikiRoot' — skipping" -ForegroundColor Yellow
    Write-Host "         Q&A will work but wiki pages will be empty." -ForegroundColor DarkGray
}

# Raw files (optional; can be large — 10-50+ GB)
if (-not $SkipRaw) {
    $rawResolved = $null
    try { $rawResolved = (Resolve-Path $RawRoot -ErrorAction Stop).Path } catch {}
    if ($rawResolved -and (Test-Path $rawResolved)) {
        $rawDst = Join-Path $distDir "raw"
        $rawFileCount = (Get-ChildItem $rawResolved -Recurse -File | Measure-Object).Count
        $rawGB = [math]::Round(
            (Get-ChildItem $rawResolved -Recurse | Measure-Object -Property Length -Sum).Sum / 1GB, 2
        )
        Write-Host "  Copying raw files ($rawGB GB, $rawFileCount files) — this may take several minutes ..."
        Write-Host "  Source: $rawResolved"
        if (Test-Path $rawDst) { Remove-Item $rawDst -Recurse -Force }
        Copy-Item $rawResolved $rawDst -Recurse
        Write-Host "  [ok] Raw files copied ($rawGB GB) → $rawDst" -ForegroundColor Green
    } else {
        Write-Host "  [warn] ask_jojo_raw not found at '$RawRoot' — skipping" -ForegroundColor Yellow
        Write-Host "         Raw tab will be empty; use -RawRoot to specify a different path." -ForegroundColor DarkGray
    }
} else {
    Write-Host "  [skip] Raw files omitted (-SkipRaw)" -ForegroundColor DarkGray
}

# Place README next to JojoBot.exe
$readmeSrc = Join-Path $PSScriptRoot "README.txt"
if (Test-Path $readmeSrc) {
    Copy-Item $readmeSrc (Join-Path $distDir "README.txt") -Force
    Write-Host "  [ok] README.txt placed" -ForegroundColor Green
}

# ---- Summary -----------------------------------------------------------------
$totalMB = [math]::Round(
    (Get-ChildItem $distDir -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB, 0
)

Write-Host ""
Write-Host "=== Build complete ===" -ForegroundColor Green
Write-Host "  App:   $distExe"
Write-Host "  Total: $totalMB MB (full JojoBot\ folder)"
Write-Host ""
Write-Host "To run:  double-click $distExe" -ForegroundColor Cyan
Write-Host "To share: zip the entire dist\JojoBot\ folder and send it." -ForegroundColor DarkGray
Write-Host ""
Write-Host "  Logs (if the app fails to open): %LOCALAPPDATA%\JojoBot\launcher.log" -ForegroundColor DarkGray
Write-Host ""
