"""Ingest router — real endpoints for drive + upload (Phase 1 local tier).

Cloud/NurixNet endpoints still return 501 with a phase-pointing message.
Windows Task Scheduler integration (GET/POST /schedule) is deferred to the
local-mode packaging pass (end of Phase 1) — it's Windows-only and best
implemented alongside the installer.

Design notes:
- The `IngestDriver` is synchronous. For real deployments we wrap the call
  in an RQ job (see `_queue_sync`) so the FastAPI request cycle returns
  immediately and the UI can poll via GET /jobs.
- In dev / tests, we fall back to running inline when Redis isn't reachable
  — prevents the tests from needing a live broker just to hit the endpoint.
- Raw root, staging dir, and Redis URL come from the backend config. For
  now we read them from env vars (JOJO_RAW_ROOT, JOJO_UPLOAD_DIR,
  JOJO_REDIS_URL). DPAPI-backed config.json loading lands in local-mode
  packaging.
"""

from __future__ import annotations

import logging
import os
import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field

log = logging.getLogger("jojo.ingest_router")

router = APIRouter()

# -------------------------------------------------------------------- config
_DEFAULT_RAW = Path(os.environ.get("JOJO_RAW_ROOT", "./ask_jojo_raw")).resolve()
_DEFAULT_UPLOAD_DIR = Path(
    os.environ.get("JOJO_UPLOAD_DIR", "./ask_jojo_raw/_staging")
).resolve()
_REDIS_URL = os.environ.get("JOJO_REDIS_URL", "redis://localhost:6379/0")

# In-process job registry for dev mode. Real deployments use RQ; the shape of
# the dict mirrors what rq.Job would return so the UI doesn't care which
# backend is live.
_INPROC_JOBS: dict[str, dict] = {}


# -------------------------------------------------------------------- schemas
class SyncRequest(BaseModel):
    source: str | None = Field(
        None,
        description="Required for drive connector — the folder to walk.",
    )
    access_level: str = "all_fte"
    since: str | None = Field(
        None,
        description="ISO datetime for incremental sync. Ignored by connectors that can't honor it.",
    )


class JobHandle(BaseModel):
    job_id: str
    status: str
    connector: str


# -------------------------------------------------------------------- helpers
def _known_connectors() -> dict[str, str]:
    """Name → readiness-status so the UI can disable unready buttons.

    SharePoint is env-driven: "ready" when both JOJO_GRAPH_ACCESS_TOKEN and
    JOJO_SHAREPOINT_SITES are set, otherwise "needs-token". OneDrive + public
    drive come out of local mounts (ADR 0008) — they flip to "ready" as soon
    as JOJO_ONEDRIVE_PATH / JOJO_PUBLIC_DRIVE_PATH point at the sync folder
    / mount point. NurixNet isn't listed — it's a SharePoint site and rides
    along with the sharepoint connector's site list.
    """
    sharepoint_status = (
        "ready"
        if os.environ.get("JOJO_GRAPH_ACCESS_TOKEN") and os.environ.get("JOJO_SHAREPOINT_SITES")
        else "needs-token"
    )
    onedrive_status = "ready" if os.environ.get("JOJO_ONEDRIVE_PATH") else "needs-path"
    publicdrive_status = (
        "ready" if os.environ.get("JOJO_PUBLIC_DRIVE_PATH") else "needs-path"
    )
    return {
        "drive": "ready",
        "upload": "ready",
        "sharepoint": sharepoint_status,
        "onedrive": onedrive_status,
        "publicdrive": publicdrive_status,
    }


def _run_sync_inproc(connector_name: str, raw_root: Path, request: SyncRequest) -> dict:
    """Synchronous fallback. Returns the result payload the UI expects."""
    from datetime import datetime

    from jojo_ingest.driver import IngestDriver

    since = None
    if request.since:
        try:
            since = datetime.fromisoformat(request.since)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    if connector_name == "drive":
        from jojo_ingest.drive import DriveConnector

        if not request.source:
            raise HTTPException(status_code=400, detail="drive connector requires `source`")
        source = Path(request.source).expanduser().resolve()
        if not source.exists():
            raise HTTPException(status_code=400, detail=f"source path does not exist: {source}")
        connector = DriveConnector(source, access_level=request.access_level)
    elif connector_name == "sharepoint":
        from jojo_ingest.sharepoint import (
            SharePointEnvError,
            build_sharepoint_connector_from_env,
        )

        try:
            connector = build_sharepoint_connector_from_env(access_level=request.access_level)
        except SharePointEnvError as exc:
            # 400: the caller can fix this by setting an env var / pasting a
            # fresh token. Not 500 (server broken) or 501 (feature missing).
            raise HTTPException(status_code=400, detail=str(exc)) from exc
    elif connector_name == "onedrive":
        from jojo_ingest.onedrive import (
            OneDriveEnvError,
            build_onedrive_connector_from_env,
        )

        try:
            connector = build_onedrive_connector_from_env(
                access_level=request.access_level,
                path_override=request.source,
            )
        except OneDriveEnvError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
    elif connector_name == "publicdrive":
        from jojo_ingest.publicdrive import (
            PublicDriveEnvError,
            build_publicdrive_connector_from_env,
        )

        try:
            connector = build_publicdrive_connector_from_env(
                access_level=request.access_level,
                path_override=request.source,
            )
        except PublicDriveEnvError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
    else:
        # Nothing should land here any more — all known connectors are wired.
        # Keep the 501 for defense-in-depth so a future stub addition that
        # misses a branch still fails loudly.
        raise HTTPException(
            status_code=501,
            detail=(
                f"connector '{connector_name}' is not wired into the router "
                "yet — see packages/jojo_ingest for the implementation plan."
            ),
        )

    driver = IngestDriver(raw_root)
    result = driver.run([connector], since=since)
    return _serialize_result(result)


def _serialize_result(result) -> dict:
    return {
        "results": {
            name: {
                "added": cr.added,
                "updated": cr.updated,
                "skipped": cr.skipped,
                "errors": cr.errors,
                "failures": cr.failures,
            }
            for name, cr in result.results.items()
        },
        "change_record": str(result.change_record_path) if result.change_record_path else None,
    }


def _queue_sync(connector_name: str, raw_root: Path, request: SyncRequest) -> JobHandle:
    """Try to enqueue onto RQ; fall back to inproc on any failure."""
    job_id = uuid.uuid4().hex
    try:
        from redis import Redis
        from rq import Queue

        redis_conn = Redis.from_url(_REDIS_URL)
        redis_conn.ping()
        queue = Queue("jojo-ingest", connection=redis_conn)
        queue.enqueue(
            "jojo_ingest.driver.IngestDriver",  # placeholder until worker module exists
            args=(str(raw_root),),
            job_id=job_id,
            meta={"connector": connector_name},
        )
        _INPROC_JOBS[job_id] = {
            "status": "queued",
            "connector": connector_name,
            "result": None,
        }
        return JobHandle(job_id=job_id, status="queued", connector=connector_name)
    except Exception as exc:
        log.info("RQ unavailable (%s); running inproc", exc)

    result = _run_sync_inproc(connector_name, raw_root, request)
    _INPROC_JOBS[job_id] = {
        "status": "finished",
        "connector": connector_name,
        "result": result,
    }
    return JobHandle(job_id=job_id, status="finished", connector=connector_name)


# -------------------------------------------------------------------- endpoints
@router.get("/connectors")
def list_connectors() -> dict:
    """Return the set of connectors the backend knows about + readiness."""
    return {
        "connectors": [
            {"name": name, "status": status} for name, status in _known_connectors().items()
        ]
    }


@router.post("/sync/{connector}", response_model=JobHandle)
def sync_connector(connector: str, request: SyncRequest) -> JobHandle:
    if connector not in _known_connectors():
        raise HTTPException(status_code=404, detail=f"unknown connector: {connector}")
    return _queue_sync(connector, _DEFAULT_RAW, request)


@router.post("/resync/{connector}", response_model=JobHandle)
def resync_connector(connector: str, request: SyncRequest) -> JobHandle:
    # `resync` is `sync` with no --since. Clear it defensively.
    request = request.model_copy(update={"since": None})
    return _queue_sync(connector, _DEFAULT_RAW, request)


@router.post("/upload", response_model=JobHandle)
def upload_file(
    file: UploadFile = File(...),
    title: str | None = Form(None),
    author: str = Form(""),
    access_level: str = Form("all_fte"),
) -> JobHandle:
    """Save an uploaded file to the staging dir, then run it through upload connector."""
    _DEFAULT_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = Path(file.filename or "upload.bin").name
    dest = _DEFAULT_UPLOAD_DIR / f"{uuid.uuid4().hex}_{safe_name}"
    with dest.open("wb") as out:
        shutil.copyfileobj(file.file, out)

    job_id = uuid.uuid4().hex
    try:
        from jojo_ingest.driver import IngestDriver
        from jojo_ingest.upload import UploadConnector

        conn = UploadConnector(
            dest,
            title=title or safe_name,
            author=author,
            access_level=access_level,
        )
        driver = IngestDriver(_DEFAULT_RAW)
        result = driver.run([conn])
        _INPROC_JOBS[job_id] = {
            "status": "finished",
            "connector": "upload",
            "result": _serialize_result(result),
        }
    except Exception as exc:
        _INPROC_JOBS[job_id] = {
            "status": "failed",
            "connector": "upload",
            "error": str(exc),
        }
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return JobHandle(job_id=job_id, status="finished", connector="upload")


@router.get("/jobs")
def list_jobs() -> dict:
    return {"jobs": [{"job_id": jid, **meta} for jid, meta in _INPROC_JOBS.items()]}


@router.get("/jobs/{job_id}")
def get_job(job_id: str) -> dict:
    if job_id not in _INPROC_JOBS:
        raise HTTPException(status_code=404, detail="job not found")
    return {"job_id": job_id, **_INPROC_JOBS[job_id]}


@router.get("/status")
def ingest_status() -> dict:
    """Summary over the current manifest."""
    from jojo_connectors_common import Manifest

    raw = _DEFAULT_RAW
    if not (raw / "manifest.json").exists():
        return {"raw_root": str(raw), "total_entries": 0, "by_source": {}}
    manifest = Manifest.load(raw / "manifest.json")
    by_source: dict[str, int] = {}
    for entry in manifest.entries.values():
        by_source[entry.source_type] = by_source.get(entry.source_type, 0) + 1
    return {
        "raw_root": str(raw),
        "total_entries": len(manifest.entries),
        "by_source": by_source,
        "supersedence_chains": len(manifest.supersedence),
    }


@router.get("/schedule")
def get_schedule() -> None:
    """Windows Task Scheduler integration — deferred to local-mode packaging pass."""
    raise HTTPException(
        status_code=501,
        detail=(
            "Scheduler integration is deferred to the local-mode packaging pass "
            "at end of Phase 1 (Windows Task Scheduler wrappers). "
            "See PLAN.md §6 Phase 1."
        ),
    )
