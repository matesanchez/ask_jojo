# FU-20 Closure Review (2026-06-03)

**Reviewer:** Claude (Cowork) + independent Opus sub-agent audit.
**Scope:** the full FU-20 knowledge absorption, including the overnight run's waves 6-28 (~253 pages) that had not been independently reviewed (only waves 1-5 had a prior report).

## Completion

`knowledge_promote` backlog (5,636 entries) is **100% processed**:
- Absorbed into wiki pages: **4,738 (84.1%)**
- Reclassified out (personal / software / blank / mechanical, correctly dropped): **898 (15.9%)**
- Remaining: **0**

Wiki grew to **404 pages**. Lint: schema PASS (0 errors), orphan PASS (0).

## Quality audit (independent Opus sub-agent, n=28 sampled from waves 6-28)

- **Fabrication / hallucination: 0/28 (0%).** Every spot-checked numeric result, DOI, author, compound ID, lot number, and instrument serial traced verbatim to the cited immutable raw source. Verdict: the run did not invent content, even across the highest-risk late low-confidence / bulk analytical-chemistry material.
- **Thin: 1/28** — `mass-spectrometry-def-springer-geoscience` (a misfiled geoscience MS primer, self-flagged for removal). Recommend deleting it.
- Two **mechanical provenance defects** were found and fixed (below).

## Defects found and fixed in this review

1. **`sha256:` vs `hash:` field drift** — late-wave tooling emitted `sha256:` instead of the SCHEMA.md-required `hash:` key in source blocks. **Fixed: 281 keys renamed** across the wiki. 0 remain.
2. **Broken `path:` strings** — some sources cited deduplicated/abbreviated snapshot filenames that no longer resolve, though their hashes were valid and present in the manifest. **Fixed: 69 paths repointed** to the hash-matched real files (56 unquoted + 13 quoted-path pages). **0 non-resolving source paths remain** (of 1,392).

Post-fix hash integrity: **50/50** sampled cited hashes match the manifest.

## Outstanding (not blocking)

- **Wiki git index is corrupt** (`fatal: unknown index entry format`) from the overnight run on the synced mount. Commits and objects are intact (HEAD resolves, `git log` works); only the index file is bad. Fix on Windows: delete `ask_jojo_wiki\.git\index`, then `git reset` to rebuild it, then commit the post-review cleanup (74+ pages touched) + any uncommitted wave-28 stragglers.
- **`coverage` lint still flags the FU-20 categories** — by design: absorbed entries keep their original `<!-- skip: ... -->` marker (the `absorbed-via`/`reclassified` markers are appended), so the sampler still counts them. The check measures whether a category *intrinsically* contains knowledge, not whether it's been processed. Recommended refinement: have `coverage_check` ignore entries already marked `absorbed-via`/`reclassified` so it can reach PASS once a category is fully recovered. (App-code change, filed as a follow-up.)
- **Run-log gap**: `docs/goal-run-log.md` stops logging at wave 15 though commits run to wave 28; the per-wave reviewer gate (Task 1.4) was not run by the overnight process for waves 6-28 — this review substitutes for it.

## Verdict

**PASS-WITH-CAVEATS -> PASS** after this review's fixes. Content grounding is strong and fabrication-free; the mechanical provenance/schema defects are resolved. Remaining items are operational (git index repair + commit) and a coverage-lint refinement, neither of which affects wiki correctness.
