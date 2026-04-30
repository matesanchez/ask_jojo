# Phase 3 Execution Prompt

Paste this prompt verbatim at the start of a fresh Cowork or Claude Code session to execute Phase 3 from start to finish.

---

## PROMPT (copy everything below this line)

---

You are implementing Phase 3 of JoJo Bot v2.0 for Nurix Therapeutics. Read this entire prompt before writing a single line of code.

## Context

JoJo Bot is a three-repo project:
- `ask_jojo/` — the app (FastAPI backend + Next.js frontend + Python packages). **This is the repo you are working in.**
- `ask_jojo_wiki/` — the compiled wiki (138 markdown pages, sibling directory on disk)
- `ask_jojo_raw/` — the raw source snapshots (immutable, sibling directory on disk)

Workspace root on disk: `C:\Users\mdelosrios\Claude_Local\jojo_bot_v2.0\`

Phase 0 (scaffolding), Phase 1 (ingest), and Phase 2 (wiki compile) are **complete**. You are starting Phase 3.

## Your first actions

Before writing any code:

1. Read `ask_jojo/docs/phase-3-impl-plan.md` in full. That document is your specification. Every endpoint shape, component structure, test requirement, and commit message format is defined there. Do not deviate from it without flagging the deviation.

2. Read `ask_jojo/src/frontend/app/(tabs)/raw/page.tsx` in full. This is the primary code reference for the frontend — the Wiki tab and Ops tab must match its architecture, naming conventions, and CSS class prefix pattern (`wiki-` and `ops-` respectively instead of `raw-`).

3. Read `ask_jojo/src/backend/routers/raw_router.py` to understand the backend pattern for file-serving endpoints.

4. Read `ask_jojo/src/backend/routers/ingest_router.py` to understand how the RQ job queue is accessed.

5. Read `ask_jojo/packages/jojo_core/config.py` to understand how to call `config.get(key, default)`.

6. Skim `ask_jojo/tests/test_raw_endpoints.py` to see the test fixture and assertion patterns to follow.

Only after reading all six files should you begin implementation.

## What you are building

Five steps in this order. Complete and commit each step before starting the next. The test suite (`ruff` + `pytest`) must be clean after each commit.

### Step 1 — `wiki_router.py` (backend)

File: `ask_jojo/src/backend/routers/wiki_router.py`

Replace all 501 stubs. Implement:
- `GET /api/wiki/tree`
- `GET /api/wiki/page` (query param `path`)
- `GET /api/wiki/backlinks` (query param `slug`)
- `GET /api/wiki/search` (query param `q`, minimum 2 chars, return ≤20 results)
- `GET /api/wiki/stats`
- `POST /api/wiki/edit` — feature-flagged: check `config.get("anthropic_api_key", None)`; if absent return `{ "status": "api_key_required", "message": "..." }` with HTTP 200; if present call Claude Sonnet and return proposed diff. Keep the write-back (`PATCH /api/wiki/page`) as a 501 stub with message "Write-back coming in Phase 3 final pass".

The wiki root path is read via `config.get("wiki_root", str(Path(__file__).resolve().parents[4] / "ask_jojo_wiki"))`. Adjust the relative path resolution to match the actual disk layout.

Path traversal guard: any `page` path that resolves outside `wiki_root` after `Path.resolve()` must return HTTP 400.

Tests: create `ask_jojo/tests/test_wiki_endpoints.py`. Fixture: a temporary directory with 3 sample wiki pages (include proper YAML frontmatter), a `_backlinks.json`, and a `_index.md`. All cases listed in the spec document.

Commit message: `feat(wiki-api): implement wiki_router /tree /page /backlinks /search /stats /edit`

---

### Step 2 — `wiki/page.tsx` (frontend, tree + preview + metadata)

File: `ask_jojo/src/frontend/app/(tabs)/wiki/page.tsx`
New file: `ask_jojo/src/frontend/app/(tabs)/wiki/types.ts`

Build the three-pane Wiki IDE. Replace the "Phase 1 coming soon" placeholder entirely.

Architecture rules:
- `"use client"` directive at top (same as `raw/page.tsx`)
- All state local to the page component, no Zustand yet
- Poll `/api/wiki/stats` every 15s for the page count badge (same `setInterval` pattern as Raw tab)
- No polling on tree or page content — fetch on mount, re-fetch on selection

Top bar: search input (debounced 300ms, calls `/api/wiki/search?q=`), result dropdown, "Request edit from JoJo" button (disabled if no page selected), page count badge.

Left pane: collapsible directory tree grouped by type directory. Each file node shows title + confidence badge. Confidence badge colours: `high` = `wiki-badge-high` (green), `medium` = `wiki-badge-medium` (yellow), `low` = `wiki-badge-low` (red).

Center pane: render body via `react-markdown` + `remark-gfm`. Wikilink resolution: pre-process the body string with a regex before passing to ReactMarkdown — replace `[[slug|label]]` with `[label](#wiki:slug)` and `[[slug]]` with `[slug](#wiki:slug)`. Add an `onClick` handler on the wrapping `<article>` that intercepts `href` values starting with `#wiki:`, extracts the slug, and calls `setSelectedSlug(slug)`.

Right pane (two sections):
1. Metadata: title, type, confidence, corpus, last_updated, last_reviewed, schema_version, tags, aliases. Each entry in `sources[]` renders as a clickable button that sets `localStorage.setItem("rawSelectedId", source.hash)` and navigates to `/raw`.
2. Backlinks: loads `/api/wiki/backlinks?slug=<current>`, renders list. Each entry is clickable and loads that page.

Install dependencies first:
```
cd ask_jojo/src/frontend
npm install remark-wiki-link rehype-highlight highlight.js
```

No new backend tests needed for this step (backend was tested in Step 1). Do add `types.ts` with all TypeScript interfaces.

Commit message: `feat(wiki-tab): three-pane Wiki IDE — tree, preview, metadata, backlinks`

---

### Step 3 — "Request edit from JoJo" modal

File: `ask_jojo/src/frontend/app/(tabs)/wiki/page.tsx` (extend the existing file)

Add the edit modal as a component within the same file (or a new `EditModal.tsx` in the same directory — your call based on line count).

Modal states:
1. **Idle** — textarea for the instruction, "Ask JoJo" button
2. **Loading** — spinner, textarea and button disabled
3. **api_key_required** — display the message from the API response, with a link to "configure in Ops tab"
4. **Proposed** — side-by-side diff rendered line-by-line (changed lines: old=red background, new=green background; unchanged=default). "Reject" button closes modal. "Accept" button is rendered but disabled with tooltip "Write-back coming soon".
5. **Error** — API call failed, show error message with "Try again" button

The "Request edit from JoJo" button in the top bar triggers this modal. It is disabled when no page is currently selected.

No new backend work needed. No new tests needed (modal is UI-only; the API endpoint was tested in Step 1).

Commit message: `feat(wiki-tab): Request edit from JoJo modal with diff view`

---

### Step 4 — `ops_router.py` (backend)

File: `ask_jojo/src/backend/routers/ops_router.py`

Replace all 501 stubs. Implement:
- `GET /api/ops/status` — combined wiki stats + connector health + api_key_configured + queue depth. Reuse the helper functions from `wiki_router.py` (stats) and `ingest_router.py` (connector status + manifest summary) — import them rather than re-implementing.
- `GET /api/ops/jobs` — thin proxy over `/api/ingest/jobs` data
- `POST /api/ops/absorb` — return `{ "job_id": "absorb-<iso-timestamp>", "status": "logged", "message": "Absorb queued. Run the Cowork absorb session to process." }`. Do not attempt to enqueue a real RQ job — that's the API-key-dependent path that lands when `jojo_compile absorb` is wired.
- `GET /api/ops/events` — SSE heartbeat stream (emit `event: heartbeat\ndata: {}\n\n` every 10s). Use `starlette.responses.StreamingResponse` with an async generator.

Tests: create `ask_jojo/tests/test_ops_endpoints.py`. Cases: status returns correct shape, absorb returns logged status, jobs returns list, events returns text/event-stream content type, api_key_configured is False when env absent.

Commit message: `feat(ops-api): implement ops_router /status /absorb /jobs /events`

---

### Step 5 — `ops/page.tsx` (frontend)

File: `ask_jojo/src/frontend/app/(tabs)/ops/page.tsx`

Replace the Phase 3/6 placeholder. Build the Ops dashboard. Poll `/api/ops/status` every 15s (same pattern as Raw tab). Subscribe to `/api/ops/events` via the `EventSource` API for live job updates.

Sections (top to bottom):

1. **Wiki Health card** — total_pages, last commit sha (8 chars), last commit date, schema version. Data from `status.wiki`.

2. **Connector Health row** — four badges (onedrive, publicdrive, sharepoint, drive). Use the same `connectorStatusClass()` helper logic as the Raw tab (copy the function — don't import across tabs). Each badge shows `last_synced` on hover tooltip.

3. **API Key status row** — green check or yellow warning as described in the spec.

4. **Job Queue panel** — pending count, failed count, "Trigger Absorb" button. On click: `POST /api/ops/absorb`, show the returned message in an inline banner below the button for 5 seconds, then clear. SSE job updates received via `EventSource` update the pending/failed counts in real time without polling.

5. **Recent Jobs list** — last 20 jobs from `/api/ops/jobs`. Status badge per job (queued/started/finished/failed). Failed jobs expandable for error detail.

6. **Phase 6 placeholder cards** — two cards at the bottom, labeled "Lint History — Phase 6 coming soon" and "Review Queue — Phase 6 coming soon". Use CSS class `ops-phase6-placeholder` so they can be found and filled in easily.

No new backend tests needed for this step.

Commit message: `feat(ops-tab): Ops dashboard — wiki health, connectors, job queue`

---

### Final step — Update status tracker

File: `ask_jojo/docs/v2_status.md`

1. In the Phase Summary table: mark Phase 3 exit-criterion-met with today's date.
2. In the Phase 3 deliverables checklist: tick all completed items.
3. In the Phase 3 Notes: add a dated entry summarising what was shipped.
4. In the Snapshot table at the top: advance current phase to "Phase 4 — Q&A over the Wiki" and update "Last updated".

Commit message: `status: close Phase 3, open Phase 4 (<date>)`

---

## Invariants — do not violate these

- **Do not touch v1.0 behavior.** The existing chat interface, session store, and ÄKTA Q&A path must continue to work unchanged. Do not modify `chat_router.py`, the v1.0 RAG path, or any file under the v1.0 namespace.
- **Do not write to `ask_jojo_wiki/` or `ask_jojo_raw/`.** Those repos are read-only from the app's perspective during Phase 3.
- **Do not push to GitHub.** Mateo reviews and pushes manually.
- **Commit after each step.** Use `git -c user.email='cowork@anthropic.com' -c user.name='Cowork' commit`. Never combine two steps in one commit.
- **Every `.ps1` file must remain pure ASCII** (no em-dashes, smart quotes, or non-ASCII characters — CP1252 / PowerShell 5.1 parser requirement). You are not writing any new `.ps1` files in this phase, but if you touch existing ones for any reason, verify ASCII.
- **`ruff` + `pytest` must be green before each commit.** Run `ruff check . && pytest` from `ask_jojo/` before committing.
- **Path traversal guard** on all endpoints that accept a `path` query parameter.

## When you are done

Report back with:
1. A list of all files created or modified
2. The git log of the commits made (short format)
3. Any deviations from the spec and why
4. Any blockers or questions for Mateo before Phase 4 begins
