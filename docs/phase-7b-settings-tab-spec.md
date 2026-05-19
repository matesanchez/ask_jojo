# Settings Tab — Implementation Spec

**Phase:** 7b (standalone shared-computer install)
**Status:** Spec — to be implemented during the /goal run
**Author:** Mateo + Claude, 2026-05-19

## Purpose

The Settings tab is the runtime configuration surface for a shared-computer
JoJo Bot install. It replaces the developer-mode `jojo-core config set ...`
CLI for end users (department staff, scientists, anyone without comfort in
PowerShell). Every setting that the deployed app needs to function — API
keys, Graph auth, connector paths, lint cadence — is editable from this one
tab.

The design constraint that shapes everything: the user of the shared
workstation may not be the person who installed it. The tab must be
self-documenting, validate inputs aggressively, and never silently
truncate or corrupt config.

## Information architecture

One tab, five sections, stacked vertically with anchor links in a left
rail (`#api-key`, `#models`, `#graph`, `#connectors`, `#lint`). Right
column is a fixed "Status" sidebar showing whether each section is
configured correctly (green check / yellow warning / red error). The
sidebar polls `/api/settings/status` every 10 seconds.

```
+----------------------------------+--------------------------+
|  [Settings nav]   API key        |  Status                  |
|                   Models         |  --------                |
|                   Graph auth     |  API key:     [check]    |
|                   Connectors     |  Models:      [check]    |
|                   Lint cadence   |  Graph:       [warn]     |
|                                  |  Connectors:  [check]    |
|  +---  API key  -----------+     |  Lint:        [check]    |
|  | Anthropic key field     |     |                          |
|  | [Test connection]       |     |  Restart server          |
|  +-------------------------+     |  [restart]               |
|  ...                              |                          |
+----------------------------------+--------------------------+
```

## Section 1 — Anthropic API key

**Component:** `<ApiKeySection />` in
`src/frontend/components/settings/ApiKeySection.tsx`.

### Fields

- **API key** (password input)
  - Placeholder: `sk-ant-api03-...`
  - Masked by default; toggle eye icon to reveal.
  - On blur: client-side validate `^sk-ant-(api|admin)[0-9]{2}-[A-Za-z0-9_-]{60,}$`.
  - On submit: POST `/api/settings/anthropic-key` with `{ key }`.
- **Test connection** button (secondary)
  - POST `/api/settings/test-anthropic` with the (in-memory or saved) key.
  - Spinner during request, then green check + "Sonnet 4.6 responded in
    234 ms" or red error with the exact message from the API.

### Behavior

- The field is empty by default after install. Once a key is saved, the
  field re-loads showing `sk-ant-...XXXX` (last 4 chars only); editing
  the field clears it and requires re-entry.
- `Test connection` works on either an unsaved-in-field key or the
  saved-and-masked one — both round-trip through the same endpoint.
- Save button is disabled until the field has a value matching the
  regex.
- After a successful save, a toast appears: "API key saved. JoJo Bot
  will use this key for all model calls."

### Backend contract

`POST /api/settings/anthropic-key`
  - Body: `{ key: string }`
  - Validates length + prefix.
  - Stores via `jojo_core.config.set(KEY_ANTHROPIC_API_KEY, key)` —
    DPAPI-encrypted on Windows, plaintext fallback elsewhere.
  - Returns `{ ok: true, masked: "sk-ant-...XXXX" }`.

`POST /api/settings/test-anthropic`
  - Body: `{ key?: string }` — if absent, uses the saved key.
  - Calls `anthropic.Anthropic(api_key=k).messages.create(...)` with a
    10-token prompt against Sonnet 4.6.
  - Returns `{ ok: true, model: "claude-sonnet-4-6", latency_ms: 234 }`
    or `{ ok: false, error: "..." }`.

`GET /api/settings/anthropic-key`
  - Returns `{ configured: bool, masked: "sk-ant-...XXXX" | null }`.
  - Never returns the unmasked key.

## Section 2 — Model tier

**Component:** `<ModelsSection />`.

### Fields

- **Default tier** (radio group)
  - Haiku 4.5 — "Fastest, cheapest. Best for routing and simple
    queries."
  - Sonnet 4.6 — "Balanced. Default for Q&A synthesis." (default)
  - Opus 4.6 — "Highest quality. Best for contradiction checks and
    complex syntheses. Most expensive."
- **Per-task overrides** (table)
  - Rows: `synthesis`, `nightly-lint`, `weekly-contradiction`,
    `compile-absorb`, `format-classify`.
  - Each row: dropdown of [Haiku 4.5, Sonnet 4.6, Opus 4.6].
  - Defaults match `docs/budget-model.xlsx`: synthesis = Sonnet,
    nightly-lint = Sonnet, weekly-contradiction = Opus,
    compile-absorb = Sonnet, format-classify = Haiku.

### Backend contract

`GET /api/settings/models` and `POST /api/settings/models` over
`{ default_tier, per_task: {...} }` stored under
`KEY_MODEL_DEFAULT_TIER` + `KEY_MODEL_PER_TASK` (new keys to add to
`packages/jojo_core/config.py`).

## Section 3 — MS Graph authentication

**Component:** `<GraphAuthSection />`.

### Fields

- **Auth mode** (radio group)
  - "Pasted token (Path A)" — short-lived, ~60 min.
  - "Device-code login (Path B)" — long-lived, ~90 days. (default)
- **(Path A)** Pasted token (password input + paste button)
  - Validate JWT shape client-side (`eyJ...` and 3 base64-url-safe
    segments).
  - Save button POSTs to `/api/settings/graph-token`.
- **(Path B)** "Run device-code login" button
  - Spawns the helper subprocess (`python -m jojo_ingest auth
    device-code`) via `/api/settings/start-device-code`.
  - Modal opens showing the device code + verification URL +
    countdown. Polls `/api/settings/device-code-status` every 2s.
  - On completion: modal shows "Login complete, cache valid until
    YYYY-MM-DD" and closes after 3s.
- **Tenant ID** + **Client ID** (advanced; collapsed by default)
  - Pre-populated with defaults `1c966021-d551-45e4-89a5-849f81b69208`
    + `14d82eec-204b-4c2f-b7e8-296a70dab67e`. Most users never touch
    these.

### Backend contract

`GET /api/settings/graph` returns
`{ mode: "device-code" | "pasted", configured: bool, cache_expires: ISO
| null }`.

`POST /api/settings/graph-token` (Path A) stores under
`KEY_GRAPH_ACCESS_TOKEN`.

`POST /api/settings/start-device-code` spawns the MSAL flow in a
background task. Returns `{ task_id, user_code, verification_uri,
expires_at }`.

`GET /api/settings/device-code-status?task_id=...` returns
`{ status: "pending" | "complete" | "failed" | "timeout",
   cache_expires: ISO | null }`.

## Section 4 — Connector paths

**Component:** `<ConnectorPathsSection />`.

### Fields

- **OneDrive sync path** (text input with "Browse" button)
  - Default: `C:\Users\<current-user>\OneDrive - Nurix Therapeutics`.
  - Validation: path exists + readable + contains at least one `.docx`
    or `.pptx` or `.xlsx` somewhere in its tree (sanity check —
    confirms it's actually a synced OneDrive folder, not an empty
    placeholder).
- **Public drive path** (text input with "Browse" button)
  - Default: `P:\` (the Nurix SMB drive mapping).
  - Validation: path exists + readable.
- **SharePoint sites** (textarea, one URL per line)
  - Default empty. The OneDrive mount covers most cases; this is
    here for the rare SharePoint site that isn't synced locally.
  - Validation: each line parses as a SharePoint URL via
    `normalize_site_url` from `packages/jojo_ingest/graph.py`.

### Backend contract

`GET /api/settings/connectors` and `POST /api/settings/connectors`.
The "Browse" button calls `/api/settings/browse-folder` which opens a
Tkinter folder picker (or whatever native FS dialog the host OS
provides) — the FastAPI host process spawns it, returns the chosen
path. (This is one of the trickier pieces; an alternative is to skip
the picker and rely on paste-the-path.)

## Section 5 — Lint cadence

**Component:** `<LintCadenceSection />`.

### Fields

- **Nightly lint time** (time picker, 24h format)
  - Default 02:00.
  - Saves to `KEY_LINT_NIGHTLY_TIME`.
- **Weekly contradiction-check day + time** (day-of-week dropdown +
  time picker)
  - Default: Sunday 04:00.
  - Saves to `KEY_LINT_WEEKLY_DAY` + `KEY_LINT_WEEKLY_TIME`.
- **Enable nightly lint** (toggle, default on)
- **Enable weekly Opus pass** (toggle, default on; disables itself
  with a warning if no API key is configured)

### Backend contract

`GET /api/settings/lint` and `POST /api/settings/lint` round-trip the
above. On save, the backend re-registers the Windows Scheduled Tasks
via `ops/scheduler/Register-JojoBotTasks.ps1` (called as a subprocess
with the new cadence args).

## Status sidebar

Polls `/api/settings/status` every 10 seconds. The endpoint aggregates
across all five sections and returns:

```json
{
  "api_key":     { "ok": true,  "detail": "Sonnet 4.6 last ping 234ms" },
  "models":      { "ok": true,  "detail": "default Sonnet 4.6" },
  "graph":       { "ok": false, "detail": "device-code cache expired" },
  "connectors":  { "ok": true,  "detail": "OneDrive ok (38,728 files), publicdrive ok" },
  "lint":        { "ok": true,  "detail": "nightly 02:00, weekly Sun 04:00" }
}
```

Green check / yellow warning / red error rendered per section.
Clicking a row scrolls to and highlights that section.

## Restart server button

Bottom-right of the sidebar. POSTs to `/api/ops/restart`. The endpoint
sends SIGTERM to itself after a short delay (so it can return 200 first);
the Windows Service supervisor restarts the process automatically. The
client-side button shows a spinner + "Restarting..." for 10 seconds and
then refreshes the page.

## Frontend state

- Each section is its own React component with local `useState` for
  form fields.
- On mount, each calls its `GET /api/settings/<section>` to populate.
- "Dirty" indicator (small dot) appears next to the section title if
  the form has unsaved changes.
- Save button is per-section, not global.
- A global confirm-on-leave dialog warns if any section is dirty when
  the user clicks away from the tab.

## Acceptance tests

- [ ] Fresh-install flow: open Settings, paste API key, click Test
  connection, see green check; click "Run device-code login", complete
  the MSAL flow, see green check; reload Settings tab, all fields
  re-populate with masked/saved values.
- [ ] Invalid key: paste `not-a-real-key`, Test connection returns
  401 with the actual Anthropic error message.
- [ ] Device-code cancellation: start the flow, close the modal,
  status reverts to "no cache."
- [ ] Cadence change: change nightly lint from 02:00 to 03:00, click
  save, verify via `schtasks /query /tn "\JojoBot\nightly-lint"` that
  the schedule actually changed.
- [ ] Status sidebar updates: stop the local `python -m jojo_ingest
  auth ...` cache file, watch sidebar flip Graph from green to red
  within 10 seconds.
- [ ] Restart server: click restart, browser shows spinner for 10s,
  page reloads, sidebar returns to green.

## Out of scope

- Per-user accounts within an install. The Settings tab edits the
  install-wide config; everyone using the shared workstation sees the
  same settings.
- Cloud-synced config (e.g., dept settings stored in OneDrive). Not
  needed for MVP; revisit if departments report wanting cross-machine
  config replication.
- Audit log of who changed what. Add later if compliance asks for it.
