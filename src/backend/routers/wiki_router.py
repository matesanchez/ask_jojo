"""Wiki API router. Populated in Phase 3 (JoJo Bot IDE Tabs)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

router = APIRouter()

_PHASE_MSG = (
    "Wiki API is not implemented yet (Phase 0 skeleton). "
    "Scheduled for Phase 3 — see ask_jojo/PLAN.md §6 Phase 3."
)


@router.get("/tree")
def list_tree() -> None:
    raise HTTPException(status_code=501, detail=_PHASE_MSG)


@router.get("/page/{path:path}")
def get_page(path: str) -> None:
    _ = path
    raise HTTPException(status_code=501, detail=_PHASE_MSG)


@router.get("/backlinks/{path:path}")
def get_backlinks(path: str) -> None:
    _ = path
    raise HTTPException(status_code=501, detail=_PHASE_MSG)
