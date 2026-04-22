# ADR 0004 — Local-First Deployment for Phases 0–6

**Status:** Accepted
**Date:** 2026-04-22
**Deciders:** Mateo de los Rios
**Supersedes:** none
**Related:** `ADR 0002` (three-repo split), `PLAN.md` §4 D1 + D11, Phase 7b

## Context

v2.0 needs a deployment model that lets a solo developer (plus Claude Code) ship working software in months, not quarters. The production footprint of the eventual system — scheduled ingest, a background absorb pipeline, a nightly lint, a frontend — could be a small Nurix-internal server. But standing up a shared server requires IT coordination, SSO integration, per-user access control, and a deployment pipeline. That is substantial scope for Phase 0.

At the same time, the v1.0 `.exe` distribution model (Windows Task Scheduler, per-user ChromaDB, local .env files) works. Scientists have it installed. They use it. Extending that model to v2.0 gets a working system into users' hands much sooner.

Two deployment shapes were considered.

**Option A: build the server from day one.** Everything runs on a Nurix-internal VM; users connect via browser. Phase 0 includes IT sign-off, SSO, per-article ACLs, a deployment pipeline.

**Option B: local-first, promote to server later.** Phases 0–6 ship as an enhanced `.exe` that each scientist runs locally, with the git-backed wiki on their own disk. Phase 7b promotes the system to a shared server once the pipelines are proven.

## Decision

**Adopt Option B. Phases 0–6 are local-first, packaged as an enhanced .exe. Phase 7b promotes the system to a shared Nurix-internal server once the MVP has been validated.**

In local mode:

- All three repos clone to the user's local disk (`C:\Users\mdelosrios\Claude_Local\jojo_bot_v2.0\`, not in OneDrive).
- Ingest, compile, and lint run as Windows scheduled tasks on the user's machine.
- Secrets (Anthropic API keys, Microsoft Graph tokens) live in `%APPDATA%\JojoBot\config.json`, encrypted via DPAPI.
- The backend is FastAPI on `localhost`; the frontend is Next.js in an Electron shell or a browser tab.
- Ingest only pulls content the authenticated user's Microsoft Graph token can already read — access control is inherited from the source system, not enforced separately.

In server mode (Phase 7b):

- A Nurix-internal VM holds the authoritative `ask_jojo_raw/` and `ask_jojo_wiki/`.
- Scheduled pipelines run centrally.
- Azure AD / Nurix SSO gates every API call.
- Per-article ACLs are enforced at the backend, inherited from source-system permissions.
- Local clones continue to work for development, but users in production hit the server.

## Rationale

Users ship sooner. A working local .exe in Mateo's hands within a few months beats a half-built server in six.

Risk is contained. Bugs, cost overruns, and prompt-drift episodes happen on a single user's machine, not on a shared VM with company-wide visibility.

IT dependencies are deferred. Server promotion requires SSO, deployment tooling, and per-article ACLs — all non-trivial. Building them before the pipeline is validated risks over-engineering the wrong thing. Phase 7b lands after the pipeline has been exercised on real content.

Access control is simple at first. The "all-FTE" initial corpus (see `PLAN.md` §4 D7) means a scientist's local clone only contains documents they could already read. There is no new access-control surface to defend.

## Consequences

### Positive

- Time-to-first-user is short. The Protein Sciences pilot can be running in Mateo's office before Phase 7 is even scoped.
- The single-user mode is a natural development environment. "Run the app" is the same command a user runs.
- Bugs that corrupt the wiki only corrupt one user's clone. A git pull repairs it.
- The v1.0 packaging pattern (Windows Task Scheduler, .exe, local config) is proven.

### Negative

- No shared wiki until Phase 7b. If two scientists are running absorb independently, they will diverge. The pilot mitigates this by having one "canonical" user run absorb; others read via `git pull`.
- Scheduled tasks on user machines are fragile. A laptop that stays closed for a week misses absorb runs. Acceptable for MVP; Phase 7b solves it.
- API key management is per-user. Each scientist needs their own Anthropic key (or a Nurix-shared key distributed out-of-band). Cost attribution becomes harder.
- Microsoft Graph OAuth on a desktop app has its own gotchas (redirect URI, token refresh across sessions). Solved patterns exist; budget time.

## Alternatives Considered

**Option A: server-first.** Rejected for the reasons above — too much upfront IT scope for a project that has not yet proven its own pipelines work. Phase 7b reaches the same end state, after the pipelines are validated.

**Hybrid from day one: local dev + shared server.** Rejected as a false economy. Running both code paths in parallel doubles the test surface and doubles the failure modes, for a deployment we are not yet sure we need.

**Keep v2.0 local-only, never promote to server.** Rejected. The pilot will prove value; once it does, a shared server is the natural way to let the whole Protein Sciences group use the tool without everyone running their own absorb pipeline.

## References

- `PLAN.md` §4 D1 (workspace location), D11 (local-first deployment), and Phase 7b (server promotion).
- v1.0 packaging patterns (Windows .exe, Task Scheduler, DPAPI-encrypted config).
- Microsoft Graph SDK `Files.Read.All` + `Sites.Read.All` scopes.
