# ADR 0013 — Phase 7b: Standalone Per-Department Workstation Installer

**Status:** Accepted
**Date:** 2026-05-19
**Deciders:** Mateo de los Rios
**Supersedes:** `ADR 0000` §Phase 7b deployment model (shared internal server)
**Related:** `ADR 0004` (local-first deployment), `ADR 0009` (DPAPI secrets), `ADR 0012` (OneDrive mount supersedes Path C)

## Context

`PLAN.md` and `ADR 0000`'s roadmap described Phase 7b as deploying JoJo Bot as a
shared internal service — a central server that multiple users would connect to. This
model was motivated by the desire to share ingest effort and a single canonical wiki
across a team.

On 2026-05-19, that model was reconsidered for three reasons:

1. **Infrastructure overhead.** A shared internal server requires IT involvement for
   provisioning, port exposure, service-account setup, and ongoing maintenance. For a
   team tool in a small biotech, that overhead is disproportionate to the benefit.

2. **The local-first decision holds.** `ADR 0004` established that JoJo Bot runs
   locally to keep data off cloud services and eliminate network latency. A "shared
   server" is still a local server, but it introduces the networking, auth, and
   multi-tenancy complexity that ADR 0004 was designed to avoid.

3. **Standalone workstations cover the actual use case.** Each Nurix department has
   a shared Windows workstation that staff use for presentations and file access.
   Installing JoJo Bot there — one install per department, with its own wiki and
   ingest state — is the minimal viable shared deployment. OneDrive is already synced
   to those machines; P:\ is already mapped. The install adds nothing to the IT
   footprint beyond a Windows Service on one machine.

## Decision

**Phase 7b = standalone Windows installer per department workstation (not a shared
internal server).**

### Packaging

- Single `.zip` artifact produced by `Build-JojoBotRelease.ps1`.
- Contents: frozen Python interpreter + bundled packages, Next.js static build,
  `Install-JojoBot.ps1` (creates Windows Service, writes default config, opens
  browser to `/welcome`), `Uninstall-JojoBot.ps1`.
- FastAPI backend on `localhost:8765` as a Windows Service managed by NSSM
  (or a lightweight C# service wrapper if NSSM is unavailable).
- Distribution: `.zip` via SharePoint or email + one-page install guide.

### Configuration

- Config stored in `%APPDATA%\JojoBot\config.json` DPAPI-encrypted per `ADR 0009`.
- All runtime settings (API key, Graph auth, connector paths, lint cadence)
  editable from the Settings tab in the UI — no PowerShell required for end users.
- Defaults pre-populated for Nurix tenant/client IDs and common connector paths.

### Wiki and ingest state

- Each install has its own wiki directory and its own ingest manifest.
- No cross-department sync in MVP. If two departments want shared content, they
  can point both installs at the same wiki directory on `P:\` — that is a
  documented option but not a supported or tested configuration for v2.0.

### Auth

- OneDrive and public drive via local mount (`ADR 0008` / `ADR 0012`).
- SharePoint via Path B MSAL device-code (`ADR 0007` / `ADR 0012`).
- Settings tab surfaces cache expiry and provides a one-click "Re-authenticate" button.

## Consequences

### Positive

- No IT server project. The workstation install is entirely self-service.
- DPAPI encryption continues to work — it is a per-machine key, compatible with a
  shared workstation where multiple Windows accounts could log in (all accounts on
  the same machine share the machine key; DPAPI with user-key scope would isolate
  accounts, but install-wide config is intentional per the Settings tab spec).
- The `.zip` + `Install-JojoBot.ps1` pattern is simple enough for a non-developer
  staff member to follow with the install guide.
- Aligns with `ADR 0004`'s local-first principle: JoJo Bot is still on-premise,
  data does not traverse a network to reach the service.

### Negative

- Each department's wiki is independent. Cross-department knowledge sharing requires
  a shared wiki directory on P:\ or a future sync mechanism.
- DPAPI machine-key scope means anyone with local admin on the workstation can read
  the config.json — acceptable for a shared department workstation, document in the
  security section of the install guide.
- No central admin view of which workstations are running which version. Version
  management is manual (re-distribute the `.zip` when a new version ships).

## Revisit When

- A department explicitly asks for centralized multi-department access from their
  own desks (not a shared workstation) — consider a local-network server at that
  point, and revisit Path C per `ADR 0012`.
- Compliance or IT requires per-user audit logs of who queried what — DPAPI
  machine-key scope becomes inadequate; re-evaluate per-user key scope.
- The install guide proves too complex for staff to follow without developer help —
  consider a proper Windows installer (`.msi` or MSIX) at that point.
