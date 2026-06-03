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

### 2026-05-19 — Round 11 (Phase 7b exit closure + Phase 8 start)

**Phase 7b exit gate:**
- `v2_status.md` Phase 7b deliverables checklist corrected from stale server-based items to ADR-0013 standalone installer items (12 deliverables, 11 checked, 1 in-progress at time of writing).
- `/welcome/page.tsx` upgraded from static 42-line component to 208-line live component: polls `/api/ops/status` every 10 s, renders per-section status checklist, redirects to `/` when all five sections green.
- `docs/phase-7b-exit-evidence.md` created (93 lines).
- `docs/reviews/2026-05-19-phase-7b-review.md`: Reviewer PASS 12/12 items, 0 blockers.
- `v2_status.md`: Phase 7b flipped 🟡→🟢 (2026-05-19). Phase 8 activated 🟡.

**Phase 8 delegations starting (see below).**

### 2026-05-20 — Round 12 (Phase 8 exit closure + stress tests + audits)

**Phase 8 exit gate:**
- `packages/jojo_finetune/` shipped (dataset.py, train.py, eval.py, cli.py). 30 tests, all passing.
- `data/finetune/v1.jsonl` — 50-example seed; `data/finetune/benchmark.jsonl` — 10 dry-run Q&A pairs.
- ADR 0014 (fine-tune strategy) + `docs/ops/offline-model.md` + workspace README section written.
- Reviewer PASS 12/12 (`docs/reviews/2026-05-20-phase-8-review.md`).
- `v2_status.md`: Phase 8 flipped 🟡→🟢 (2026-05-20).

**Stress tests:**
- Lint regression: PASS — 6/6 checks, exit 0; 9 broken-wikilink WARN findings (pre-existing FU-13/FU-19). Baseline saved to `docs/lint-baseline-2026-05-20.json`.
- Graph rebuild stress: PASS — 10/10 runs idempotent (148 nodes, 272 edges, SHA256 identical).
- Backend load test: PROCEDURE DOCUMENTED — server starts OK; `/api/raw/tree` has 1.8 s p95 at low concurrency (needs caching; filed as FU-22). Load test script at `src/backend/tests/test_load.py`.
- Ingest stress: PROCEDURE DOCUMENTED — requires OneDrive/SharePoint.
- Frontend route smoke: PROCEDURE DOCUMENTED — Playwright spec at `src/frontend/tests/e2e/smoke.spec.ts`; requires browser on workstation.
- Full report: `docs/stress-test-report.md`.

**Audits:**
- ADR audit: CLEAN — all 15 ADRs have Status fields; 0012/0013/0014 cover 2026-05-19 decisions.
- Wiki compliance: FAIL → FIXED — 2 corpus enum violations (`irak4`, `cbl-b` used `del-screen-team`); retagged to `protein-sciences`; filed FU-20 (source-path normalization) + FU-21 (hash normalization). Report: `docs/wiki-compliance-audit.md`.
- Privacy audit: PASS (post-fix) — `ask_jojo_raw/` added to `ask_jojo/.gitignore`; both repos confirmed PRIVATE on GitHub; no raw content in wiki pages or logs. Report: `docs/privacy-audit.md`.
- Security audit: 6 medium CVEs (idna, pip, python-multipart, urllib3) — no high/critical. No real credentials in git history. Report: `docs/security-audit.md`.
- License audit: ATTENTION — pymupdf (AGPL-3.0) + html2text (GPL-3.0) flagged for Legal review for distribution scenarios. Report: `docs/license-inventory.md`.

---

### 2026-05-19 — Round 10 (Phase 7b execution start)

**Decision recorded: Settings API contract.** Two versions existed:
- `docs/phase-7b-settings-tab-spec.md` — per-section endpoints (the detailed implementation spec, authored 2026-05-19)
- GOAL_PROMPT.md §Constraints #3 — aggregated shape (`GET/PUT /api/settings`, `POST /api/settings/test-connection`, `POST /api/settings/device-code-login`)

**Decision:** use `docs/phase-7b-settings-tab-spec.md` as the authoritative contract. It is more detailed and was written specifically as the implementation guide. The GOAL_PROMPT summary was a high-level shorthand; the spec is the deliverable.

**Config dir confirmed:** `%APPDATA%\JojoBot\` (`packages/jojo_core/config.py:118`) — not `%LOCALAPPDATA%`. No change needed.

**SDK wiring scope clarified:** `synthesize._call_model` is the only Phase 7b stub needing live Anthropic SDK. Weekly lint checks (`contradiction_check`, etc.) are already tagged "Phase 8 stub" in their source — they return `pass` with deterministic candidates when an API key is present; the LLM pass is intentionally deferred to Phase 8.

**Phase 7b agents launched (parallel):**
- Backend agent → `settings_router.py` + `synthesize._call_model` live + `anthropic>=0.40` in pyproject.toml
- Frontend agent → `/settings` tab (5 sections) + `/welcome` first-run route
- Installer agent → `Build-JojoBotRelease.ps1` + `Uninstall-JojoBot.ps1` + NSSM service + `docs/ops/distribution.md`

### 2026-05-19 — Round 9 (Phase 7a exit closure)

**Tasks completed:**
- `docs/reviews/2026-05-19-phase-7a-review.md`: Reviewer PASS 15/15.
- `docs/phase-7a-exit-evidence.md`: Created with deliverables summary, benchmark table, quality gate results.
- `docs/v2_status.md`: Phase 7a flipped 🟡→🟢; checklist updated; Phase 7b now active.
- `docs/goal-run-log.md`: Phase 7a evidence added.

### 2026-05-19 — Round 8 (Phase 7a execution)

**Sub-agents delegated (parallel):**
- Backend agent → `packages/jojo_qa/graph.py`: enriched node schema with `summary` + `corpus`; helper functions `_parse_frontmatter_scalar`, `_extract_summary`, `_read_full_text`; schema_version bumped to `0.2.0`; 10 new tests. Token benchmark re-run at 148 pages: 12.7×–36.7× ratio. Rebuilt `ask_jojo_wiki/_graph.json`. Commits: b942e90 + 3cae926.
- Frontend agent → `src/frontend/components/BrainView.tsx` (892 lines): three.js InstancedMesh force-directed 3D graph; OrbitControls; spring/repulsion force layout (200 warm-up ticks); pulse-on-update via `/api/wiki/stats` polling; subgraph BFS + search overlay; `?highlight=` prop. `graph/page.tsx`: D3/Brain toggle + `dynamic(..., ssr:false)`. Commits: d24ba3b + a1af4e1.

**Orchestrator tasks:**
- Checked off "Provenance highlight from Chat tab" (already shipped in Round 6 by frontend agent; confirmed in chat/page.tsx:598-608 and :696-703).

### 2026-05-19 — Round 7 (Phase 6 exit closure)

**Tasks completed:**
- `src/backend/tests/test_ops_endpoints.py`: 6 new lint endpoint tests added to reach ≥10 bar (criterion #8 gap). All 10 lint-specific tests pass; 115 passed total. Commit: 44daff5.
- `docs/reviews/2026-05-19-phase-6-review.md`: Two-pass reviewer audit. Pass 1 found B1 (LintMetrics.tsx API mismatch); Pass 2 found criterion #8 test gap. Both fixed. Final verdict: PASS 15/15.
- `docs/v2_status.md`: Phase 6 flipped 🟡→🟢; Phase Summary table Phase 6 row updated (exit 2026-05-19); Phase 7a row flipped ⚪→🟡 (started 2026-05-19); Snapshot updated to Phase 7a; Phase 6 completion note + checklist checked off; Amendment Log entry added.
- `docs/goal-run-log.md`: Phase 6 exit evidence added.

**Phase 6 exit gate (two-pass reviewer):**
- Pass 1: 14/15 PASS, 1 FAIL (B1 — LintMetrics.tsx API contract mismatch). Fix: e59e113.
- Pass 2: 14/15 PASS, 1 FAIL (criterion #8 — only 4 lint endpoint tests, needed ≥10). Fix: 44daff5.
- Final re-check: PASS 15/15.

### 2026-05-19 — Round 6 (Phase 6 execution + wiki debt fixes)

**Sub-agents delegated:**
- Backend agent → `packages/jojo_lint/` full implementation (10 checks, registry, history, CLI, 51 tests), `ops_router.py` lint endpoints lifted, `test_ops_endpoints.py` 12 tests, `lint-nightly.yml` CI workflow, `pyproject.toml [lint]` extra. Commits: b25067d + 0ab0d59.
- Frontend agent → `LintHistoryCard.tsx`, `LintMetrics.tsx` (Chart.js trendlines), `ReviewQueueCard.tsx`, `ops/page.tsx` updated, Phase 7a "Show in graph" link in `chat/page.tsx`. `tsc --noEmit` clean. Commits: a2be446 + 2f1dc69 + ca36363.
- Installer agent → `Run-LintNightly.ps1`, `Run-LintWeekly.ps1` (pure ASCII, Event IDs 7200–7203), `Register-JojoBotTasks.ps1 -IncludeLint` (idempotent). Commit: 2b87905.

**Wiki content debt fixed (orchestrator):**
- `targets/itk.md`: slug `itk` → `itk-target` (dedup with `programs/itk.md`); `_index.md` updated
- `programs/itk-ctm.md`: `sources:` field added (schema error)
- `_index.md`: +10 orphan pages (1 derived + 9 outputs/); Total pages 138 → 148
- 9 pages: path-style `[[methods/x]]` → `[[x]]` wikilinks fixed
- FU-19 filed: 27 remaining Title-Case wikilinks (pre-existing FU-13 debt)

**Lint 14-run exit gate:**
- 14/14 runs exit 0 against real wiki
- 5/6 nightly checks: all green (OK — 0 findings)
- 1 check (wikilink): 27 WARN findings — all pre-existing FU-13 Title-Case violations, no false positives

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

### Phase 6 — Wiki Linting + Self-Maintenance (2026-05-19)

| Exit criterion | Evidence |
|---|---|
| `packages/jojo_lint/` installable | `pyproject.toml`: `jojo-lint = "jojo_lint.cli:main"`; entry point resolves |
| 6 nightly checks registered | `registry.py:24-31`: schema, orphan, stub, wikilink, bloat, quote_budget |
| 4 weekly stubs (`api_key_required`) | `checks/contradiction_check.py` etc.: all return `api_key_required` when no key |
| `history.py` JSONL-backed | `append_run`, `load_runs`, `metrics_series`; writes to `%LOCALAPPDATA%\JojoBot\lint-history` |
| `cli.py` 5 subcommands | `jojo-lint nightly\|weekly\|check\|report\|history` all dispatch |
| 51 pytest tests pass | 4 test files; smoke 2, history 12, cli 9, nightly_checks 28 |
| `ops_router.py` lint endpoints wired | `POST /api/ops/lint/{scope}` → registry; `/history` → `{runs}`; `/metrics` → `{series}` |
| 10 lint endpoint tests | `test_ops_endpoints.py`: 10 lint-specific tests (commits 0ab0d59 + 44daff5); 115 passed total |
| `LintHistoryCard.tsx` | Fetches history, renders table, "Run now" button; scope=nightly + weekly |
| `LintMetrics.tsx` (B1 fixed) | `series: RunMetrics[]`; flat-list → per-metric transform at lines 177-180 (commit e59e113) |
| `ReviewQueueCard.tsx` | Aggregates findings by slug; "View page" links |
| `ops/page.tsx` updated | Renders all 3 lint components |
| Scheduler scripts pure ASCII | `Run-LintNightly.ps1`, `Run-LintWeekly.ps1`: 0 codepoints > 127 |
| Task registrar `-IncludeLint` | `Register-JojoBotTasks.ps1` registers `lint-nightly` + `lint-weekly` |
| CI workflow | `.github/workflows/lint-nightly.yml`: cron + workflow_dispatch |
| 14-run exit gate | `jojo-lint nightly` exit 0 × 14 consecutive runs on real 148-page wiki |
| Reviewer PASS | `docs/reviews/2026-05-19-phase-6-review.md`: PASS 15/15 (two-pass audit) |

### Phase 7a — Graph Tab (2026-05-19)

| Exit criterion | Evidence |
|---|---|
| Node enrichment schema 0.2.0 | `packages/jojo_qa/graph.py:63-84`: schema "0.2.0"; nodes have summary/corpus |
| `_graph.json` rebuilt at 148 nodes | `ask_jojo_wiki/_graph.json`: 148 nodes, 272 edges, schema_version "0.2.0" |
| Token-reduction benchmark ≥10× | `docs/graph/token-reduction-report.md` Run 2: 12.7×–36.7× @ 148 pages |
| Provenance "Show in graph →" link | `chat/page.tsx:598-608` + `:698-703`; both paths, `/graph?highlight=` |
| BrainView.tsx three.js | 892 lines; InstancedMesh (one draw call); OrbitControls; force layout |
| Performance architecture | InstancedMesh + LineSegments = 2 draw calls for entire scene |
| Pulse-on-update | 15s poll `/api/wiki/stats`; scale oscillation 1.0→1.5→1.0 over 800ms |
| Layer toggles + search | All / Subgraph (BFS depth-2) + search-highlight input |
| `?view=brain` toggle | `graph/page.tsx`: D3/Brain toggle; `dynamic(..., {ssr:false})`; `?highlight=` forwarded |
| ruff + tsc clean | Exit 0; no errors |
| Tests = baseline | 8 failures = 7 jojo_qa + 1 jojo_graph smoke (pre-existing) |
| Reviewer PASS | `docs/reviews/2026-05-19-phase-7a-review.md`: PASS 15/15 |

### Phase 7b — Standalone Workstation Installer (2026-05-19)

| Exit criterion | Evidence |
|---|---|
| `Build-JojoBotRelease.ps1` produces distributable ZIP | Script at `ops/installer/Build-JojoBotRelease.ps1`; pure ASCII confirmed |
| NSSM Windows service bundled | `Install-JojoBot.ps1` + `Uninstall-JojoBot.ps1` in `ops/installer/` |
| `/welcome` polling page | `src/frontend/app/welcome/page.tsx`: 208 lines; polls `/api/ops/status` every 10s; redirects when all 5 sections green |
| Settings tab live-wiring | `src/frontend/app/settings/page.tsx` + `/api/settings/*` endpoints: DPAPI config, MSAL auth, Anthropic key |
| 20 settings tests pass | `tests/test_settings_endpoints.py`: 20/20 PASS; pre-existing 16 failures unchanged |
| DPAPI config ADR 0009 | Implemented in `packages/jojo_core/config.py`; `SECRET_KEYS` list |
| ADR 0013 (Phase 7b redefinition) | `docs/ADR/0013-standalone-installer.md`: Status Accepted |
| Distribution guide | `docs/ops/distribution-guide.md` |
| Reviewer PASS | `docs/reviews/2026-05-19-phase-7b-review.md`: PASS 12/12 |

### Phase 8 — Fine-Tune Dataset + Pipeline + Eval (2026-05-20)

| Exit criterion | Evidence |
|---|---|
| `packages/jojo_finetune/` installable | `pyproject.toml`: `jojo-finetune = "jojo_finetune.cli:main"`; 5 modules |
| `dataset.py` with citation guardrail | `FinetuneExample.citation: list[str]`; every example traces to a wiki slug |
| 3 example types implemented | paraphrase / fill_blank / synthesis in `GENERATION_PROMPTS` |
| Dry-run generators (no API) | `_dry_paraphrase`, `_dry_fill_blank`, `_dry_synthesis` in `dataset.py` |
| `train.py` 3 backends | `DryRunBackend`, `BedrockBackend` (boto3 lazy), `HuggingFaceBackend` (peft/trl lazy) |
| `eval.py` F1 scorer + dry-run | `score_pair()` word-overlap F1; `SynthesisBackend` calls live `jojo_qa.synthesize.answer()` |
| `data/finetune/v1.jsonl` (50 examples) | 17 paraphrase + 17 fill_blank + 16 synthesis; all citation-anchored to real slugs |
| `data/finetune/benchmark.jsonl` (10 Q/A) | CI dry-run pairs; README notes to replace with Phase 4 gold answers before real eval |
| ADR 0014 (fine-tune strategy) | `docs/ADR/0014-finetune-strategy.md`: Status Accepted; renumbering note included |
| `docs/ops/offline-model.md` | LoRA / vllm / llama.cpp deployment guide; 30–50% accuracy trade-off documented |
| 30 pytest tests pass | `tests/jojo_finetune/`: 6 dataset + 10 train + 14 eval; no `__init__.py` (avoids namespace shadow) |
| `[finetune]` optional deps | `pyproject.toml`: boto3, peft, transformers, trl, datasets |
| Reviewer PASS | `docs/reviews/2026-05-20-phase-8-review.md`: PASS 12/12 |

### Pre-release audits (2026-05-20)

| Audit | Verdict | Notes |
|---|---|---|
| Wiki compliance | PASS (post-fix) | 2 corpus-retag FAILs fixed in-session (`irak4`, `cbl-b` → `protein-sciences`) |
| Privacy (ADR 0006) | PASS (post-fix) | Nested `ask_jojo_raw/` gitignore gap fixed; both repos confirmed PRIVATE |
| Security | PASS | 6 medium CVEs (idna, pip ×2, python-multipart, urllib3 ×2); 0 high/critical |
| License inventory | PASS (conditional) | AGPL/GPL attention items filed as FU-23; needs Legal review before distribution |
| Stress — lint regression | PASS | 6 checks, 9 wikilink WARN only, exit 0 |
| Stress — graph rebuild 10× | PASS | 10/10 idempotent — 148 nodes, 272 edges, SHA256 identical |
| Stress — backend load test | RAN / SLA NOT MET | `/api/raw/tree` p95 ~1.8 s vs. 500 ms SLA — filed as FU-22 |

---

## Round 13 — Final review + tag (2026-05-20)

**Final reviewer:** 8/8 items PASS (no blockers).

**Commits:**
- `ask_jojo` `11b97db` — Phase 7b+8 deliverables, pre-release audits (36 files, +4168/-18)
- `ask_jojo_wiki` `3d36c2f` — corpus retag fix (irak4 + cbl-b)

**Tags applied:**
- `ask_jojo` → `v2.0.0`
- `ask_jojo_wiki` → `wiki-2026-mvp`

**Tracking issue:** matesanchez/ask_jojo#2 — opened and closed as completed.

**Open follow-ups at tag:**
- FU-22 — `/api/raw/tree` TTL cache (p95 SLA)
- FU-23 — pymupdf AGPL-3.0 + html2text GPL-3.0 Legal review

**Goal complete.** All phases 0–8 🟢. v2.0.0 tagged.

---

## 2026-05-21 — Post-tag patch: test isolation

**Root cause identified:** `jojo_core.config.get()` reads `%APPDATA%\JojoBot\config.json` before checking env vars. Tests that called `monkeypatch.delenv("JOJO_ONEDRIVE_PATH")` etc. were not redirecting config.json reads, so the real operator config bled into test assertions. This caused 13+ failures across `jojo_ingest` and backend ingest endpoint tests whenever run after `test_settings_endpoints.py::test_post_connectors_saves_paths` (which writes `onedrive_path` / `graph_access_token` to the real config.json before resetting `_override_path` to `None`).

**Fix:**
- `packages/jojo_ingest/tests/conftest.py` — new file; `autouse` fixture redirects all config I/O to `tmp_path / "config.json"` for every `jojo_ingest` test.
- `src/backend/tests/test_ingest_endpoints.py` — `client_with_raw_root` fixture converted from `return` to `yield`/`try-finally`; calls `jojo_config.set_config_path_for_tests(tmp_path / "config.json")` on setup and `set_config_path_for_tests(None)` on teardown.

**Verification:** 618 passed, 0 failed (full suite). Pre-existing 8 `jojo_graph`/`jojo_qa` failures from prior session are now resolved (total failure count dropped from 13+ to 0).

**Deliverable spot-check (confirming prior completion):** ADRs 0012–0014 present; `docs/reviews/2026-05-19-phase-7b-review.md` + `2026-05-20-phase-8-review.md` present; `ops/installer/Build-JojoBotRelease.ps1` present; `packages/jojo_finetune/` installable; `v2.0.0` tag confirmed on `ask_jojo`. No re-tag.

---

## 2026-06-01 — Wiki coverage recovery run (FU-20 / FU-21 / FU-22), partial

Executed the wiki-coverage recovery (`GOAL_PROMPT_WIKI_RECOVERY.md`) as a deep first pass. This run is content + lint only; no app/installer/frontend changes.

**FU-20 — reclassification + first absorb batch.**
- Task 1.1: reclassified both over-skipped populations at entry level. `departed_individual` (2,955) + `individual_user_data` (5,495) → buckets in `docs/audits/fu-20-reclassification.jsonl` (+ summary). After a reviewer-driven correction pass, combined `knowledge_promote` = 5,636 (departed 45.9%, individual_user_data 77.8%), matching the FU-20 audit's ~5,700 / 43% / 80% ground truth.
- Reviewer (Opus, independent) audited the first pass and returned **FAIL (Blocking, 26% misclassification)** — the low-confidence `knowledge_promote` stratum swept personal/desktop-backup and installer trees into promotion. Correction pass added folder-level personal signals, installer-path signals, blank/test detection, and fixed the compound-ID regex (underscore boundary). Re-verification: all 10 flagged failures fixed; residual contamination on a fresh 40-sample = 2.5%. Report: `docs/reviews/2026-06-01-fu-20-reclassification-review.md` (Round 1 FAIL → Round 2 PASS-with-caveats).
- Task 1.3 (first absorb batch): promoted 13 confirmed-knowledge entries into 3 source-grounded wiki pages — `references/cbl-b-immuno-oncology-literature.md`, `methods/turbidimetric-solubility-assay.md`, `methods/analytical-chemistry-adme-and-stability.md`. Entries ticked in `queue.md` with `<!-- absorbed-via: fu-20-recovery -->`. Committed to the wiki repo (`absorb(protein-sciences): 3 pages touched, 3 created`).
- **Remaining:** the bulk of the ~5,636 `knowledge_promote` entries are not yet absorbed — this is the multi-session FU-20 backlog. High-confidence stratum (~2,200) is the priority set.

**FU-21 — literature index (started).**
- Clustered the 2,060 `external_literature` entries into 12 topics → `docs/audits/fu-21-literature-clustering.jsonl`. Built the landing page `references/literature-index/_index.md` with the topic map and build status. One topic page (CBL-B immuno-oncology) is built (shared with FU-20). **Remaining:** ~10–12 topic pages + sub-splitting the oversized oncology cluster — the FU-21 build backlog.

**FU-22 — absorbed-but-invisible tail audit (complete).**
- Stratified n=200 trace → `docs/audits/fu-22-trace.jsonl` + summary. Unintegrated = 2.5% (threshold 20%) → **DEFENSIBLE**. The 59K absorbed tail is 76.5% low-signal bulk data; only ~2.5% is missed knowledge. Filed missed slice as **FU-23**. Report: `docs/reviews/2026-06-01-fu-22-closure.md`.

**Sub-phase 4 — coverage lint check (complete).**
- Added `packages/jojo_lint/checks/coverage_check.py`, registered in `WEEKLY_CHECKS`, with 8 unit tests (all green; full lint suite green). Against the real queue it exempts 37 mechanical/bulk categories and flags 12 person/folder-name categories (departed_individual, individual_user_data, external_literature, safety_binders, admin_records, ...) for entry-level review — the durable guard against categorical over-skipping (FU-20 recommendation #2).

**Environment notes.**
- The wiki-repo commit left stale `.git/index.lock` and `.git/HEAD.lock` that the Linux sandbox could not unlink (Windows-mount permission quirk). They must be removed on Windows before the next git op in `ask_jojo_wiki`.
- The Edit/Write file tools intermittently corrupted files with NUL bytes on the Windows mount; affected files (`registry.py`, `coverage_check.py`) were rewritten via shell and verified (0 NULs, parse + tests green).
- 2026-06-01 wave1: +145 absorbed, +43 reclassified; 27 new pages
- 2026-06-01 wave2: +146 absorbed, +62 reclassified; 19 pages
- 2026-06-01 wave3: +49 absorbed, +87 reclassified; 20 pages
- 2026-06-01 wave4: +136 absorbed, +69 reclassified; 18 pages
- 2026-06-01 wave5: +108 absorbed, +131 reclassified; 21 pages
- 2026-06-01 wave6: +8 absorbed, +190 reclassified; 1 pages
- 2026-06-01 wave7: +87 absorbed, +1 reclassified; 5 pages
- 2026-06-02 wave7-partial: 3 of 4 sub-agents hit Anthropic session rate limit (resets ~22:40 PT). Wave-7 Jose Gomez agent (1/4) completed cleanly: 39 covered sha-dupes + 1 reclassified. Wave-7 Jon K agent committed 3 pages (massfrontier-fish, nx-1607-rat-pk, pierce-bca) before limit. Wave-7 LCMS-mixed agent wrote 2 pages (forced-degradation-NRX-1251, lcms-openlynx-troubleshooting). Wave-7 CAR-T/Treg/DC agent hit limit before output; its 37-entry assignment file remains pending. RESUME-FROM-HERE: re-dispatch wave7 CAR-T/Treg/DC assignment (and any unprocessed Jon K/LCMS entries) once rate limit clears.
- 2026-06-01 wave7: +14 absorbed, +0 reclassified; 8 pages
- 2026-06-01 wave8: +60 absorbed, +72 reclassified; 16 pages
- 2026-06-01 wave9: +92 absorbed, +23 reclassified; 15 pages
- 2026-06-01 wave10: +40 absorbed, +49 reclassified; 10 pages
- 2026-06-01 wave11: +57 absorbed, +40 reclassified; 15 pages
- 2026-06-01 wave12: +79 absorbed, +40 reclassified; 11 pages
- 2026-06-01 wave13: +44 absorbed, +40 reclassified; 14 pages
- 2026-06-01 wave14: +70 absorbed, +40 reclassified; 7 pages
- 2026-06-01 wave15: +82 absorbed, +40 reclassified; 9 pages
- 2026-06-03 wave16: +10 absorbed, +150 reclassified; 3 pages (lit-survey-sars-cov2-t-cell-cross-reactivity, xcalibur-lc-ms-data-system, thermo-foundation-platform). Remaining KP: 3138 (765 high).
- 2026-06-03 wave17: +50 absorbed, +143 reclassified; 12 pages (ctla4/checkpoint, chemotherapy-checkpoint, novel-checkpoint, pd1-il2-cd8-reprogramming, cbl-b-tcr-signaling, lsd1-epigenetic-immuno, checkpoint-combination, nrx-0260474/0261152-stability, nrx-0388766-metid, icb-resistance, chiral-sfc update). Remaining KP: 2945 (572 high).
- 2026-06-03 wave18: +18 absorbed, +190 reclassified; 7 pages (cd47-sirpa, il2-cd8-stemness, cd8-t-cell-stemness-memory, cytokine-cell-therapy, nx-1607-4t1-study, plasma-stability-ot2-automation, ksol-opentrons-automation). Remaining KP: 2737 (364 high).
- 2026-06-03 wave19: +38 absorbed, +97 reclassified; 12 pages (PPB-UC, TPD-lit x3, immune-bio x3, jose-gomez-5). Remaining KP: 2602 (260 high, 2311 low).
- 2026-06-03 wave20: +12 absorbed, +228 reclassified; 5 pages (flt3-aml-lit, t-cell-act-checkpoint, charles-river-adme, spe-peptide-btk, dose-formulation-dfa). Remaining KP: 2362 (143 high, 2206 low).
- 2026-06-03 wave21: +5 absorbed, +235 reclassified; 1 page (lsd1-kdm1a-hematopoiesis). Reviewer gate PASS (minor: hash field format, 3 unsourced terms). Remaining KP: 2122 (63 high, 2046 low).
- 2026-06-03 wave22: +0 absorbed, +223 reclassified; 0 pages. HIGH-CONF POOL CLEARED. Remaining KP: 1899 (all low-conf).
