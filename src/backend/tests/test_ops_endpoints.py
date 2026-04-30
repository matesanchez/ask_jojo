"""Real-endpoint tests for /api/ops.

Follows the pattern established by test_raw_endpoints.py and
test_wiki_endpoints.py: fixture-based isolation, TestClient, and assertions
on response shapes.

Required test cases (per Phase 3 spec):
- GET /api/ops/status returns dict with wiki, connectors, api_key_configured, queue
- GET /api/ops/status -- api_key_configured is False when env var absent
- POST /api/ops/absorb returns { status: "logged" }
- GET /api/ops/jobs returns { jobs: [...] }
- GET /api/ops/events returns text/event-stream content type
- POST /api/ops/lint/* returns 501
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

# -------------------------------------------------------------------- fixture

@pytest.fixture
def client(tmp_path, monkeypatch):
    """Return a TestClient with a clean environment.

    Points JOJO_RAW_ROOT at an empty tmp dir so the ops router doesn't
    accidentally read the developer's real manifest. Also ensures no
    ANTHROPIC_API_KEY leaks in from the environment.
    """
    raw = tmp_path / "ask_jojo_raw"
    raw.mkdir()
    monkeypatch.setenv("JOJO_RAW_ROOT", str(raw))
    monkeypatch.setenv("JOJO_WIKI_ROOT", str(tmp_path / "ask_jojo_wiki"))
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    from backend.main import app
    return TestClient(app)


# -------------------------------------------------------------------- /status

def test_status_returns_required_keys(client):
    r = client.get("/api/ops/status")
    assert r.status_code == 200
    body = r.json()
    assert "wiki" in body
    assert "connectors" in body
    assert "api_key_configured" in body
    assert "queue" in body


def test_status_wiki_has_page_count(client):
    r = client.get("/api/ops/status")
    wiki = r.json()["wiki"]
    assert "total_pages" in wiki
    assert isinstance(wiki["total_pages"], int)


def test_status_connectors_is_list(client):
    r = client.get("/api/ops/status")
    connectors = r.json()["connectors"]
    assert isinstance(connectors, list)
    # All four user-facing connectors should appear.
    names = {c["name"] for c in connectors}
    assert names == {"onedrive", "publicdrive", "sharepoint", "drive"}


def test_status_api_key_configured_false_when_key_absent(client, monkeypatch):
    """api_key_configured must be False when ANTHROPIC_API_KEY is not set."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    # Also ensure config.json has no key (conftest already redirects to tmp).
    r = client.get("/api/ops/status")
    assert r.status_code == 200
    assert r.json()["api_key_configured"] is False


def test_status_queue_has_counts(client):
    r = client.get("/api/ops/status")
    queue = r.json()["queue"]
    assert "pending" in queue
    assert "failed" in queue
    assert "recent_jobs" in queue


# -------------------------------------------------------------------- /absorb

def test_absorb_returns_logged_status(client):
    r = client.post("/api/ops/absorb")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "logged"
    assert "job_id" in body
    assert body["job_id"].startswith("absorb-")
    assert "message" in body


# -------------------------------------------------------------------- /jobs

def test_jobs_returns_list(client):
    r = client.get("/api/ops/jobs")
    assert r.status_code == 200
    body = r.json()
    assert "jobs" in body
    assert isinstance(body["jobs"], list)


# -------------------------------------------------------------------- /events

def test_events_returns_sse_content_type():
    """GET /api/ops/events must return text/event-stream.

    Drives the ASGI app directly (raw scope/receive/send) so we can cancel
    the task as soon as the response headers arrive — avoiding the TestClient
    and httpx.ASGITransport issue where infinite generators never set
    ``more_body=False`` and the transport hangs waiting for the body to end.
    """
    import asyncio

    from backend.main import app

    status_code: int | None = None
    resp_headers: dict[str, str] = {}

    async def _run() -> None:
        nonlocal status_code, resp_headers

        scope = {
            "type": "http",
            "http_version": "1.1",
            "method": "GET",
            "path": "/api/ops/events",
            "raw_path": b"/api/ops/events",
            "root_path": "",
            "scheme": "http",
            "query_string": b"",
            "headers": [(b"host", b"testserver")],
            "client": ("127.0.0.1", 9999),
            "server": ("testserver", 80),
            "state": {},
        }

        headers_received: asyncio.Event = asyncio.Event()

        async def receive() -> dict:  # type: ignore[type-arg]
            # Block until headers arrive, then signal disconnect so the app
            # can clean up; the task is cancelled immediately after anyway.
            await headers_received.wait()
            return {"type": "http.disconnect"}

        async def send(message: dict) -> None:  # type: ignore[type-arg]
            nonlocal status_code, resp_headers
            if message["type"] == "http.response.start":
                status_code = message["status"]
                resp_headers = {
                    k.decode(): v.decode() for k, v in message.get("headers", [])
                }
                headers_received.set()

        app_task = asyncio.create_task(app(scope, receive, send))
        # Wait for the response-start event, then cancel the infinite generator.
        await headers_received.wait()
        app_task.cancel()
        try:
            await app_task
        except (asyncio.CancelledError, Exception):
            pass  # Cancellation during asyncio.sleep is expected.

    asyncio.run(_run())

    assert status_code == 200
    ct = resp_headers.get("content-type", "")
    assert "text/event-stream" in ct


# -------------------------------------------------------------------- /lint (501 stub)

def test_lint_returns_501(client):
    r = client.post("/api/ops/lint/nightly")
    assert r.status_code == 501
    assert "Phase 6" in r.json()["detail"]
