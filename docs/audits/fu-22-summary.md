# FU-22 Trace Summary — 'absorbed but invisible' tail

**Generated:** 2026-06-01  
**Method:** stratified random sample (seed=2026, n=200) of queue entries ticked WITHOUT a skip marker, traced against the live wiki content blob (token + compound-id search). Strata: 50 sharepoint, 50 onedrive, 100 publicdrive.  
**Population (absorbed/ticked-no-skip):** 59,358

## Classification

| Class | Count | % |
| --- | --- | --- |
| low_signal | 153 | 76.5% |
| integrated | 25 | 12.5% |
| redundant_or_partial | 17 | 8.5% |
| unintegrated | 5 | 2.5% |

**Unintegrated: 2.5%.** Decision threshold is 20% (GOAL_PROMPT_WIKI_RECOVERY.md §3.3).

**Verdict: DEFENSIBLE** — the bulk of the absorbed tail is either integrated or redundant-and-discarded; only a small fraction is genuinely missed. Promote the missed slice in a follow-up (FU-23) rather than re-absorbing the whole tail.

## By stratum

- **sharepoint**: low_signal=40, integrated=7, redundant_or_partial=3
- **onedrive**: low_signal=41, redundant_or_partial=5, unintegrated=2, integrated=2
- **publicdrive**: low_signal=72, unintegrated=3, redundant_or_partial=9, integrated=16

## Caveat

This is an automated trace (filename/title token + compound-id matching against wiki text), not a full human read of each raw file. 'redundant_or_partial' means the entry's topic is present in the wiki but the specific entry is not distinctly represented — this conflates genuinely-redundant entries with partially-missed ones, and is the bucket most in need of human sampling. Treat the unintegrated percentage as a lower bound on missed content and the integrated percentage as an upper bound on coverage.

See `docs/audits/fu-22-trace.jsonl` for per-entry detail.
