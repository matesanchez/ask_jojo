"""Graph builder -- thin wrapper around the graphify CLI.

Two execution paths:

1. **graphify path (preferred)**: when the ``graphify`` CLI is on
   ``$PATH`` (or importable as a Python module), rebuild via subprocess
   and produce ``graph.html`` + ``graph.json`` + ``GRAPH_REPORT.md``
   under ``ask_jojo_wiki/.graphify/``.

2. **fallback path**: when graphify isn't available, use
   ``packages/jojo_qa/graph.build`` to produce a slim ``_graph.json``
   in the wiki root (Phase 4 already does this) plus a synthetic
   ``GRAPH_REPORT.md`` from the deterministic graph stats. The Graph
   tab gets a "graphify not installed" notice and the iframe is
   replaced with the embedded D3 visualization that ships with this
   package.

The fallback keeps the Graph tab usable today (graphify isn't yet on
Mateo's laptop), and makes the Phase 7a exit criterion measurable
even before the install lands.

Public API:

- ``GraphArtifacts``     dataclass with all four artifact paths.
- ``rebuild(wiki_root)`` run the build; return GraphArtifacts.
- ``stats(wiki_root)``   summary dict (nodes/edges/components/etc).
- ``html_path(wiki_root)`` / ``report_path(wiki_root)``
- ``is_graphify_available()`` for the Ops tab badge.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jojo_qa import graph as qa_graph

# graphify produces artifacts under .graphify/ inside the corpus dir.
GRAPHIFY_SUBDIR = ".graphify"


@dataclass
class GraphArtifacts:
    """Paths to the four graph artifacts.

    Attributes:
        graph_html: path to graph.html (Graph tab iframe target).
        graph_json: path to the rich graphify graph.json (or fallback
            to the slim _graph.json in the wiki root when graphify
            isn't installed).
        graph_report: path to GRAPH_REPORT.md.
        used_fallback: True iff the build came from the deterministic
            fallback rather than graphify.
        node_count / edge_count: summary stats for the Ops tab.
    """

    graph_html: Path
    graph_json: Path
    graph_report: Path
    used_fallback: bool
    node_count: int
    edge_count: int


def is_graphify_available() -> bool:
    """Return True iff the graphify CLI is on $PATH."""
    return shutil.which("graphify") is not None


def html_path(wiki_root: Path | str) -> Path:
    return Path(wiki_root) / GRAPHIFY_SUBDIR / "graph.html"


def report_path(wiki_root: Path | str) -> Path:
    return Path(wiki_root) / GRAPHIFY_SUBDIR / "GRAPH_REPORT.md"


def rebuild(wiki_root: Path | str) -> GraphArtifacts:
    """Rebuild graph artifacts. graphify if available; else fallback."""
    wiki_root = Path(wiki_root).resolve()
    out_dir = wiki_root / GRAPHIFY_SUBDIR
    out_dir.mkdir(parents=True, exist_ok=True)

    if is_graphify_available():
        return _rebuild_via_graphify(wiki_root, out_dir)
    return _rebuild_fallback(wiki_root, out_dir)


def _rebuild_via_graphify(wiki_root: Path, out_dir: Path) -> GraphArtifacts:
    """Spawn the graphify CLI. Falls back to ``_rebuild_fallback`` on error."""
    cmd = ["graphify", "build", str(wiki_root), "--output", str(out_dir)]
    try:
        subprocess.run(cmd, check=True, capture_output=True, timeout=600, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))  # noqa: S603
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        # graphify failed; fall back to the deterministic builder so the
        # Graph tab still has *something* to show.
        return _rebuild_fallback(wiki_root, out_dir)

    graph_json = out_dir / "graph.json"
    nodes = edges = 0
    if graph_json.exists():
        try:
            data = json.loads(graph_json.read_text(encoding="utf-8"))
            nodes = len(data.get("nodes", []))
            edges = len(data.get("edges", data.get("links", [])))
        except (json.JSONDecodeError, OSError):
            pass

    return GraphArtifacts(
        graph_html=out_dir / "graph.html",
        graph_json=graph_json,
        graph_report=out_dir / "GRAPH_REPORT.md",
        used_fallback=False,
        node_count=nodes,
        edge_count=edges,
    )


def _rebuild_fallback(wiki_root: Path, out_dir: Path) -> GraphArtifacts:
    """Build the slim graph + a synthetic report + a minimal HTML view."""
    g = qa_graph.build(wiki_root)
    qa_graph.write(g, wiki_root)
    s = qa_graph.stats(g)

    # Synthetic report.
    report = out_dir / "GRAPH_REPORT.md"
    report.write_text(_render_fallback_report(s), encoding="utf-8")

    # Minimal HTML viewer (no external CDN; pure inline d3-free SVG via
    # a force-directed layout served by the Graph tab in iframe mode).
    # When graphify lands, this gets replaced.
    html = out_dir / "graph.html"
    html.write_text(_render_fallback_html(g, s), encoding="utf-8")

    # Copy the slim graph into .graphify/graph.json so callers reading
    # from there get something.
    rich_json = out_dir / "graph.json"
    rich_json.write_text(
        json.dumps(g.to_json(), indent=2),
        encoding="utf-8",
    )

    return GraphArtifacts(
        graph_html=html,
        graph_json=rich_json,
        graph_report=report,
        used_fallback=True,
        node_count=s["node_count"],
        edge_count=s["edge_count"],
    )


def _render_fallback_report(s: dict[str, Any]) -> str:
    """Synthetic GRAPH_REPORT.md from the slim builder's stats."""
    return f"""# Graph Report (fallback)

Built by `packages/jojo_graph/builder.py` because the `graphify` CLI is
not installed. Install graphify (see `docs/graph/graphify-setup.md`) to
get community detection, centrality measures, and the rich D3 viewer.

## Summary

- **Nodes:** {s['node_count']}
- **Edges:** {s['edge_count']}
- **Average degree:** {s['avg_degree']}
- **Max degree:** {s['max_degree']}
- **Connected components:** {s['connected_components']}
- **Orphans:** {s['orphan_count']}

## What's missing without graphify

- No community detection (which clusters of pages form natural topics).
- No centrality measures (which pages are structural anchors).
- No interactive force-directed layout (the fallback HTML is static).
- No `--watch` mode for incremental rebuilds.

The fallback graph is enough to drive Phase 4's relational-question
retrieval (BFS shortest path between two slugs); the visual layer is
a usability improvement, not a correctness requirement.
"""


def _render_fallback_html(g: qa_graph.WikiGraph, s: dict[str, Any]) -> str:
    """Static-SVG fallback viewer.

    Renders nodes in a simple grid layout (no force-directed physics).
    Good enough for a "I can see the structure" view; graphify
    replaces this with a real interactive viz.
    """
    import math

    n = max(s["node_count"], 1)
    cols = max(1, int(math.ceil(math.sqrt(n))))
    cell = 60
    width = cols * cell + 40
    rows = math.ceil(n / cols)
    height = rows * cell + 40

    coords: dict[str, tuple[int, int]] = {}
    for i, slug in enumerate(sorted(g.nodes.keys())):
        col = i % cols
        row = i // cols
        coords[slug] = (20 + col * cell + cell // 2, 20 + row * cell + cell // 2)

    edge_lines = []
    for a, b in g.edges:
        if a in coords and b in coords:
            x1, y1 = coords[a]
            x2, y2 = coords[b]
            edge_lines.append(
                f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
                f'stroke="#aaa" stroke-width="0.5" stroke-opacity="0.4"/>'
            )

    node_circles = []
    for slug, (x, y) in coords.items():
        meta = g.nodes[slug]
        type_ = meta.get("type", "")
        color = _type_color(type_)
        title_attr = (
            f'<title>{_escape_xml(slug)} ({_escape_xml(type_)}): '
            f'{_escape_xml(meta.get("title", ""))}</title>'
        )
        node_circles.append(
            f'<g><circle cx="{x}" cy="{y}" r="6" fill="{color}" '
            f'stroke="#333" stroke-width="0.5">{title_attr}</circle></g>'
        )

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>JoJo wiki graph (fallback)</title>
<style>
  body {{ font-family: -apple-system, system-ui, sans-serif; margin: 16px; color: #222; }}
  .header {{ margin-bottom: 12px; }}
  .header small {{ color: #666; }}
  svg {{ background: #fafafa; border: 1px solid #ddd; }}
  .legend {{ margin-top: 12px; font-size: 12px; }}
  .legend span {{ display: inline-block; padding: 2px 6px; margin-right: 6px; border-radius: 3px; }}
</style>
</head>
<body>
<div class="header">
  <strong>JoJo Wiki Graph</strong>
  <small>(fallback view; install graphify for the rich D3 layout)</small>
  &middot; {s['node_count']} nodes &middot; {s['edge_count']} edges &middot; {s['connected_components']} components
</div>
<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  {''.join(edge_lines)}
  {''.join(node_circles)}
</svg>
<div class="legend">
  <span style="background:#1f77b4;color:white">program</span>
  <span style="background:#ff7f0e;color:white">target</span>
  <span style="background:#2ca02c;color:white">method</span>
  <span style="background:#d62728;color:white">decision</span>
  <span style="background:#9467bd;color:white">platform</span>
  <span style="background:#8c564b;color:white">concept</span>
  <span style="background:#7f7f7f;color:white">other</span>
</div>
</body>
</html>
"""


def _type_color(type_: str) -> str:
    """Pick a color per page type. Matches the legend in the fallback HTML."""
    palette = {
        "program": "#1f77b4",
        "target": "#ff7f0e",
        "method": "#2ca02c",
        "decision": "#d62728",
        "platform": "#9467bd",
        "concept": "#8c564b",
        "protocol": "#e377c2",
        "equipment": "#bcbd22",
        "reference": "#17becf",
    }
    return palette.get(type_, "#7f7f7f")


def _escape_xml(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def stats(wiki_root: Path | str) -> dict[str, Any]:
    """Return graph stats from the artifacts on disk.

    Reads .graphify/graph.json if present (graphify path) or
    _graph.json + qa_graph.stats() (fallback path).
    """
    wiki_root = Path(wiki_root)
    rich = wiki_root / GRAPHIFY_SUBDIR / "graph.json"
    if rich.exists():
        try:
            data = json.loads(rich.read_text(encoding="utf-8"))
            return {
                "node_count": len(data.get("nodes", [])),
                "edge_count": len(data.get("edges", data.get("links", []))),
                "source": "graphify",
            }
        except (json.JSONDecodeError, OSError):
            pass
    g = qa_graph.load(wiki_root)
    if not g.nodes:
        g = qa_graph.build(wiki_root)
    return {**qa_graph.stats(g), "source": "fallback"}
