# Phase 4 Q&A Benchmark — Batch C (q-036 through q-050)

**Status:** 15 entries added 2026-05-19 (Cowork session, writer sub-agent).
**Batch:** C (relational × 4, router-stress × 4, v1-routing × 3, edge × 4)
**Governing ADR:** `docs/ADR/0011-qa-via-cowork-while-api-pending.md`
**Merge target:** `ask_jojo/docs/qa/benchmark-questions.md` (adds entries q-036 through q-050 to the canonical set)

All gold answers in `docs/qa/answers/2026-05-19-*.md`. Pending domain-reviewer sign-off before merge into canonical benchmark.

---

## q-036 — BTK/CRBN connection (relational)

- **Question:** What is the connection between the BTK program and CRBN/CRL4 at Nurix — is there a molecular glue or PROTAC angle to BTK?
- **Expected route:** `wiki`
- **Expected cited slugs:** `btk-ctm`, `targeted-protein-degradation`, `crbn-cereblon-platform`
- **Category:** relational
- **Difficulty:** hard
- **Gold answer file:** `docs/qa/answers/2026-05-19-btk-crbn-connection.md`
- **Notes:** Correct answer states BTK CTMs are CRBN-based PROTACs (bifunctional), not molecular glues. CRBN connection must be marked CITED (btk-ctm opens with "CRBN-based"). Must flag `crbn-cereblon-platform` as confidence:low. Molecular glue is explicitly ruled out. Three hops required: btk-ctm → targeted-protein-degradation → crbn-cereblon-platform. Inventing a molecular glue program for BTK is an immediate fail.
- **Added:** 2026-05-19 by writer-agent

## q-037 — CBL-B → CRBN → DEL chain (relational)

- **Question:** Trace the chain from the CBL-B program to the CRBN platform to the DEL screening platform — how are they connected?
- **Expected route:** `wiki`
- **Expected cited slugs:** `cbl-b`, `cbl-b-ctm`, `crbn-cereblon-platform`, `targeted-protein-degradation`, `del-screening`, `del-libraries`
- **Category:** relational
- **Difficulty:** hard
- **Gold answer file:** `docs/qa/answers/2026-05-19-cbl-b-crbn-del-chain.md`
- **Notes:** Correct answer identifies NRX-0395370 as the DEL hit (Vipergen screen) that became the parental compound for both the inhibitor series AND the CRBN CTM series. The bifurcation (same DEL hit → two programs) is the key insight. Must cite `cbl-b-ctm` for the NRX-0395370 connection. Must flag `crbn-cereblon-platform` as confidence:low. Six-slug retrieval required. Answers that describe only the inhibitor chain (DEL → NX-1607) without the CTM chain are partial fails.
- **Added:** 2026-05-19 by writer-agent

## q-038 — Pellino-1 → IRAK4 → TLR pathway (relational)

- **Question:** What is the mechanistic connection between Pellino-1 and IRAK4 in the TLR pathway — and why does Nurix care about it for the Pellino-1 program?
- **Expected route:** `wiki`
- **Expected cited slugs:** `pellino-1-target`, `irak4`, `pellino-1`
- **Category:** relational
- **Difficulty:** hard
- **Gold answer file:** `docs/qa/answers/2026-05-19-pellino1-irak4-tlr-pathway.md`
- **Notes:** CRITICAL: Pellino-1 ubiquitinates IRAK1/IRAK4/RIP1 to AMPLIFY TLR signaling in macrophages (not degrade IRAK4). Any answer that says "Pellino-1 degrades IRAK4" or "Pellino-1 promotes IRAK4 proteasomal degradation" is an immediate fail. The wiki does not specify K48/K63 chain linkage type — answers that assert chain linkage from external knowledge are also fails. Must explain the dual-role complexity (T-cell negative regulator of c-Rel vs macrophage proinflammatory amplifier via IRAK1/IRAK4/RIP1) as the program-relevance context. IRAK4 as a separate DEL target should be noted if retrieved.
- **Added:** 2026-05-19 by writer-agent

## q-039 — SKP2 → S-phase → cancer (relational)

- **Question:** What is SKP2's role in S-phase regulation, and how does that make it a cancer target — what was Nurix's approach?
- **Expected route:** `wiki`
- **Expected cited slugs:** `skp2`, `skp2-inhibitor`
- **Category:** relational
- **Difficulty:** medium
- **Gold answer file:** `docs/qa/answers/2026-05-19-skp2-s-phase-cancer.md`
- **Notes:** Correct answer names p27 (CDKN1B) as the SKP2 substrate and explains the ubiquitin-mediated mechanism (SKP2 ubiquitylates p27 → p27 degradation → CDK2 active → S-phase entry). Must name the SKP2-Cks1 interface as the drug target. Three discovery tracks (TR-FRET HTS, virtual screen, DEL) must be cited from `skp2-inhibitor`. Calling SKP2 a "kinase" is a factual error (it is an F-box protein) and should be flagged as a fail.
- **Added:** 2026-05-19 by writer-agent

## q-040 — Pellino-1 ÄKTA buffer prep (router-stress)

- **Question:** What's the standard buffer prep procedure for an ÄKTA run on the Pellino-1 protein?
- **Expected route:** `v1`
- **Expected cited slugs:** _(none — v1 route bypasses the wiki)_
- **Category:** router-stress
- **Difficulty:** easy
- **Gold answer file:** `docs/qa/answers/2026-05-19-pellino1-akta-buffer-prep-router-stress.md`
- **Notes:** Router test only. ÄKTA + buffer keywords must override the Pellino-1 program keyword. Any attempt to answer from the wiki is a routing fail. Mirrors q-005 (BTK ÄKTA buffer). The program name is a red herring.
- **Added:** 2026-05-19 by writer-agent

## q-041 — CBL-B chromatography column (router-stress)

- **Question:** Which chromatography column should I use for CBL-B purification?
- **Expected route:** `v1`
- **Expected cited slugs:** _(none — v1 route bypasses the wiki)_
- **Category:** router-stress
- **Difficulty:** easy
- **Gold answer file:** `docs/qa/answers/2026-05-19-cbl-b-chrom-column-router-stress.md`
- **Notes:** Router test only. `chromatography` + `purification` must override CBL-B program keyword. Any attempt to retrieve CBL-B wiki pages is a routing fail.
- **Added:** 2026-05-19 by writer-agent

## q-042 — SIAH1 DEL buffer (router-stress)

- **Question:** What buffer did we use for the SIAH1 DEL screen?
- **Expected route:** `wiki`
- **Expected cited slugs:** `del-buffer-stability-testing`, `siah1`
- **Category:** router-stress
- **Difficulty:** medium
- **Gold answer file:** `docs/qa/answers/2026-05-19-siah1-del-buffer-router-stress.md`
- **Notes:** CRITICAL: This is the REVERSE of q-040/q-041. The `buffer` keyword here co-occurs with `DEL screen` (wiki context) not `ÄKTA`/`chromatography` (v1 context). Correct route is `wiki`. Answer should cite 5X Core Buffer (20 mM HEPES pH 7.5, 1 mM MgCl2) from `del-buffer-stability-testing`. Routing to v1 is an immediate routing fail. Must hedge that the pre-screen characterization buffer may differ from the final campaign buffer.
- **Added:** 2026-05-19 by writer-agent

## q-043 — NX-1607 purification yield (router-stress)

- **Question:** What's the typical purification yield for NX-1607?
- **Expected route:** `v1`
- **Expected cited slugs:** _(none — v1 route bypasses the wiki)_
- **Category:** router-stress
- **Difficulty:** easy
- **Gold answer file:** `docs/qa/answers/2026-05-19-nx1607-purif-yield-router-stress.md`
- **Notes:** Router test only. `purification yield` / `purif` keyword must override NX-1607 compound keyword. Any attempt to retrieve CBL-B wiki pages is a routing fail.
- **Added:** 2026-05-19 by writer-agent

## q-044 — ÄKTA Pure 25 vs ÄKTA Avant (v1-routing)

- **Question:** What's the difference between the ÄKTA Pure 25 and the ÄKTA Avant — which one should I use for protein purification?
- **Expected route:** `v1`
- **Expected cited slugs:** _(none — v1 route bypasses the wiki)_
- **Category:** v1-routing
- **Difficulty:** easy
- **Gold answer file:** `docs/qa/answers/2026-05-19-akta-pure25-vs-avant-v1-routing.md`
- **Notes:** Router test only. Unambiguous v1 route — both ÄKTA instrument names present, no program keyword. This is the cleanest v1 signal in the benchmark. Any wiki retrieval is a fail.
- **Added:** 2026-05-19 by writer-agent

## q-045 — UNICORN method editor errors (v1-routing)

- **Question:** What are the most common errors in the UNICORN method editor when setting up a new gradient?
- **Expected route:** `v1`
- **Expected cited slugs:** _(none — v1 route bypasses the wiki)_
- **Category:** v1-routing
- **Difficulty:** easy
- **Gold answer file:** `docs/qa/answers/2026-05-19-unicorn-method-editor-errors-v1-routing.md`
- **Notes:** Router test only. UNICORN + method editor + gradient = unambiguous v1. No program keyword present.
- **Added:** 2026-05-19 by writer-agent

## q-046 — CEX buffer pH for kinase (v1-routing)

- **Question:** What's the typical buffer pH range for cation-exchange chromatography on a typical kinase?
- **Expected route:** `v1`
- **Expected cited slugs:** _(none — v1 route bypasses the wiki)_
- **Category:** v1-routing
- **Difficulty:** easy
- **Gold answer file:** `docs/qa/answers/2026-05-19-cex-buffer-ph-v1-routing.md`
- **Notes:** Router test only. `cation-exchange chromatography` + `buffer pH` = v1. "Typical kinase" is NOT a specific Nurix program keyword. Must not retrieve IRAK4, ZAP-70, or other kinase wiki pages.
- **Added:** 2026-05-19 by writer-agent

## q-047 — Refeyn maintenance schedule (edge)

- **Question:** What's the maintenance schedule for the Refeyn mass photometry instrument?
- **Expected route:** `wiki`
- **Expected cited slugs:** `refeyn-mass-photometry`
- **Category:** edge
- **Difficulty:** medium
- **Gold answer file:** `docs/qa/answers/2026-05-19-refeyn-maintenance-schedule-edge.md`
- **Notes:** Edge case: the wiki has a `refeyn-mass-photometry` page (confidence:low) but the page contains no maintenance schedule. Routing to wiki is correct; the miss is a content gap. Correct answer: "not in the wiki; page exists but is exploratory-demo content with no SOPs." Hallucinating a maintenance schedule (e.g., "clean flow cell weekly") is an immediate fail. `miss_logged: true`.
- **Added:** 2026-05-19 by writer-agent

## q-048 — Pellino-1 publications (edge)

- **Question:** Has anyone published from the Pellino-1 program at Nurix — is there a paper or abstract?
- **Expected route:** `wiki`
- **Expected cited slugs:** `pellino-1`, `pellino-1-target`, `publications-index`
- **Category:** edge
- **Difficulty:** hard
- **Gold answer file:** `docs/qa/answers/2026-05-19-pellino1-publications-edge.md`
- **Notes:** Edge case: three-hop retrieval finds no Nurix-authored Pellino-1 publication in the wiki. Correct answer: "not found in wiki, miss logged, `publications-index` is confidence:low and may not cover all disclosures." Must NOT invent a publication. Murphy et al. JBC 2015 is an external Pellino-1 paper referenced in the target page, not a Nurix output. `miss_logged: true`.
- **Added:** 2026-05-19 by writer-agent

## q-049 — SIAH1 and ZAP-70 DEL queue status (edge)

- **Question:** Where did SIAH1 and ZAP-70 stand in the DEL screen queue at the end of 2022?
- **Expected route:** `wiki`
- **Expected cited slugs:** `2022-del-screen-queue`, `q4-2022-screening-budget`, `siah1`, `zap-70-platform`
- **Category:** edge
- **Difficulty:** hard
- **Gold answer file:** `docs/qa/answers/2026-05-19-siah1-zap70-q4-2022-status-edge.md`
- **Notes:** Asymmetric answer required: SIAH1 = answerable (High Complexity/EOY queue; C3+C4 hit resynthesis 2022-10-01 per `2022-del-screen-queue`); ZAP-70 = not answerable from wiki (`zap-70-platform` is confidence:low, not named in queue). Correct answer returns SIAH1 data AND an honest miss on ZAP-70. Hallucinating a ZAP-70 queue position is an immediate fail. `miss_logged: true` (for ZAP-70 component).
- **Added:** 2026-05-19 by writer-agent

## q-050 — Refeyn vs DEL protein estimation (edge)

- **Question:** How does Refeyn mass photometry compare to the DEL protein estimation method for determining how much protein we need?
- **Expected route:** `wiki`
- **Expected cited slugs:** `refeyn-mass-photometry`, `del-screen-protein-estimation`
- **Category:** edge
- **Difficulty:** hard
- **Gold answer file:** `docs/qa/answers/2026-05-19-refeyn-vs-del-protein-estimation-edge.md`
- **Notes:** Category-error question: these two methods answer different questions (MW characterization vs nmol planning) and do not compare. Correct answer identifies the category error and explains each method's role. Must NOT introduce BCA, Nanodrop, or A280 — those are not mentioned in either wiki page. Must flag `refeyn-mass-photometry` as confidence:low. Must describe `del-screen-protein-estimation` as a planning calculator (four scenario templates), not a concentration assay. Any answer that invents a comparison or fabricates a concentration assay is an immediate fail.
- **Added:** 2026-05-19 by writer-agent

---

## Batch C Summary

| q-ID | Category | Route | Difficulty | Miss logged |
|------|----------|-------|------------|-------------|
| q-036 | relational | wiki | hard | no |
| q-037 | relational | wiki | hard | no |
| q-038 | relational | wiki | hard | no |
| q-039 | relational | wiki | medium | no |
| q-040 | router-stress | v1 | easy | no |
| q-041 | router-stress | v1 | easy | no |
| q-042 | router-stress | wiki | medium | no |
| q-043 | router-stress | v1 | easy | no |
| q-044 | v1-routing | v1 | easy | no |
| q-045 | v1-routing | v1 | easy | no |
| q-046 | v1-routing | v1 | easy | no |
| q-047 | edge | wiki | medium | yes |
| q-048 | edge | wiki | hard | yes |
| q-049 | edge | wiki | hard | yes (ZAP-70 only) |
| q-050 | edge | wiki | hard | no |

**Totals:** 15 entries. relational ×4, router-stress ×4, v1-routing ×3, edge ×4. Routes: wiki ×8, v1 ×7. Miss logged: q-047, q-048, q-049 (partial).

**Running benchmark total:** 5 (seeded 2026-04-30) + 15 (batch C, 2026-05-19) = 20 entries attributable to this batch. Remaining to target: 30 entries (batches from writer A/B may add to this total independently).
