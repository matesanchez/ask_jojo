# Wiki Constitutional Compliance Audit

**Date:** 2026-05-20
**Pages sampled:** 15
**Schema version:** SCHEMA.md v0.2.0
**Constitution source:** `ask_jojo/schema/CLAUDE.md` v0.1.0

## Methodology

1. Read the wiki constitution at `ask_jojo/schema/CLAUDE.md` and the schema at `ask_jojo_wiki/SCHEMA.md` (v0.2.0).
2. Read `ask_jojo_wiki/_index.md` (148 pages total) and selected a 15-page stratified sample across types:
   - 5 targets: `cbl-b-target`, `fem1b`, `irak4`, `pellino-1-target`, `btk`
   - 3 programs: `cbl-b-cmc`, `cbl-b`, `itk-ctm-merged`
   - 2 methods: `dsf`, `sec-mals`
   - 2 decisions: `q4-2022-screening-budget`, `loka-ml-engagement`
   - 2 outputs: `cbl-b-efficacy-table`, `del-pipeline-diagram`
   - 1 concept: `targeted-protein-degradation`
3. For each page, verified: (a) required frontmatter fields; (b) no raw verbatim content in body; (c) wikilinks use `[[slug]]` or `[[slug|label]]` format and resolve to `_index.md` entries.

## Findings

| Page | Finding | Severity |
|------|---------|---------|
| `targets/irak4.md` | `corpus: del-screen-team` — not in SCHEMA.md §3 enum (`protein-sciences`, `early-discovery`, `nurix-wide`). **FIXED 2026-05-20: retagged to `protein-sciences`.** | ~~FAIL~~ FIXED |
| `programs/cbl-b.md` | `corpus: del-screen-team` — same enum violation. **FIXED 2026-05-20: retagged to `protein-sciences`.** | ~~FAIL~~ FIXED |
| `targets/fem1b.md` | `related:` contains `[[E3-Ubiquitin Ligase Family]]`, `[[Protein Expression and Purification]]`, `[[GenScript Protein Expression]]` — bare-title format, none resolve in `_index.md`. | WARN — tracked in FU-13 & FU-19 |
| `methods/dsf.md` | `related:` contains `[[Protein Biophysics Methods]]`, `[[Thermal Stability Assessment]]`, `[[Tycho Instrument]]` — bare-title, none resolve. | WARN — tracked in FU-13 & FU-19 |
| `methods/sec-mals.md` | `related:` uses bare-title format `[[Protein Quality Control]]` etc. | WARN — tracked in FU-13 |
| `concepts/targeted-protein-degradation.md` | `related:` has `[[Ternary Complex Formation]]` etc. — unresolved slugs, bare-title. | WARN — tracked in FU-13 & FU-19 |
| `decisions/loka-ml-engagement.md` | `related:` has `[[Machine Learning Automation]]`, `[[Lead ID and Hit Prioritization]]` — unresolved, bare-title. | WARN — tracked in FU-13 & FU-19 |
| Multiple (9 pages) | Source paths inconsistent: some use `raw/onedrive/...` (SCHEMA.md §3 form), others use `ask_jojo_raw/publicdrive/...` (workspace-relative form). | WARN — filed as FU-20 |
| Multiple (6 pages) | Hash field lengths vary: some full 64-hex SHA256, some 16-hex or 8-hex truncated. SCHEMA.md §3 specifies SHA256. Truncated hashes defeat change-detection invariant. | WARN — filed as FU-21 |
| `programs/itk-ctm-merged.md` | `sources:` uses `hash: merged-into-itk-program` sentinel; `status: deleted` not in SCHEMA.md. Intentional merge-tombstone pattern; in-page note present. | INFO |
| `outputs/` pages (2) | `sources: pending-source-resolution` — explicitly permitted in SCHEMA.md v0.2.0 §3 for `type: output`. | INFO |
| All 15 pages | No raw verbatim file content present in bodies. | PASS |
| All 15 pages | Required frontmatter fields all present (subject to corpus FAIL, now fixed). | PASS |
| `targets/btk.md` | All `related:` entries resolve in index; full 64-hex hashes throughout. Exemplary compliance. | PASS |

## Summary

15 pages sampled · 4 issue classes found  
- **FAIL → FIXED: 2** (corpus enum on `irak4` + `cbl-b` — retagged to `protein-sciences` 2026-05-20)
- **WARN: 7** (broken/bare-title wikilinks, source-path inconsistency, truncated hashes)
- **INFO: 3** (merge tombstone, output pending-source, clean exemplar)

## Verdict: PASS (post-fix)

The two FAIL findings were remediated in-session (corpus retag). WARN items are tracked follow-ups (FU-13, FU-19, FU-20, FU-21) and do not block the v2.0 tag under the existing follow-up policy.

## Recommended follow-ups filed

- **FU-20**: Normalize source paths to `raw/...` form across the corpus (15+ pages use `ask_jojo_raw/...`).
- **FU-21**: Normalize hash field to full SHA256 (64 hex chars) across the corpus (multiple pages use truncated hashes).
