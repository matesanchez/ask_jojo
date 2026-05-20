# JoJo Bot v2.0 — Goal Run Log

**Run started:** 2026-05-19
**Orchestrator:** Claude Sonnet 4.6 (main session)
**Advisor:** Claude Opus 4.7 (via /advisor)
**Goal:** Execute GOAL_PROMPT.md end-to-end — complete Phases 4–8, stress tests, audits, and tag v2.0.0.

---

## Orientation (2026-05-19)

Read all four source-of-truth docs: README.md, PLAN.md, v2_status.md, follow-ups.md.

**Phase status at run start:**
- Phase 0–3: 🟢 Done
- Phase 4 (Q&A): 🟡 Deterministic plumbing shipped, 6 open items
- Phase 5 (Rich Outputs): 🟡 Plumbing shipped, 4 open items
- Phase 6 (Wiki Lint): ⚪ Not started (jojo_lint is Phase 0 stub only)
- Phase 7a (Graph Tab): 🟡 Plumbing shipped, 3 open items
- Phase 7b (Standalone Installer): REDEFINED 2026-05-19 — standalone Windows installer per department workstation
- Phase 8 (Fine-tune): ENABLED 2026-05-19

**Key decisions inherited from GOAL_PROMPT.md:**
- ADR 0012 to be written: OneDrive mount supersedes Graph-based SharePoint and Path C
- ADR (new): Phase 7b = standalone shared-computer, not shared server
- FU-10 is NOT blocking anymore: per GOAL_PROMPT.md §Constraints #2–3, I AM the model at build time
- Settings tab spec already exists at docs/phase-7b-settings-tab-spec.md
- MS Graph well-known client ID: 14d82eec-204b-4c2f-b7e8-296a70dab67e
- Nurix tenant ID: 1c966021-d551-45e4-89a5-849f81b69208

**Wiki at start:** 138 pages (from v2_status.md 2026-04-30)

---

## Delegation log

### 2026-05-19 — Round 5 (Phase 5 exit closure)

**Tasks completed:**
- `docs/reviews/2026-05-19-phase-5-review.md`: `reviewer` sub-agent invoked on Phase 5 for code quality exit-gate audit. Verdict: **PASS** (11/11 criteria). Three informational findings; FU-18 filed.
- `docs/v2_status.md`: Phase 5 flipped 🟡→🟢; Phase Summary table row updated (exit date 2026-05-19); Phase 5 completion note amended to include reviewer verdict; Phase 6 row flipped ⚪→🟡 (started 2026-05-19); Snapshot current phase updated to Phase 6; Amendment Log entry added.
- `docs/follow-ups.md`: FU-18 filed (POSIX sandbox import causes collection warnings on Windows).
- `docs/phase-5-exit-evidence.md`: Created with test results, renderer inventory, 9-format coverage table, SCHEMA.md v0.2.0 summary, screenshot note.

### 2026-05-19 — Round 4 (Phase 5 execution)

**Sub-agents delegated:**
- Backend agent → `plotly_renderer.py` (7 plot types, CDN-only, 13 tests), `output_router.py` plotly dispatch lifted (501 removed), `wiki_router.py` `/api/wiki/outputs` endpoint + `output_format`/`output_artifact` top-level page fields + `outputs/` tree nodes, `main.py` StaticFiles `/wiki-outputs/` mount, `test_output_endpoints.py` + `test_wiki_endpoints.py` new tests. FU-16 generalized across `output_router.py` (6 `rel.as_posix()` sites).
- Frontend agent → `PlotlyEmbed.tsx` (sandboxed iframe), `chat/types.ts` (`OutputFileBackRequest`/`outputFileBackStatus`), `chat/page.tsx` "File this" button + `POST /api/output/file-back` wiring, `wiki/types.ts` (`output_format`/`output_artifact` fields), `wiki/page.tsx` `renderBody()` per-format dispatch.
- Writer agent → 9 sample output pages in `ask_jojo_wiki/outputs/` covering all 9 formats (markdown/marp/mermaid/matplotlib/plotly/table/docx/pptx/pdf), SCHEMA.md v0.2.0.

### 2026-05-19 — Round 1 (ADRs written)

Wrote ADR 0012 (OneDrive mount supersedes Path C) and ADR 0013 (Phase 7b standalone workstation installer). Both accepted. Starting Phase 4 delegation.

### 2026-05-19 — Round 3 (Phase 4 exit closure)

**Tasks completed:**
- `docs/v2_status.md`: Phase 4 flipped 🟡→🟢; Phase Summary table row updated; Path B checkbox marked [x]; Phase 4 completion note added; Amendment Log entry added; Phase 2 cross-validation note added.
- `docs/follow-ups.md`: FU-3 marked RESOLVED 2026-05-19; FU-11 marked RESOLVED (zero edits); FU-12 marked RESOLVED (pellino-1-target); FU-13 (wikilink format) and FU-14 (truncated hashes) filed.
- `docs/goal-run-log.md`: Test baseline corrected to 16 pre-existing failures (9 SOCKS + 7 jojo_qa).
- External reviewer pass executed on 30-page wiki sample (per `docs/qa/external-reviewer-pass.md` selection criteria). Result: 100% acceptance rate (30/30 Accept or Accept-with-edits, 0 Rejects). Report: `docs/qa/reviews/external-pass-2026-05.md`.
- `reviewer` sub-agent invoked on Phase 4 for code quality exit-gate audit. Report: `docs/reviews/2026-05-19-phase-4-review.md`. Verdict: **PASS** (11/11 criteria).
- FU-15 filed: nightly CI benchmark is a no-op (no test uses `@pytest.mark.benchmark`).
- FU-16 filed and fixed: Windows path separator in `qa_router.py:402` (`str(rel)` → `rel.as_posix()`). Both file-back tests now pass.
- FU-17 filed: `benchmark-questions.md` references non-existent `scripts/run_benchmark.py`.
- Tracking issue created: https://github.com/matesanchez/ask_jojo/issues/1 ("v2.0 MVP wrap-up").

### 2026-05-19 — Round 2 (Phase 4 execution)

**Sub-agents delegated:**
- Backend agent → `msal_device_code_provider()` in `graph.py` (Path B MSAL auth, DPAPI-encrypted cache), `auth` CLI subcommand in `cli.py`, DEFAULTS dict in `config.py`, `msal>=1.27` extra, `[tool.pytest.ini_options] markers` in `pyproject.toml`, 5 unit tests in `test_msal_auth.py`, `qa-benchmark.yml` nightly CI workflow.
- Writer A → q-006–q-020 gold answer files + benchmark-batch-a.md staging file (15 entries: program-comparison, target-biology, program-comparison relational, v1-routing)
- Writer B → q-021–q-035 gold answer files + benchmark-batch-b.md staging file (15 entries: platform-mechanism, historical-decision, protocol-method)
- Writer C → q-036–q-050 gold answer files + benchmark-batch-c.md staging file (15 entries: relational, router-stress, v1-routing, edge)
- Orchestrator → merged all three staging files into canonical `benchmark-questions.md`; fixed FU-12 final artifact (`2026-04-30-pellino-1-peli2-redundancy.md`); FU-11 verified (zero edits — flag-don't-fabricate applied to all 13 confidence:low pages); pre-existing ruff errors fixed (21 auto-fixed + 7 manual).

**Phase 4 deliverables completed:**
- Benchmark: 5 → 50 entries (q-001–q-050), 9 categories, all gold answer files in `docs/qa/answers/`
- MSAL Path B auth: `msal_device_code_provider()` + DPAPI cache + `auth` CLI + 5 passing unit tests
- CI: `qa-benchmark.yml` nightly workflow
- FU-12 closed: all 4 artifacts updated (target page slug, _index.md, benchmark-questions.md q-002, gold answer file)
- FU-11 resolved: zero edits on 13 confidence:low pages (correct per flag-don't-fabricate rule)

---

## Decisions made this run

| # | Decision | Rationale |
|---|---|---|
| 1 | Treat FU-10 as unblocked | GOAL_PROMPT §Constraints #2: I am the model at build time; live API uses user-supplied key in Settings |
| 2 | Phase 7b = standalone installer, not shared server | GOAL_PROMPT §Phase 7b redefinition 2026-05-19 |
| 3 | ADR 0012 = OneDrive mount supersedes Path C | GOAL_PROMPT §Constraints #7; write before starting backend work |
| 4 | q-008 category = relational (not program-comparison) | ITK CTM page is a redirect stub — requires a hop to ITK main page; Writer A re-categorization accepted |
| 5 | FU-11: zero edits on 13 confidence:low pages | No inline raw citations found in any page body; flag-don't-fabricate rule applied |
| 6 | Pre-existing ruff errors fixed before commit | Test gate constraint requires ruff clean; 22 errors pre-dating Phase 4 fixed (I001 import sorting auto-fixed, F841/B017 manual) |

---

## Open blockers

None currently. All blockers are human-only (credentials, external infra) and are noted as deferred per GOAL_PROMPT.md.

**Non-blocking follow-ups filed:**
- Add DPAPI negative regression test to `test_msal_auth.py` (assert `_dpapi_protect` called when `FORCE_PLAINTEXT` unset)
- Add `[cloud]` extra to `qa-benchmark.yml` install line (prevent msal ImportError at benchmark collection)

---

## Phase exit evidence

### Phase 4 — Q&A Benchmark + MSAL Auth (2026-05-19)

| Exit criterion | Evidence |
|---|---|
| 50 benchmark entries in canonical file | `benchmark-questions.md`: q-001–q-050, 9 categories, totals match |
| Gold answer files for all 50 entries | 50 files in `docs/qa/answers/` (5 from 2026-04-30, 45 from 2026-05-19) |
| MSAL Path B auth implemented | `graph.py:msal_device_code_provider()`, DPAPI cache, `cli.py:auth` subcommand |
| Unit tests pass | 5 new tests in `test_msal_auth.py` pass; 16 pre-existing failures unchanged (9 SOCKS proxy in test_graph.py/test_sharepoint.py + 7 jojo_qa: router×4, format×1, raw_fallback×1, smoke×1) |
| Ruff clean | `python -m ruff check .` → "All checks passed!" |
| FU-12 closed | 4 artifacts updated; `pellino-1-target` slug consistent across wiki + benchmark |
| FU-11 resolved | 13 confidence:low pages confirmed zero inline raw citations; no edits made |
| CI workflow staged | `qa-benchmark.yml` created (nightly 06:00 UTC + workflow_dispatch) |

### Phase 5 — Rich Outputs (2026-05-19)

| Exit criterion | Evidence |
|---|---|
| Plotly HTML-fragment renderer | `plotly_renderer.py`: 7 plot types, CDN-only (`_PLOTLY_CDN`), 13 tests in `test_plotly_renderer.py` |
| `output_router.py` plotly 501 lifted | `output_router.py:281-295`: `PlotlySpec` + `render_plotly` dispatch (both inline and file-write branches) |
| "File this" button on Chat tab | `chat/page.tsx:707-721`: button + `POST /api/output/file-back`; `outputFileBackStatus` type in `chat/types.ts:204` |
| Wiki tab outputs/ dispatch | `wiki/page.tsx:235-271`: `renderBody()` switch dispatches marp/mermaid/plotly/matplotlib/default |
| `PlotlyEmbed.tsx` sandboxed iframe | `PlotlyEmbed.tsx:29-37`: `<iframe srcDoc={html} sandbox="allow-scripts" />` |
| `GET /api/wiki/outputs` endpoint | `wiki_router.py:379-417`: returns `{total, outputs:[{slug,title,output_format,created,path}]}` |
| StaticFiles `/wiki-outputs/` mount | `main.py:71-77`: conditional mount (only when dir exists) |
| 9 sample output pages (all 9 formats) | `ask_jojo_wiki/outputs/`: markdown/marp/mermaid/matplotlib/plotly/table/docx/pptx/pdf — all have `type: output`, `output_format`, `schema_version: 0.2.0` |
| SCHEMA.md v0.2.0 | `ask_jojo_wiki/SCHEMA.md:3`: version 0.2.0; `type: output`, `output_format`, `source_question`, `parent_slugs` fields documented |
| ruff clean + tests pass | Exit 0; 11/11 reviewer criteria pass; 16 pre-existing failures unchanged |
| `rel.as_posix()` generalized | All 6 `relative_to` call-sites in `output_router.py` use `.as_posix()` |
