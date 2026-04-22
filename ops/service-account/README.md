# `jojo-bot` Service Account — Operational Runbook

This directory contains the machinery for the `jojo-bot` service identity that authors every automated commit to `ask_jojo_wiki/` and `ask_jojo_raw/`. It implements the two-phase strategy defined in `docs/ADR/0005-jojo-bot-service-account.md`.

**Current phase:** Phases 0–6 (local mode) — git-identity overlay only. No GitHub App yet.

## What This Directory Provides

| File | Purpose |
| --- | --- |
| `README.md` | This file. Operational runbook for the current phase. |
| `bot-identity.ps1` | Dot-sourceable script that exports `$BOT_NAME` and `$BOT_EMAIL`, plus an `Invoke-BotCommit` function. Every scheduled task imports this. |
| `bot-commit.ps1` | Standalone wrapper: `bot-commit.ps1 -Repo <path> -Message "<msg>" -Files "<globs>"`. Used by scheduled tasks that shell out rather than dot-source. |
| `test-bot-identity.ps1` | Smoke test: runs a bot commit in a temp directory, asserts `git log --author=jojo-bot` sees it. Run before first scheduled-task install. |
| `PHASE_7B_APP_SETUP.md` | GitHub App provisioning instructions for when the server phase arrives. Not used in Phases 0–6. |

## How the Overlay Works

Every automated commit uses a git-identity overlay instead of the machine's default `user.name` and `user.email`:

```powershell
git -c user.name="jojo-bot" `
    -c user.email="jojo-bot@nurixtx.com" `
    commit -m "<structured message>"
```

Human commits use Mateo's configured identity (whatever `git config user.name` and `git config user.email` return globally). `git log --author=jojo-bot` on any repo then yields exactly the automated commits.

The commit-message prefix (see `schema/CLAUDE.md` §9) provides a second, orthogonal audit dimension: `absorb:`, `lint:`, `checkpoint:` for bot commits; `[manual]` for humans acting on the wiki directly. A commit that has the bot's author but a `[manual]` prefix, or a human author but an `absorb:` prefix, is a lint violation and gets flagged.

## Installing on a New Workstation

One-time setup, from PowerShell in `C:\Users\<user>\Claude_Local\jojo_bot_v2.0\ask_jojo\ops\service-account\`:

```powershell
# 1. Verify your own GitHub credentials work (needed for push)
gh auth status
# If not authenticated: gh auth login (see main README)

# 2. Smoke-test the bot identity
.\test-bot-identity.ps1
# Expected: "PASS: bot identity commits with author jojo-bot <jojo-bot@nurixtx.com>"

# 3. Nothing to install globally. The overlay is per-invocation;
#    bot-identity.ps1 is dot-sourced by scheduled tasks that need it.
```

That is the entirety of the setup. There is no GitHub account to create, no private key to store, no PAT to rotate in this phase.

## Using the Bot Identity in a Scheduled Task

When the Phase 1 ingest pipeline or the Phase 2 absorb pipeline needs to commit, it calls the bot-commit helper rather than raw `git commit`. Two patterns:

### Pattern A — dot-source, use the function

```powershell
# at top of scheduled-task script
. $PSScriptRoot\..\ops\service-account\bot-identity.ps1

# ...later, after staging files...
Invoke-BotCommit -RepoPath $wikiRepo -Message @"
absorb(protein-sciences): 8 pages touched, 2 created
  - programs/tyk2-program.md            (updated)
  - targets/tyk2.md                      (created)
  ...
  Source: raw/sharepoint/protein-sciences/tyk2-strategy-2026.docx
"@
```

### Pattern B — invoke the wrapper script

```powershell
& "$PSScriptRoot\..\ops\service-account\bot-commit.ps1" `
    -Repo $wikiRepo `
    -StagedOnly `
    -Message "absorb(protein-sciences): 8 pages touched, 2 created`n..."
```

Either pattern produces the same result. Pattern A is preferred in Python-invoked flows that already have a PowerShell entry point; Pattern B is preferred for shell-agnostic callers.

## What This Does NOT Do

- **Push to GitHub.** Pushes use Mateo's existing `gh auth login` credentials. The bot identity is for *authoring* commits, not for authenticating pushes. In Phase 7b, the GitHub App takes over both responsibilities.
- **Enforce the identity.** Nothing at the git layer prevents a scheduled task from committing with a different identity by mistake. The commit-message prefix lint check (Phase 6) is the enforcement surface: a commit whose author is `jojo-bot` but whose message does not start with an allowed bot prefix gets flagged.
- **Sign commits.** GPG/SSH signing is out of scope for Phases 0–6. When Phase 7b lands, the GitHub App signs with a deploy key; see `PHASE_7B_APP_SETUP.md`.

## Migration to Phase 7b

When the server phase arrives, this directory grows: the overlay scripts stay (development still happens locally) and the GitHub App instructions in `PHASE_7B_APP_SETUP.md` get executed. Server-side scheduled tasks use the app's installation token; local development keeps the overlay. A deprecation note will land in this README at that time.

## References

- `docs/ADR/0005-jojo-bot-service-account.md` — the decision record.
- `schema/CLAUDE.md` §9 — commit-message prefix conventions.
- `PLAN.md` §4 D10 — git hygiene overview.
