# Phase 7b — Provisioning the `jojo-bot` GitHub App

This document describes the GitHub App setup for Phase 7b (shared Nurix-internal server). **Do not execute these steps during Phases 0–6.** The git-identity overlay in `bot-identity.ps1` is sufficient for local mode.

When Phase 7b kicks off, this document is the runbook: follow it exactly, check off each step, and file any deviations as a new ADR.

## Why a GitHub App in Phase 7b

- Commits authored by the app get GitHub's native `jojo-bot[bot]` styling in the UI.
- Per-installation tokens are short-lived (~1 hour) and rotate automatically.
- Permissions are per-repo and fine-grained; the app can be uninstalled from one repo without touching the others.
- The private key lives on the server only; no human ever handles it after provisioning.
- The audit trail extends: every push is attributed to the app's installation ID, not just a commit author string.

## Prerequisites

- A Nurix GitHub organization that owns `ask_jojo`, `ask_jojo_wiki`, and `ask_jojo_raw` (or personal org until the migration). If the repos are still under a personal account when Phase 7b arrives, either migrate them first or create the app under the personal account.
- Org-level permission to create GitHub Apps (organization owner, or a role with the "Manage apps" permission).
- Access to the target deployment server.

## Step 1 — Create the App

1. Navigate to `https://github.com/organizations/<nurix-org>/settings/apps/new` (or `https://github.com/settings/apps/new` if using a personal account).
2. Fill in the form:
   - **App name:** `jojo-bot` (must be globally unique on GitHub; if taken, try `nurix-jojo-bot`).
   - **Homepage URL:** the internal URL where the Phase 7b server lives, or `https://github.com/<org>/ask_jojo` as a placeholder.
   - **Webhook:** disabled. Phase 7b pipelines are pulled by the server, not pushed by GitHub.
   - **Repository permissions:**
     - Contents: **Read & write**
     - Metadata: Read (automatic)
     - Pull requests: Read & write (for the "Request edit from JoJo" diff flow in Phase 3)
     - Commit statuses: Read & write (for the lint-in-CI gate)
   - **Organization permissions:** none.
   - **User permissions:** none.
   - **Where can this app be installed:** "Only on this account".
3. Create the app. Save the **App ID** that GitHub displays.
4. Scroll to "Private keys" → **Generate a private key**. A `.pem` file downloads. This is the *only* copy — store it immediately per Step 3.

## Step 2 — Install on the Three Repos

1. From the app's settings page → "Install App" → pick the target org/account.
2. Select **Only select repositories** and choose:
   - `ask_jojo`
   - `ask_jojo_wiki`
   - `ask_jojo_raw`
3. Confirm. Save the **Installation ID** that GitHub shows in the URL (`/installations/<id>`).

## Step 3 — Store the Credentials on the Server

On the Phase 7b server (Windows VM assumed; adjust for Linux as needed):

```powershell
# On the server, NOT on a developer machine.
$appDir = "$env:PROGRAMDATA\JojoBot\service-account"
New-Item -ItemType Directory -Path $appDir -Force | Out-Null

# Copy the downloaded .pem into $appDir\jojo-bot.pem
# Then encrypt in place using DPAPI, scoped to the service account:
$plain    = Get-Content "$appDir\jojo-bot.pem" -Raw
$secure   = ConvertTo-SecureString $plain -AsPlainText -Force
$encrypted = $secure | ConvertFrom-SecureString  # DPAPI, user-scoped
Set-Content -Path "$appDir\jojo-bot.pem.enc" -Value $encrypted
Remove-Item "$appDir\jojo-bot.pem"  # delete the plaintext copy

# App ID and Installation ID go into a JSON config file.
@{
    app_id          = "<the App ID from Step 1>"
    installation_id = "<the Installation ID from Step 2>"
    key_path        = "$appDir\jojo-bot.pem.enc"
    repos           = @("ask_jojo", "ask_jojo_wiki", "ask_jojo_raw")
} | ConvertTo-Json | Set-Content -Path "$appDir\config.json"
```

Note the key is encrypted under the *service-account user's* DPAPI scope. Only that account (or an admin reading the key with `protect: false`) can decrypt. The server runs pipelines under this account.

## Step 4 — Update `bot-identity.ps1` to Support Both Modes

By Phase 7b, `bot-identity.ps1` gains a branch: if `$env:JOJO_BOT_MODE` is `app`, mint an installation token via JWT and use it for pushes; otherwise fall back to the overlay. The function signatures stay identical so callers do not change.

Pseudocode to implement when this phase starts:

```powershell
function Get-BotInstallationToken {
    # 1. Load encrypted key with DPAPI
    # 2. Sign a JWT (iss=app_id, iat=now, exp=now+10min, alg=RS256)
    # 3. POST to https://api.github.com/app/installations/<id>/access_tokens
    # 4. Cache the returned token in memory for ~50 minutes
    # 5. Return token
}

function Invoke-BotCommit { ... unchanged ... }

function Push-BotCommits {
    # 1. $token = Get-BotInstallationToken
    # 2. git -c http.extraheader="Authorization: Bearer $token" push
}
```

## Step 5 — Smoke Test

1. On the server, run `test-bot-identity.ps1 -Mode app`. (Add the `-Mode` parameter when implementing Step 4.)
2. Expected: `PASS: bot identity commits with author jojo-bot[bot]`, push succeeds, GitHub UI shows the bot badge.
3. Verify `gh api /repos/<org>/ask_jojo_wiki/commits/main --jq '.commit.author'` returns the bot identity.

## Step 6 — Retire the Overlay on the Server

Once Step 5 passes for one absorb cycle:

1. In the server's scheduled-task definitions, set `JOJO_BOT_MODE=app`.
2. Local developer machines keep the overlay — no change needed there.
3. Add a deprecation note to `ops/service-account/README.md` describing the split.
4. File the Phase 7b completion commit.

## Failure Modes to Watch

- **Private key leaked.** Revoke immediately from the app's settings page → "Revoke all". Generate a new one, re-encrypt, redeploy. All existing installation tokens expire within an hour.
- **Installation removed by org admin.** All pushes fail with 403. Either reinstall (same App ID, new Installation ID — update `config.json`) or restore the install.
- **Rate limits.** The app has 5000 requests/hour per installation. If absorb bursts exceed this, implement a token-bucket in `bot-identity.ps1`; do not try to raise the limit.

## References

- `docs/ADR/0005-jojo-bot-service-account.md`
- GitHub Apps docs: https://docs.github.com/en/apps
- JWT signing spec: https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-a-json-web-token-jwt-for-a-github-app
