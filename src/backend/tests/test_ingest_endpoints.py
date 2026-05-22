"""Real-endpoint tests for /api/ingest.

These go beyond the 501 smoke tests — they hit the drive + upload + status
endpoints with tmp directories, to make sure the router correctly wires
into `IngestDriver` and falls back to inproc execution when Redis isn't
available (which is the case in CI).
"""

from __future__ import annotations

import importlib
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from jojo_core import config as jojo_config


@pytest.fixture
def client_with_raw_root(tmp_path: Path, monkeypatch):
    """Spin up a TestClient pointed at an isolated tmp JOJO_RAW_ROOT.

    We reload the router module so the module-level env-var reads pick up
    our tmp path rather than whatever the dev env had when pytest started.
    Config I/O is redirected to a tmp file so the real %APPDATA%\\JojoBot\\config.json
    (which may have onedrive_path, graph tokens, etc.) doesn't bleed into tests.
    """
    raw = tmp_path / "ask_jojo_raw"
    monkeypatch.setenv("JOJO_RAW_ROOT", str(raw))
    monkeypatch.setenv("JOJO_UPLOAD_DIR", str(raw / "_staging"))
    # Force Redis URL to a port nothing's listening on — we want the inproc
    # fallback to kick in deterministically.
    monkeypatch.setenv("JOJO_REDIS_URL", "redis://127.0.0.1:1/0")
    monkeypatch.setenv("JOJO_CONFIG_FORCE_PLAINTEXT", "1")

    jojo_config.set_config_path_for_tests(tmp_path / "config.json")
    try:
        from backend import main
        from backend.routers import ingest_router

        importlib.reload(ingest_router)
        importlib.reload(main)

        yield TestClient(main.app), raw
    finally:
        jojo_config.set_config_path_for_tests(None)


def test_connectors_endpoint_lists_known_connectors(client_with_raw_root, monkeypatch):
    """The registry reports the five real connectors with env-driven status.

    NurixNet isn't a separate connector — it's one of the SharePoint sites
    the sharepoint connector already walks (see ADR 0008).
    """
    # Make sure no env-driven status leaks from the dev shell.
    monkeypatch.delenv("JOJO_GRAPH_ACCESS_TOKEN", raising=False)
    monkeypatch.delenv("JOJO_SHAREPOINT_SITES", raising=False)
    monkeypatch.delenv("JOJO_ONEDRIVE_PATH", raising=False)
    monkeypatch.delenv("JOJO_PUBLIC_DRIVE_PATH", raising=False)

    client, _ = client_with_raw_root
    r = client.get("/api/ingest/connectors")
    assert r.status_code == 200
    names = {c["name"] for c in r.json()["connectors"]}
    assert names == {"drive", "upload", "sharepoint", "onedrive", "publicdrive"}
    by_name = {c["name"]: c["status"] for c in r.json()["connectors"]}
    assert by_name["drive"] == "ready"
    assert by_name["upload"] == "ready"
    # SharePoint uses delegated tokens (ADR 0007) — "needs-token" until env is set.
    assert by_name["sharepoint"] == "needs-token"
    # OneDrive + public drive come out of local mounts (ADR 0008) —
    # "needs-path" until the operator sets the env var.
    assert by_name["onedrive"] == "needs-path"
    assert by_name["publicdrive"] == "needs-path"


def test_connectors_endpoint_reports_onedrive_ready_when_env_set(
    client_with_raw_root, monkeypatch, tmp_path: Path
):
    """When JOJO_ONEDRIVE_PATH is set, the registry flips onedrive to ready."""
    onedrive = tmp_path / "OneDrive - Nurix"
    onedrive.mkdir()
    monkeypatch.setenv("JOJO_ONEDRIVE_PATH", str(onedrive))
    client, _ = client_with_raw_root
    r = client.get("/api/ingest/connectors")
    by_name = {c["name"]: c["status"] for c in r.json()["connectors"]}
    assert by_name["onedrive"] == "ready"


def test_status_endpoint_on_empty_raw_root(client_with_raw_root):
    client, raw = client_with_raw_root
    r = client.get("/api/ingest/status")
    assert r.status_code == 200
    body = r.json()
    assert body["total_entries"] == 0
    assert body["by_source"] == {}
    assert body["raw_root"] == str(raw)


def test_sync_drive_end_to_end(client_with_raw_root, tmp_path: Path):
    client, raw = client_with_raw_root
    source = tmp_path / "src"
    (source / "sop").mkdir(parents=True)
    (source / "sop" / "recipe.md").write_text("# Recipe\n\nBody.\n", encoding="utf-8")

    r = client.post("/api/ingest/sync/drive", json={"source": str(source)})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["connector"] == "drive"
    # Redis is unreachable → inproc fallback → finished immediately.
    assert body["status"] == "finished"

    # Manifest now has one entry.
    status = client.get("/api/ingest/status").json()
    assert status["total_entries"] == 1
    assert status["by_source"] == {"drive": 1}

    # The job shows up in /jobs with its serialized result.
    job = client.get(f"/api/ingest/jobs/{body['job_id']}").json()
    assert job["status"] == "finished"
    assert job["result"]["results"]["drive"]["added"] == 1


def test_sync_drive_requires_source(client_with_raw_root):
    client, _ = client_with_raw_root
    r = client.post("/api/ingest/sync/drive", json={})
    assert r.status_code == 400
    assert "source" in r.json()["detail"].lower()


def test_sync_unknown_connector_returns_404(client_with_raw_root):
    client, _ = client_with_raw_root
    r = client.post("/api/ingest/sync/does-not-exist", json={})
    assert r.status_code == 404


def test_sync_sharepoint_without_env_returns_400(client_with_raw_root, monkeypatch):
    """Missing SharePoint env vars → 400 with actionable detail.

    400 (not 501) because this is a configuration issue the caller can fix
    without new code.
    """
    monkeypatch.delenv("JOJO_GRAPH_ACCESS_TOKEN", raising=False)
    monkeypatch.delenv("JOJO_SHAREPOINT_SITES", raising=False)
    client, _ = client_with_raw_root
    r = client.post("/api/ingest/sync/sharepoint", json={})
    assert r.status_code == 400
    detail = r.json()["detail"]
    assert "JOJO_SHAREPOINT_SITES" in detail or "JOJO_GRAPH_ACCESS_TOKEN" in detail


def test_sync_onedrive_without_env_returns_400(client_with_raw_root, monkeypatch):
    """Missing JOJO_ONEDRIVE_PATH → 400 naming the env var (not 501)."""
    monkeypatch.delenv("JOJO_ONEDRIVE_PATH", raising=False)
    client, _ = client_with_raw_root
    r = client.post("/api/ingest/sync/onedrive", json={})
    assert r.status_code == 400
    assert "JOJO_ONEDRIVE_PATH" in r.json()["detail"]


def test_sync_onedrive_end_to_end(client_with_raw_root, tmp_path: Path, monkeypatch):
    """With JOJO_ONEDRIVE_PATH pointed at a tmp folder, ingest runs end-to-end.

    Manifest source_type is "onedrive", proving the subclass correctly stamps
    provenance (so later phases can tell OneDrive content apart from arbitrary
    drive paths).
    """
    onedrive = tmp_path / "OneDrive - Nurix"
    (onedrive / "notes").mkdir(parents=True)
    (onedrive / "notes" / "plan.md").write_text("# Plan\n\nShip it.\n", encoding="utf-8")
    monkeypatch.setenv("JOJO_ONEDRIVE_PATH", str(onedrive))
    client, _ = client_with_raw_root
    r = client.post("/api/ingest/sync/onedrive", json={})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["connector"] == "onedrive"
    assert body["status"] == "finished"

    status = client.get("/api/ingest/status").json()
    assert status["total_entries"] == 1
    assert status["by_source"] == {"onedrive": 1}


def test_sync_publicdrive_without_env_returns_400(client_with_raw_root, monkeypatch):
    monkeypatch.delenv("JOJO_PUBLIC_DRIVE_PATH", raising=False)
    # Force the platform check to miss the Windows default so non-Windows CI
    # boxes (and macOS dev machines) exercise the "no env var" branch.
    monkeypatch.setattr("sys.platform", "linux")
    client, _ = client_with_raw_root
    r = client.post("/api/ingest/sync/publicdrive", json={})
    assert r.status_code == 400
    assert "JOJO_PUBLIC_DRIVE_PATH" in r.json()["detail"]


def test_upload_end_to_end(client_with_raw_root, tmp_path: Path):
    client, _ = client_with_raw_root
    upload = tmp_path / "notes.md"
    upload.write_text("# Notes\n\nBody.\n", encoding="utf-8")

    with upload.open("rb") as fh:
        r = client.post(
            "/api/ingest/upload",
            files={"file": ("notes.md", fh, "text/markdown")},
            data={"title": "Notes", "author": "Mateo", "access_level": "all_fte"},
        )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["connector"] == "upload"
    assert body["status"] == "finished"

    # Manifest reflects the upload.
    status = client.get("/api/ingest/status").json()
    assert status["total_entries"] == 1
    assert status["by_source"] == {"upload": 1}


def test_jobs_404_for_unknown_id(client_with_raw_root):
    client, _ = client_with_raw_root
    r = client.get("/api/ingest/jobs/does-not-exist")
    assert r.status_code == 404
