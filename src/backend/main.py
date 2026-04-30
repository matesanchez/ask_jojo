"""FastAPI entry point for JoJo Bot v2.0.

Run locally::

    uvicorn backend.main:app --reload --port 8000

Phase 0 ships 501 stubs for every non-health endpoint so the frontend
can be wired up in parallel without waiting for real logic. Each
router points at the PLAN.md phase that will implement it.
"""

from __future__ import annotations

from fastapi import FastAPI

from backend.routers import (
    ingest_router,
    ops_router,
    output_router,
    qa_router,
    raw_router,
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


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    """Liveness probe. Always returns 200 in Phase 0."""
    return {"status": "ok", "version": app.version, "phase": "0"}
