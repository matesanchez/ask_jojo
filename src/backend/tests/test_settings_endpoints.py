"""Tests for /api/settings endpoints.

All tests use a tmp config file so they never touch %APPDATA%\\JojoBot\\config.json.
Anthropic calls are mocked to avoid real HTTP.
"""

from __future__ import annotations

import types
import unittest.mock as mock
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

# ----------------------------------------------------------------- fixtures


@pytest.fixture(autouse=True)
def _force_plaintext(monkeypatch: pytest.MonkeyPatch) -> None:
    """Disable DPAPI for all tests in this module."""
    monkeypatch.setenv("JOJO_CONFIG_FORCE_PLAINTEXT", "1")


@pytest.fixture()
def config_tmpfile(tmp_path: Path) -> Any:
    """Redirect all config I/O to a temporary file and clean up afterward."""
    from jojo_core import config

    cfg = tmp_path / "config.json"
    config.set_config_path_for_tests(cfg)
    yield cfg
    config.set_config_path_for_tests(None)


@pytest.fixture()
def client(config_tmpfile: Path) -> TestClient:
    """TestClient with a fresh config file for each test."""
    from backend.main import app

    return TestClient(app)


# ----------------------------------------------------------------- Section 1: API key


def test_get_anthropic_key_unconfigured(client: TestClient) -> None:
    r = client.get("/api/settings/anthropic-key")
    assert r.status_code == 200
    body = r.json()
    assert body["configured"] is False
    assert body["masked"] is None


def test_post_anthropic_key_stores_and_masks(client: TestClient) -> None:
    r = client.post(
        "/api/settings/anthropic-key",
        json={"key": "sk-ant-api03-ABCDEFGHIJKLMNOPQRSTUVWX"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["masked"].endswith("VWXY") or body["masked"].endswith("UVWX")
    # Last 4 chars of the test key.
    assert "UVWX" in body["masked"] or body["masked"].endswith(
        "sk-ant-api03-ABCDEFGHIJKLMNOPQRSTUVWX"[-4:]
    )


def test_get_anthropic_key_after_save(client: TestClient) -> None:
    key = "sk-ant-api03-TESTKEY1234"
    client.post("/api/settings/anthropic-key", json={"key": key})
    r = client.get("/api/settings/anthropic-key")
    assert r.status_code == 200
    body = r.json()
    assert body["configured"] is True
    assert body["masked"] is not None
    assert key not in body["masked"]  # never expose full key


def test_post_anthropic_key_empty_rejected(client: TestClient) -> None:
    r = client.post("/api/settings/anthropic-key", json={"key": ""})
    assert r.status_code == 400


def test_test_anthropic_no_key_returns_error(client: TestClient) -> None:
    r = client.post("/api/settings/test-anthropic", json={})
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is False
    assert "error" in body


def test_test_anthropic_mocked_success(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    fake_content = types.SimpleNamespace(text="pong")
    fake_resp = types.SimpleNamespace(content=[fake_content])
    fake_messages = mock.MagicMock()
    fake_messages.create.return_value = fake_resp
    fake_client_instance = types.SimpleNamespace(messages=fake_messages)
    FakeAnthropic = mock.MagicMock(return_value=fake_client_instance)

    with mock.patch("anthropic.Anthropic", FakeAnthropic):
        r = client.post(
            "/api/settings/test-anthropic",
            json={"key": "sk-ant-fake-test-key"},
        )

    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["model"] == "claude-sonnet-4-6"
    assert "latency_ms" in body


def test_test_anthropic_auth_error(client: TestClient) -> None:
    import anthropic

    FakeAnthropic = mock.MagicMock()
    FakeAnthropic.return_value.messages.create.side_effect = anthropic.AuthenticationError(
        message="Invalid API key",
        response=mock.MagicMock(status_code=401),
        body={"error": {"type": "authentication_error", "message": "Invalid API key"}},
    )

    with mock.patch("anthropic.Anthropic", FakeAnthropic):
        r = client.post(
            "/api/settings/test-anthropic",
            json={"key": "sk-ant-invalid"},
        )

    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is False
    assert "error" in body


# ----------------------------------------------------------------- Section 2: Models


def test_get_models_returns_defaults(client: TestClient) -> None:
    r = client.get("/api/settings/models")
    assert r.status_code == 200
    body = r.json()
    assert body["default_tier"] == "sonnet"
    assert "per_task" in body
    assert body["per_task"]["synthesis"] == "sonnet"
    assert body["per_task"]["weekly-contradiction"] == "opus"
    assert body["per_task"]["format-classify"] == "haiku"


def test_post_models_updates_default_tier(client: TestClient) -> None:
    r = client.post("/api/settings/models", json={"default_tier": "opus"})
    assert r.status_code == 200
    assert r.json()["ok"] is True

    r2 = client.get("/api/settings/models")
    assert r2.json()["default_tier"] == "opus"


def test_post_models_updates_per_task(client: TestClient) -> None:
    r = client.post(
        "/api/settings/models",
        json={"per_task": {"synthesis": "haiku", "nightly-lint": "haiku"}},
    )
    assert r.status_code == 200
    r2 = client.get("/api/settings/models")
    assert r2.json()["per_task"]["synthesis"] == "haiku"


# ----------------------------------------------------------------- Section 4: Connectors


def test_get_connectors_fresh_install(client: TestClient) -> None:
    r = client.get("/api/settings/connectors")
    assert r.status_code == 200
    body = r.json()
    assert "onedrive_path" in body
    assert "public_drive_path" in body
    assert "sharepoint_sites" in body
    # Fresh install: all None.
    assert body["onedrive_path"] is None
    assert body["public_drive_path"] is None


def test_post_connectors_saves_paths(client: TestClient, tmp_path: Path) -> None:
    onedrive = str(tmp_path / "OneDrive")
    r = client.post(
        "/api/settings/connectors",
        json={"onedrive_path": onedrive, "public_drive_path": "P:\\"},
    )
    assert r.status_code == 200
    assert r.json()["ok"] is True

    r2 = client.get("/api/settings/connectors")
    body = r2.json()
    assert body["onedrive_path"] == onedrive
    assert body["public_drive_path"] == "P:\\"


# ----------------------------------------------------------------- Section 5: Lint


def test_get_lint_returns_defaults(client: TestClient) -> None:
    r = client.get("/api/settings/lint")
    assert r.status_code == 200
    body = r.json()
    assert body["nightly_time"] == "02:00"
    assert body["weekly_day"] == "Sunday"
    assert body["weekly_time"] == "04:00"
    assert body["nightly_enabled"] is True
    assert body["weekly_enabled"] is True


def test_post_lint_updates_cadence(client: TestClient) -> None:
    r = client.post(
        "/api/settings/lint",
        json={"nightly_time": "03:00", "weekly_day": "Saturday", "weekly_time": "05:00"},
    )
    assert r.status_code == 200
    assert r.json()["ok"] is True

    r2 = client.get("/api/settings/lint")
    body = r2.json()
    assert body["nightly_time"] == "03:00"
    assert body["weekly_day"] == "Saturday"
    assert body["weekly_time"] == "05:00"


def test_post_lint_disables_nightly(client: TestClient) -> None:
    r = client.post("/api/settings/lint", json={"nightly_enabled": False})
    assert r.status_code == 200
    r2 = client.get("/api/settings/lint")
    assert r2.json()["nightly_enabled"] is False


# ----------------------------------------------------------------- Status sidebar


def test_get_status_shape(client: TestClient) -> None:
    r = client.get("/api/settings/status")
    assert r.status_code == 200
    body = r.json()
    for section in ("api_key", "models", "graph", "connectors", "lint"):
        assert section in body
        assert "ok" in body[section]
        assert "detail" in body[section]


def test_get_status_api_key_false_when_unconfigured(client: TestClient) -> None:
    r = client.get("/api/settings/status")
    body = r.json()
    assert body["api_key"]["ok"] is False


def test_get_status_api_key_true_after_save(client: TestClient) -> None:
    client.post("/api/settings/anthropic-key", json={"key": "sk-ant-fake-key-for-status"})
    r = client.get("/api/settings/status")
    body = r.json()
    assert body["api_key"]["ok"] is True


def test_get_status_models_always_ok(client: TestClient) -> None:
    r = client.get("/api/settings/status")
    body = r.json()
    assert body["models"]["ok"] is True


def test_get_status_lint_always_ok(client: TestClient) -> None:
    r = client.get("/api/settings/status")
    body = r.json()
    assert body["lint"]["ok"] is True
    assert "nightly" in body["lint"]["detail"]
