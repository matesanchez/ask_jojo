# Phase 5 Exit-Gate Review — 2026-05-19

**Reviewer:** `reviewer` sub-agent (Claude, cold-context read-only audit)
**Orchestrator:** Claude Sonnet 4.6
**Verdict: PASS** — 11/11 exit criteria pass. Three informational findings (no FAIL, no WARN). Phase 6 may proceed.

---

## Per-Criterion Table

| # | Criterion | Result | Evidence |
|---|---|---|---|
| 1 | `plotly_renderer.py` exists, 7 plot types, CDN-only, ≥10 tests | PASS | `plotly_renderer.py:44` Literal["bar","line","scatter","pie","heatmap","histogram","box"]; `_PLOTLY_CDN` constant at line 22; no `import plotly`; 13 tests in `test_plotly_renderer.py` |
| 2 | `output_router.py` plotly path no longer 501; dispatches to `PlotlySpec`/`render_plotly` | PASS | `output_router.py:281-295` imports `PlotlySpec` + `render_plotly`, validates, dispatches both inline-HTML and out-file branches |
| 3 | Chat tab "File this" wiring — `POST /api/output/file-back`, `outputFileBackStatus` state | PASS | `chat/types.ts:204` declares `outputFileBackStatus`; `chat/page.tsx:308` calls `fetchJSON("/api/output/file-back", ...)`; button at `chat/page.tsx:707-721` only when `richFormat !== "markdown"` |
| 4 | Wiki tab outputs/ dispatch on `output_format` for marp/mermaid/plotly/matplotlib/markdown | PASS | `wiki/page.tsx:235-271` `renderBody()` switch with all 4 cases plus default ReactMarkdown fallback |
| 5 | `PlotlyEmbed.tsx` exists with sandboxed `<iframe srcDoc>` | PASS | `components/PlotlyEmbed.tsx:29-37` — `<iframe srcDoc={html} sandbox="allow-scripts" />` |
| 6 | `GET /api/wiki/outputs` endpoint in `wiki_router.py` | PASS | `wiki_router.py:379-417` — `@router.get("/outputs")` returns `{total, outputs:[{slug,title,output_format,created,path}]}` |
| 7 | StaticFiles `/wiki-outputs/` mount in `main.py` | PASS | `main.py:71-77` — conditional mount (only when dir exists) |
| 8 | `ask_jojo_wiki/outputs/` has ≥5 sample pages with valid frontmatter | PASS | 9 pages found; all carry `type: output`, `output_format`, `schema_version: 0.2.0`, date fields, `parent_slugs` |
| 9 | SCHEMA.md ≥0.2.0 with `type: output` documented | PASS | `SCHEMA.md:3` version 0.2.0; v0.1.0→v0.2.0 changelog at lines 9-18 names `type: output` row |
| 10 | `ruff check .` clean; no regressions beyond 16-test baseline | PASS | Exit 0; all Phase 5 tests pass; 7 baseline `jojo_qa` failures reproduced unchanged; POSIX sandbox tests skip correctly on Windows |
| 11 | `rel.as_posix()` used (not `str(rel)`) at every relative-path return site in `output_router.py` | PASS | All 6 `relative_to` call-sites use `.as_posix()` at lines 223, 246, 262, 278, 293, 372, 376, 413; zero `str(rel)` occurrences |

---

## Informational Findings

### INFO-1 — POSIX-only sandbox import collects warnings on Windows

`packages/jojo_output/sandbox/runner.py:29` does `import resource` at module level, making `test_ast_guard.py`, `test_sandbox_runner.py`, `test_sandbox_spec.py` uncollectable under `pytest packages/` on Windows. The integration tests in `test_output_endpoints.py` (lines 68, 153, 173, 193) correctly carry `@pytest.mark.skipif(win32)` and skip gracefully. Pre-existing platform conditional, not a Phase 5 regression. Small improvement: `pytest.importorskip("resource")` at the module level of the affected test files, or a platform guard in `sandbox/__init__.py`. Filed as **FU-18**.

### INFO-2 — `/wiki-outputs/` vs `/wiki-outputs` (trailing slash)

`docs/phase-5-exit-evidence.md` references the mount as `/wiki-outputs/` but `main.py:74` registers it as `"/wiki-outputs"` (no trailing slash). Functionally identical under Starlette's routing. No action required.

### INFO-3 — Plotly XSS hardening (defense-in-depth)

`plotly_renderer.py:182-183` escapes only `</` sequences in the JSON payload. Adequate against the documented `</script>` smuggling vector tested at `test_plotly_renderer.py:159-171`. If untrusted strings ever enter `title`/`x_label`/`y_label`, an additional HTML-escape pass would harden defense-in-depth. Not blocking; the sandboxed iframe already isolates the parent doc.

---

## Verdict

**PASS.** All 11 criteria pass. Phase 5 — Rich Outputs — deterministic deliverables are complete and consistent with the v2_status.md claim. The API-day flip (`synthesize.answer` → `{format, spec}`) remains correctly gated on FU-10 per ADR-0011 and is NOT an exit blocker.

**Phase 6 may proceed.**
