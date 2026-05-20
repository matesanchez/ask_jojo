# Phase 7a Code Quality Review — Graph Tab

**Date:** 2026-05-19
**Reviewer:** reviewer sub-agent (cold context)
**Verdict: PASS — 15/15 criteria**

## Criterion results

| # | Criterion | Result | Note |
|---|---|---|---|
| 1 | `graph.py` `to_json()` schema_version=0.2.0 + summary/corpus nodes | PASS | `packages/jojo_qa/graph.py:68-84`; schema "0.2.0"; all 6 node fields present |
| 2 | `_graph.json` rebuilt: 0.2.0, ≥140 nodes with summary/corpus | PASS | 148 nodes; keys: corpus, path, slug, summary, title, type |
| 3 | Token-reduction report re-run at 148 pages ≥10× | PASS | Run 2 @ 148 pages: index_first ratios 12.7×–36.7× (all ≥10×) |
| 4 | "Show in graph →" link in Chat tab both paths | PASS | `chat/page.tsx:600-609` (api_key_required) + `:698-703` (answered); both `/graph?highlight=` |
| 5 | `BrainView.tsx` exists, ≥200 lines | PASS | 892 lines |
| 6 | `THREE.InstancedMesh` for nodes | PASS | `BrainView.tsx:476` — single InstancedMesh for all node spheres |
| 7 | `OrbitControls` from three/examples/jsm | PASS | `BrainView.tsx:33` import; `:393` instantiated |
| 8 | Force layout + 200 warm-up ticks | PASS | `K_REPULSION=150`, `K_SPRING=0.02`; 200 warm-up ticks at line 462 |
| 9 | Pulse on `/api/wiki/stats` SHA change | PASS | Lines 334-357; 15s poll; pulse 0.8s scale oscillation on SHA diff |
| 10 | All / Subgraph toggle + search input | PASS | Lines 829-857; toggle buttons + search input wired to filterModeRef + searchQueryRef |
| 11 | D3/Brain toggle, `?view=brain`, `?highlight=` forwarded | PASS | `graph/page.tsx:168-184` toggles; `BrainView` receives `highlight` prop |
| 12 | BrainView SSR-safe via `dynamic(..., { ssr: false })` | PASS | `graph/page.tsx:25-32` |
| 13 | `tsc --noEmit` clean | PASS | Exit 0, no output |
| 14 | `ruff check .` clean | PASS | "All checks passed!" |
| 15 | Tests = pre-existing baseline only | PASS | 8 failures: 7 jojo_qa + 1 jojo_graph smoke — exact pre-existing baseline |

## Informational observations

- BrainView caps provenance highlights at 5 slugs (`chat/page.tsx:601-604`) to keep URLs readable.
- Token-reduction raw baseline grew 3.4% (218k → 225k tokens at 148 pages vs 138) — index_first bound by k=8 stays stable; ratio trend healthy.
- `OrbitControls` auto-rotate resumes after 5s inactivity — satisfies "camera orbits gently when idle."

## Overall verdict

**PASS — 15/15 criteria.** Phase 7b may proceed.
