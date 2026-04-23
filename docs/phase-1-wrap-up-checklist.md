# Phase 1 Wrap-Up Checklist

**Purpose.** One-page gate sheet for declaring Phase 1 done and moving on to Phase 2 with a clean conscience. Every MUST item is exit-criterion-adjacent; every SHOULD item is hygiene that future-Mateo (or future-anyone) will thank present-Mateo for.

**How to use.** Walk top to bottom. If a box is unchecked, either check it or explicitly write "deferred — see follow-up FU-N" next to it. No blank checkboxes — every box gets an answer.

**Date started.** 2026-04-23
**Date completed.** _TBD — fill in when every MUST is either ✅ or "deferred with a tracked follow-up"_

---

## Exit criterion gates (from `PLAN.md` §6 Phase 1)

These are the six gates decomposed in `docs/phase-1-exit-evidence.md`. Reproduced here as a single-line checklist so the wrap-up session doesn't need to open a second doc.

- [x] **G1.** ≥100 files ingested into `ask_jojo_raw/` (observed 19,310+ at 2026-04-23 11:09 PT)
- [x] **G2.** ≥2 connectors contributing (OneDrive + SharePoint; publicdrive landing alongside)
- [x] **G3.** Access-level metadata correct on every entry (`all-FTE` per ADR 0006)
- [x] **G4.** No crashes — ingest exits 0; per-file failures logged-and-skipped
- [x] **G5.** Manifest shows what got ingested (19k+ entries; per-change audit trail in `_changes/`)
- [ ] **G6.** Daily incremental sync runs unattended for a week — **soak window 2026-04-23 → 2026-04-30**; SharePoint gated on Path B (FU-3) for fully-unattended. Three of four connectors already fully unattended.

---

## MUST-have items before calling Phase 1 done

- [x] **M1.** `docs/phase-1-exit-evidence.md` exists, cites at least one validation report under `ops/validation/reports/`, and covers all six gates.
- [x] **M2.** `docs/v2_status.md` reflects Phase 1 as 🟢 with exit date, and a dated note explaining what tipped it over.
- [x] **M3.** Amendment-log entry added for 2026-04-23 in `docs/v2_status.md`.
- [x] **M4.** Every item on the Phase 1 deliverables checklist in `v2_status.md` is either `[x]` done or `[ ]` with a tracked follow-up in `docs/follow-ups.md` or an open ADR.
- [x] **M5.** All new or modified `.ps1` files in this phase are pure-ASCII (CP1252-safe per feedback memory + ADR 0009).
- [x] **M6.** `pytest -q` green on the tip. 129 tests minimum (108 from Phase 1b + 21 post-1b hardening + DPAPI). **Verify immediately before staging the final commit.**
- [x] **M7.** `ruff check` clean on `packages/` and `src/backend/`.
- [x] **M8.** `ask_jojo_raw/` remains a **private** GitHub repo (ADR 0006 invariant). Spot check with `gh repo view matesanchez/ask_jojo_raw --json visibility`. Verified 2026-04-23 after push: visibility=PRIVATE. Sibling-repo remote verification filed as FU-5 so this gap catches itself in future phases.
- [x] **M9.** Staging plan in `docs/ops/phase-1-staging-plan.md` lists every uncommitted file and explains which commit each belongs to. Nothing uncommitted that isn't accounted for.
- [x] **M10.** Three commits pushed to `origin/main` in order per staging plan: Track 2 pt. 2 → resilience tidy-up → docs wrap-up. Pushed 2026-04-23 as `bc563ed` → `19082b7` → `13ce982`.
- [ ] **M11.** Seven-day unattended-sync soak kicked off (G6). Leave unchecked until 2026-04-30 when the window closes cleanly. If a crash lands inside the window, record the incident + reset the window.

---

## SHOULD-have hygiene before Phase 2 starts

- [x] **S1.** Follow-ups carried out of Phase 1 are each filed in `docs/follow-ups.md` with severity + acceptance criteria + starting pointer (FU-1 through FU-4 today).
- [x] **S2.** `docs/v2_status.md` has a Phase 2 kickoff note (starting date + first concrete work item).
- [x] **S3.** Open questions list in `docs/v2_status.md` reviewed; anything cleared gets an answer date in the table.
- [ ] **S4.** Anthropic API key provisioned — reclassified from Phase 0 blocker to Phase 2 prerequisite (Phase 1 made no Claude calls). **Action before first `jojo_compile absorb` run.**
- [ ] **S5.** `packages/jojo_compile/` skeleton stood up. Phase 2's equivalent of Phase 1's "package skeleton first, fill in later" pattern.
- [ ] **S6.** Quick look at the Raw tab UI in a browser against the real 19k-file manifest — confirm tree paginates / doesn't hang, metadata panel populates, supersedence pointers resolve.
- [ ] **S7.** Skim the latest `sync-all_*.log` for anything noisy we should file as an additional follow-up (unexpected warnings, long-running stages we didn't anticipate, weird file types we should ignore via `.jojoignore`).
- [ ] **S8.** `ask_jojo_raw/` backed up off-laptop somewhere non-OneDrive — it's private + git-tracked, but a one-time `robocopy` snapshot to an external drive the day before the 7-day soak lands gives us a known-good baseline if the soak surfaces a manifest corruption bug.
- [ ] **S9.** Paging through FU-3 (Path B) with IT to confirm the Entra app registration path hasn't changed since `docs/ops/path-b-msal-device-code-setup.md` was written — even though we're not shipping it this phase, a 10-minute email exchange now de-risks the next phase.

---

## NICE-to-have — take these if there's time, otherwise move on

- [ ] **N1.** ADR 0010 draft for Path B (if we decide to write one — see FU-4).
- [ ] **N2.** Add a manifest-integrity smoke test: every `entry_id` in `manifest.json` has a matching file on disk; every `.md` in `ask_jojo_raw/{connector}/` has a matching manifest entry. Pure hygiene — catches bugs before a compile pass trips on them.
- [ ] **N3.** Dashboard/metrics view: simple CLI `jojo-ingest status --summary` that prints "OneDrive: 18,111 files (last sync 2h ago); SharePoint: 1,199 files (last sync 15m ago); …" — the data is all in the manifest, just not collated.
- [ ] **N4.** Retrospective note at the bottom of `docs/v2_status.md` or a short entry under `docs/retros/phase-1.md` — what went well, what we'd change. Useful before starting Phase 2, cheap to write, useful if we ever onboard someone new.

---

## Sanity-check session before the final push

A 15-minute single-session walk-through at the end of the day so nothing ships broken:

1. `cd C:\Users\mdelosrios\Claude_Local\jojo_bot_v2.0\ask_jojo && git status` — confirm only the files in the staging plan are uncommitted.
2. Pure-ASCII sweep on every `.ps1` you're about to commit (script in `docs/ops/phase-1-staging-plan.md` under Commit A).
3. `pytest -q` — must be green.
4. `ruff check` — must be clean.
5. Open the Raw tab UI and click into a SharePoint file + a OneDrive file — confirm the frontmatter + body both render.
6. Run `Get-ScheduledTask -TaskPath '\JojoBot\' | Format-Table TaskName,State` — confirm four tasks present + `Ready`.
7. Stage and commit per `docs/ops/phase-1-staging-plan.md` — A, then B, then C.
8. `pytest -q` once more on the post-commit tip.
9. `git push origin main`.
10. Check box M10. Spin up Phase 2.

---

## Abort criteria — when NOT to declare Phase 1 done

Check anything here? Stop, fix, and re-run this checklist. Do not push.

- [ ] `pytest -q` fails.
- [ ] `ruff check` reports violations.
- [ ] `ask_jojo_raw/` GitHub visibility is anything other than `private`.
- [ ] Any `.ps1` file you're committing has a non-ASCII character.
- [ ] `manifest.json` is missing fields required by the 0.1.0 schema (spot-check one SharePoint entry + one OneDrive entry).
- [ ] A scheduled task you just registered fails on its first run with a non-zero exit code not already explained by "needs a fresh Graph token."
