# jojo_qa

Q&A over the compiled wiki plus the query router. Phase 4 owns this package.

## Scope

- **Query router.** ÄKTA / UNICORN questions continue to route through the v1.0 RAG path. Everything else routes to the wiki path. Router lives here.
- **Index-first retrieval.** Sonnet reads `_index.md`, picks 3–8 candidate pages, follows wikilinks 1–2 hops. Works well up to ~200 pages.
- **Raw fallback.** If wiki coverage is insufficient, fall back to raw; log the miss so the next absorb pass can close the gap.
- **`qmd` escalation.** Installed but dormant. Activates once `_index.md` exceeds ~200 pages — then BM25 + vector index takes over candidate selection, with wiki-follow still doing the final read.

## Invariants

- Every answer cites at least one wiki page.
- p95 latency target < 8s.
- Misses are logged as structured events (not lost) so the absorb loop can improve coverage.

## Current state

Phase 0 skeleton. CLI stub only.

## References

- `ask_jojo/PLAN.md` §6 Phase 4.
- `ask_jojo/docs/ADR/0001-wiki-over-rag.md` — why index-first instead of always-RAG.
