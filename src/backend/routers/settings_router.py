"""Settings API router — backs the Settings tab in the JoJo Bot frontend.

Endpoint map:

Section 1 — Anthropic API key:
  POST /api/settings/anthropic-key   {key}            → {ok, masked}
  GET  /api/settings/anthropic-key                    → {configured, masked}
  POST /api/settings/test-anthropic  {key?}           → {ok, model?, latency_ms?, error?}

Section 2 — Model tier:
  GET  /api/settings/models                           → {default_tier, per_task}
  POST /api/settings/models          {default_tier?, per_task?} → {ok}

Section 3 — MS Graph auth:
  GET  /api/settings/graph                            → {mode, configured, cache_expires}
  POST /api/settings/graph-token     {token}          → {ok}
  POST /api/settings/start-device-code               → {task_id, user_code, verification_uri, expires_at}
  GET  /api/settings/device-code-status?task_id=...  → {status, cache_expires}

Section 4 — Connector paths:
  GET  /api/settings/connectors                       → {onedrive_path, public_drive_path, sharepoint_sites}
  POST /api/settings/connectors      same fields      → {ok}

Section 5 — Lint cadence:
  GET  /api/settings/lint                             → {nightly_time, weekly_day, weekly_time, nightly_enabled, weekly_enabled}
  POST /api/settings/lint            same fields      → {ok}

Status sidebar:
  GET  /api/settings/status                           → {api_key, models, graph, connectors, lint}
"""

from __future__ import annotations

import logging
import os
import threading
import time
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from jojo_core import config

log = logging.getLogger("jojo.settings_router")

router = APIRouter()

# Module-level registry for device-code flow state, keyed by task_id.
_DEVICE_CODE_TASKS: dict[str, dict[str, Any]] = {}

# Default per-task model tier assignments.
_DEFAULT_PER_TASK: dict[str, str] = {
    "synthesis": "sonnet",
    "nightly-lint": "sonnet",
    "weekly-contradiction": "opus",
    "compile-absorb": "sonnet",
    "format-classify": "haiku",
}


# ----------------------------------------------------------------- helpers

def _mask_key(key: str) -> str:
    """Return masked representation showing only last 4 chars."""
    if len(key) <= 4:
        return "sk-ant-..." + key
    return f"sk-ant-...{key[-4:]}"


def _msal_cache_path() -> str:
    appdata = os.environ.get("APPDATA") or str(
        os.path.join(os.path.expanduser("~"), "AppData", "Roaming")
    )
    return os.path.join(appdata, "JojoBot", "tokencache.bin")


# ----------------------------------------------------------------- Section 1 models

class AnthropicKeyRequest(BaseModel):
    key: str


class TestAnthropicRequest(BaseModel):
    key: str | None = None


# ----------------------------------------------------------------- Section 1 endpoints

@router.post("/anthropic-key")
def save_anthropic_key(req: AnthropicKeyRequest) -> dict[str, Any]:
    """Store the Anthropic API key encrypted via jojo_core.config."""
    if not req.key:
        raise HTTPException(status_code=400, detail="key must be non-empty")
    config.set(config.KEY_ANTHROPIC_API_KEY, req.key)
    return {"ok": True, "masked": _mask_key(req.key)}


@router.get("/anthropic-key")
def get_anthropic_key() -> dict[str, Any]:
    """Return whether an API key is configured and its masked form."""
    key = config.get(config.KEY_ANTHROPIC_API_KEY, None)
    if not key:
        return {"configured": False, "masked": None}
    return {"configured": True, "masked": _mask_key(key)}


@router.post("/test-anthropic")
def test_anthropic(req: TestAnthropicRequest) -> dict[str, Any]:
    """Test the Anthropic connection with a minimal prompt."""
    import anthropic  # lazy so missing dep surfaces clearly

    key = req.key or config.get(config.KEY_ANTHROPIC_API_KEY, None)
    if not key:
        return {"ok": False, "error": "No API key provided or configured."}

    start = time.monotonic()
    try:
        client = anthropic.Anthropic(api_key=key)
        resp = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=10,
            messages=[{"role": "user", "content": "ping"}],
        )
        latency_ms = int((time.monotonic() - start) * 1000)
        _ = resp.content[0].text
        return {
            "ok": True,
            "model": "claude-sonnet-4-6",
            "latency_ms": latency_ms,
        }
    except anthropic.AuthenticationError as exc:
        return {"ok": False, "error": str(exc)}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc)}


# ----------------------------------------------------------------- Section 2 models

class ModelsRequest(BaseModel):
    default_tier: str | None = None
    per_task: dict[str, str] | None = None


# ----------------------------------------------------------------- Section 2 endpoints

@router.get("/models")
def get_models() -> dict[str, Any]:
    """Return current model tier configuration."""
    default_tier = config.get(config.KEY_MODEL_DEFAULT_TIER, "sonnet")
    per_task_raw = config.get(config.KEY_MODEL_PER_TASK, None)
    if isinstance(per_task_raw, dict):
        per_task = per_task_raw
    else:
        per_task = dict(_DEFAULT_PER_TASK)
    return {"default_tier": default_tier, "per_task": per_task}


@router.post("/models")
def save_models(req: ModelsRequest) -> dict[str, Any]:
    """Update model tier configuration."""
    if req.default_tier is not None:
        config.set(config.KEY_MODEL_DEFAULT_TIER, req.default_tier)
    if req.per_task is not None:
        config.set(config.KEY_MODEL_PER_TASK, req.per_task)
    return {"ok": True}


# ----------------------------------------------------------------- Section 3 models

class GraphTokenRequest(BaseModel):
    token: str


# ----------------------------------------------------------------- Section 3 endpoints

@router.get("/graph")
def get_graph() -> dict[str, Any]:
    """Return MS Graph auth mode and whether the token cache exists."""
    mode = config.get(config.KEY_GRAPH_AUTH_MODE, "device-code")
    cache_path = _msal_cache_path()
    configured = os.path.exists(cache_path) and os.path.getsize(cache_path) > 0
    return {"mode": mode, "configured": configured, "cache_expires": None}


@router.post("/graph-token")
def save_graph_token(req: GraphTokenRequest) -> dict[str, Any]:
    """Store a pasted MS Graph access token."""
    if not req.token:
        raise HTTPException(status_code=400, detail="token must be non-empty")
    config.set(config.KEY_GRAPH_ACCESS_TOKEN, req.token)
    return {"ok": True}


@router.post("/start-device-code")
def start_device_code() -> dict[str, Any]:
    """Initiate a device-code login flow and return the user code to display."""
    import msal  # lazy import so msal absence is a clear error

    client_id = config.get(config.KEY_MSAL_CLIENT_ID)
    tenant_id = config.get(config.KEY_MSAL_TENANT_ID)
    authority = f"https://login.microsoftonline.com/{tenant_id}"
    scopes = ["Files.Read.All", "Sites.Read.All", "offline_access"]

    msal_app = msal.PublicClientApplication(client_id, authority=authority)
    flow = msal_app.initiate_device_flow(scopes=scopes)

    if "error" in flow:
        raise HTTPException(
            status_code=502,
            detail=f"MSAL device flow initiation failed: {flow.get('error_description', flow['error'])}",
        )

    task_id = str(uuid4())
    expires_in = flow.get("expires_in", 900)
    expires_at = (datetime.now(tz=timezone.utc) + timedelta(seconds=expires_in)).isoformat()

    _DEVICE_CODE_TASKS[task_id] = {"status": "pending", "cache_expires": None}

    def _acquire(tid: str, app: Any, f: dict[str, Any]) -> None:
        try:
            result = app.acquire_token_by_device_flow(f)
            if result and "access_token" in result:
                config.set(config.KEY_GRAPH_ACCESS_TOKEN, result["access_token"])
                _DEVICE_CODE_TASKS[tid]["status"] = "complete"
                _DEVICE_CODE_TASKS[tid]["cache_expires"] = (
                    datetime.now(tz=timezone.utc) + timedelta(days=90)
                ).isoformat()
            else:
                err = result.get("error", "unknown") if result else "no_result"
                if err in ("authorization_declined", "expired_token"):
                    _DEVICE_CODE_TASKS[tid]["status"] = "timeout"
                else:
                    _DEVICE_CODE_TASKS[tid]["status"] = "failed"
        except Exception as exc:  # noqa: BLE001
            log.error("Device code acquire failed: %s", exc)
            _DEVICE_CODE_TASKS[tid]["status"] = "failed"

    t = threading.Thread(target=_acquire, args=(task_id, msal_app, flow), daemon=True)
    t.start()

    return {
        "task_id": task_id,
        "user_code": flow["user_code"],
        "verification_uri": flow["verification_uri"],
        "expires_at": expires_at,
    }


@router.get("/device-code-status")
def get_device_code_status(task_id: str) -> dict[str, Any]:
    """Poll the status of a running device-code flow."""
    task = _DEVICE_CODE_TASKS.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Unknown task_id: {task_id!r}")
    return {"status": task["status"], "cache_expires": task.get("cache_expires")}


# ----------------------------------------------------------------- Section 4 models

class ConnectorsRequest(BaseModel):
    onedrive_path: str | None = None
    public_drive_path: str | None = None
    sharepoint_sites: str | None = None


# ----------------------------------------------------------------- Section 4 endpoints

@router.get("/connectors")
def get_connectors() -> dict[str, Any]:
    """Return configured connector paths."""
    return {
        "onedrive_path": config.get(config.KEY_ONEDRIVE_PATH, None),
        "public_drive_path": config.get(config.KEY_PUBLIC_DRIVE_PATH, None),
        "sharepoint_sites": config.get(config.KEY_SHAREPOINT_SITES, None),
    }


@router.post("/connectors")
def save_connectors(req: ConnectorsRequest) -> dict[str, Any]:
    """Update connector path configuration."""
    if req.onedrive_path is not None:
        config.set(config.KEY_ONEDRIVE_PATH, req.onedrive_path)
    if req.public_drive_path is not None:
        config.set(config.KEY_PUBLIC_DRIVE_PATH, req.public_drive_path)
    if req.sharepoint_sites is not None:
        config.set(config.KEY_SHAREPOINT_SITES, req.sharepoint_sites)
    return {"ok": True}


# ----------------------------------------------------------------- Section 5 models

class LintRequest(BaseModel):
    nightly_time: str | None = None
    weekly_day: str | None = None
    weekly_time: str | None = None
    nightly_enabled: bool | None = None
    weekly_enabled: bool | None = None


# ----------------------------------------------------------------- Section 5 endpoints

@router.get("/lint")
def get_lint() -> dict[str, Any]:
    """Return current lint cadence configuration."""
    nightly_enabled_raw = config.get(config.KEY_LINT_NIGHTLY_ENABLED, "true")
    weekly_enabled_raw = config.get(config.KEY_LINT_WEEKLY_ENABLED, "true")
    return {
        "nightly_time": config.get(config.KEY_LINT_NIGHTLY_TIME, "02:00"),
        "weekly_day": config.get(config.KEY_LINT_WEEKLY_DAY, "Sunday"),
        "weekly_time": config.get(config.KEY_LINT_WEEKLY_TIME, "04:00"),
        "nightly_enabled": str(nightly_enabled_raw).lower() not in ("false", "0", "no"),
        "weekly_enabled": str(weekly_enabled_raw).lower() not in ("false", "0", "no"),
    }


@router.post("/lint")
def save_lint(req: LintRequest) -> dict[str, Any]:
    """Update lint cadence configuration."""
    if req.nightly_time is not None:
        config.set(config.KEY_LINT_NIGHTLY_TIME, req.nightly_time)
    if req.weekly_day is not None:
        config.set(config.KEY_LINT_WEEKLY_DAY, req.weekly_day)
    if req.weekly_time is not None:
        config.set(config.KEY_LINT_WEEKLY_TIME, req.weekly_time)
    if req.nightly_enabled is not None:
        config.set(config.KEY_LINT_NIGHTLY_ENABLED, str(req.nightly_enabled).lower())
    if req.weekly_enabled is not None:
        config.set(config.KEY_LINT_WEEKLY_ENABLED, str(req.weekly_enabled).lower())
    return {"ok": True}


# ----------------------------------------------------------------- Status sidebar

@router.get("/status")
def get_status() -> dict[str, Any]:
    """Aggregate status across all settings sections for the sidebar."""
    api_key = config.get(config.KEY_ANTHROPIC_API_KEY, None)
    api_key_ok = bool(api_key)
    api_key_detail = "Key configured." if api_key_ok else "No API key configured."

    default_tier = config.get(config.KEY_MODEL_DEFAULT_TIER, "sonnet")
    models_detail = f"default {default_tier}"

    cache_path = _msal_cache_path()
    graph_ok = os.path.exists(cache_path) and os.path.getsize(cache_path) > 0
    graph_detail = "Token cache present." if graph_ok else "No valid token cache."

    onedrive_path = config.get(config.KEY_ONEDRIVE_PATH, None)
    connectors_ok = bool(onedrive_path) and os.path.exists(str(onedrive_path))
    connectors_detail = (
        f"OneDrive: {onedrive_path}" if connectors_ok else "OneDrive path not configured or missing."
    )

    nightly_time = config.get(config.KEY_LINT_NIGHTLY_TIME, "02:00")
    weekly_day = config.get(config.KEY_LINT_WEEKLY_DAY, "Sunday")
    weekly_time = config.get(config.KEY_LINT_WEEKLY_TIME, "04:00")
    lint_detail = f"nightly {nightly_time}, weekly {weekly_day} {weekly_time}"

    return {
        "api_key": {"ok": api_key_ok, "detail": api_key_detail},
        "models": {"ok": True, "detail": models_detail},
        "graph": {"ok": graph_ok, "detail": graph_detail},
        "connectors": {"ok": connectors_ok, "detail": connectors_detail},
        "lint": {"ok": True, "detail": lint_detail},
    }
