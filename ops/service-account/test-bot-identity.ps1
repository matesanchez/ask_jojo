# test-bot-identity.ps1
#
# Smoke test for bot-identity.ps1. Creates a throwaway git repo in
# $env:TEMP, makes a bot commit, asserts the author matches, and
# cleans up. Run this before installing any scheduled task that
# depends on the overlay.
#
#   .\test-bot-identity.ps1

$ErrorActionPreference = 'Stop'

. "$PSScriptRoot\bot-identity.ps1"

$testDir = Join-Path $env:TEMP "jojo-bot-identity-test-$([guid]::NewGuid().ToString('N').Substring(0,8))"
Write-Host "Creating test repo at $testDir"
New-Item -ItemType Directory -Path $testDir -Force | Out-Null

try {
    Push-Location $testDir
    try {
        git init -b main -q
        if ($LASTEXITCODE -ne 0) { throw "git init failed ($LASTEXITCODE)" }

        # Seed file so the commit has something to include.
        Set-Content -Path "seed.txt" -Value "seed for bot-identity test at $(Get-Date -Format o)"
        git add seed.txt
        if ($LASTEXITCODE -ne 0) { throw "git add failed ($LASTEXITCODE)" }
    } finally {
        Pop-Location
    }

    Invoke-BotCommit -RepoPath $testDir -Message "absorb(test): smoke test for bot identity"

    $ok = Assert-BotIdentity -RepoPath $testDir -Sha HEAD

    if ($ok) {
        Write-Host "PASS: bot identity commits with author $BOT_NAME <$BOT_EMAIL>" -ForegroundColor Green
        exit 0
    } else {
        Write-Host "FAIL: Assert-BotIdentity returned non-true without throwing" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "FAIL: $_" -ForegroundColor Red
    exit 2
} finally {
    # Cleanup
    if (Test-Path $testDir) {
        Remove-Item -Recurse -Force -Path $testDir -ErrorAction SilentlyContinue
    }
}
