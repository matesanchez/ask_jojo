# bot-commit.ps1
#
# Standalone wrapper around Invoke-BotCommit for callers that prefer to
# spawn a PowerShell process rather than dot-source bot-identity.ps1.
#
#   bot-commit.ps1 -Repo <path> -Message "<msg>" [-Files "<glob>[,<glob>...]"] [-StagedOnly]
#
# Use -Files to stage specific files before committing. Use -StagedOnly
# to commit whatever is already staged. Specify exactly one.
#
# See docs/ADR/0005-jojo-bot-service-account.md and README.md in this directory.

[CmdletBinding(DefaultParameterSetName = 'Files')]
param(
    [Parameter(Mandatory = $true)]
    [string]$Repo,

    [Parameter(Mandatory = $true)]
    [string]$Message,

    [Parameter(ParameterSetName = 'Files', Mandatory = $true)]
    [string]$Files,

    [Parameter(ParameterSetName = 'StagedOnly', Mandatory = $true)]
    [switch]$StagedOnly,

    [switch]$AllowEmpty
)

$ErrorActionPreference = 'Stop'

# Load the identity functions.
. "$PSScriptRoot\bot-identity.ps1"

if (-not (Test-Path -Path $Repo -PathType Container)) {
    throw "bot-commit: Repo '$Repo' does not exist."
}

# Stage files if requested.
if ($PSCmdlet.ParameterSetName -eq 'Files') {
    Push-Location $Repo
    try {
        $globs = $Files -split ','
        foreach ($g in $globs) {
            $g = $g.Trim()
            if ($g) {
                git add -- $g
                if ($LASTEXITCODE -ne 0) {
                    throw "bot-commit: git add '$g' failed (exit $LASTEXITCODE)."
                }
            }
        }
    } finally {
        Pop-Location
    }
}

# Commit with the bot identity.
$invokeParams = @{
    RepoPath = $Repo
    Message  = $Message
}
if ($AllowEmpty) { $invokeParams.AllowEmpty = $true }

Invoke-BotCommit @invokeParams

Write-Host "bot-commit: committed to $Repo as $BOT_NAME <$BOT_EMAIL>."
