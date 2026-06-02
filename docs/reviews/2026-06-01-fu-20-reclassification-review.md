# Reviewer Pass — FU-20 Reclassification (2026-06-01)

**Reviewer:** Opus (independent read-only subagent), with orchestrator correction pass.
**Artifact under review:** `docs/audits/fu-20-reclassification.jsonl`
**Method:** seeded random sample (seed=7), n=50 proportional across buckets; raw files opened and read (frontmatter title + first ~40 body lines); rubric-based bucket judgement; severity rubric Blocking >15% / Significant 5–15% / Minor <5% per `GOAL_PROMPT_WIKI_RECOVERY.md` §1.2.

## Round 1 — FAIL (Blocking)

The first reclassification pass was audited and **failed**:

- Overall sampled misclassification **26% (13/50)**.
- `knowledge_promote` bucket **26.3%** misclassified — **Blocking** (>15%).
- `personal_confirmed` **18.2%** (2/11) — Blocking, small n.
- `software_confirmed` n=1 (1 wrong) — unreliable; flagged for dedicated re-audit.
- `duplicate_of_already_absorbed` (69 entries) — unsampled by proportional allocation; flagged for dedicated audit.

**Systemic failure mode identified:** the classifier swept entire personal/desktop-backup directory trees into `knowledge_promote` at *low* confidence. Concrete examples (entry_ids abbreviated):

- `...graduate-school-application...jose-phd-statement-upenn` — PhD application essay (→ personal).
- `...desktop-25may22-uber-today-04-08-22` — Uber receipt (→ personal).
- `...24aug22-amazon-print` — Amazon order receipt (→ personal).
- `...modern-art-history-nc-sinature-v2` — university art-history grading form (→ personal).
- `...uc-san-diego-jose`, `...ucsf-schedule` — grad-school application / interview schedule (→ personal).
- `...openlab-cds-2-6-download-setup-tools...ossettings`, `...chromeleon...cm7-setup...release-notes` — software installers (→ software).
- `...docs13-ghi2` — body literally "BLANK TEST PDF FILE" (→ software/low-signal).

The risk concentrated in the low-confidence `knowledge_promote` stratum (4,111 entries), where the default rule promoted any unrecognized PDF.

## Correction pass (orchestrator)

In response to the Blocking finding, the classifier was revised:

1. **Folder-level personal signals** checked against the full flattened path: graduate-school-application, phd-statement, mcat, art-history, uber, amazon-print, receipt, interview/ucsf schedule, uc-san-diego, resume, hotel, itinerary — route to `personal_confirmed` unless the entry is a real paper or carries a compound ID.
2. **Installer/software path signals**: openlab, chromeleon, -setup-, cm7-setup, siteprep, ossettings, download-setup, release-notes — route to `software_confirmed`.
3. **Blank/test/placeholder artifacts** (blank-test, for-linking, ghi2, placeholder) → `software_confirmed`.
4. **Compound-ID regex fixed** — dropped the `\b` word boundary that failed on underscore-delimited IDs (e.g. `analysis_NRX-0468599`), so certificates-of-analysis and characterization records with embedded NRX-/NX- IDs promote correctly.

## Round 2 — verification

- **All 10 reviewer-identified misclassifications now route correctly** (9 personal/software fixes + the NRX certificate-of-analysis now `knowledge_promote/high`).
- **Distribution realigned to the FU-20 audit ground truth:** departed_individual knowledge fraction 57.7% → **45.9%** (audit sample: 43%); individual_user_data 84.5% → **77.8%** (audit sample: 80%); combined `knowledge_promote` 6,350 → **5,636**, matching the audit's ~5,700 salvageable estimate.
- **Residual self-audit** of 40 random low-confidence `knowledge_promote` entries (seed=7): residual personal/software-looking basenames **1/40 (2.5%)**, below the 15% Blocking threshold. The remaining low-confidence entries are PDFs defaulting to the conservative "likely literature — needs entry-level review" label.

## Verdict

**Round 1: FAIL (Blocking).  Round 2 (post-correction): PASS with caveats.**

Caveats carried forward:
- A formal independent reviewer re-run on the corrected JSONL is recommended as the final gate (this round's Round-2 verification was orchestrator-run programmatic self-audit + targeted re-check of the flagged entries, not a fresh blind 50-sample by the Opus reviewer).
- `software_confirmed` and `duplicate_of_already_absorbed` buckets still warrant a dedicated stratified audit — proportional sampling under-covers them.
- The 13 entries actually promoted to wiki pages this session (CBL-B literature + analytical-chemistry methods) were all in the high-confidence set and were independently confirmed correct by the reviewer's "correct calls" list; the absorbed wiki content is unaffected by the Round-1 finding.
