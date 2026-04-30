"""Graph API router -- backs the Phase 7a Graph tab.

Endpoints:

  GET  /api/graph/html       serve graph.html (iframe target)
  GET  /api/graph/json       serve graph.json (rich graphify graph)
  GET  /api/graph/report     serve GRAPH_REPORT.md
  GET  /api/graph/stats      summary stats (Ops tab feed)
  GET  /api/graph/available  is graphify on PATH? -> 'graphify'|'fallback'
  POST /api/graph/rebuild    trigger a rebuild (subprocess via jojo_graph)

The graph artifacts live under ``ask_jojo_wiki/.graphify/``:

- graph.html      iframe target for the Graph tab.
- graph.json      adjacency / nodes / edges (graphify-compatible).
- GRAPH_REPORT.md human-readable summary; surfaced in the Ops tab.

When graphify isn't installed, packages/jojo_graph emits a *fallback*
artifact set (slim graph.json + synthetic GRAPH_REPORT.md + minimal
SVG viewer). The fallback keeps the Graph tab working today; the
graphify install is a quality upgrade when it lands.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, PlainTextResponse

from jojo_core import config
from jojo_graph import builder

router = APIRouter()


def _wiki_root() -> Path:
    default = str(Path(__file__).resolve().parents[4] / "ask_jojo_wiki")
    env_val = os.environ.get("JOJO_WIKI_ROOT")
    if env_val:
        return Path(env_val).resolve()
    return Path(config.get("wiki_root", default)).resolve()


# ---------------------------------------------------------------- serve files


@router.get("/html")
def get_graph_html() -> FileResponse:
    """Serve the graph.html iframe target."""
    path = builder.html_path(_wiki_root())
    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail="graph.html missing -- POST /api/graph/rebuild first",
        )
    return FileResponse(path, media_type="text/html")


@router.get("/json")
def get_graph_json() -> FileResponse:
    """Serve the graph.json file."""
    path = _wiki_root() / ".graphify" / "graph.json"
    if not path.exists():
        # Fall back to the slim _graph.json in the wiki root.
        slim = _wiki_root() / "_graph.json"
        if slim.exists():
            return FileResponse(slim, media_type="application/json")
        raise HTTPException(
            status_code=404,
            detail="graph.json missing -- POST /api/graph/rebuild first",
        )
    return FileResponse(path, media_type="application/json")


@router.get("/report", response_class=PlainTextResponse)
def get_graph_report() -> str:
    """Serve GRAPH_REPORT.md as plain text (the Ops tab will markdown-render)."""
    path = builder.report_path(_wiki_root())
    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail="GRAPH_REPORT.md missing -- POST /api/graph/rebuild first",
        )
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------- stats / availability


@router.get("/stats")
def get_graph_stats() -> dict[str, Any]:
    """Summary stats for the Ops tab card."""
    return builder.stats(_wiki_root())


@router.get("/available")
def get_graphify_available() -> dict[str, Any]:
    """Whether graphify is on PATH.

    Returns ``{"available": True, "source": "graphify"}`` when installed
    and ``{"available": False, "source": "fallback"}`` otherwise.
    """
    avail = builder.is_graphify_available()
    return {
        "available": avail,
        "source": "graphify" if avail else "fallback",
    }


# ---------------------------------------------------------------- rebuild


@router.post("/rebuild")
def post_rebuild() -> dict[str, Any]:
    """Rebuild graph artifacts.

    Synchronous for now (the build runs in well under 30 s on the
    current 138-page wiki). When the corpus grows, route through RQ
    via ingest_router's job pattern.
    """
    artifacts = builder.rebuild(_wiki_root())
    wiki = _wiki_root()
    return {
        "status": "ok",
        "graph_html": str(artifacts.graph_html.relative_to(wiki)),
        "graph_json": str(artifacts.graph_json.relative_to(wiki)),
        "graph_report": str(artifacts.graph_report.relative_to(wiki)),
        "used_fallback": artifacts.used_fallback,
        "node_count": artifacts.node_count,
        "edge_count": artifacts.edge_count,
    }
