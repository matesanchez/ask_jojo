"""Visualization / rich output router. Populated in Phase 5."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

router = APIRouter()

_PHASE_MSG = (
    "Viz / rich-output API is not implemented yet (Phase 0 skeleton). "
    "Scheduled for Phase 5 — see ask_jojo/PLAN.md §6 Phase 5."
)


@router.post("/marp")
def render_marp() -> None:
    raise HTTPException(status_code=501, detail=_PHASE_MSG)


@router.post("/plot")
def render_plot() -> None:
    raise HTTPException(status_code=501, detail=_PHASE_MSG)


@router.post("/export/{fmt}")
def export_document(fmt: str) -> None:
    _ = fmt
    raise HTTPException(status_code=501, detail=_PHASE_MSG)
