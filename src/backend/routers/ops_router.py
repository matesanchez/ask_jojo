"""Ops router. Populated in Phase 3 (Ops tab) and Phase 6 (lint runs)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

router = APIRouter()

_PHASE_MSG = (
    "Ops API is not implemented yet (Phase 0 skeleton). "
    "Absorb / lint triggers land in Phase 3 + Phase 6 — see ask_jojo/PLAN.md §6."
)


@router.get("/status")
def get_status() -> None:
    raise HTTPException(status_code=501, detail=_PHASE_MSG)


@router.post("/absorb")
def trigger_absorb() -> None:
    raise HTTPException(status_code=501, detail=_PHASE_MSG)


@router.post("/lint/{scope}")
def trigger_lint(scope: str) -> None:
    _ = scope
    raise HTTPException(status_code=501, detail=_PHASE_MSG)


@router.get("/jobs/{job_id}")
def get_job(job_id: str) -> None:
    _ = job_id
    raise HTTPException(status_code=501, detail=_PHASE_MSG)
