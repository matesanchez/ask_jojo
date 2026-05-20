# Follow-ups

**Purpose.** Running list of non-blocking items we've explicitly chosen to defer, with enough context that picking one up later doesn't require re-deriving the decision. Anything blocking is in `docs/v2_status.md` under "Risk Watchlist" instead. Items are named `FU-N` ("Follow-Up N") so they can be referenced in commit messages, ADRs, and cross-links without re-describing the whole thing.

Sorted newest-first. Each entry includes a severity hint (`must` = must ship before the phase that references it; `should` = quality-of-life; `nice` = worth doing if a future pass is nearby), the phase under which it was surfaced, and a clear exit condition.

---

## 2026-05-20 — Pre-release audits

### FU-23. pymupdf (AGPL-3.0) + html2text (GPL-3.0) — Legal review required before distribution — **OPEN**

**Severity:** must (before any binary distribution of the installer to end-user workstations).
**Surfaced:** License inventory audit (2026-05-20) — `docs/license-inventory.md` flagged two dependencies with copyleft licenses incompatible with proprietary distribution.

- **pymupdf** (AGPL-3.0): Used in `packages/jojo_ingest/` for PDF text extraction. AGPL requires source disclosure for any networked use; distributing the Windows installer containing pymupdf without source release or a commercial license from Artifex may create a compliance exposure.
- **html2text** (GPL-3.0): Used in `packages/jojo_ingest/` for HTML-to-Markdown conversion. GPL-3.0 requires any combined work to also be GPL-licensed, which conflicts with Nurix's proprietary codebase. MIT-licensed replacement `markdownify` has been identified as a drop-in.

**Exit condition (two paths):**
1. **(Preferred)** Replace `html2text` with `markdownify` (MIT). For `pymupdf`, either obtain an Artifex commercial license or replace with `pypdf` (MIT/BSD) — note that `pypdf` has weaker table extraction than pymupdf. Get Legal sign-off on the final dependency list before shipping an installer build.
2. **(Alternative)** Legal confirms in writing that internal-only distribution to Nurix workstations (never shipped to customers or distributed externally) falls within acceptable use. Update `license-inventory.md` with that confirmation.

---

### FU-22. `/api/raw/tree` p95 latency ~1.8 s — **OPEN**

**Severity:** should (blocking for production load-test SLA of 500 ms p95).
**Surfaced:** Stress test (2026-05-20) — async load test showed `GET /api/raw/tree` consistently takes 1.8 s p95 at low concurrency because it walks all 15,473 raw-repo entries on every call.
**Exit condition:** Add a 30–60 s TTL cache on the raw tree response (or paginate) so p95 falls below 500 ms under 100 concurrent users.

---

### FU-21. Hash field normalization — full SHA256 (64 hex) required — **OPEN**

**Severity:** should.
**Surfaced:** Wiki compliance audit (2026-05-20) — multiple pages use truncated 16-hex or 8-hex hash values in `sources:` frontmatter. SCHEMA.md §3 specifies full SHA256.
**Exit condition:** Re-run absorb on affected pages or write a migration script to backfill full-length hashes. Update lint pipeline to enforce 64-hex on new pages.

---

### FU-20. Source path normalization — use `raw/...` form consistently — **OPEN**

**Severity:** should.
**Surfaced:** Wiki compliance audit (2026-05-20) — some pages use `ask_jojo_raw/publicdrive/...` (workspace-relative) while SCHEMA.md §3 shows `raw/onedrive/...`, `raw/publicdrive/...`.
**Exit condition:** Choose one canonical form, add a lint check for it, backfill the 15+ affected pages.

---

## 2026-05-19 — Phase 6 execution (lint surfaced wiki debt)

### FU-19. 9 wikilinks reference genuinely missing wiki pages — **PARTIALLY RESOLVED 2026-05-19**

Writer agent pass reduced broken wikilinks from 27 → 9 (commits c3dc4ef + f70baaf). The 18 resolved links were format violations (Title Case → `[[slug|Title]]`). The remaining 9 reference concepts that have no wiki page yet:
- `[[Machine Learning Automation]]` — `loka-ml-engagement`
- `[[AKTA Chromatography Systems]]` — `laboratory-instruments`
- `[[Thermal Shift Analyzer (Tycho)]]` — `laboratory-instruments`
- `[[Protein Degradation Assays]]` — `cell-screening`
- `[[Echo Liquid Handler]]` — `cell-screening`
- `[[Activity Base LIMS]]` — `cell-screening`
- `[[Thermal Stability Assessment]]` (×2) — `protein-quality-control`, `protein-sciences-sops`
- `[[Large-Scale Expression Planning]]` — `fermentation-request`

- **Severity.** should (each is a genuine content gap — wiki page for this concept doesn't exist yet)
- **What "done" looks like.** Create a stub wiki page for each concept, or absorb relevant raw source material into a real page; then `jojo-lint check wikilink` reports 0 findings.
- **Why deferred.** These require a Phase 2-style absorb pass on relevant raw source documents (AKTA, Tycho, Echo, Activity Base LIMS, etc.). Scope: ~9 new pages.

---

## 2026-05-19 — Phase 5 exit (code reviewer pass)

### FU-18. POSIX-only sandbox import causes collection warnings on Windows

- **Severity.** should
- **Surfaced while.** Phase 5 reviewer pass 2026-05-19.
- **Problem.** `packages/jojo_output/sandbox/runner.py:29` does `import resource` at module level. On Windows, this makes `test_ast_guard.py`, `test_sandbox_runner.py`, `test_sandbox_spec.py` uncollectable under `pytest packages/jojo_output/` — pytest prints import-collection errors rather than clean skips. The integration tests in `test_output_endpoints.py` correctly carry `@pytest.mark.skipif(win32)` and skip gracefully, so the effect is cosmetic rather than functional.
- **What "done" looks like.** Add `pytest.importorskip("resource")` at the top of each affected test file, or add a platform guard inside `packages/jojo_output/sandbox/__init__.py` so the module-level import only happens on POSIX hosts. Either approach gives `pytest packages/` a clean collection pass on Windows.
- **Why deferred.** Pre-existing and cosmetic. Tests still run correctly (skip gracefully); the only consequence is a collection warning in the output.

---

## 2026-05-19 — Phase 4 exit (code reviewer pass)

### FU-17. `benchmark-questions.md` references non-existent `scripts/run_benchmark.py`

- **Severity.** should (before anyone tries to run the benchmark harness)
- **Surfaced while.** code reviewer pass 2026-05-19.
- **Problem.** `docs/qa/benchmark-questions.md:13` says "The harness in `scripts/run_benchmark.py`" but no such file exists. `scripts/graph_token_benchmark.py` is a Phase 7a token-reduction benchmark, not a Q&A benchmark.
- **What "done" looks like.** Either ship `scripts/run_benchmark.py` (the Q&A benchmark harness per FU-15 scope) or update the reference in `benchmark-questions.md` to point at whatever the actual harness turns out to be.
- **Why deferred.** Tightly coupled to FU-15. Will resolve together.

### FU-16. Windows path separator in `/api/qa/file-back` response  — **RESOLVED 2026-05-19**

Fixed immediately: `qa_router.py:402` changed from `str(rel)` to `rel.as_posix()`. Both `test_file_back_writes_derived_page` and `test_file_back_slug_sanitized` now pass on Windows.

- **Severity.** must (2 test failures on Windows, none on Linux)
- **Surfaced while.** code reviewer pass 2026-05-19.
- **Problem.** `rel.relative_to(wiki_root)` returns a `pathlib.Path` with OS-native separators. `str(rel)` on Windows produces `derived\2026-05-19-...md`; tests assert `startswith("derived/")`. Fix: `rel.as_posix()`.

### FU-15. Nightly CI benchmark workflow is a no-op

- **Severity.** should (before Phase 5 exit — the benchmark gate is a real exit criterion)
- **Surfaced while.** code reviewer pass 2026-05-19.
- **Problem.** `.github/workflows/qa-benchmark.yml` runs `pytest -m benchmark`. No test in the repo carries `@pytest.mark.benchmark`. `pytest --collect-only -m benchmark` collects 0 tests. Nightly exits 0, green badge, asserts nothing.
- **What "done" looks like.** Either (a) add `@pytest.mark.benchmark` to router/retrieval tests that assert `expected_route` on each q-001–q-050 entry, or (b) ship `scripts/run_benchmark.py` (referenced in `benchmark-questions.md`) as a real benchmark harness and wire it into the workflow. Option (b) gives a richer benchmark signal (full retrieval bundle, not just route classification).
- **Where to start.** `scripts/run_benchmark.py` — load `benchmark-questions.md`, run `router.classify + index_loader.rank_candidates` on each question, assert `expected_route`, output pass/fail. ~150 LOC. Then update `qa-benchmark.yml` to call it.
- **Why deferred.** The workflow plumbing exists; the harness is the missing piece. Safe to ship before Phase 5 exit.

---

## 2026-05-19 — Phase 4 exit (external reviewer pass)

### FU-14. Truncated source hashes + cluster-path source entry

- **Severity.** should (before Phase 6 nightly citation-chain integrity check)
- **Surfaced while.** external reviewer pass 2026-05-19 — reading wiki page frontmatter.
- **Problem.** ~15% of `sources[*].hash` fields are truncated (8–20 chars vs 64-char SHA256). One page (`baculovirus-expression.md`) has a cluster-level `sources.path = raw/onedrive/baculovirus-cluster` rather than a leaf manifest key. Both break the citation chain that `raw_fallback.search` uses.
- **What "done" looks like.** All `sources.hash` fields are 64-char SHA256. `baculovirus-expression.md`'s source is broken out to individual manifest entries. `jojo-compile verify --fix-hashes` runs clean.
- **Where to start.** `jojo_compile/verify.py` — walk `ask_jojo_wiki/`, parse frontmatter, for each `sources[*]` entry look up path in `manifest.json`, compare and replace hash.
- **Why deferred.** Does not affect content accuracy or Phase 4 retrieval. Safe to do before Phase 6 citation-chain lint check.

### FU-13. Wikilink format in `related` field — `[[Title]]` → `[[slug|Title]]`

- **Severity.** should (before next `_graph.json` rebuild at scale)
- **Surfaced while.** external reviewer pass 2026-05-19 — ~80% of reviewed pages had this issue.
- **Problem.** Most wiki pages use bare-title wikilinks in `related:` YAML list (e.g., `"[[Delphi]]"`) rather than `[[slug|Title]]` per SCHEMA.md §3. The graph builder cannot resolve bare-title links to graph nodes; the next `_graph.json` rebuild will produce "unresolved wikilink" warnings for these edges.
- **What "done" looks like.** All `related:` entries in non-derived pages use `[[slug|Title]]` format. `jojo-graph rebuild` runs without unresolved-wikilink warnings.
- **Where to start.** New `scripts/fix_related_wikilinks.py`: load slug-to-title map from `_index.md`, walk all `.md` files in `ask_jojo_wiki/`, parse `related:` YAML, resolve each title to its slug, rewrite. One pass, ~30 minutes of scripting.
- **Why deferred.** Does not affect Phase 4 slug-index-first retrieval. Graph will still build (with unresolved edges silently skipped). Safe to fix before Phase 6.

---

## 2026-04-30 — Phase 4

### FU-11. Source backfill on the 13 frontmatter-backfilled needs-review pages  — **RESOLVED 2026-05-19**

Zero edits made per the flag-don't-fabricate rule (GOAL_PROMPT.md §Constraints): no page body contained inline raw citations that could be resolved to `manifest.json` entries without fabricating source paths. Pages retain `confidence: low` and `sources: [pending-backfill-from-raw]`; the retrieval scorer correctly deprioritizes them. Resolution: the flag-don't-fabricate rule is the correct policy here — this FU is closed as "won't backfill from prose alone." When API key lands, `jojo-compile absorb --migrate-frontmatter` can re-derive sources from the raw corpus.

- **Severity.** must (before Phase 4 Q&A starts citing these pages with confidence > low)
- **Surfaced while.** auditing `_needs_review.md` ahead of Phase 4 deterministic plumbing. 13 pages predated the post-batch-24-cbl checkpoint and were missing required frontmatter fields (`title`, `slug`, `created`, `last_updated`, `last_reviewed`, `sources`). The 2026-04-30 backfill (this session) added all of those fields with placeholder values; the `sources:` field has a single `pending-backfill-from-raw` entry instead of the real raw paths.
- **Problem.** Five `decisions/...` pages and eight `programs/...` pages have valid frontmatter shape but their `sources:` field is a placeholder. Phase 4 Q&A's citation chain depends on `sources[*].path` resolving to real raw entries; today these pages return placeholder strings to any downstream consumer that reads frontmatter. `confidence: low` is a partial mitigation (the retrieval-rank scoring deprioritizes low-confidence pages) but Q&A *can* still pick them as candidates if the question matches their title or slug.
- **What "done" looks like.** For each of the 13 pages: read the body prose, identify the raw entries cited inline (the body is descriptive of what was in the source), use `raw_fallback.search` or a manual `manifest.json` lookup to resolve the citation to a real raw entry path + hash, replace the placeholder `sources:` block. Promote `confidence: low` to `medium` when the source resolves cleanly. Update `_needs_review.md` to drop the page from "Source backfill pending."
- **Where to start.** The 13 pages are listed in `_needs_review.md` under "Source backfill pending." Each is small (median ~30 lines of body prose); the work is a focused 30-minute Cowork session per page or one consolidated batch session against the 13 pages. The compile pipeline can also do this once the API key lands by running an absorb pass with `--migrate-frontmatter` against just these pages.
- **Why deferred.** Frontmatter shape is now valid (constitutional violation cleared); Phase 4 plumbing can ship without resolving this. Acceptable for the first ~10–20 Cowork Q&A sessions, since the deterministic retrieval will deprioritize `confidence: low` pages anyway.

### FU-12. Pellino-1 slug collision (program vs target page share `slug: pellino-1`)  — **RESOLVED 2026-05-19**

`targets/pellino-1.md` renamed to `pellino-1-target` slug; `_index.md` entry and `benchmark-questions.md` q-002 and gold answer `2026-04-30-pellino-1-peli2-redundancy.md` all updated. Convention now consistent with `cbl-b` / `cbl-b-target`.

- **Severity.** should
- **Surfaced while.** smoke-testing `index_loader.load_index` against the real wiki on 2026-04-30. Two pages share the same slug `pellino-1`: `programs/pellino-1.md` (program) and `targets/pellino-1.md` (target). `index_by_slug`'s last-write-wins behavior means one page silently shadows the other in any retrieval call that goes through the slug -> entry dict.
- **Problem.** Constitutional violation per `SCHEMA.md` §3 ("the `slug` must match the filename without the `.md` extension, which makes wikilinks unambiguous"). Two pages with the same slug means wikilinks like `[[pellino-1]]` resolve ambiguously — the index, the graph builder, and the retrieval bundle all collapse the two pages into one entry. The Q&A session that asked about "Peli2 redundancy" today (q-002) noticed and read both pages, but the deterministic retrieval bundle would have picked only one.
- **What "done" looks like.** Rename one of the slugs. Convention: program pages keep the bare slug (`pellino-1`), target pages take the `-target` suffix (`pellino-1-target`) — matching `cbl-b` (program) / `cbl-b-target` (target) which already follows this rule. Edit `targets/pellino-1.md` frontmatter to `slug: pellino-1-target`, rename the file (or leave the file but update `_index.md` and `_backlinks.json` references), and update any inbound wikilinks. The compile pipeline's link-step at the next checkpoint catches the dangling references and a small absorb pass fixes them.
- **Where to start.** `ask_jojo_wiki/targets/pellino-1.md` frontmatter; `_index.md` line for the target page; `_backlinks.json` keys + values. About 15 minutes of work.
- **Why deferred.** Phase 4 plumbing absorbs the cost (the Pellino-1 question's answer is correct because the Cowork session read both pages by hand). Worth fixing before the API-driven loop runs at scale.

---

## 2026-04-24 — Phase 2

### FU-10. Anthropic API key — unblock AWS payment leg

- **Severity.** must (for automated Phase 2 absorb, lint, and Q&A; Phase 6 nightly lint is entirely gated on this)
- **Surfaced while.** planning Phase 2 execution. AWS payment-method onboarding for Anthropic API billing has been in flight since 2026-04-22 and remains stuck. Every earlier Phase 0 plan assumed keys would land before Phase 2 started; they have not. Captured formally as a follow-up (rather than just a `[~]` on the Phase 0 checklist) so there is a single stable reference for other docs to point at.
- **Problem.** `packages/jojo_compile/`, `packages/jojo_lint/`, and `packages/jojo_qa/` all require live Anthropic API access to reach their exit criteria. Today we have Claude model access via claude.ai and the Cowork desktop app but no programmatic key — so the autonomous pipelines can't run. ADR 0010 is the decision to run Phase 2 absorb via human-triggered Cowork sessions while this stays open; the plumbing that ADR ships (prompt + queue + constitutional commit format) is intentionally designed to collapse into `jojo_compile absorb` the moment the key lands.
- **What "done" looks like.** (a) A working API key in `%APPDATA%\JojoBot\config.json` under `anthropic_api_key` (SECRET_KEYS), routed through `jojo_core.config.get`. (b) Smoke test: `jojo-compile ping` calls the Messages API against Sonnet 4.6 with a 10-token prompt and returns a 200. (c) Budget alerts wired up on the Anthropic console per `docs/budget-model.xlsx` caps. (d) First live absorb run replays the human-triggered queue and its output diff is reviewed — that is the natural regression baseline.
- **Where to start.** Not a code task — a billing / procurement task. When it unblocks, `packages/jojo_core/config.py` already has the DPAPI machinery; adding `"anthropic_api_key"` to `SECRET_KEYS` is a one-line edit. `packages/jojo_compile/write.py` will host the Anthropic client.
- **Why deferred.** External dependency. Not the team's to resolve day-to-day. Filed here so ADR 0010, v2_status.md, and future phase notes have a stable identifier.

---

## 2026-04-24 — Phase 1

### FU-9. `DriveConnector._walk` hangs indefinitely on torn-down SMB sessions  — **RESOLVED 2026-04-24**

Resolved by the 2026-04-24 ingest-hardening pass: `packages/jojo_ingest/_watchdog.py` + call-site integration in `drive.py` (`_walk` `iterdir`, `_safe_stat`, and `_build_entry` convert hand-off all now run inside daemon threads with per-call timeouts of 30s / 10s / 120s respectively). Operational prerequisite (layer b, NIC power-management) is still on Mateo before the next overnight publicdrive run.

- **Severity.** must (before any unattended first-walk of publicdrive can complete)
- **Surfaced while.** running an overnight manual publicdrive ingest from 2026-04-23 15:52 through 2026-04-24 ~09:00. Process alive at 17h wall-clock but with **0.03 seconds of CPU time**, 12 MB working set, and the log's `LastWriteTime` frozen at 15:55:18 (3 minutes after launch). Zero `.md` files written, zero manifest entries added. The python handle was blocked inside a single `os.scandir`/`os.stat` syscall for the entire night. `P:\` itself was reachable in the morning — the handle was orphaned, not the drive.
- **Problem.** `packages/jojo_ingest/drive.py:_walk` issues blocking `os.scandir`/`os.stat` calls against SMB with no per-call timeout. The Track 2 `OSError` catch (task #51) rescues the walker when the syscall *returns* an error (WinError 59, etc.) — it does nothing for syscalls that never return at all, which is the common failure mode when the NIC goes to selective suspend and the SMB session is torn down silently. Scheduled tasks have an `ExecutionTimeLimit=2h` in `Register-JojoBotTasks.ps1`, which kills these hangs at the 2h boundary; manual runs have no such safety net. Either way, the 2h budget is almost certainly not enough for a first-walk of publicdrive, so the scheduled task will also never succeed at an initial walk until the underlying hang is fixed.
- **What "done" looks like.** Two layers, both needed.
    - **(a) Code.** Wrap every `os.scandir`/`os.stat` call in `_walk` in a watchdog thread with a ~30s timeout. On timeout, log a WARNING and skip the subtree — treat it the same as any other `OSError`. The watchdog does not have to be cross-platform elegant; Python stdlib `threading.Thread` + `Event` is fine. One new test: seed a mock `os.scandir` that sleeps longer than the watchdog's budget, assert the walker emits a timeout warning and continues.
    - **(b) Operational doc.** Add a "first-walk prerequisites" section to `ops/scheduler/README.md`: disable "Allow the computer to turn off this device to save power" on the active ethernet adapter before any overnight publicdrive run, and prefer kicking off the first walk on a desktop rather than a laptop. Cheap edits, expensive omissions.
- **Where to start.** `packages/jojo_ingest/drive.py` — `_walk` is the only caller that hits SMB; upload/onedrive (local mount) don't need it. `packages/jojo_ingest/test_drive.py` already has an `OSError`-path test from Track 2; the new hang test slots in next to it.
- **Why deferred.** Three of four connectors already soak cleanly; publicdrive is the one laggard. Phase 2's compile pipeline doesn't touch publicdrive yet (compile consumes from `ask_jojo_raw/` via the manifest, and it's still >19k files from the other three connectors). First walk can be manually kicked off chunk-by-chunk (narrow `--source` to one top-level folder at a time) as a workaround until (a) ships.

---

## 2026-04-23 — Phase 1

### FU-8. Six SharePoint sites 401 under delegated Mateo-identity token

- **Severity.** should
- **Surfaced while.** reviewing the 11:07 and 15:00 sync-sharepoint runs on 2026-04-23. The 11:07 run used a fresh Graph Explorer token and successfully absorbed 313 files across the rest of SharePoint, but six sites 401'd anyway — meaning this isn't the "token expired" failure mode (which the 15:00 run cleanly demonstrated). It's an access-control failure that a fresh token will not fix.
- **Problem.** Two distinct sub-cases, both worth capturing because the fix differs:
    - **Site-level 401 (5 sites).** `NurixNet`, `DELTriageSeedProjects`, `DELScreenTeam`, `CRUKGrant`, `BiortusDiscoveryCo.Ltd` all 401 on the initial `GET /sites/nurix.sharepoint.com:/sites/<site>` discovery call. Mateo's user identity is not a member of these sites.
    - **Item-level 401 (1 site).** `ProteinScience` resolves at the site level but 401s on a specific `/items/013A66TNQTEULTEZ4ABBB2LAMWRYJT7IFB/children` call — i.e. a restricted subfolder inside an otherwise-accessible site.
  Neither case is token-related. Because Path B (MSAL device-code) also runs as the signed-in user, upgrading auth paths will not change the outcome — Path B gets the same `401` from the same permission check. The only fixes are (a) per-site access grants from SharePoint admins (solves the 5-site case site-by-site and the 1-site subfolder case), or (b) Path C client-credentials with tenant-wide `Sites.Read.All` / `Sites.FullControl.All` app permission (solves all six in one shot but is explicitly out of scope per ADR 0007 and requires IT sign-off).
- **What "done" looks like.** A short written decision per site: either "request access from <owner>, track grant, re-enable sync" or "accept as out-of-scope, drop from `ingest_config.sites`." For ProteinScience specifically, narrow the `items/.../children` call so the restricted subfolder is excluded rather than repeatedly triggering a 401 every run. If more than ~half of requested sites fall into category (b), that's the forcing function to revisit Path C with IT.
- **Where to start.** Confirm the owners list in SharePoint admin UI for each of the five site-level-denied sites (fastest: email the site's displayed "Owner" contact). `packages/jojo_ingest/sharepoint.py` already logs-and-skips cleanly, so nothing is broken — this is a coverage/scope decision, not a code bug. If we go the exclusion route for the ProteinScience subfolder, the `config.json` schema already supports `exclude_item_ids` (check against current shape).
- **Why deferred.** Not in Phase 1 exit criterion. The connector degrades gracefully (401 → warning → exit 0, no crash, no scheduler noise). 313 files/run from the accessible sites is enough to satisfy Gate 2 (≥2 connectors contributing). Resolution requires cross-org coordination that doesn't block Phase 2 compile work.

### FU-7. Default `--raw` from config.json or sibling-directory convention

- **Severity.** should
- **Surfaced while.** running `python -m jojo_ingest sync publicdrive` interactively to chase down the long-walk symptom and getting `error: the following arguments are required: --raw`. Every real invocation of `sync` (scheduled tasks, validation wrappers, one-off debugging runs) targets the same `ask_jojo_raw/` sibling directory — yet the CLI insists the operator spell it out every time.
- **Problem.** `--raw` is required on `jojo-ingest sync`, which makes sense in the abstract (the tool should not guess where to write raw ingest output) but in practice means (a) every scheduled-task registration hard-codes the path, (b) every ad-hoc operator run gets a confusing error on first try, and (c) there's nowhere to override per-machine without editing the scheduler script. Meanwhile `%APPDATA%\JojoBot\config.json` already exists and is the natural home for machine-local paths.
- **What "done" looks like.** Three-layer resolution order for `--raw`: explicit CLI flag > `config.json` key `raw_repo_path` > derived default `<cwd_ancestor_containing_ask_jojo>/ask_jojo_raw`. CLI help text spells out the resolution order. `jojo-core config set raw_repo_path <path>` is the supported way to pin a machine-wide default. Scheduled-task registration stops hard-coding the path.
- **Where to start.** `packages/jojo_ingest/cli.py` — the argparse subparser for `sync`. `packages/jojo_core/config.py` already has the DPAPI-aware get/set helpers; `raw_repo_path` is not a secret so it skips the SECRET_KEYS list. One new test: config-set path wins over derived default, CLI flag wins over config-set.
- **Why deferred.** Annoying papercut, not a correctness issue. Scheduled tasks already work; they just carry a hard-coded path that a future machine migration will have to retrace.

### FU-6. Venv preflight in `jojo_ingest.cli.main()`

- **Severity.** should
- **Surfaced while.** debugging `ModuleNotFoundError: No module named 'httpx'` from a bare `python -m jojo_ingest sync` on Mateo's laptop. Root cause: the active shell Python was the Microsoft Store launcher stub, not `ask_jojo\.venv\Scripts\python.exe`. Fix on the call site was a fully-qualified venv Python path — but the error surface was a 12-line traceback ending in a library import, which reads like a code bug rather than an environment bug.
- **Problem.** First-time operator runs (or runs from a new terminal where the venv wasn't activated) fail with cryptic import errors instead of a clear "you're not in the venv" message. Even experienced users waste a minute diagnosing. And scheduled tasks, which always invoke via absolute venv Python paths, don't exercise this path at all — so a regression here wouldn't be caught until an interactive run.
- **What "done" looks like.** `jojo_ingest.cli.main()` (and peer CLIs — `jojo_core`, `jojo_compile`, etc. once they exist) starts with a three-line preflight: `import sys; if "ask_jojo" not in sys.executable and not os.environ.get("JOJO_SKIP_VENV_CHECK"): print_friendly_error_and_exit()`. Friendly error shows the expected venv path and the activation command. Escape hatch env var is documented for CI (GitHub Actions ships its own Python; no venv in the ask_jojo sense).
- **Where to start.** `packages/jojo_ingest/cli.py` top of `main()`. New module `packages/jojo_core/_venv_check.py` so every CLI shares the same check. One new test per CLI that sets `JOJO_SKIP_VENV_CHECK` to confirm the escape hatch works and another that spawns a subprocess from a tempdir with a non-venv Python shim to confirm the friendly error path.
- **Why deferred.** Not a correctness bug; scheduled tasks and CI both skip this path entirely (they use venv-qualified or CI-environment Pythons). Worth doing before onboarding a second operator.

### FU-5. Verify sibling-repo remote before declaring "pushed"

- **Severity.** should
- **Surfaced while.** running M8 (private-visibility check) of the Phase 1 wrap-up. `gh repo view matesanchez/ask_jojo_raw --json visibility` returned "Could not resolve to a Repository" — not because the visibility was wrong but because the repo had never been pushed at all. `ask_jojo_raw/.git/config` was git-init'd locally with three scaffolding commits on `main` but had no `[remote "origin"]` block. The privacy invariant from ADR 0006 was trivially true (nothing to be public) and also not meaningfully verifiable.
- **Problem.** The Phase 1 deliverables checklist in `v2_status.md` and the wrap-up checklist both assumed `ask_jojo_raw/` was a live GitHub repo from day one. Nothing in our tooling catches the case where a sibling repo is git-init'd but never pushed — the ingest driver writes files, the manifest grows, change records accumulate, and none of it leaves the laptop. One laptop failure = all raw content gone. This would have been silently true right up until we needed the backup.
- **What "done" looks like.** Two layers of defense. (a) Acceptance-style check in `ops/validation/Run-ValidationSyncAll.ps1` or a new `ops/validation/Check-RawRepoRemote.ps1` that runs `git -C "$rawDir" remote -v` and fails loud if empty, plus `gh repo view <org>/<repo> --json visibility,isPrivate` to confirm visibility is PRIVATE. Wire it into the scheduled sync wrapper so Path A scheduled tasks refuse to run if the raw tree is laptop-only. (b) Extend `Install-JojoBot.ps1` with a one-time `gh repo create <org>/<repo> --private --source <rawDir> --remote origin --push` step so greenfield installs land a pushed repo by default.
- **Where to start.** `ops/scheduler/Run-ScheduledSync.ps1` already tees output and writes event-log entries — a 20-line prelude that checks `git -C $rawRepoPath remote -v` slots in cleanly. The installer side is a single new `Ensure-RawRepoRemote` function called from `Install-JojoBot.ps1` step 4-or-5.
- **Why deferred.** Only surfaces as an incident if the laptop dies before we find out — which we just did find out, at Phase 1 exit, while the raw tree is still under 1 GB and easily recreatable. Good enough to file, act on before the 7-day soak accumulates another round of ingest that we'd hate to lose.

### FU-1. Publicdrive walker — streaming writes + timeout  — **PARTIALLY RESOLVED 2026-04-24**

Streaming writes leg resolved by d06e8a3 (`packages/jojo_ingest/driver.py` periodic `manifest.save()` every 500 absorbs). Watchdog timeout leg addressed at the wrapper level by 2026-04-24's `Run-ScheduledSync.ps1` rewrite (`-MaxRuntimeMinutes` param, defaults 1440m for publicdrive / 720m onedrive / 360m drive / 120m sharepoint, exit 124 on deadline). Still open: the connector-level `config.json` watchdog described below — an operator running `python -m jojo_ingest sync publicdrive` interactively (bypassing the wrapper) still has no per-call deadline beyond the in-process `_watchdog.py` per-syscall timeouts. Low priority once Path A scheduling is the canonical flow.

- **Severity.** should
- **Surfaced while.** running the first real `sync-all` against `P:\` on Mateo's laptop — the initial walk ran multi-hour before producing any manifest output.
- **Problem.** `packages/jojo_ingest/drive.py`'s `_walk` yields lazily but `IngestDriver` today batches writes via a single `manifest.save()` call at end-of-run. For a ~100k file tree with per-item conversion, that's hours of "did it crash or is it still walking?" with nothing visible to an operator or to the Raw tab UI.
- **What "done" looks like.** `IngestDriver` flushes change records + manifest updates every N successful entries (N=500 is a reasonable default) so progress is visible mid-run and a mid-walk crash costs only the last N files. Plus a watchdog timeout per-connector (say, 4 hours for publicdrive first-walk; configurable via `config.json`) that fails loud instead of hanging a scheduled task forever.
- **Where to start.** `packages/jojo_ingest/driver.py` — there's one call site for `manifest.save`. A 30-line change plus 1 new test (seed 2000 mock entries, assert manifest.save called >=4 times).
- **Why deferred.** Not in the Phase 1 exit criterion. First publicdrive walk is a one-time tax; subsequent runs already short-circuit via manifest dedup.

### FU-2. Per-connector singleton lock  — **PARTIALLY RESOLVED 2026-04-24**

Wrapper-level lock added in 2026-04-24's `Run-ScheduledSync.ps1` rewrite (PID-stamped `%TEMP%\JojoBot-<connector>.lock`, stale-lock detection, `-IgnoreLock` override). Catches the Task-Scheduler double-fire case, which is the actual incident class. Still open: a Python-layer `jojo_core/singleton.py` context manager for the case where someone runs `python -m jojo_ingest sync publicdrive` interactively while a scheduled run is also live — the wrapper-level lock can't see that. Low priority but worth doing before adding a second operator.

- **Severity.** should
- **Surfaced while.** debugging publicdrive status today — observed two `python -m jojo_ingest sync publicdrive` processes alive simultaneously. One was a Microsoft Store Python launcher stub (harmless), but the observation exposes that nothing in the code prevents a real double-invocation from racing the same manifest and change-record files.
- **Problem.** Manifest append-only semantics protect us from straight-up corruption, but two walkers of the same tree will double the I/O, potentially thrash SMB handles on `P:\`, and produce contradictory change records on the same date.
- **What "done" looks like.** A per-connector lock file under `%APPDATA%\JojoBot\locks\<connector>.lock` acquired at the top of each `sync` command. Windows: `msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)` with a friendly "another `sync <connector>` run is in progress (pid N since T)" error; Unix: `fcntl.flock` with `LOCK_EX | LOCK_NB`. Stale-lock detection via pid + start time vs `psutil.Process()` (if the PID is gone, re-claim).
- **Where to start.** New `packages/jojo_core/singleton.py` as a context manager; `jojo_ingest.cli` wraps each `sync` command in it. One new test per platform.
- **Why deferred.** Nice hygiene; not yet seen to cause actual corruption.

### FU-3. Path B — MSAL device-code token provider  — **RESOLVED 2026-05-19**

`msal_device_code_provider()` shipped in `packages/jojo_ingest/graph.py` with DPAPI-encrypted token cache at `%APPDATA%\JojoBot\tokencache.bin` (Phase 4 round-2 backend delegation). `auth` CLI subcommand added to `packages/jojo_qa/cli.py`. 5 unit tests in `test_msal_auth.py` passing. Path B checkbox in Phase 1 deliverables checklist marked done.

- **Severity.** must (for fully unattended SharePoint scheduled runs)
- **Surfaced in.** ADR 0007.
- **Problem.** Delegated tokens from Graph Explorer (Path A) live ~60 minutes. Scheduled SharePoint task re-auths to a dead token between 4h runs until the operator manually pastes a fresh one via `jojo-core config set graph_access_token "<new>"`.
- **What "done" looks like.** `msal_device_code_provider()` slots in behind the existing `TokenProvider` interface. First invocation prompts device-code flow (browser URL + one-time code); thereafter reads `%APPDATA%\JojoBot\tokencache.bin` (DPAPI-sealed per ADR 0009's SECRET_KEYS pattern), silently refreshing the short-lived access token from the long-lived refresh token (~90 days). Scheduler wrapper gains an "auth broken, operator please re-run Install-JojoBot.ps1 -Reconfigure" event-log path.
- **Where to start.** `docs/ops/path-b-msal-device-code-setup.md` already has the dummy's-guide walkthrough of the Entra app registration side. `packages/jojo_ingest/graph.py` is the code-side slot; net new deps: `msal`.
- **Why deferred.** IT hasn't needed to approve the app registration yet (delegated `Sites.Read.All` consent covers Phase 1). Path A gets us through the exit criterion; Path B is the upgrade for fully unattended day-to-day.

### FU-4. New ADR for Path B (if needed)

- **Severity.** nice
- **Surfaced from.** FU-3.
- **Problem.** When Path B ships, ADR 0007 was framed as "start with Path A, track B + C as later paths." The provisioning that unblocks Path B (app registration + consented scopes) plus any operational quirks we discover while deploying are worth capturing — the question is whether that's a new ADR or a follow-up amendment to ADR 0007.
- **What "done" looks like.** Decide at ship time. If Path B ships as drawn in ADR 0007 with no surprises, an amendment note under "Revisit triggers" is enough. If the deploy surfaces new decisions (cert vs secret storage, cache location, refresh-before-expiry window), write a new ADR at the next available number. (ADR 0010 was originally earmarked for this here; it has since been consumed by the compile-via-Cowork decision — the reservation is released.)
- **Why deferred.** Premature to write the ADR before the decision exists.

---

## Template for new entries

```
### FU-N. <short title>

- **Severity.** must | should | nice
- **Surfaced while.** <what you were doing when this came up>
- **Problem.** <one paragraph>
- **What "done" looks like.** <concrete acceptance criteria>
- **Where to start.** <file / function / test pointer>
- **Why deferred.** <the reason you're not doing it right now>
```
