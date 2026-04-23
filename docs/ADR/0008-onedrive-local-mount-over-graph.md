# ADR 0008 — OneDrive and Public Drive via Local Mount, Not MS Graph

**Status:** Accepted
**Date:** 2026-04-22
**Deciders:** Mateo de los Rios
**Supersedes:** refines `PLAN.md` §6 Phase 1 and `ADR 0007`'s "next up: OneDrive via Graph" line
**Related:** `ADR 0004` (local-first deployment), `ADR 0007` (SharePoint delegated-auth first)

## Context

Phase 1b shipped the SharePoint connector against MS Graph using a delegated bearer token pasted from Graph Explorer (`ADR 0007`). The natural next step was OneDrive against the same Graph stack — `Files.Read.All` instead of `Sites.Read.All`, otherwise identical. The plan in ADR 0007 called out OneDrive as "next up once we add `Files.Read.All` to the delegated scope set."

On 2026-04-22, two things became clear:

1. **The tenant currently blocks delegated `Files.Read.All` consent.** Mateo has `Sites.*` + `Application.ReadWrite.All` consented to Graph Explorer, but `Files.Read.All` shows an "unconsent" state the UI refuses to toggle despite the scope listing it as non-admin. Root cause unclear — could be a tenant policy, a conditional-access rule, or a role scoping quirk. Debugging it means opening an IT ticket on a low-priority question, which is slow work.

2. **OneDrive is already mirrored to local disk.** The OneDrive desktop client syncs the entire tenant-mapped folder to `C:\Users\<user>\OneDrive - Nurix Therapeutics\` on Windows. The same content the Graph API would return is sitting on Mateo's laptop as ordinary files. And the "public drive" (Nurix's company-wide SMB share) is mapped to `P:\` using the same Windows-client plumbing — also a filesystem walk away.

Meanwhile, `packages/jojo_ingest/drive.py` already does the thing — walks a filesystem root, respects `.jojoignore`, runs every file through the shared converter pipeline. There is no new traversal code to write; the only reason Graph ever looked attractive was that SharePoint genuinely isn't filesystem-accessible.

## Decision

**Ingest OneDrive and the Nurix public drive by walking their local sync / mount points, not via MS Graph.**

Implementation:

- `packages/jojo_ingest/onedrive.py` becomes a one-class subclass of `DriveConnector` that overrides `source_type = "onedrive"`. Env factory reads `JOJO_ONEDRIVE_PATH` (e.g. `C:\Users\mdelosrios\OneDrive - Nurix Therapeutics`).
- `packages/jojo_ingest/publicdrive.py` is the same shape for the `P:\` drive, reading `JOJO_PUBLIC_DRIVE_PATH` (with a Windows-only default of `P:\`).
- CLI + router wire both into the existing `--source` / `request.source` override surface, same shape as `jojo-ingest sync drive`.
- `OneDriveEnvError` / `PublicDriveEnvError` translate missing-env / missing-path failures into HTTP 400 rather than 500 or 501 — config-fixable, not feature-missing.
- `packages/jojo_ingest/nurixnet.py` is deleted. NurixNet is a SharePoint site (`https://nurix.sharepoint.com/sites/NurixNet`), already walked by the SharePoint connector via `JOJO_SHAREPOINT_SITES`. The prior framing (Playwright over VPN) assumed NurixNet was a separate intranet app, which it is not.

The Graph-based OneDrive path stays available as a future option behind the existing `TokenProvider` abstraction (`ADR 0007`). If the tenant opens `Files.Read.All`, or Phase 7b's service-account app lands with admin-consented `Files.Read.All`, we can introduce a `OneDriveGraphConnector` that produces the same `SourceEntry` shape without touching anything downstream.

## Rationale

Four reasons pushed local-mount ingestion ahead of Graph for OneDrive + public drive:

1. **Unblock today.** The code already exists. `OneDriveConnector` is a five-line subclass of `DriveConnector`; no MS Graph, no token lifecycle, no tenant paperwork, no dependency on whether IT will eventually consent `Files.Read.All`.

2. **Same content, strictly less infrastructure.** The OneDrive sync client is already the authoritative renderer of OneDrive content on Windows. Anything the Graph API would return that Mateo can read also lives in the sync folder. The public drive has no Graph equivalent at all — it's SMB-only. Going through Graph for OneDrive would add HTTP + auth + throttling + pagination for the same bytes we can `os.walk`.

3. **The abstraction stays honest.** `source_type` is a value, not a code path. The manifest and downstream wiki-compile pipeline don't care whether the bytes came from Graph or from a local walker; they care that the `SourceEntry` has the right `source_type`, `source_url` (`file://…` URI is fine), and content. Swapping in a Graph-backed `OneDriveConnector` later doesn't change any contract.

4. **Provenance is preserved.** Because `OneDriveConnector` and `PublicDriveConnector` are distinct classes with distinct `source_type` values, the manifest's `by_source` breakdown still says "this came from OneDrive" vs. "this came from an arbitrary drive path". Later phases (access-level enforcement, absorb pipeline, Phase 7b per-user ACLs) can tell them apart.

## Consequences

### Positive

- OneDrive and public drive ingest work **today**, zero new infrastructure, no IT ticket required.
- NurixNet stub removed — one less Playwright-over-VPN line item, which would have been one of the hardest connectors in Phase 1.
- Stub-era 501 responses (`GET /api/ingest/sync/onedrive` returning "connector is stubbed") go away. All five connector endpoints now execute real code or return 400 with actionable messages.
- The `TokenProvider` abstraction from ADR 0007 stays unused for OneDrive, but unchanged — it's still the right shape when / if a Graph path becomes desirable.

### Negative

- **Only Mateo's OneDrive ingests**, not any other Nurix employee's. This is identical to the situation in `ADR 0007` for SharePoint (delegated auth → reading lens is the operator's), and acceptable for V1 — Mateo is the only operator. The shared-server Phase 7b deployment will need per-user ingest, which forces Graph + service-account scopes at that point.
- **Walk is whole-tree, no delta endpoint.** Graph's `/delta` would be faster for incremental sync. For a laptop-scale OneDrive (~tens of thousands of files), `os.walk` + the driver's SHA256 hash check is still fast enough that this doesn't matter in Phase 1. Revisit if scheduled syncs start costing minutes.
- **Public drive content over SMB can be slow to `stat`.** Operator is responsible for passing `--since` on scheduled runs so `os.stat` fires only for recently-changed files.
- **`source_url` is a `file://` URI**, not a browsable SharePoint / OneDrive web URL. Fine for a local-single-user V1 where the operator can just open the path; awkward for Phase 7b's multi-user surface. Revisit when Phase 7b introduces a shared raw repo.
- **Files not yet synced to disk won't be ingested.** This is a OneDrive-client quirk more than a design flaw — if the user has "Files On-Demand" enabled and a folder hasn't been downloaded, the walker sees the placeholder. Mitigation: the OneDrive client has a "Always keep on this device" option per folder; document it in the operator runbook.

## Revisit When

- Tenant opens up delegated `Files.Read.All` (allows a Graph-backed `OneDriveGraphConnector` alongside the local-mount one; local-mount stays the default because it's cheaper).
- Phase 7b begins — multi-user ingest on a shared server forces Graph + service-account scopes; local-mount becomes local-mode only.
- Scheduled incremental sync starts taking long enough that `/delta` would noticeably help.
- A file appears in OneDrive that the operator explicitly wants ingested but that OneDrive client has not synced locally (rare).
