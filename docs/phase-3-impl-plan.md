# Phase 3 Implementation Plan — JoJo Bot IDE Tabs

**Status:** In progress (opened 2026-04-30)
**Phase in roadmap:** Phase 3 — JoJo Bot IDE Tabs (Wiki / Raw / Ops) per `docs/ADR/0000-v2-roadmap.md` §6
**Estimate:** 4–6 weeks
**Author:** Mateo de los Rios + Cowork

---

## Scope

Build the two remaining IDE tabs so scientists can browse the compiled wiki and monitor system health entirely inside JoJo Bot.

**In scope:**
- Sub-phase 3a — Wiki tab (backend router + frontend page + "Request edit from JoJo" diff flow)
- Sub-phase 3b — Ops tab (backend router + frontend page)

**Already done — do not re-implement:**
- Raw tab — fully shipped in Phase 1c (`src/frontend/app/(tabs)/raw/page.tsx`). Use it as the primary code and style reference throughout this phase.

**Deferred to Phase 6 — leave as stubs:**
- Manual override monaco editor in the Wiki tab
- Per-page `<LintBadge>` showing outstanding lint issues
- Review queue and lint history dashboard in the Ops tab
- Contradiction / staleness / orphan report panes

---

## Pre-conditions (already true — verify before starting)

| Item | Location |
| --- | --- |
| Three-pane Raw tab in production | `src/frontend/app/(tabs)/raw/page.tsx` |
| Header nav with `/wiki` and `/ops` route anchors | `src/frontend/app/layout.tsx` |
| `wiki_router.py` stub returning 501s | `src/backend/routers/wiki_router.py` |
| `ops_router.py` stub returning 501s | `src/backend/routers/ops_router.py` |
| `ask_jojo_wiki/` on disk with `_index.md`, `_backlinks.json`, page files | sibling repo |
| `react-markdown` + `remark-gfm` already in `package.json` | `src/frontend/package.json` |
| `config.get(key, default)` in `jojo_core` | `packages/jojo_core/config.py` |
| RQ job queue wired via `ingest_router.py` | `src/backend/routers/ingest_router.py` |

---

## Sub-phase 3a — Wiki Tab

### Step 1 — Backend: `wiki_router.py`

Replace the 501 stubs in `src/backend/routers/wiki_router.py` with real implementations.
All endpoints are **read-only file operations** — no Claude API calls, no external network.
The wiki root path is read via `config.get("wiki_root", "../ask_jojo_wiki")`.

#### Endpoint: `GET /api/wiki/tree`

Returns the full directory tree of the wiki, grouped by type directory (targets, programs,
methods, etc.), suitable for rendering a collapsible file tree.

Response shape:
```json
{
  "tree": [
    {
      "kind": "dir",
      "name": "targets",
      "children": [
        {
          "kind": "file",
          "slug": "cbl-b",
          "title": "CBL-B (Casitas B-lineage Lymphoma B)",
          "type": "target",
          "path": "targets/cbl-b.md",
          "confidence": "high",
          "last_updated": "2026-04-29"
        }
      ]
    }
  ],
  "total_pages": 138
}
```

Implementation notes:
- Walk `ask_jojo_wiki/` with `pathlib.Path.rglob("*.md")`
- Skip `_index.md`, `_backlinks.json`, `README.md`, `SCHEMA.md`, `_needs_review.md`
- Parse YAML frontmatter from each file (`---` block) to extract `slug`, `title`, `type`, `confidence`, `last_updated`
- Group by the first path segment (directory name), sort directories alphabetically, sort files by `title` within each directory
- Return a nested structure mirroring `raw_router.py`'s `/tree` response shape

#### Endpoint: `GET /api/wiki/page`

Query param: `path` (e.g. `targets/cbl-b.md` or `targets/cbl-b`)

Returns the page body and parsed frontmatter.

Response shape:
```json
{
  "path": "targets/cbl-b.md",
  "slug": "cbl-b",
  "title": "CBL-B (Casitas B-lineage Lymphoma B)",
  "type": "target",
  "confidence": "high",
  "last_updated": "2026-04-29",
  "last_reviewed": "2026-04-29",
  "schema_version": "0.1.0",
  "corpus": "protein-sciences",
  "tags": ["target", "e3-ligase"],
  "aliases": ["CBL-B", "Cbl-b"],
  "related": ["[[del-screening|DEL Screening]]"],
  "sources": [
    { "path": "raw/onedrive/...", "hash": "abc123", "ingested": "2026-04-29" }
  ],
  "body": "## Overview\n\nCBL-B is..."
}
```

Implementation notes:
- Accept `.md` extension or bare slug — resolve either to the full path
- Path traversal guard: resolved path must be inside `wiki_root`
- Return 404 if file does not exist
- Split frontmatter from body using the same `---` delimiter parsing as `raw_router.py`'s `/file/{id}`

#### Endpoint: `GET /api/wiki/backlinks`

Query param: `slug`

Reads `_backlinks.json` and returns the list of slugs that link to the given slug.

Response shape:
```json
{
  "slug": "cbl-b",
  "linked_from": ["cbl-b-program", "del-screening", "irak4"]
}
```

Implementation notes:
- Load `_backlinks.json` once at startup or on each call (file is small, on-call read is fine for now)
- Return empty list (not 404) when the slug has no inbound links

#### Endpoint: `GET /api/wiki/search`

Query param: `q` (string, minimum 2 characters)

Searches page titles, slugs, and aliases for the query string (case-insensitive substring match).
Returns up to 20 results. Used for the search box autocomplete in the frontend.

Response shape:
```json
{
  "query": "cbl",
  "results": [
    { "slug": "cbl-b", "title": "CBL-B (Casitas B-lineage Lymphoma B)", "type": "target", "path": "targets/cbl-b.md" },
    { "slug": "cbl-b-program", "title": "CBL-B Program", "type": "program", "path": "programs/cbl-b.md" }
  ]
}
```

Implementation notes:
- Parse `_index.md` for a fast alias + title lookup table, OR just walk all pages (138 pages is cheap)
- Match against `title`, `slug`, and each entry in `aliases`
- No fuzzy matching needed at this scale — simple `q.lower() in field.lower()` is sufficient

#### Endpoint: `GET /api/wiki/stats`

Returns high-level wiki health info. Used by the Ops tab.

Response shape:
```json
{
  "total_pages": 138,
  "last_commit_sha": "61f11eb",
  "last_commit_message": "Checkpoint 36: add 8 DEL target pages…",
  "last_commit_date": "2026-04-30T00:00:00Z",
  "schema_version": "0.1.0",
  "index_page_count": 138
}
```

Implementation notes:
- Run `git -C <wiki_root> log -1 --format="%H|%s|%cI"` via `subprocess.run` to get last commit info
- Count pages by walking the filesystem (same walk as `/tree`)
- Parse `schema_version` from `SCHEMA.md` frontmatter in the wiki root

#### Endpoint: `POST /api/wiki/edit`

Body:
```json
{ "path": "targets/cbl-b.md", "instruction": "Add a note that NX-1607 reduces PSA in mCRPC patients." }
```

Response (when API key is configured):
```json
{
  "status": "proposed",
  "path": "targets/cbl-b.md",
  "diff": "--- a/targets/cbl-b.md\n+++ b/targets/cbl-b.md\n@@...",
  "proposed_body": "## Overview\n\n..."
}
```

Response (when API key is NOT configured):
```json
{ "status": "api_key_required", "message": "Configure JOJO_API_KEY (or set it in config.json) to enable JoJo-written edits." }
```

Implementation notes:
- Check `config.get("anthropic_api_key", None)` — if absent, return the `api_key_required` response with HTTP 200 (not an error — the UI will show a nudge, not a crash)
- When the key IS present: read the target page, build a Sonnet prompt asking it to apply the instruction and return the full revised body, compute a unified diff between original and proposed body, return both
- Use `difflib.unified_diff` for the diff — no external deps
- Write-through (accepting the diff and committing) is a follow-on step handled client-side via a separate `PATCH /api/wiki/page` endpoint — keep this endpoint proposal-only for now
- Stub `PATCH /api/wiki/page` as 501 "Page write-back coming in Phase 3 final pass" — the Accept button in the UI will be grayed out until that lands

#### Tests for `wiki_router.py`

Create `tests/test_wiki_endpoints.py`. Pattern: use `pytest` + `httpx.AsyncClient` with `app` from `src/backend/main.py`, fixture a fake wiki directory with 3–5 sample pages.

Required test cases:
- `GET /api/wiki/tree` returns correct grouped structure
- `GET /api/wiki/page?path=targets/cbl-b.md` returns correct frontmatter + body
- `GET /api/wiki/page?path=targets/cbl-b` (no extension) resolves correctly
- `GET /api/wiki/page?path=../../../etc/passwd` returns 400 (traversal guard)
- `GET /api/wiki/page?path=targets/nonexistent.md` returns 404
- `GET /api/wiki/backlinks?slug=cbl-b` returns correct linked_from list
- `GET /api/wiki/backlinks?slug=orphan-page` returns empty list (not 404)
- `GET /api/wiki/search?q=cb` returns pages matching title or alias
- `GET /api/wiki/search?q=x` (1 char) returns 400
- `GET /api/wiki/stats` returns dict with `total_pages` and `last_commit_sha`
- `POST /api/wiki/edit` without API key returns `api_key_required` status
- Existing 501 smoke tests for `/api/wiki/tree` etc. should be removed or updated

---

### Step 2 — Frontend: `src/frontend/app/(tabs)/wiki/page.tsx`

Replace the Phase 1 placeholder with a full three-pane IDE view.

**Model closely on `raw/page.tsx`** — same layout structure, same polling pattern, same CSS class naming conventions (replace `raw-` prefix with `wiki-`). Read raw/page.tsx in full before writing a single line of wiki/page.tsx.

#### Layout

```
[ top bar: search box | "Request edit from JoJo" button | page count badge ]
[ tree pane | markdown preview pane | metadata/backlinks pane ]
```

No bottom status bar needed (the wiki doesn't have connector sync jobs).

#### Top bar

- Search `<input>` that calls `GET /api/wiki/search?q=<value>` (debounced 300ms) and renders results as a dropdown (max 20 items). Clicking a result selects that page in the tree and loads it in the preview pane.
- "Request edit from JoJo" button — opens the edit modal (see Step 3 below). Disabled when no page is selected.
- Page count badge (e.g. "138 pages") pulled from `/api/wiki/stats`.

#### Left pane — Tree

Same collapsible directory tree as the Raw tab. Each leaf node shows:
- Page title (from frontmatter, not filename)
- A confidence badge: `high` → green, `medium` → yellow, `low` → red, no badge if absent

Clicking a leaf loads that page.

Top-level directories correspond to the wiki taxonomy directories: `targets`, `programs`, `methods`, `platforms`, `concepts`, `decisions`, `equipment`, `references`, `protocols`. An `other` bucket catches anything not in a known directory.

#### Center pane — Markdown preview

Render the page body with:
- `react-markdown` + `remark-gfm` (already in package.json)
- Wikilink resolution: `[[slug|label]]` and `[[slug]]` patterns should render as clickable links that load the target page within the Wiki tab. Implement this as a custom remark plugin or a simple regex pre-process that converts `[[slug|label]]` → `[label](#wiki/slug)` and `[[slug]]` → `[slug](#wiki/slug)` before passing to ReactMarkdown. When the fragment href is clicked, intercept it in an `onClick` handler on the article element and call `setSelectedSlug(slug)`.
- Code blocks with syntax highlighting (rehype-highlight is in the roadmap — add it if not already in package.json)
- Tables via remark-gfm (already enabled)

Show the page `title` as an `<h1>` above the body (the markdown body itself starts with `## Overview` — don't duplicate the title).

#### Right pane — Metadata & Backlinks

Two sections, vertically stacked:

**Metadata section** (top ~60% of pane):
```
Title: CBL-B (Casitas B-lineage Lymphoma B)
Type: target
Confidence: high ●
Corpus: protein-sciences
Last updated: 2026-04-29
Last reviewed: 2026-04-29
Schema: 0.1.0
Tags: target, e3-ligase, cbl-b, clinical-stage
Aliases: CBL-B, Cbl-b, NX-1607
```
Each source in `sources[]` renders as a clickable entry that navigates to the Raw tab at that file's entry_id. The Raw tab already supports deep-linking via URL — the wiki tab should set `localStorage.setItem("rawSelectedId", source.hash)` (or use a URL query param) so the Raw tab can pick it up on navigation.

**Backlinks section** (bottom ~40% of pane):
Loads `GET /api/wiki/backlinks?slug=<current-slug>` and shows:
```
Linked from (3):
  • CBL-B Program  →  programs/cbl-b.md
  • DEL Screening  →  programs/del-screening.md
  • IRAK4          →  targets/irak4.md
```
Each entry is clickable and loads that page.

#### Types file

Create `src/frontend/app/(tabs)/wiki/types.ts` with TypeScript interfaces for all API response shapes:
`WikiTreeResponse`, `WikiTreeNode`, `WikiTreeDir`, `WikiTreeFile`, `WikiPage`, `WikiSearchResult`, `WikiSearchResponse`, `WikiStats`, `WikiEditResponse`, `WikiBacklinksResponse`.
Model on `src/frontend/app/(tabs)/raw/types.ts`.

---

### Step 3 — "Request edit from JoJo" diff flow

This is a modal within `wiki/page.tsx` triggered by the "Request edit from JoJo" button.

#### Modal structure

```
┌─────────────────────────────────────────────────────────┐
│  Request an edit to: CBL-B (Casitas B-lineage Lymphoma B)│
│                                                         │
│  Describe the change you'd like JoJo to make:          │
│  ┌───────────────────────────────────────────────────┐  │
│  │ Add a note that clinical PSA reduction in mCRPC   │  │
│  │ patients is not replicated in LnCaP in vitro.     │  │
│  └───────────────────────────────────────────────────┘  │
│                                              [Ask JoJo]  │
│                                                         │
│  ── Proposed changes ──────────────────────────────────  │
│  [side-by-side diff renders here after JoJo responds]   │
│                                                         │
│                              [Reject]  [Accept ✓ (soon)] │
└─────────────────────────────────────────────────────────┘
```

#### Behaviour

- "Ask JoJo" → `POST /api/wiki/edit` with `{ path, instruction }`
- If response is `api_key_required`: replace the diff area with: "JoJo can propose edits once the Anthropic API key is configured in Ops → Settings. The edit request has been logged."
- If response is `proposed`: render a side-by-side diff. Each changed line shows old (red background) and new (green background). Use a simple line-by-line diff render — no external diff library needed at this scale.
- "Reject" → close the modal with no changes
- "Accept" → grayed out with tooltip "Write-back coming in Phase 3 final pass" until `PATCH /api/wiki/page` is implemented. When it is: `PATCH /api/wiki/page` with `{ path, body: proposed_body }`, backend writes the file, runs `git commit`, returns new commit sha. On success close modal and reload the page preview.

---

## Sub-phase 3b — Ops Tab

### Step 4 — Backend: `ops_router.py`

Replace the 501 stubs in `src/backend/routers/ops_router.py`.

#### Endpoint: `GET /api/ops/status`

Returns a combined health snapshot for the Ops dashboard.

Response shape:
```json
{
  "wiki": {
    "total_pages": 138,
    "last_commit_sha": "61f11eb",
    "last_commit_date": "2026-04-30T00:00:00Z",
    "last_commit_message": "Checkpoint 36: add 8 DEL target pages…"
  },
  "connectors": [
    { "name": "onedrive", "status": "ready", "last_synced": "2026-04-30T06:00:00Z", "file_count": 38728 },
    { "name": "publicdrive", "status": "ready", "last_synced": "2026-04-30T06:00:00Z", "file_count": 99019 },
    { "name": "sharepoint", "status": "needs-token", "last_synced": null, "file_count": 1199 },
    { "name": "drive", "status": "ready", "last_synced": "2026-04-30T06:00:00Z", "file_count": 1426 }
  ],
  "api_key_configured": false,
  "queue": {
    "pending": 0,
    "failed": 0,
    "recent_jobs": []
  }
}
```

Implementation notes:
- Reuse `/api/wiki/stats` logic to populate the `wiki` section (call the stats helper function, don't duplicate)
- Reuse `/api/ingest/connectors` + `/api/raw/manifest` logic for connector health — pull from existing ingest_router helpers rather than re-implementing
- `api_key_configured`: `config.get("anthropic_api_key", None) is not None`
- `queue` section: read from RQ if available, fall back to an empty struct if Redis isn't reachable (same pattern as ingest_router)

#### Endpoint: `GET /api/ops/jobs`

Returns recent jobs from the RQ queue (same data as `/api/ingest/jobs` but with wiki-compile job types included when they exist). For now this is a thin proxy over the ingest jobs list.

Response shape: same as `GET /api/ingest/jobs`.

#### Endpoint: `POST /api/ops/absorb`

Enqueues a wiki-compile absorb trigger. Because `jojo_compile absorb` is not yet automated (API key pending, ADR 0010), this endpoint:
- Logs a structured entry to `ask_jojo/docs/compile/queue.md`-style log
- Returns a job record with `status: "logged"` and `message: "Absorb queued. Run the Cowork absorb session to process."`
- When API key lands and `jojo_compile absorb` is wired, swap the body to enqueue a real RQ job — the response shape stays identical

Response shape:
```json
{ "job_id": "absorb-2026-04-30T12:00:00", "status": "logged", "message": "Absorb queued. Run the Cowork absorb session to process." }
```

#### Endpoint: `GET /api/ops/events` (SSE)

Server-sent events stream for live job progress. Returns a `text/event-stream` response.

Events emitted:
- `heartbeat` every 10s (keeps the connection alive)
- `job_update` when any job in the queue changes status (poll RQ every 2s internally)

Implementation: use `starlette.responses.StreamingResponse` with an async generator. Pattern is identical to how `ingest_router.py` handles any streaming endpoints — look there first.

#### Tests for `ops_router.py`

Create `tests/test_ops_endpoints.py`.

Required test cases:
- `GET /api/ops/status` returns dict with `wiki`, `connectors`, `api_key_configured`, `queue` keys
- `GET /api/ops/status` — `api_key_configured` is False when env var absent
- `POST /api/ops/absorb` returns `{ status: "logged" }`
- `GET /api/ops/jobs` returns `{ jobs: [...] }`
- 501 smoke tests for the old stubs removed

---

### Step 5 — Frontend: `src/frontend/app/(tabs)/ops/page.tsx`

Replace the Phase 3/6 placeholder with a real Ops dashboard.

**Model on `raw/page.tsx`** — same polling cadence (15s), same `fetchJSON` helper, same error banner pattern.

#### Layout

```
[ Wiki Health ]  [ Connector Health ]  [ API Key status ]

[ Job Queue — with "Trigger Absorb" button ]

[ Recent Jobs list ]

[ Placeholders: Lint History (Phase 6) | Review Queue (Phase 6) ]
```

#### Wiki Health card

Shows: total pages, last compile timestamp ("Checkpoint 36 · 2026-04-30"), last commit SHA (shortened to 8 chars with a "copy" button), schema version.

Data from `GET /api/ops/status` → `wiki` field.

#### Connector Health row

Four badges (onedrive, publicdrive, sharepoint, drive) with the same `connectorStatusClass()` styling from the Raw tab. Copy the badge helper — don't import it (it's in a different page's scope). Each badge shows last-synced time on hover/tooltip.

Data from `GET /api/ops/status` → `connectors` field.

#### API Key status

A simple row:
- ✅ "API key configured — JoJo edits enabled" (green) when `api_key_configured: true`
- ⚠️ "API key not configured — JoJo edits and automated absorb disabled. Set `anthropic_api_key` in config.json." (yellow) when false

Link to `docs/ops/redis-setup.md` for config instructions (or just point to `jojo-core config set`).

#### Job Queue panel

Shows current queue depth (pending + failed counts). A "Trigger Absorb" button that posts to `POST /api/ops/absorb` and shows the returned message in a toast/banner. When API key is not configured, the button label is "Queue Absorb (manual)" and the button is not grayed out — it still enqueues the logged trigger.

#### Recent Jobs list

A scrollable list of the last 20 jobs (from `/api/ops/jobs`), each showing: job type, status badge (queued/started/finished/failed), timestamp, short message. Failed jobs show in red with an expandable error detail.

#### Phase 6 placeholders

Two clearly-labeled placeholder cards at the bottom of the page:
```
┌─────────────────────────────────────┐
│ Lint History  [Phase 6 coming soon] │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│ Review Queue  [Phase 6 coming soon] │
└─────────────────────────────────────┘
```

These are structural placeholders — they exist so Phase 6 can fill them in without changing the page layout.

---

## Dependency notes

`remark-wiki-link` is not yet in `package.json`. Install it:
```bash
cd src/frontend && npm install remark-wiki-link
```

`rehype-highlight` is mentioned in the roadmap for code highlighting. Install it:
```bash
cd src/frontend && npm install rehype-highlight highlight.js
```

All other dependencies (`react-markdown`, `remark-gfm`, `zustand`) are already in `package.json`.

No new Python package dependencies for backend steps.

---

## Commit discipline

Follow the same pattern as Phase 1 — commit each step separately:

```
feat(wiki-api): implement wiki_router GET /tree, /page, /backlinks, /search, /stats
feat(wiki-api): implement POST /wiki/edit with API-key feature flag
feat(wiki-tab): three-pane Wiki IDE with tree, preview, metadata, backlinks
feat(wiki-tab): Request edit from JoJo modal with diff view
feat(ops-api): implement ops_router /status, /absorb, /jobs, /events
feat(ops-tab): Ops dashboard with wiki health, connectors, job queue
chore(phase3): update v2_status.md — Phase 3 exit criterion met
```

Do not combine multiple steps into one commit. The test suite (`ruff` + `pytest`) must be green before each commit.

---

## Exit criterion

Phase 3 is complete when:

1. A new user opens JoJo Bot, navigates to `/wiki`, and can browse all 138 wiki pages via the three-pane IDE without any placeholder text remaining.
2. Clicking a wikilink in a page body navigates to that page within the Wiki tab.
3. Clicking a source in the metadata panel navigates to the Raw tab showing that raw file.
4. The "Request edit from JoJo" button opens the modal; when no API key is configured, a clear nudge is shown rather than an error.
5. Navigating to `/ops` shows real wiki health stats, connector health badges, and a functional "Trigger Absorb" button.
6. The Phase 6 placeholder cards are visible in the Ops tab.
7. All tests pass (`ruff` clean, `pytest` green).
8. No v1.0 behavior is broken.

---

## What is deferred to Phase 6

The following items appear in the roadmap's Phase 3 section but are intentionally deferred because they depend on the lint infrastructure built in Phase 6:

- **Manual override escape hatch** — monaco editor for direct wiki page editing behind a confirmation dialog, with `[manual]` commit prefix and flag for next lint pass
- **Per-page `<LintBadge>`** — confidence/freshness/outstanding-issues badge shown on every wiki page view
- **Review queue in Ops tab** — list of pages flagged `review_pending: true`, sorted by hub-centrality
- **Lint history charts in Ops tab** — orphan count, avg confidence, staleness distribution, contradiction density over time

Leave stubs/placeholders for all four, clearly labeled "Phase 6 coming soon."
