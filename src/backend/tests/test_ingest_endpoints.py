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


@pytest.fixture
def client_with_raw_root(tmp_path: Path, monkeypatch):
    """Spin up a TestClient pointed at an isolated tmp JOJO_RAW_ROOT.

    We reload the router module so the module-level env-var reads pick up
    our tmp path rather than whatever the dev env had when pytest started.
    """
    raw = tmp_path / "ask_jojo_raw"
    monkeypatch.setenv("JOJO_RAW_ROOT", str(raw))
    monkeypatch.setenv("JOJO_UPLOAD_DIR", str(raw / "_staging"))
    # Force Redis URL to a port nothing's listening on — we want the inproc
    # fallback to kick in deterministically.
    monkeypatch.setenv("JOJO_REDIS_URL", "redis://127.0.0.1:1/0")

    from backend import main
    from backend.routers import ingest_router

    importlib.reload(ingest_router)
    importlib.reload(main)

    return TestClient(main.app), raw


def test_connectors_endpoint_lists_known_connectors(client_with_raw_root):
    client, _ = client_with_raw_root
    r = client.get("/api/ingest/connectors")
    assert r.status_code == 200
    names = {c["name"] for c in r.json()["connectors"]}
    assert {"drive", "upload", "sharepoint", "onedrive", "nurixnet"} <= names
    by_name = {c["name"]: c["status"] for c in r.json()["connectors"]}
    assert by_name["drive"] == "ready"
    assert by_name["upload"] == "ready"
    assert by_name["sharepoint"] == "needs-creds"


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


def test_sync_stubbed_connector_returns_501(client_with_raw_root):
    client, _ = client_with_raw_root
    # sharepoint is known but stubbed — the inproc fallback should translate
    # that into a 501 with an actionable message.
    r = client.post("/api/ingest/sync/sharepoint", json={})
    assert r.status_code == 501
    assert "stubbed" in r.json()["detail"].lower()


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
