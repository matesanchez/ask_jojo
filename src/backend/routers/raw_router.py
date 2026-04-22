"""Raw API router. Populated in Phase 3 (Raw tab)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

router = APIRouter()

_PHASE_MSG = (
    "Raw API is not implemented yet (Phase 0 skeleton). "
    "Scheduled for Phase 3 — see ask_jojo/PLAN.md §6 Phase 3."
)


@router.get("/tree")
def list_tree() -> None:
    raise HTTPException(status_code=501, detail=_PHASE_MSG)


@router.get("/file/{path:path}")
def get_file(path: str) -> None:
    _ = path
    raise HTTPException(status_code=501, detail=_PHASE_MSG)


@router.get("/manifest")
def get_manifest() -> None:
    raise HTTPException(status_code=501, detail=_PHASE_MSG)
