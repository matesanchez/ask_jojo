"""FastAPI entry point for JoJo Bot v2.0.

Run locally::

    uvicorn backend.main:app --reload --port 8000

Phase 0 ships 501 stubs for every non-health endpoint so the frontend
can be wired up in parallel without waiting for real logic. Each
router points at the PLAN.md phase that will implement it.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.routers import (
    graph_router,
    ingest_router,
    ops_router,
    output_router,
    qa_router,
    raw_router,
    settings_router,
    viz_router,
    wiki_router,
)

app = FastAPI(
    title="JoJo Bot v2.0 API",
    version="0.1.0",
    description=(
        "Phase 0 skeleton. Most endpoints return HTTP 501 until their owning "
        "phase lands. See ask_jojo/PLAN.md §6 for the phase breakdown."
    ),
)

app.include_router(wiki_router.router,   prefix="/api/wiki",   tags=["wiki"])
app.include_router(raw_router.router,    prefix="/api/raw",    tags=["raw"])
app.include_router(viz_router.router,    prefix="/api/viz",    tags=["viz"])
app.include_router(ops_router.router,    prefix="/api/ops",    tags=["ops"])
app.include_router(ingest_router.router, prefix="/api/ingest", tags=["ingest"])
app.include_router(qa_router.router,     prefix="/api/qa",     tags=["qa"])
app.include_router(output_router.router, prefix="/api/output", tags=["output"])
app.include_router(graph_router.router,   prefix="/api/graph",    tags=["graph"])
app.include_router(settings_router.router, prefix="/api/settings", tags=["settings"])

# ---------------------------------------------------------------------------
# Static-file mount: wiki outputs directory served at /wiki-outputs/.
#
# The browser uses paths like /wiki-outputs/2026-05-19-foo.png so that
# <img src={output_artifact}> resolves without any additional API round-trip.
#
# Resolution order for the on-disk path:
#   1. JOJO_WIKI_ROOT env var (allows test isolation).
#   2. Default: sibling ask_jojo_wiki/ at the repo root.
#
# If the outputs/ subdirectory does not yet exist we skip the mount silently
# rather than crashing at startup (the directory is created on first render).
# ---------------------------------------------------------------------------

def _wiki_outputs_dir() -> Path:
    env_val = os.environ.get("JOJO_WIKI_ROOT")
    if env_val:
        return Path(env_val).resolve() / "outputs"
    default_root = Path(__file__).resolve().parents[4] / "ask_jojo_wiki"
    return default_root / "outputs"


_outputs_dir = _wiki_outputs_dir()
if _outputs_dir.exists():
    app.mount(
        "/wiki-outputs",
        StaticFiles(directory=str(_outputs_dir)),
        name="wiki_outputs",
    )


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    """Liveness probe. Always returns 200 in Phase 0."""
    return {"status": "ok", "version": app.version, "phase": "0"}


# ---------------------------------------------------------------------------
# Frontend static file serving (must be LAST — catch-all `/` mount).
#
# Frozen (PyInstaller --onedir): files live in sys._MEIPASS/frontend/out.
# Dev: src/frontend/out/ is a sibling of this file's grandparent (ask_jojo/).
#
# The mount is skipped silently if the directory does not exist, so the
# dev server starts fine before the Next.js build has been run.
# ---------------------------------------------------------------------------


def _frontend_out_dir() -> Path | None:
    """Locate the Next.js static export directory.

    Frozen (PyInstaller --onedir): files are in sys._MEIPASS/frontend/out.
    Dev: src/frontend/out sibling of this file's grandparent.
    """
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", "")) / "frontend" / "out"
    dev_path = Path(__file__).resolve().parents[2] / "src" / "frontend" / "out"
    return dev_path if dev_path.exists() else None


_frontend_dir = _frontend_out_dir()
if _frontend_dir and _frontend_dir.exists():
    app.mount(
        "/",
        StaticFiles(directory=str(_frontend_dir), html=True),
        name="frontend",
    )
