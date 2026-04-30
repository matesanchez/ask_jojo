# graphify Setup

**Status:** Optional. The Graph tab works without graphify (uses the `packages/jojo_graph/builder.py` fallback); installing graphify upgrades it to a rich D3 visualization with community detection and centrality measures.

## What graphify gives you

- Interactive force-directed layout (vs the fallback's static SVG grid).
- Community detection — pages cluster automatically.
- Centrality measures — surfaces structural anchors (currently `delphi` at degree 36 in the fallback graph).
- Incremental rebuild via `--watch`.
- Provenance highlight messages — accepts `postMessage({type: "highlight", slugs: [...]})` from the Graph tab to highlight cited slugs after a Chat answer.

## Install

graphify is distributed as a Node CLI plus a Python helper for graph computations.

```
npm install -g graphify
```

Or, if you prefer keeping it scoped to the project:

```
cd src/frontend && npm install --save-dev graphify
# Then alias jojo-graph rebuild to use the local copy.
```

The Python side has no install — `packages/jojo_graph/builder.py` shells out to the `graphify` CLI when present.

Verify:

```
jojo-graph available
# -> graphify    if installed
# -> fallback    otherwise
```

## First run

```
jojo-graph rebuild --wiki ../ask_jojo_wiki
```

Produces three artifacts under `ask_jojo_wiki/.graphify/`:

- `graph.html` — iframe target for the Graph tab.
- `graph.json` — adjacency / nodes / edges with community metadata.
- `GRAPH_REPORT.md` — human-readable summary surfaced in the Ops tab.

The `.graphify/` directory is in `ask_jojo_wiki/.jojoignore` so the absorb pipeline doesn't re-ingest it. Add `.graphify/` to `ask_jojo_wiki/.gitignore` if you want to keep the rebuilt artifacts out of the wiki repo (recommended — they're regenerable; checking them in adds noise to `git log`).

## Nightly rebuild (Windows Task Scheduler)

Phase 7a includes `ops/scheduler/Run-GraphifyRebuild.ps1` (when added to the Phase 7a deliverables list). Pattern matches the existing `Run-ScheduledSync.ps1`:

- Tee output to `ops/scheduler/logs/graphify/<date>.log`.
- Event-log on success/failure under source `JojoBot`.
- 2 AM daily run added to the existing `\JojoBot\` task tree.

Register via `Register-JojoBotTasks.ps1 -IncludeGraphify`.

## Troubleshooting

**"graphify: command not found"** — npm install didn't put graphify on PATH. On Windows, check `%APPDATA%\npm\` is in `PATH`; on POSIX, check `npm config get prefix` matches a directory on `PATH`. The fallback path keeps working until this is resolved.

**Memory blowout on large corpora** — graphify allocates O(N²) for centrality calculation on undirected graphs. At 138 pages this is fine; at 5,000 pages we'd want graphify's `--sparse` mode (uses sparse-matrix shortcuts at the cost of slightly less precise centrality).

**Stale `.graphify/` artifacts after a wiki commit** — `jojo-graph rebuild` is idempotent and regenerates everything; safe to re-run any time. The nightly task runs unattended.

## Why graphify isn't a hard dependency

PLAN.md §6 Phase 7a calls graphify out as the integration target, not the *only* source of graph capability. The `packages/jojo_graph/builder.py` fallback exists because:

1. The Phase 7a Graph tab should ship before the operator has a chance to install graphify.
2. `packages/jojo_qa/graph.py` already builds the deterministic graph for Phase 4 retrieval; reusing that for the visual layer is cheap.
3. graphify is a Node tool; if Mateo's environment ever loses Node (or if the `graphify` package gets deprecated), the fallback keeps the system running.

The graphify install is therefore a quality upgrade, not a blocker.

## Token-reduction benchmark

The Phase 7a exit criterion (10× token reduction on a 500-article wiki vs raw-file baseline) is gradeable today via `scripts/graph_token_benchmark.py` against the current 138-page wiki. The current report is at `docs/graph/token-reduction-report.md`; re-run after the wiki grows by 50 pages to track the trend curve.
