# bot-identity.ps1
#
# Dot-source this script from any scheduled-task entry point that needs
# to commit as the jojo-bot service identity.
#
#   . $PSScriptRoot\..\ops\service-account\bot-identity.ps1
#
# Exports:
#   $BOT_NAME, $BOT_EMAIL                 - identity strings
#   Invoke-BotCommit -RepoPath -Message   - commits as the bot
#   Assert-BotIdentity -RepoPath -Sha     - verifies a commit was authored by the bot
#
# See docs/ADR/0005-jojo-bot-service-account.md for the decision record,
# and ops/service-account/README.md for the operational context.

$Script:BOT_NAME  = "jojo-bot"
$Script:BOT_EMAIL = "jojo-bot@nurixtx.com"

# Expose at script scope for dot-sourcing callers.
$BOT_NAME  = $Script:BOT_NAME
$BOT_EMAIL = $Script:BOT_EMAIL

function Invoke-BotCommit {
    <#
    .SYNOPSIS
    Commit staged changes in a repo as the jojo-bot service identity.

    .PARAMETER RepoPath
    Absolute or relative path to the git repository working directory.

    .PARAMETER Message
    The commit message. Should follow schema/CLAUDE.md section 9 prefixes
    (absorb:, lint:, checkpoint:). NEVER use [manual] here -- that is
    reserved for human emergency overrides and must not come from a
    scheduled task.

    .PARAMETER AllowEmpty
    If set, passes --allow-empty to git commit. Defaults to false
    because empty commits from automated runs usually indicate a bug.

    .EXAMPLE
    Invoke-BotCommit -RepoPath "C:\...\ask_jojo_wiki" -Message "absorb(protein-sciences): 3 pages touched"
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$RepoPath,

        [Parameter(Mandatory = $true)]
        [string]$Message,

        [switch]$AllowEmpty
    )

    if (-not (Test-Path -Path $RepoPath -PathType Container)) {
        throw "Invoke-BotCommit: RepoPath '$RepoPath' does not exist or is not a directory."
    }

    # Reject the manual-override prefix; bots must never claim manual status.
    if ($Message -match '^\s*\[manual\]') {
        throw "Invoke-BotCommit: commit message uses [manual] prefix, which is reserved for human overrides. Use absorb:, lint:, or checkpoint: instead."
    }

    $extraArgs = @()
    if ($AllowEmpty) { $extraArgs += '--allow-empty' }

    Push-Location $RepoPath
    try {
        # -c flags apply for this invocation only; no global state is touched.
        git -c "user.name=$Script:BOT_NAME" `
            -c "user.email=$Script:BOT_EMAIL" `
            commit @extraArgs -m $Message
        if ($LASTEXITCODE -ne 0) {
            throw "Invoke-BotCommit: git commit failed with exit code $LASTEXITCODE."
        }
    } finally {
        Pop-Location
    }
}

function Assert-BotIdentity {
    <#
    .SYNOPSIS
    Verify that a given commit SHA was authored by the jojo-bot identity.

    .PARAMETER RepoPath
    Path to the git repository.

    .PARAMETER Sha
    The commit SHA to inspect. Defaults to HEAD.

    .OUTPUTS
    Throws on mismatch; returns $true on match.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$RepoPath,
        [string]$Sha = "HEAD"
    )

    Push-Location $RepoPath
    try {
        $authorName  = git log -1 --format='%an' $Sha
        $authorEmail = git log -1 --format='%ae' $Sha
    } finally {
        Pop-Location
    }

    if ($authorName -ne $Script:BOT_NAME -or $authorEmail -ne $Script:BOT_EMAIL) {
        throw "Assert-BotIdentity: commit $Sha authored by '$authorName <$authorEmail>', expected '$Script:BOT_NAME <$Script:BOT_EMAIL>'."
    }
    return $true
}

# If dot-sourced, the functions and $BOT_NAME / $BOT_EMAIL are now available in the caller's scope.
