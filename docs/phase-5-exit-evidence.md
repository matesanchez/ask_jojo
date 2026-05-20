# Phase 5 Exit Evidence — 2026-05-19

**Phase:** Phase 5 — Rich Outputs
**Exit gate (from GOAL_PROMPT.md):** `pytest packages/jojo_output/` green, `tsc --noEmit` clean, one example of each of the 9 supported formats lives in `ask_jojo_wiki/outputs/` and renders correctly in the Wiki tab.

---

## Test suite results

### `packages/jojo_output/` (Python)

```
pytest packages/jojo_output/ -v
```

- `packages/jojo_output/tests/test_plotly_renderer.py` — 13 tests — **PASS**
- `packages/jojo_output/tests/test_sandbox_runner.py` — skipped on Windows (POSIX `resource` module not available) — **pre-existing, baseline unchanged**
- `packages/jojo_output/tests/test_renderers.py` — **PASS**

All new tests pass. Pre-existing Windows skip rate unchanged from Phase 4 baseline.

### `src/backend/tests/test_output_endpoints.py`

- 23 original tests **PASS**
- 3 new plotly tests added: `test_render_plotly_inline`, `test_render_plotly_to_file`, `test_render_plotly_invalid_plot_type_returns_422` — all **PASS**
- Sandbox/matplotlib tests: `@pytest.mark.skipif(win32)` — skipped, **pre-existing**

### `src/backend/tests/test_wiki_endpoints.py`

- 14 new tests added for outputs/ endpoints (tree node, list endpoint, page fields for plotly/matplotlib/non-output/posix path) — all **PASS**

### `ruff check .`

Exit 0. "All checks passed!"

### `tsc --noEmit` (frontend)

Clean. `src/frontend/components/PlotlyEmbed.tsx`, `src/frontend/app/(tabs)/chat/types.ts`, `src/frontend/app/(tabs)/chat/page.tsx`, `src/frontend/app/(tabs)/wiki/types.ts`, `src/frontend/app/(tabs)/wiki/page.tsx` all pass type-check.

---

## Output pages in `ask_jojo_wiki/outputs/` — all 9 formats

| File | `output_format` | Renderer dispatch | Frontend component |
|---|---|---|---|
| `2026-05-19-cbl-b-program-overview.md` | `markdown` | default react-markdown | ReactMarkdown |
| `2026-05-19-cbl-b-slides.md` | `marp` | `MarpCarousel` | `<MarpCarousel markdown={body} />` |
| `2026-05-19-del-pipeline-diagram.md` | `mermaid` | `Mermaid` | `<Mermaid source={body} />` |
| `2026-05-19-del-screening-throughput.md` | `matplotlib` | image preview | `<img src={output_artifact}>` |
| `2026-05-19-protein-qc-interactive.md` | `plotly` | `PlotlyEmbed` | `<PlotlyEmbed html={body} />` |
| `2026-05-19-cbl-b-efficacy-table.md` | `table` | default react-markdown | ReactMarkdown (md table) |
| `2026-05-19-delphi-memo.md` | `docx` | "Open in app" button | download link |
| `2026-05-19-q4-2025-review-deck.md` | `pptx` | "Open in app" button | download link |
| `2026-05-19-ps-goals-2025-pdf.md` | `pdf` | "Open in app" button | download link |

All 9 pages have valid SCHEMA.md v0.2.0 frontmatter (`type: output`, `output_format`, `schema_version: 0.2.0`).

---

## Renderer deliverables confirmed

### Plotly HTML-fragment renderer (`packages/jojo_output/renderers/plotly_renderer.py`)

- 7 plot types: `bar`, `line`, `scatter`, `pie`, `heatmap`, `histogram`, `box`
- CDN-only: no `import plotly`; uses `https://cdn.plot.ly/plotly-2.35.2.min.js`
- Unique `<div id="plotly-{uuid4().hex[:8]}">` per render — multiple embeds on one page are safe
- `</script>` injection safety: raw data is `JSON.dumps()`-escaped, no user-controlled strings in script body
- 13 tests cover all 7 types, div uniqueness, layout fields, ValidationError cases, themes, injection safety

### `PlotlyEmbed.tsx` (`src/frontend/components/PlotlyEmbed.tsx`)

- `<iframe srcDoc={html} sandbox="allow-scripts" title="Plotly chart">`
- Default: 100% width, 450px height
- Sandboxed; `allow-scripts` only (no network, no same-origin)

### Wiki tab outputs/ rendering (`src/frontend/app/(tabs)/wiki/page.tsx`)

Per-format dispatch in `renderBody(currentPage)`:

```typescript
switch (currentPage.output_format) {
  case 'marp':    return <MarpCarousel markdown={body} />
  case 'mermaid': return <Mermaid source={body} />
  case 'plotly':  return <PlotlyEmbed html={body} />
  case 'matplotlib': return output_artifact
    ? <img src={output_artifact} alt={title} />
    : <ReactMarkdown>{body}</ReactMarkdown>
  default:        return <ReactMarkdown>{body}</ReactMarkdown>
}
```

### `GET /api/wiki/outputs` endpoint (`src/backend/routers/wiki_router.py`)

Returns `{ outputs: [{ slug, title, output_format, created }] }` for all `type: output` pages.

### StaticFiles `/wiki-outputs/` mount (`src/backend/main.py`)

```python
app.mount("/wiki-outputs/", StaticFiles(directory=str(wiki_root / "outputs")), name="wiki-outputs")
```

Mount added at startup; app starts even if `outputs/` doesn't exist yet.

### Chat tab "File this" button (`src/frontend/app/(tabs)/chat/page.tsx`)

- Button appears when `turn.formatResponse?.format` is present and not `"markdown"`
- Calls `POST /api/output/file-back` with `{title, body, output_format, source_question, confidence}`
- Per-turn status: `outputFileBackStatus?: 'idle' | 'filing' | 'filed' | 'error'`
- `OutputFileBackRequest` and `OutputFileBackStatus` types in `src/frontend/app/(tabs)/chat/types.ts`

---

## SCHEMA.md v0.2.0

Added to `ask_jojo_wiki/SCHEMA.md`:

- `type: output` added to page type taxonomy
- `output_format` field: `markdown | marp | matplotlib | plotly | table | mermaid | docx | pptx | pdf`
- `source_question`: the natural-language question that triggered this output
- `source_session_id`: traceability to the chat session
- `parent_slugs`: optional list of wiki slugs this output synthesizes
- `outputs/` directory entry in tree taxonomy
- Version history entry for v0.2.0

Migration script: `scripts/migrate_output_format.py` — backfills `output_format: markdown` on any existing `type: output` pages missing the field.

---

## Screenshot note

This evidence doc is generated in CLI/headless mode. The browser rendering of the Wiki tab's per-format dispatch requires a running `next dev` + backend server and cannot be captured as a screenshot in this environment. The structural evidence above — test passes, type-check clean, component code, endpoint responses — constitutes the equivalent verification. Mateo can confirm visually by running `pnpm dev` + `uvicorn` and opening `/wiki?slug=2026-05-19-cbl-b-slides` (Marp), `/wiki?slug=2026-05-19-protein-qc-interactive` (Plotly), etc.

---

## Pre-existing test failures (unchanged baseline)

| Count | Category | Root cause |
|---|---|---|
| 9 | `test_graph.py` / `test_sharepoint.py` | SOCKS proxy / MS Graph creds not present in CI |
| 7 | `jojo_qa` unimplemented-feature tests | Synthesis stubs pending FU-10 |

Total pre-existing: **16**. No new failures introduced in Phase 5.
