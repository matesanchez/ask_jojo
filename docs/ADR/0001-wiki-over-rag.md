# ADR 0001 — Compiled Wiki, Not RAG, as the Knowledge Substrate

**Status:** Accepted
**Date:** 2026-04-22
**Deciders:** Mateo de los Rios
**Supersedes:** none
**Related:** `ADR 0000` (v2 roadmap), `PLAN.md` §1–2, `ask_jojo_wiki/SCHEMA.md`

## Context

JoJo Bot v1.0 is a retrieval-augmented-generation system: PDFs chunked, embedded, stored in ChromaDB, retrieved per query, and stitched into a prompt for Claude or GPT-4o. This works acceptably for a narrow corpus of 232 Cytiva manuals, where the questions are predictable and every answer is essentially a re-assembly of passages that already exist in the source.

v2.0 needs to cover the full breadth of Nurix knowledge: programs, targets, platforms, methods, people, and the informal synthesis that sits in nobody's document but in twelve people's heads. The questions are open-ended. The right answer to "what's the current TYK2 strategy?" is not a rearrangement of three PDF chunks; it is a synthesis across dozens of documents plus an understanding of which sources superseded which.

Two architectural options were considered.

**Option A: scale up RAG.** Improve chunking, add hybrid search (BM25 + vector), add re-ranking, improve the prompt. Each query runs the same pipeline but retrieves more and better.

**Option B: compile a persistent wiki.** Use Claude as an author to produce and maintain a cross-referenced markdown wiki from the raw sources. At query time, read the compiled wiki. The expensive synthesis work runs offline during compile, not per-query.

## Decision

**Adopt Option B. The knowledge substrate for v2.0 is a compiled markdown wiki, not a RAG index.**

Retrieval-augmented generation is preserved in two narrow roles:

1. **Pre-retrieval during absorb.** When a source entry is too long to fit in a single subagent's context, v1.0's ChromaDB chunks the entry and the absorb subagent retrieves relevant chunks on demand. This is scaffolding inside the compile step, not the query path.
2. **Escalation above ~200 pages.** If `_index.md` strains the context window or index-first retrieval misses grow, `qmd` (local BM25 + vector over markdown) pre-filters to ~30 candidate pages and Sonnet picks from the shortlist. See `PLAN.md` §4 D8 for the activation thresholds.

The v1.0 RAG pipeline itself remains in production for chromatography questions, routed via a query router in Phase 4.

## Rationale

The insight from Karpathy's `llm-wiki` pattern is that RAG pays the synthesis cost on every query. A compiled wiki pays it once, then reads at near-zero marginal cost. For a corpus of Nurix's size and complexity, the per-query cost of good synthesis dominates; amortizing it offline inverts the economics.

A wiki also gives us three second-order benefits that RAG cannot:

- **Every claim has a home.** The wiki has a page for TYK2, a page for the TYK2 program, a page for the relevant assay. Contradictions surface because two pages cite disagreeing sources. In RAG, contradictions vanish into the chunk soup.
- **Compounding artifact.** The wiki gets more useful every week it is maintained. RAG indexes are stateless.
- **Human-inspectable.** A scientist can read a wiki page and decide whether to trust it. A ChromaDB `.sqlite3` file is opaque.

The cost we accept for this is more upfront engineering: a compile pipeline, a lint pipeline, a schema, and discipline about how pages are authored. That cost is front-loaded; RAG's cost is perpetual per-query drag.

## Consequences

### Positive

- The wiki is a durable artifact Nurix owns regardless of backend choice. If we replace Claude with a different model tomorrow, the wiki still works.
- Query-time cost is dominated by reading a handful of markdown files, not by embedding and re-ranking. Latency drops.
- The pipeline produces an audit trail: every claim → source document → commit.
- Future interfaces (Slack bot, VS Code extension, mobile) can read the same wiki with no duplication of effort.

### Negative

- The compile pipeline is more complex than a RAG pipeline. Phase 2 is the longest phase (6–8 weeks).
- Wiki quality depends on the discipline of `CLAUDE.md` and `SCHEMA.md`. Sloppy prompts produce sloppy wikis. This is a sustained maintenance cost, not a one-time one.
- Corpus freshness depends on the absorb pipeline running. If absorb breaks silently, the wiki ages. The nightly lint exists in part to detect staleness.
- Adding a new document is slow (one absorb pass) compared to RAG (one embedding call).

## Alternatives Considered

**Scale up RAG (Option A).** Rejected. Improved retrieval does not fix the fundamental problem that open-ended questions need synthesis, not re-assembly. The best RAG system in the world still answers "what's our TYK2 strategy?" by returning strategy-document fragments, not by telling you the strategy.

**Hybrid: RAG for retrieval, Claude for synthesis per query.** Rejected. This is what v1.0 already does for chromatography, and it works — for a narrow, well-scoped corpus. It does not scale to "all of Nurix" because Claude burns tokens re-deriving the same synthesis every single query.

**Fine-tune a model on Nurix content.** Deferred to Phase 8. Fine-tuning locks knowledge into opaque weights, creates a data-governance problem (deleting a source document does not delete its influence), and requires infrastructure we do not have. A compiled wiki is the right substrate first; a fine-tune can consume the wiki later if it proves useful.

## References

- Andrej Karpathy, `llm-wiki` pattern (see `precedent/llm-wiki.md`).
- farzaa's `wiki-gen-skill` (see `precedent/wiki-gen-skill.md`).
- `PLAN.md` §1 (Orientation) and §2 (Design Principles).
- `ask_jojo_wiki/SCHEMA.md` v0.1.0.
