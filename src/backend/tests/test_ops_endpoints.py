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


# -------------------------------------------------------------------- /lint (Phase 6 real implementation)

def test_lint_nightly_runs(client, monkeypatch, tmp_path):
    """POST /api/ops/lint/nightly returns 200 and valid result shape."""
    import yaml

    # Build a minimal wiki
    wiki = tmp_path / "wiki"
    wiki.mkdir()
    (wiki / "concepts").mkdir()
    fm = {
        "title": "Test Concept",
        "type": "concept",
        "slug": "test-concept",
        "created": "2026-01-01",
        "last_updated": "2026-04-01",
        "last_reviewed": "2026-04-01",
        "schema_version": "0.2.0",
        "confidence": "high",
        "corpus": "protein-sciences",
        "sources": [{"path": "raw/x.md", "hash": "abc", "ingested": "2026-01-01"}],
    }
    page = wiki / "concepts" / "test-concept.md"
    page.write_text(f"---\n{yaml.dump(fm)}---\n\nBody.\n", encoding="utf-8")
    (wiki / "_index.md").write_text(
        "# Wiki Index\n- [[test-concept|Test Concept]] — `concepts/test-concept.md`\n",
        encoding="utf-8",
    )

    hist = tmp_path / "hist"
    monkeypatch.setenv("JOJO_WIKI_ROOT", str(wiki))
    monkeypatch.setenv("JOJO_LINT_HISTORY_DIR", str(hist))

    from fastapi.testclient import TestClient

    from backend.main import app

    c = TestClient(app)
    r = c.post("/api/ops/lint/nightly")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["status"] == "ok"
    assert body["scope"] == "nightly"
    assert isinstance(body["results"], list)
    assert len(body["results"]) == 6  # 6 nightly checks
    for result in body["results"]:
        assert "check_name" in result
        assert "status" in result
        assert "findings" in result


def test_lint_invalid_scope(client):
    """POST /api/ops/lint/invalid returns 400."""
    r = client.post("/api/ops/lint/invalid")
    assert r.status_code == 400
    assert "nightly" in r.json()["detail"] or "weekly" in r.json()["detail"]


def test_lint_history_empty(client, monkeypatch, tmp_path):
    """GET /api/ops/lint/history returns 200 and runs: [] when no history."""
    hist = tmp_path / "empty_hist"
    monkeypatch.setenv("JOJO_LINT_HISTORY_DIR", str(hist))

    from fastapi.testclient import TestClient

    from backend.main import app

    c = TestClient(app)
    r = c.get("/api/ops/lint/history")
    assert r.status_code == 200
    body = r.json()
    assert "runs" in body
    assert body["runs"] == []


def test_lint_metrics_empty(client, monkeypatch, tmp_path):
    """GET /api/ops/lint/metrics returns 200 and series key when no history."""
    hist = tmp_path / "empty_hist2"
    monkeypatch.setenv("JOJO_LINT_HISTORY_DIR", str(hist))

    from fastapi.testclient import TestClient

    from backend.main import app

    c = TestClient(app)
    r = c.get("/api/ops/lint/metrics")
    assert r.status_code == 200
    body = r.json()
    assert "series" in body
    assert isinstance(body["series"], list)


def test_lint_weekly_no_api_key(monkeypatch, tmp_path):
    """POST /api/ops/lint/weekly returns 200 with api_key_required stubs when no key."""

    wiki = tmp_path / "wiki"
    wiki.mkdir()
    (wiki / "_index.md").write_text("# Wiki Index\n", encoding="utf-8")
    hist = tmp_path / "hist"
    monkeypatch.setenv("JOJO_WIKI_ROOT", str(wiki))
    monkeypatch.setenv("JOJO_LINT_HISTORY_DIR", str(hist))
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    from fastapi.testclient import TestClient

    from backend.main import app

    c = TestClient(app)
    r = c.post("/api/ops/lint/weekly")
    assert r.status_code == 200
    body = r.json()
    assert body["scope"] == "weekly"
    assert isinstance(body["results"], list)
    assert len(body["results"]) == 4
    statuses = {res["status"] for res in body["results"]}
    assert statuses == {"api_key_required"}


def test_lint_history_scope_filter(monkeypatch, tmp_path):
    """GET /api/ops/lint/history?scope=nightly returns only nightly runs."""
    import json
    from datetime import datetime, timezone

    hist = tmp_path / "hist"
    hist.mkdir()
    jl = hist / "lint-history.jsonl"
    now = datetime.now(tz=timezone.utc).isoformat()
    jl.write_text(
        json.dumps({"scope": "nightly", "run_at": now, "results": []}) + "\n"
        + json.dumps({"scope": "weekly", "run_at": now, "results": []}) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("JOJO_LINT_HISTORY_DIR", str(hist))

    from fastapi.testclient import TestClient

    from backend.main import app

    c = TestClient(app)
    r = c.get("/api/ops/lint/history?scope=nightly")
    assert r.status_code == 200
    runs = r.json()["runs"]
    assert all(run["scope"] == "nightly" for run in runs)
    assert len(runs) == 1


def test_lint_history_days_excludes_old_runs(monkeypatch, tmp_path):
    """GET /api/ops/lint/history?days=7 excludes runs older than 7 days."""
    import json

    hist = tmp_path / "hist"
    hist.mkdir()
    jl = hist / "lint-history.jsonl"
    jl.write_text(
        json.dumps({"scope": "nightly", "run_at": "2020-01-01T00:00:00+00:00", "results": []}) + "\n"
        + json.dumps({"scope": "nightly", "run_at": "2026-05-19T00:00:00+00:00", "results": []}) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("JOJO_LINT_HISTORY_DIR", str(hist))

    from fastapi.testclient import TestClient

    from backend.main import app

    c = TestClient(app)
    r = c.get("/api/ops/lint/history?days=7")
    assert r.status_code == 200
    runs = r.json()["runs"]
    assert all(run["run_at"] >= "2026-05-12" for run in runs)


def test_lint_metrics_with_seeded_history(monkeypatch, tmp_path):
    """GET /api/ops/lint/metrics returns populated series when history has data."""
    import json

    hist = tmp_path / "hist"
    hist.mkdir()
    jl = hist / "lint-history.jsonl"
    run = {
        "scope": "nightly",
        "run_at": "2026-05-19T00:00:00+00:00",
        "results": [
            {"check_name": "orphan", "status": "ok", "findings": [], "run_at": "2026-05-19T00:00:00+00:00", "duration_ms": 100},
            {"check_name": "schema", "status": "ok", "findings": [], "run_at": "2026-05-19T00:00:00+00:00", "duration_ms": 80},
            {"check_name": "stub", "status": "ok", "findings": [], "run_at": "2026-05-19T00:00:00+00:00", "duration_ms": 90},
            {"check_name": "wikilink", "status": "ok", "findings": [], "run_at": "2026-05-19T00:00:00+00:00", "duration_ms": 70},
            {"check_name": "bloat", "status": "ok", "findings": [], "run_at": "2026-05-19T00:00:00+00:00", "duration_ms": 60},
            {"check_name": "quote_budget", "status": "ok", "findings": [], "run_at": "2026-05-19T00:00:00+00:00", "duration_ms": 50},
        ],
    }
    jl.write_text(json.dumps(run) + "\n", encoding="utf-8")
    monkeypatch.setenv("JOJO_LINT_HISTORY_DIR", str(hist))

    from fastapi.testclient import TestClient

    from backend.main import app

    c = TestClient(app)
    r = c.get("/api/ops/lint/metrics?days=30")
    assert r.status_code == 200
    series = r.json()["series"]
    assert len(series) >= 1
    point = series[0]
    assert "run_at" in point
    assert "orphan_count" in point
    assert "avg_confidence_score" in point
    assert "stale_count" in point
    assert "wikilink_error_count" in point


def test_lint_registry_error_returns_500(monkeypatch, tmp_path):
    """POST /api/ops/lint/nightly returns 500 when the registry raises."""
    monkeypatch.setenv("JOJO_WIKI_ROOT", str(tmp_path / "wiki"))
    monkeypatch.setenv("JOJO_LINT_HISTORY_DIR", str(tmp_path / "hist"))

    import jojo_lint.registry as reg
    monkeypatch.setattr(reg, "run_nightly", lambda wiki: (_ for _ in ()).throw(RuntimeError("boom")))

    from fastapi.testclient import TestClient

    from backend.main import app

    c = TestClient(app)
    r = c.post("/api/ops/lint/nightly")
    assert r.status_code == 500
    assert "boom" in r.json()["detail"]


def test_lint_history_days_query_bounds(client):
    """GET /api/ops/lint/history?days=0 returns 422 (below ge=1 constraint)."""
    r = client.get("/api/ops/lint/history?days=0")
    assert r.status_code == 422
