<#
.SYNOPSIS
    Build JoJo Bot as a standalone double-click Windows exe.
    Output: dist\JojoBot\JojoBot.exe (+ _internal\ folder)

.DESCRIPTION
    Produces a self-contained double-click exe. The user copies the JojoBot\
    folder anywhere and double-clicks JojoBot.exe. No Python installation needed.

    The exe starts a local FastAPI server on port 8766 and opens the browser.
    The wiki and raw data directories must be present as siblings or configured
    via %APPDATA%\JojoBot\config.json.

.PARAMETER SkipFrontend
    Skip npm run build (use existing src\frontend\out\).

.PARAMETER RepoRoot
    Path to ask_jojo directory. Auto-detected from script location.

.EXAMPLE
    .\Build-JojoExe.ps1
    .\Build-JojoExe.ps1 -SkipFrontend
#>
param(
    [switch]$SkipFrontend,
    [string]$RepoRoot
)

$ErrorActionPreference = "Stop"

if (-not $RepoRoot) {
    $RepoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
}
$RepoRoot = (Resolve-Path $RepoRoot).Path

Write-Host ""
Write-Host "=== JoJo Bot Exe Builder ===" -ForegroundColor Cyan
Write-Host "Repo root: $RepoRoot"
Write-Host ""

# ---- 1. Prerequisites -------------------------------------------------------
Write-Host "[1/3] Checking prerequisites..." -ForegroundColor Cyan

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

# ---- 2. Frontend build -------------------------------------------------------
Write-Host "[2/3] Frontend build..." -ForegroundColor Cyan
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

# ---- 3. PyInstaller ---------------------------------------------------------
Write-Host "[3/3] Running PyInstaller..." -ForegroundColor Cyan
$specFile = Join-Path $PSScriptRoot "JojoBot.spec"

Push-Location $RepoRoot
try {
    & $python -m PyInstaller $specFile --noconfirm
    if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed with exit $LASTEXITCODE" }
} finally {
    Pop-Location
}

$distExe = Join-Path $RepoRoot "dist\JojoBot\JojoBot.exe"
if (-not (Test-Path $distExe)) {
    Write-Host "[error] JojoBot.exe not found at $distExe." -ForegroundColor Red
    exit 1
}

$dirMB = [math]::Round(
    (Get-ChildItem -Recurse (Join-Path $RepoRoot "dist\JojoBot") | Measure-Object -Property Length -Sum).Sum / 1MB, 1
)

Write-Host ""
Write-Host "=== Build complete ===" -ForegroundColor Green
Write-Host "  Exe:   $distExe"
Write-Host "  Size:  $dirMB MB (full JojoBot\ folder)"
Write-Host ""
Write-Host "To run: double-click $distExe" -ForegroundColor Cyan
Write-Host "Or copy the entire dist\JojoBot\ folder to any machine." -ForegroundColor DarkGray
Write-Host ""
