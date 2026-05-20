"""Ops router — backs the Ops tab in the JoJo Bot frontend.

Endpoint map:

- ``GET  /api/ops/status``   — combined wiki stats + connector health + api_key + queue.
- ``GET  /api/ops/jobs``     — thin proxy over ingest job list.
- ``POST /api/ops/absorb``   — log an absorb trigger (manual path until API key lands).
- ``GET  /api/ops/events``   — SSE heartbeat stream for live job updates.
- ``POST /api/ops/lint/{scope}``  — run nightly or weekly lint via jojo_lint.
- ``GET  /api/ops/lint/history``  — recent lint run history.
- ``GET  /api/ops/lint/metrics``  — 30-day rolling metrics series.

Implementation notes:
- Reuses ``wiki_stats()`` from wiki_router and ``_known_connectors()`` /
  ``_INPROC_JOBS`` from ingest_router rather than duplicating logic.
- The absorb endpoint intentionally does not enqueue a real RQ job yet.
  That path lands when ``jojo_compile absorb`` is wired in Phase 4/5.
- The SSE stream emits a heartbeat every 10 s and polls the in-process
  job registry every 2 s for any status changes. Uses
  ``starlette.responses.StreamingResponse`` with an async generator.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import signal
import threading
from collections.abc import AsyncGenerator
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from starlette.responses import StreamingResponse

from jojo_core import config

log = logging.getLogger("jojo.ops_router")

router = APIRouter()


# -------------------------------------------------------------------- lint helpers

def _wiki_root() -> Path:
    """Resolve the wiki root — mirrors qa_router._wiki_root()."""
    default = str(Path(__file__).resolve().parents[4] / "ask_jojo_wiki")
    env_val = os.environ.get("JOJO_WIKI_ROOT")
    if env_val:
        return Path(env_val).resolve()
    return Path(config.get("wiki_root", default)).resolve()


def _history_dir() -> Path:
    """Resolve the lint history directory."""
    default = str(Path.home() / "AppData" / "Local" / "JojoBot" / "lint-history")
    env_val = os.environ.get("JOJO_LINT_HISTORY_DIR")
    if env_val:
        return Path(env_val).resolve()
    return Path(default)


# -------------------------------------------------------------------- helpers

def _get_wiki_stats() -> dict[str, Any]:
    """Thin wrapper so ops_router can call wiki_stats without a circular import."""
    from backend.routers.wiki_router import (
        wiki_stats,  # local import avoids import-time side-effects
    )
    return wiki_stats()


def _get_connector_list() -> list[dict[str, Any]]:
    """Return connector status + manifest-derived last_synced / file_count."""
    from backend.routers.ingest_router import _known_connectors

    # Try to read manifest for last_synced + file_count.
    by_source: dict[str, int] = {}
    latest_fetched: dict[str, str] = {}
    try:
        from pathlib import Path

        from jojo_connectors_common import Manifest
        from jojo_core import config as _cfg

        raw_root = Path(_cfg.get(_cfg.KEY_RAW_ROOT, "./ask_jojo_raw")).resolve()
        manifest_path = raw_root / "manifest.json"
        if manifest_path.exists():
            mf = Manifest.load(manifest_path)
            for entry in mf.entries.values():
                by_source[entry.source_type] = by_source.get(entry.source_type, 0) + 1
                if entry.fetched and entry.fetched > latest_fetched.get(entry.source_type, ""):
                    latest_fetched[entry.source_type] = entry.fetched
    except Exception as exc:  # noqa: BLE001
        log.debug("Could not read manifest for connector stats: %s", exc)

    known = _known_connectors()
    # Ops tab shows the four user-facing connectors (omit "upload" — it's UI-only).
    ops_connectors = ["onedrive", "publicdrive", "sharepoint", "drive"]
    result = []
    for name in ops_connectors:
        status = known.get(name, "unknown")
        # source_type in manifest matches connector name for all four.
        result.append({
            "name": name,
            "status": status,
            "last_synced": latest_fetched.get(name),
            "file_count": by_source.get(name, 0),
        })
    return result


def _get_queue_info() -> dict[str, Any]:
    """Return pending/failed counts and recent jobs from in-process registry."""
    from backend.routers.ingest_router import _INPROC_JOBS

    jobs = [{"job_id": jid, **meta} for jid, meta in _INPROC_JOBS.items()]
    pending = sum(1 for j in jobs if j.get("status") in {"queued", "started"})
    failed = sum(1 for j in jobs if j.get("status") == "failed")
    return {
        "pending": pending,
        "failed": failed,
        "recent_jobs": jobs[-20:],
    }


# -------------------------------------------------------------------- endpoints

@router.get("/status")
def get_status() -> dict[str, Any]:
    """Return a combined health snapshot for the Ops dashboard.

    Response shape::

        {
          "wiki": { "total_pages": 138, "last_commit_sha": "61f11eb", ... },
          "connectors": [{ "name": "onedrive", "status": "ready", ... }, ...],
          "api_key_configured": false,
          "queue": { "pending": 0, "failed": 0, "recent_jobs": [] }
        }
    """
    # Wiki stats — gracefully degrade if wiki_root is unconfigured.
    try:
        wiki = _get_wiki_stats()
    except Exception as exc:  # noqa: BLE001
        log.debug("wiki_stats failed: %s", exc)
        wiki = {
            "total_pages": 0,
            "last_commit_sha": "",
            "last_commit_message": "",
            "last_commit_date": "",
            "schema_version": "0.1.0",
        }

    connectors = _get_connector_list()
    api_key_configured = config.get(config.KEY_ANTHROPIC_API_KEY, None) is not None
    queue = _get_queue_info()

    return {
        "wiki": wiki,
        "connectors": connectors,
        "api_key_configured": api_key_configured,
        "queue": queue,
    }


@router.get("/jobs")
def list_jobs() -> dict[str, Any]:
    """Thin proxy over the ingest job registry.

    Returns the same shape as ``GET /api/ingest/jobs``.
    """
    from backend.routers.ingest_router import _INPROC_JOBS

    jobs = [{"job_id": jid, **meta} for jid, meta in _INPROC_JOBS.items()]
    return {"jobs": jobs}


@router.post("/absorb")
def trigger_absorb() -> dict[str, Any]:
    """Log an absorb trigger.

    Does not enqueue a real RQ job yet (jojo_compile absorb is pending API
    key and ADR 0010).  Returns a stable ``job_id`` so the UI can track it.
    When the automated path lands, swap the body to call ``_queue_sync``; the
    response shape stays identical so the frontend requires no change.
    """
    job_id = f"absorb-{datetime.now(tz=timezone.utc).isoformat()}"
    log.info("Absorb trigger logged: %s", job_id)
    return {
        "job_id": job_id,
        "status": "logged",
        "message": "Absorb queued. Run the Cowork absorb session to process.",
    }


async def _sse_generator() -> AsyncGenerator[str, None]:
    """Async generator that emits SSE heartbeats every 10 s.

    Polls the in-process job registry every 2 s; emits a ``job_update`` event
    when the job count changes.
    """
    from backend.routers.ingest_router import _INPROC_JOBS

    # Emit initial heartbeat immediately so clients (and tests) get a response
    # without waiting for the first 10-second tick.
    yield "event: heartbeat\ndata: {}\n\n"

    last_job_count = len(_INPROC_JOBS)
    heartbeat_counter = 0

    while True:
        await asyncio.sleep(2)
        heartbeat_counter += 1

        current_count = len(_INPROC_JOBS)
        if current_count != last_job_count:
            last_job_count = current_count
            jobs = [{"job_id": jid, **meta} for jid, meta in _INPROC_JOBS.items()]
            yield f"event: job_update\ndata: {json.dumps({'jobs': jobs[-20:]})}\n\n"

        # Emit a heartbeat every ~10 s (5 × 2 s ticks).
        if heartbeat_counter >= 5:
            heartbeat_counter = 0
            yield "event: heartbeat\ndata: {}\n\n"


@router.get("/events")
def stream_events() -> StreamingResponse:
    """Server-sent events stream for live job progress.

    Emits:
    - ``heartbeat`` every 10 s (keeps connection alive).
    - ``job_update`` when the in-process job registry changes.
    """
    return StreamingResponse(
        _sse_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/lint/{scope}")
def trigger_lint(scope: str) -> dict[str, Any]:
    """Trigger a lint run for the given scope.

    Args:
        scope: ``"nightly"`` or ``"weekly"``.

    Returns:
        ``{"status": "ok", "scope": scope, "results": [...]}``

    Raises:
        400: when ``scope`` is not ``"nightly"`` or ``"weekly"``.
    """
    if scope not in ("nightly", "weekly"):
        raise HTTPException(
            status_code=400,
            detail=f"scope must be 'nightly' or 'weekly', got {scope!r}",
        )

    from jojo_lint import history as lint_history
    from jojo_lint import registry as lint_registry

    wiki = _wiki_root()
    hist_dir = _history_dir()

    try:
        if scope == "nightly":
            results = lint_registry.run_nightly(wiki)
        else:
            results = lint_registry.run_weekly(wiki)

        lint_history.append_run(scope, results, history_dir=hist_dir)

        return {
            "status": "ok",
            "scope": scope,
            "results": [r.to_dict() for r in results],
        }
    except Exception as exc:  # noqa: BLE001
        log.error("Lint run failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/lint/history")
def get_lint_history(
    scope: str | None = Query(None, description="Filter by scope: nightly or weekly"),
    days: int = Query(30, ge=1, le=365, description="Look-back window in days"),
) -> dict[str, Any]:
    """Return recent lint run history.

    Query params:
        scope: optional filter (``"nightly"`` or ``"weekly"``).
        days: look-back window in days (default 30).

    Returns:
        ``{"runs": [...]}``
    """
    from jojo_lint import history as lint_history

    runs = lint_history.load_runs(scope=scope, days=days, history_dir=_history_dir())
    return {"runs": runs}


@router.post("/restart")
def restart_server() -> dict[str, Any]:
    """Schedule a server restart after 2 seconds and return immediately.

    The 2-second delay ensures the HTTP response is delivered before the
    process exits. The Windows Service supervisor is expected to restart
    the process automatically after termination.
    """
    pid = os.getpid()

    def _do_restart() -> None:
        try:
            os.kill(pid, signal.SIGTERM)
        except (OSError, AttributeError):
            try:
                os.kill(pid, signal.CTRL_BREAK_EVENT)  # type: ignore[attr-defined]
            except Exception:  # noqa: BLE001
                os._exit(0)

    threading.Timer(2.0, _do_restart).start()
    return {"ok": True, "message": "Server restart scheduled in 2s."}


@router.get("/lint/metrics")
def get_lint_metrics(
    days: int = Query(30, ge=1, le=365, description="Look-back window in days"),
) -> dict[str, Any]:
    """Return the 30-day rolling lint metrics series.

    Query params:
        days: look-back window in days (default 30).

    Returns:
        ``{"series": [...]}``
    """
    from jojo_lint import history as lint_history

    series = lint_history.metrics_series(days=days, history_dir=_history_dir())
    return {"series": series}
