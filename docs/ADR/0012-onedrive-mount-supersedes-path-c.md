# ADR 0012 — OneDrive Mount Supersedes Graph-Based SharePoint and Path C

**Status:** Accepted
**Date:** 2026-05-19
**Deciders:** Mateo de los Rios
**Supersedes:** `ADR 0007` Path C (client-credentials service-account flow)
**Related:** `ADR 0007` (SharePoint delegated-auth first), `ADR 0008` (OneDrive local mount), `ADR 0013` (Phase 7b standalone installer)

## Context

`ADR 0007` defined three auth paths for the MS Graph connector and explicitly reserved
Path C (MSAL client-credentials, admin-consented `Files.Read.All` + `Sites.Read.All`)
for Phase 7b — the point where ingest moves to a shared server that has no individual
user identity to delegate from.

`ADR 0008` then took OneDrive off Graph entirely: the tenant blocks delegated
`Files.Read.All`, but the OneDrive desktop client already syncs the full folder
tree to disk. OneDrive ingest became a filesystem walk — no Graph, no scopes,
no token lifecycle. After ADR 0008 landed, Path C was only still needed for
SharePoint ingest on the future shared server.

On 2026-05-19, Phase 7b was redefined (see `ADR 0013`): the target deployment is
a **standalone Windows workstation** per department, not a central server. Every
workstation already has the OneDrive desktop client running and the public SMB drive
mounted. The original motivation for Path C — unattended, identity-independent
SharePoint access from a machine that no human sits at — does not apply to the
standalone workstation model.

Path B (MSAL device-code) gives ~90-day unattended SharePoint access after a single
interactive login. For a department workstation where a designated staff member renews
the login once per quarter, that is sufficient. The Settings tab (Phase 7b) will surface
the cache-expiry date and prompt renewal.

## Decision

**Path C (client-credentials service account) is superseded and will not be implemented
for Phase 7b.**

The standalone workstation deployment uses:
- **OneDrive ingest:** local sync mount (`JOJO_ONEDRIVE_PATH`) per `ADR 0008`
- **Public drive ingest:** SMB mount (`JOJO_PUBLIC_DRIVE_PATH`) per `ADR 0008`
- **SharePoint ingest:** Path B MSAL device-code per `ADR 0007`

The `msal_client_credentials_provider()` stub may be kept in `graph.py` as a comment
or a `NotImplementedError` body for a hypothetical future multi-site enterprise
deployment, but it is **not a roadmap item** and will not be wired into any UI,
CLI, or scheduler task.

`ADR 0007` remains accepted. Only its Path C section is superseded by this ADR.
Paths A and B are both kept: Path A for interactive dev/debug, Path B for scheduled
production ingest.

## Consequences

### Positive

- No IT app-registration paperwork. No admin-consented application permissions.
- No client secret to rotate, store, or audit.
- Phase 7b scope shrinks: one fewer auth flow to test, document, and secure.
- `ADR 0008`'s local-mount decision is now the definitive long-term answer for
  OneDrive, not a V1 shortcut.

### Negative

- SharePoint ingest requires one interactive device-code login every ~90 days per
  workstation. If the cache expires and no staff member renews it, scheduled
  SharePoint ingest stops. Mitigation: Settings tab status sidebar shows
  `Graph: cache expires YYYY-MM-DD` and turns red on expiry; the scheduler's
  pre-flight check (`jojo-ingest auth check`) exits non-zero and the task log
  surfaces the error.
- A hypothetical future need to run JoJo Bot on a headless server with no
  individual identity would require revisiting this decision and implementing
  Path C at that time.

## Revisit When

- A department requests a headless shared-server deployment (no interactive user
  to renew device-code) — at that point, implement Path C.
- IT proactively registers a public-client app with delegated scopes and offers
  a longer-lived token model — evaluate whether it simplifies Path B.
