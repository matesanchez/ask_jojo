# ADR 0003 — Modular `packages/` Layout Inside `ask_jojo/`

**Status:** Accepted
**Date:** 2026-04-22
**Deciders:** Mateo de los Rios
**Supersedes:** none
**Related:** `ADR 0002` (three-repo split), `PLAN.md` §3.3

## Context

v1.0 is a single Python package with a handful of top-level modules. That worked for a 232-PDF RAG pipeline. v2.0 introduces several distinct subsystems that need to evolve independently: ingestion connectors, the compile engine, Q&A, rich-output generation, the lint pipeline, graph integration. A flat module layout would make it impossible to reason about boundaries — everything would import everything.

We considered three organizational patterns.

**Option A: flat modules under `src/`.** What v1.0 does. Rejected for the reasons above.

**Option B: a monorepo with multiple Python packages as separate installable units.** Each subsystem is its own PyPI-style package with a `pyproject.toml`, testable and versionable independently.

**Option C: a single `ask_jojo/` package with `packages/` subdirectories.** Each subsystem is a subdirectory with clear boundaries, but they all live in one Python package and install as one unit.

## Decision

**Adopt Option C. Organize `ask_jojo/` as a single installable package with a `packages/` subdirectory containing each subsystem.**

```
ask_jojo/
├── PLAN.md
├── README.md
├── pyproject.toml
├── src/                              ← Next.js frontend + FastAPI entry points (v1.0 lineage)
├── schema/                           ← CLAUDE.md, taxonomy.yaml, ingest_rules.md
├── docs/                             ← ADRs, v2_status.md
└── packages/
    ├── jojo_core/                    ← shared types, config, logging, git helpers
    ├── jojo_connectors_common/       ← base connector interface, rate limiting, retry
    ├── jojo_ingest/                  ← SharePoint, OneDrive, drive, NurixNet, upload
    ├── jojo_compile/                 ← raw → wiki absorb loop, checkpoint orchestrator
    ├── jojo_qa/                      ← index-first retrieval, query router, answer synthesis
    ├── jojo_output/                  ← Marp, matplotlib, docx/pptx/pdf generators
    ├── jojo_lint/                    ← schema, contradiction, orphan, staleness checks
    └── jojo_graph/                   ← graphify integration, graph-assisted retrieval
```

Each `packages/<name>/` is a Python subpackage under the top-level `ask_jojo` package. It imports from `jojo_core` and (where appropriate) from `jojo_connectors_common`. It does not import sideways across peer packages without a documented reason.

## Rationale

Clear subsystem boundaries. Each package has a purpose statement, a public API, and an owner (even if the owner is Mateo for now). A developer working on connectors does not need to reason about the compile engine.

Single install. Developer ergonomics are preserved — one `pip install -e .` and the whole system is importable. No multi-repo coordination, no cross-package version pinning.

Future-proof for splitting. If a package (e.g. `jojo_graph/`) matures into something independently useful, it can be extracted into its own PyPI package with minimal refactoring. The `packages/` layout makes the boundaries explicit enough that the extraction is a mechanical move.

Pattern precedent. The approach mirrors tig-monorepo's `tig-algorithms / tig-runtime / tig-verifier / tig-benchmarker` split, which handles exactly the "one project, many clean subsystems" shape we have here.

## Consequences

### Positive

- Reasoning is local. A developer can load one package's mental model at a time.
- Testing is local. `pytest packages/jojo_compile/` runs only compile-engine tests.
- Imports are explicit. `from jojo_ingest.sharepoint import SharePointConnector` is self-documenting.
- Easy future extraction into separate PyPI packages if a subsystem outgrows the monorepo.

### Negative

- More scaffolding per subsystem than a flat layout. One `__init__.py` per package, per subpackage.
- Developers must resist the temptation to import sideways. A peer-level import (e.g. `jojo_compile` importing from `jojo_qa`) is a design smell that needs justification.
- The boundary lines are nominal, not enforced. Nothing at runtime stops a violating import. A lint check in Phase 6 can enforce this.

## Alternatives Considered

**Monorepo with independent packages (Option B).** Rejected as over-engineering for a solo-developer-plus-Claude-Code project at this phase. The extraction path (Option C → Option B) is simple if we grow into needing it.

**Flat `src/` (Option A).** Rejected. Does not scale past three or four subsystems.

**Rust-style Cargo workspaces.** Irrelevant — we are Python-primary. Noted for comparison.

## References

- `PLAN.md` §3.3 "Modular Package Layout" and Appendix A cross-walk to tig-monorepo.
- tig-monorepo precedent for subsystem splits.
