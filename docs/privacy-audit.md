# Privacy Invariant Audit

**Date:** 2026-05-20
**ADR:** 0006 — `ask_jojo_raw` Repository Privacy Invariant

## Methodology

1. Read `ask_jojo_raw/.git/config` for remote URL.
2. Verified GitHub repo visibility via `gh repo view`.
3. Inspected 15 wiki pages (sampled in wiki-compliance-audit.md) for raw verbatim content.
4. Read 3 scheduler log files from `ops/scheduler/logs/`.
5. Inspected directory layout under the workspace root and `ask_jojo/`.
6. Read `ask_jojo/.gitignore` and verified `git check-ignore` behavior.

## Checks

### 1. `ask_jojo_raw` remote visibility

- `ask_jojo_raw/.git/config`: `url = https://github.com/matesanchez/ask_jojo_raw.git`
- `gh repo view matesanchez/ask_jojo_raw`: `{"isPrivate":true,"visibility":"PRIVATE"}`
- `gh repo view matesanchez/ask_jojo`: `{"isPrivate":true,"visibility":"PRIVATE"}`
- **Verdict:** PASS — both repos PRIVATE on GitHub as of 2026-05-20.

### 2. Raw content in wiki pages

- 15-page sample inspected for raw verbatim file content.
- No raw document bodies found. Pages contain processed/paraphrased prose, attributed quotes within SCHEMA.md §4 quote budget, EXTRACTED/INFERRED markers. Source filenames are cited as metadata (path + hash) — permitted under ADR 0006.
- **Verdict:** PASS for the sampled set. Full corpus (148 pages) would require a lint-pass extension; filed as FU recommendation.

### 3. Raw content in scheduler logs

- `ops/scheduler/logs/` has subdirectories `sharepoint/`, `publicdrive/`, `onedrive/`.
- Log files contain: ingest progress markers, Graph API throttle warnings, OAuth 401 messages, openpyxl warnings, JSON result blocks (counts only). No document body text.
- File/folder paths appear in logs (e.g. `Discovery Biology - Documents/CBL/...`) — metadata, not content; consistent with ADR 0006 stance.
- `*.log` and `logs/` are excluded by `ask_jojo/.gitignore` lines 53–54.
- **Verdict:** PASS.

### 4. `ask_jojo_raw` directory isolation

**Finding (fixed 2026-05-20):**
A nested `ask_jojo/ask_jojo_raw/` directory was present containing real raw content (manifest.json ~15 MB, publicdrive markdown files) with **no** `.git/` of its own. Prior to the fix, `ask_jojo/.gitignore` did not list `ask_jojo_raw/`, meaning a `git add -A` from inside `ask_jojo/` would have staged raw content into the PRIVATE `matesanchez/ask_jojo` repo.

**Fix applied 2026-05-20:** Added `ask_jojo_raw/` to `ask_jojo/.gitignore` with an explanatory comment referencing ADR 0006.

- **Verdict:** PASS (post-fix). The ADR 0006 invariant is now defended by two independent controls: (1) both repos PRIVATE on GitHub, (2) `ask_jojo_raw/` explicitly ignored in `ask_jojo/.gitignore`.

## Verdict: PASS (post-fix)

All four checks pass after the gitignore addition. The significant pre-fix finding (nested raw directory unprotected by gitignore) was remediated in-session.

## Non-blocking follow-ups recommended

- Extend the nightly lint pipeline to scan all 148 wiki pages for long unattributed verbatim passages (>3 consecutive sentences without an EXTRACTED or INFERRED marker from a page that cites a raw source).
- Confirm `*.log` exclusion in `ask_jojo/.gitignore` covers any new log paths added in future phases.
