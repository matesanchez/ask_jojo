# jojo_graph

Graphify integration. Drives the Graph tab in the JoJo Bot UI. Phase 7a owns this package.

## Scope

- Wraps the upstream `graphify` CLI dependency (not vendored).
- Points graphify at `ask_jojo_wiki/`; outputs land in `ask_jojo_wiki/.graphify/` (listed in `.jojoignore` so graph artifacts never round-trip through compile).
- Surfaces `graph.html` inside the Graph tab via iframe.
- Surfaces `GRAPH_REPORT.md` inside the Ops tab.
- Nightly rebuild hook so the graph tracks wiki state without manual runs.

## Invariants

- `.graphify/` is always `.jojoignore`'d — never treated as a wiki source.
- Graph is derived, never edited by hand.
- Nightly rebuild is resilient to partial wikis (skips unparsable pages rather than crashing).

## Current state

Phase 0 skeleton. CLI stub only.

## References

- `ask_jojo/PLAN.md` §6 Phase 7a.
- Upstream graphify tool (external dependency).
