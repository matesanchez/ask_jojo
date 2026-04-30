"""Smoke tests for the FastAPI skeleton.

Health + any still-stubbed endpoint. Ingest endpoints that *do* work now
get their own suite in `test_ingest_endpoints.py` so this file stays focused
on what's intentionally 501 until its owning phase lands.

Phase 3 update: wiki and ops endpoints are now implemented — removed from
this 501 list. Lint (Phase 6) and viz (Phase 3) remain as stubs.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_health_returns_200() -> None:
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["version"] == "0.1.0"
    assert body["phase"] == "0"


@pytest.mark.parametrize(
    "method,path",
    [
        # Viz lands in a later phase.
        ("post", "/api/viz/marp"),
        ("post", "/api/viz/plot"),
        # Lint triggers land in Phase 6.
        ("post", "/api/ops/lint/nightly"),
        # Scheduler integration deferred to local-mode packaging pass.
        ("get",  "/api/ingest/schedule"),
        # Wiki write-back stub tested with path param in test_wiki_endpoints.py.
    ],
)
def test_pending_endpoints_return_501(method: str, path: str) -> None:
    r = getattr(client, method)(path)
    assert r.status_code == 501, f"{method.upper()} {path} returned {r.status_code}"
    detail = r.json().get("detail", "")
    # Every stub message must point the caller at the owning phase or next pass.
    assert (
        "Phase" in detail or "packaging pass" in detail or "pass" in detail.lower()
    ), f"{method.upper()} {path} missing phase hint: {detail!r}"
