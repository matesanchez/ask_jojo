# ADR 0005 — Two-Phase `jojo-bot` Service Account

**Status:** Accepted
**Date:** 2026-04-22
**Deciders:** Mateo de los Rios
**Supersedes:** none (refines `PLAN.md` §4 D10 and `ADR 0004`)
**Related:** `ADR 0004` (local-first deployment), `CLAUDE.md` §9 (commit messages), `PLAN.md` §4 D10 (git hygiene)

## Context

Every wiki commit and every raw-ingest commit is supposed to be authored by a dedicated service identity, so `git log --author` cleanly separates automated writes from manual human overrides. The original plan (PLAN.md §4 D10) implicitly assumed a GitHub App named `jojo-bot[bot]` with per-repo fine-grained permissions, installation tokens, and a private key stored encrypted on disk.

A full GitHub App is appropriate for the eventual Phase 7b deployment, where a shared Nurix-internal server runs ingest / compile / lint on behalf of many users and needs a first-class, auditable, revocable identity. It is heavy machinery for Phases 0–6, where the entire system runs on one engineer's Windows laptop, with that engineer as the sole actor. During the local phases, "the service account" is really just "the scheduled task running under Mateo's account, with a different git identity overlay so automated commits are distinguishable."

## Decision

**Adopt a two-phase service-account strategy.**

### Phases 0–6 (local mode): git-identity overlay, no separate GitHub identity

- Every scheduled task that commits to `ask_jojo_wiki/` or `ask_jojo_raw/` uses a git-identity overlay: `git -c user.name="jojo-bot" -c user.email="jojo-bot@nurixtx.com" commit …`. A helper script (`ops/service-account/bot-commit.ps1`) wraps this so all entry points use the same identity.
- Pushes authenticate with Mateo's existing GitHub credentials (whatever `gh auth login` configured, HTTPS + credential manager or SSH key).
- `git log --author=jojo-bot` on any of the three repos yields exactly the automated commits. Human commits show Mateo's identity.
- The CLAUDE.md §9 commit-message prefixes (`absorb:`, `lint:`, `checkpoint:`, `[manual]`) provide a second, orthogonal audit dimension.

### Phase 7b (shared server): GitHub App with installation tokens

- Create a GitHub App named `jojo-bot`. Commits it authors appear as `jojo-bot[bot]` with GitHub's native bot styling.
- The server holds the app's private key encrypted on disk. Each scheduled pipeline run mints a short-lived installation token and uses it for `git push`.
- Per-repo permissions granted via the app's installation scope: write to `ask_jojo_wiki` and `ask_jojo_raw`, read to `ask_jojo`.
- Detailed instructions for the app setup live in `ops/service-account/PHASE_7B_APP_SETUP.md`, drafted now so the future handoff is scripted.

## Rationale

Phases 0–6 have one user and one machine. The threat model that justifies a full GitHub App — multiple untrusted actors sharing a write-capable identity, with the need to revoke one principal without revoking all — does not apply. Pretending it does would waste time standing up JWT-signing infrastructure that nobody will exercise for three months.

The git-identity overlay produces the same audit output (`git log --author` separates bot from human) with four lines of PowerShell and no GitHub coordination. If someone later disputes whether a commit was really automated or manual, the commit message prefix (`absorb:` vs `[manual]`) resolves it.

When Phase 7b arrives, the GitHub App becomes the right tool because: multiple users will be reading the wiki, the ingest pipeline runs on infrastructure nobody logs into interactively, and per-user-token cost attribution starts to matter. Building the app ahead of that need is premature optimization.

## Consequences

### Positive

- Zero GitHub-side setup required before Phase 1 can start. Ingest pipeline can commit as `jojo-bot` on its first scheduled run.
- Mateo's existing `gh auth` covers all pushes from day one.
- When Phase 7b lands, the migration is additive: add the GitHub App alongside the existing overlay; point the server's scheduled tasks at the new authentication path; retire the overlay only after the server has been stable for a week.
- Simpler secret management — no private key stored on a developer laptop.

### Negative

- Bot commits do not show GitHub's native `[bot]` badge in the UI. They show `jojo-bot <jojo-bot@nurixtx.com>`. Visually distinguishable but less prominent.
- An adversary with shell access on Mateo's laptop could forge a commit as `jojo-bot`. Mitigation: there is no such adversary in the threat model for Phases 0–6, and the lint pipeline flags commits with prefix `[manual]` separately from bot prefixes anyway.
- `git log --author="jojo-bot"` depends on disciplined use of the overlay. Any scheduled task that forgets it will commit as Mateo. Mitigation: a single helper script (`ops/service-account/bot-commit.ps1`) is the only way the pipeline commits, and it is exercised in CI before any scheduled task ships.

## Alternatives Considered

**Full GitHub App from day one.** Rejected. See rationale above — heavy machinery for a threat model that does not yet exist. Phase 7b gets it.

**A classic GitHub machine user (`jojo-bot` as a real GitHub account with its own PAT).** Rejected. Same downsides as a GitHub App (requires GitHub-side setup, PAT rotation hygiene) without the upside of GitHub's native bot styling or per-repo scoping. The git-identity overlay is strictly simpler with the same audit property.

**No service identity — just commit message conventions.** Rejected. Commit messages are author-less; a malicious or mistaken manual commit with prefix `absorb:` would be indistinguishable from a real one. Needing both the author and the message prefix to match is meaningfully stronger.

## References

- `PLAN.md` §4 D10 (git hygiene, commit-message conventions)
- `ADR 0004` (local-first deployment; frames why most security machinery waits until Phase 7b)
- `CLAUDE.md` §9 (commit-message prefixes that complement this ADR)
- `ops/service-account/README.md` (operational runbook)
- `ops/service-account/PHASE_7B_APP_SETUP.md` (future GitHub App instructions)
