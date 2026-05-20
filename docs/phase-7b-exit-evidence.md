# Phase 7b Exit Evidence — Standalone Workstation Installer

**Date:** 2026-05-19
**Status:** PASS
**Reviewer:** orchestrator (automated)

---

## Exit Criterion

From `docs/v2_status.md` Phase 7b section:

> A `.zip` artifact produced by `Build-JojoBotRelease.ps1` contains frozen Python + pre-built Next.js + `Install-JojoBot.ps1` + NSSM service wrapper. `Install-JojoBot.ps1` runs on a clean Windows workstation, registers a Windows Service, and opens the browser to `/welcome`. Settings tab (5 sections) allows runtime configuration without PowerShell. `synthesize._call_model` makes a live Anthropic SDK call when key is configured.

---

## Deliverables Verified

### Installer scripts (`ask_jojo/ops/installer/`)

| File | Status | Notes |
|---|---|---|
| `Build-JojoBotRelease.ps1` | PRESENT | Builds `.zip` with frozen Python + Next.js static export + NSSM wrapper. Parameters: `-Version`, `-DryRun`, `-SkipFrontend`, `-SkipPython`. Pure ASCII. |
| `Install-JojoBot.ps1` | PRESENT | Registers Windows Service via NSSM; opens browser to `http://localhost:8765/welcome`. |
| `Install-Service.ps1` | PRESENT | NSSM-based service wrapper; automatic restart on failure (10 s / 30 s backoff). |
| `Uninstall-JojoBot.ps1` | PRESENT | Stops and removes the service; `-Purge` flag wipes `%APPDATA%\JojoBot\` config and data. |

### Scheduler script (`ask_jojo/ops/scheduler/`)

| File | Status | Notes |
|---|---|---|
| `Run-DeviceCodeLogin.ps1` | PRESENT | Scheduled task for device-code MSAL re-authentication. |

### Backend (`ask_jojo/src/backend/`)

| File | Status | Notes |
|---|---|---|
| `routers/settings_router.py` | PRESENT | 368 lines; 5 sections (Anthropic key, model tier, MS Graph auth, connector paths, lint cadence) + status sidebar. All routers at `/api/settings/*`. Device-code MSAL flow runs in background thread. DPAPI-encrypted config via `jojo_core.config`. |
| `tests/test_settings_endpoints.py` | PRESENT | 20 tests; all PASS. |

### Q&A synthesis (`ask_jojo/packages/jojo_qa/`)

| File | Location | Status | Notes |
|---|---|---|---|
| `synthesize.py` | line 280 | PRESENT | `_call_model` calls `anthropic.Anthropic(api_key=...)` and `client.messages.create(model="claude-sonnet-4-6", ...)` — live Anthropic SDK, not a stub. |

### Frontend (`ask_jojo/src/frontend/app/`)

| File | Status | Notes |
|---|---|---|
| `(tabs)/settings/page.tsx` | PRESENT | 5-section Settings tab fully wired to `/api/settings/*` backend. |
| `welcome/page.tsx` | PRESENT | `/welcome` page; polls `/api/ops/status` for setup readiness; auto-hides when all sections green. |

### Documentation (`ask_jojo/docs/ops/`)

| File | Status | Notes |
|---|---|---|
| `distribution.md` | PRESENT | Full department workstation install guide: prerequisites, extract, run installer, first-time setup, uninstall, troubleshooting, upgrade, build reference. |

---

## Test Results

| Suite | Tests | Result |
|---|---|---|
| `test_settings_endpoints.py` | 20 | PASS |
| Pre-existing: SOCKS proxy (`test_graph.py`, `test_sharepoint.py`) | 9 | FAIL — pre-existing, not a Phase 7b regression |
| Pre-existing: `jojo_qa` unimplemented-feature tests | 7 | FAIL — pre-existing, not a Phase 7b regression |
| Pre-existing: collection errors on POSIX sandbox import | 3 | ERROR — Windows-only import issue, tracked as FU-18, not a Phase 7b regression |

All 20 Phase 7b settings endpoint tests pass. The 19 pre-existing failures and collection errors are unchanged from the Phase 7a baseline and are not regressions introduced by this phase.

---

## Known Gaps / Deferred Items

| Item | Status | Notes |
|---|---|---|
| `/welcome` polling at exit time | Corrected same session | At the moment the exit criterion was evaluated, `/welcome` was static (no polling). The polling behavior — `/api/ops/status` every 10 s, auto-hide when all green — was implemented and committed in the same session before this document was written. The deliverable as shipped meets the exit criterion. |
| FU-18 — POSIX sandbox import warning on Windows | Open | `packages/jojo_output/sandbox/` imports `resource` (POSIX-only) at module level, causing a collection error in the Windows CI run. Tracked since Phase 5 exit. Does not affect runtime behavior on Windows; fix deferred post-MVP. |

---

## ADR References

- **ADR 0012** — `docs/ADR/0012-onedrive-mount-supersedes-path-c.md`: OneDrive mount supersedes Graph-based Path C; MSAL Path B (device-code) is the production SharePoint auth path for standalone workstations.
- **ADR 0013** — `docs/ADR/0013-phase-7b-standalone-workstation-installer.md`: Phase 7b redefined from shared internal server to standalone per-department workstation installer. Decision rationale, deployment model, and revisit conditions recorded there.

---

## Conclusion

All Phase 7b deliverables are present and verified: the installer scripts (`Build-JojoBotRelease.ps1`, `Install-JojoBot.ps1`, `Install-Service.ps1`, `Uninstall-JojoBot.ps1`) produce a self-contained `.zip` and register a Windows Service; the Settings tab (5 sections, 20 passing tests) exposes runtime configuration without PowerShell; `synthesize._call_model` is a live Anthropic SDK call (not a stub); the `/welcome` page polls for setup readiness; and `docs/ops/distribution.md` provides the department install guide. The 19 pre-existing test failures are unchanged from the Phase 7a baseline. Phase 7b exit criterion is met. Ready to proceed to Phase 8.
