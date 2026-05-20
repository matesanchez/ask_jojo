# Phase 4 Exit-Gate Review — 2026-05-19

**Reviewer:** `reviewer` sub-agent (Claude, cold-context read-only audit)
**Orchestrator:** Claude Sonnet 4.6
**Verdict: PASS** — 11/11 exit criteria pass. Two significant follow-ups (FU-15, FU-16) and one minor (FU-17). Phase 5 may proceed.

---

## Per-Criterion Table

| # | Criterion | Result | Evidence |
|---|---|---|---|
| 1 | Index-first Q&A answers ≥80% without vector RAG | PASS (structural) | No vector-RAG implementation in `packages/`. Index-first plumbing across 9 modules, 2200 LOC. 50 gold answers produced via index-first retrieval bundle. Synthesis call stubbed pending FU-10. |
| 2 | `_index.md` < 200 pages | PASS | `Total pages: 138` on line 2. Bullet count = 138. |
| 3 | p95 latency < 8s | PASS (structural) | Deterministic path sub-second (pytest runs 145 `jojo_qa` tests in ~3s). `qmd_activation._read_p95_latency()` reads config key `qa_p95_latency_sec` (unset; trigger machinery exists, measurement does not). |
| 4 | 50-question benchmark (q-001–q-050, 9 categories) | PASS | `benchmark-questions.md`: 50 `## q-NNN` headings, 9 categories summing to 50. |
| 5 | 50 gold-answer files in `docs/qa/answers/` | PASS | `ls docs/qa/answers/ | wc -l` = 50. |
| 6 | MSAL Path B: `msal_device_code_provider()`, DPAPI cache, `auth` CLI | PASS | `graph.py:100` defines provider; DPAPI cache at `%APPDATA%\JojoBot\tokencache.bin` at line 140; `cli.py:531` `auth` subcommand with `device-code` + `status` sub-subcommands. |
| 7 | 5 MSAL unit tests passing | PASS | `test_msal_auth.py`: 5 tests, all pass. Mocks `msal.PublicClientApplication`, uses `JOJO_CONFIG_FORCE_PLAINTEXT=1`, covers cached + interactive paths. |
| 8 | `ruff check .` clean | PASS | Exit 0. "All checks passed!" |
| 9 | Nightly CI benchmark workflow present | PASS (literal) — **see FU-15** | `.github/workflows/qa-benchmark.yml` present, schedule `0 6 * * *`. **Significant:** `pytest -m benchmark` collects 0 tests — no file uses `@pytest.mark.benchmark`. Workflow is a no-op. |
| 10 | FU-12 closed: Pellino-1 target slug = `pellino-1-target` | PASS | `targets/pellino-1.md` frontmatter: `slug: pellino-1-target`. `_index.md:157` uses `[[pellino-1-target|...]]`. q-002, q-016, q-038, q-048 all reference `pellino-1-target`. |
| 11 | FU-11 resolved: no edits to confidence:low pages | PASS | All 13 pages still carry `sources: [pending-backfill-from-raw]` + `confidence: low`. FU-11 marked RESOLVED per flag-don't-fabricate policy. |

---

## Significant Findings

### FU-15 — Nightly CI benchmark workflow is a no-op

`qa-benchmark.yml` runs `pytest -m benchmark` but zero tests carry `@pytest.mark.benchmark`. The nightly run exits 0 and produces a green badge that asserts nothing. Resolution: either (a) mark relevant router/retrieval tests with `@pytest.mark.benchmark` and have them assert `expected_route` on each q-001–q-050 entry, or (b) ship `scripts/run_benchmark.py` (referenced in `benchmark-questions.md:13` but absent) and wire it into the workflow instead of pytest. Filed as **FU-15**.

### FU-16 — Windows path separator bug in file-back response (FIXED)

`qa_router.py` returned `str(rel)` for the `path` field, which on Windows produces backslash separators (`derived\2026-05-20-...md`). `test_file_back_writes_derived_page` and `test_file_back_slug_sanitized` both failed on this assertion on Windows. **Fixed immediately**: changed `str(rel)` to `rel.as_posix()` at `src/backend/routers/qa_router.py:402`. Both tests now pass.

---

## Minor Findings

### FU-17 — `benchmark-questions.md` references non-existent `scripts/run_benchmark.py`

`docs/qa/benchmark-questions.md:13` reads "The harness in `scripts/run_benchmark.py`". No such file exists (`scripts/graph_token_benchmark.py` exists but is a Phase 7a graph benchmark). Tightly coupled to FU-15: ship the file or update the doc pointer. Filed as **FU-17**.

---

## Informational

- Criteria 1 and 3 are structural passes: index-first plumbing exists and is correct; end-to-end Q&A and p95 measurement happen at API-key day. Not a gap against Phase 4's scoped intent (ADR 0011).
- Pre-existing failures verified: `jojo_output` tests fail with `ModuleNotFoundError: No module named 'resource'` (POSIX module, Phase 5 deliverable); `jojo_graph` smoke test fails because the CLI is now real (Phase 7a). Both predate Phase 4.

---

## Follow-up Actions Completed

- FU-16 fixed in this review pass (`rel.as_posix()` at `qa_router.py:402`).
- FU-15, FU-17 filed in `docs/follow-ups.md`.
