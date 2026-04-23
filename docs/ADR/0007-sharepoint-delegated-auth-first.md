# ADR 0007 — SharePoint Delegated-Auth First, Service-Account Later

**Status:** Accepted
**Date:** 2026-04-22
**Deciders:** Mateo de los Rios
**Supersedes:** none (refines `PLAN.md` §6 Phase 1 and `ADR 0005`)
**Related:** `ADR 0004` (local-first deployment), `ADR 0005` (two-phase jojo-bot identity)

## Context

Phase 1b of the plan lights up the cloud-tier connectors (SharePoint, OneDrive). The original assumption (encoded in `ADR 0005` and in the old `sharepoint.py` stub's docstring) was that IT would register an app in the Nurix Entra tenant with `Files.Read.All` + `Sites.Read.All` as **application-type permissions**, admin-consented, with a client secret stored DPAPI-encrypted in `%APPDATA%\JojoBot\config.json`. The SharePoint connector would then authenticate via MSAL's client-credentials flow and ingest org-wide as an unattended service account.

On 2026-04-22 it became clear that:

1. Mateo already has broad delegated scopes consented to Graph Explorer in the Nurix tenant, including `Sites.Read.All`, `Sites.ReadWrite.All`, `Sites.FullControl.All`, and `Application.ReadWrite.All`. A Graph Explorer-issued JWT produces a ~60 min bearer token that can read SharePoint immediately.
2. Mateo's tenant roles (JWT `wids` claim) suggest he personally has app-registration rights — the original "blocked on IT" framing was wrong.
3. The shared-server Phase 7b deployment isn't due for months; V1 runs locally on Mateo's laptop with Mateo as the only operator.

A service-account app registration is still the right endpoint for Phase 7b (unattended server, content beyond what any one human can see), but it's not a blocker for V1 ingest and it's not trivial to stand up correctly.

## Decision

**Implement SharePoint (and, next, OneDrive) against a pluggable auth interface, shipping Path A (delegated token) first, with Path B (MSAL device-code) and Path C (service-account) landing as later slots.**

### The interface — one abstraction, three auth flows

`packages/jojo_ingest/graph.py` defines a `TokenProvider` (any `Callable[[], str]`) and a `GraphClient` that takes one. All auth complexity lives behind that callable. The connector never knows which flow is in use.

### Path A — Delegated token from env var (V1, shipping now)

- `env_token_provider("JOJO_GRAPH_ACCESS_TOKEN")` reads a Graph Explorer–issued JWT from the environment on every request.
- ~60 min token lifetime. When it expires Graph returns 401 and the connector raises a `GraphError` that names the env var, so the operator (Mateo) pastes a fresh token and re-runs.
- `JOJO_SHAREPOINT_SITES` is a comma-separated list of site URLs. Scoping the crawl explicitly means we don't accidentally index HR folders that happened to be shared with Mateo.
- Ingested content inherits Mateo's reading lens. For a V1 that serves the Protein Sciences, NurixNet, DEL, CRUK, and Biortus sites — all of which are broadly readable — that lens is wide enough.

### Path B — MSAL device-code flow (next)

- `msal_device_code_provider()` wraps `PublicClientApplication`. First run prints a code + URL; the operator signs in once in a browser; MSAL caches refresh tokens to `%APPDATA%\JojoBot\tokencache.bin` and auto-refreshes for ~90 days.
- Can either use Nurix's own public client app registration (if IT grants one; very small ask, no secret or admin consent needed) or fall back to Microsoft's well-known Azure-PowerShell public client id.
- Same delegated scope posture as Path A, but unattended after first login.

### Path C — Client-credentials service account (Phase 7b)

- `msal_client_credentials_provider()` wraps `ConfidentialClientApplication`. Needs a real app registration with admin-consented `Files.Read.All` + `Sites.Read.All` app permissions and a client secret (or cert, preferred).
- Uses DPAPI-encrypted config.json per `ADR 0004` on Windows; Key Vault reference on Linux/server once Phase 7b arrives.
- Decoupled from any individual's identity — won't break when Mateo takes vacation or leaves the company.

## Rationale

Three concerns pushed delegated auth ahead of service-account auth for V1:

1. **Unblock today.** A pasted token lets the SharePoint connector validate end-to-end against actual Nurix content this afternoon. A service-account registration, even if Mateo can self-serve it, is a day of portal clicks + testing + secret storage — and we only find out if the whole pipeline works after all that.
2. **Correct abstraction for free.** Going straight to MSAL client-credentials conflates two decisions (which auth flow; how we handle secret rotation) and would bake both into the connector. Routing everything through `TokenProvider` means Path C lands as a 40-line MSAL wrapper without touching the connector.
3. **V1 scope matches delegated auth's limits.** The six sites Mateo named — Protein Sciences, NurixNet, DEL Triage / Screen Team, CRUK Grant, Biortus — are content Mateo can already read. Delegated auth sees everything V1 cares about.

Path C is still the endpoint. We keep the existing `ADR 0005` Phase-7b service-account plan intact: the GitHub App and the Graph app registration both land in the same phase, on the same shared server.

## Consequences

### Positive

- SharePoint connector ships in Phase 1b without waiting on IT or on app-registration paperwork.
- `TokenProvider` abstraction means Path B and Path C are additive work; neither requires rewriting the connector.
- Token handling is the operator's responsibility in V1 — there's no secret committed anywhere, no DPAPI dependency yet, nothing to leak if the repo goes public.

### Negative

- Path A requires a human to paste a fresh token every ~60 minutes during active development. Acceptable for interactive dev; unacceptable for scheduled runs. Path B lifts this ceiling to ~90 days per interactive login. Scheduled ingest is therefore **blocked until Path B ships** (or Path C, whichever comes first).
- Content visible to the ingest is gated on Mateo's personal access. If a site opens to the company after he changed roles, the bot wouldn't see it until Phase 7b's service account gets an independent, admin-consented scope.
- The operational surface becomes "what env vars do I need" rather than "is the config.json in place". Documented in the connector + CLI error messages and in `docs/v2_status.md` Phase 1b notes.

## Revisit When

- IT decides to register the app themselves ahead of Phase 7b (accelerates Path C, makes Path B unnecessary).
- Mateo finds himself re-pasting tokens more than twice a day (prioritize Path B).
- A site comes into scope that Mateo doesn't have personal access to (forces Path C).
- Phase 7b begins (definitively replaces Path A and B with Path C on the shared server; Path A stays available for local-mode debugging).
