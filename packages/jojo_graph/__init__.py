"""jojo_graph -- graphify integration for the Graph tab.

Phase 7a (mostly integration). Wraps graphify (when installed) and
falls back to the deterministic graph builder in
``packages/jojo_qa/graph.py`` when graphify isn't available.

The graphify CLI produces three artifacts at
``ask_jojo_wiki/.graphify/``:

  graph.html        -- interactive D3/cytoscape visualization (the
                       Graph tab's iframe target).
  graph.json        -- the underlying graph (richer than our
                       packages/jojo_qa/graph._graph.json -- includes
                       community detection, centrality, etc).
  GRAPH_REPORT.md   -- human-readable summary surfaced in the Ops tab.

Public API:

- ``rebuild(wiki_root)`` -- run graphify; falls back to
  ``jojo_qa.graph.build`` if graphify isn't installed.
- ``stats(wiki_root)`` -- summary stats from graph.json.
- ``report_path(wiki_root)`` -- path to GRAPH_REPORT.md.
- ``html_path(wiki_root)`` -- path to graph.html.
- ``is_graphify_available()`` -- whether the graphify CLI is
  importable / on $PATH.
"""

__version__ = "0.1.0"

from .builder import (
    GraphArtifacts,
    html_path,
    is_graphify_available,
    rebuild,
    report_path,
    stats,
)

__all__ = [
    "GraphArtifacts",
    "html_path",
    "is_graphify_available",
    "rebuild",
    "report_path",
    "stats",
]
