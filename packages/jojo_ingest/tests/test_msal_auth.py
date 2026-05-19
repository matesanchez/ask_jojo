"""Fully-mocked unit tests for msal_device_code_provider.

No real MSAL, no real DPAPI, no network calls. Uses monkeypatch to:
  - Set JOJO_CONFIG_FORCE_PLAINTEXT=1 so the code skips DPAPI on Windows.
  - Mock msal.PublicClientApplication so no Microsoft network traffic occurs.
  - Optionally mock msal.SerializableTokenCache when the cache interaction
    needs explicit control.

All five tests pass on Linux CI (where DPAPI is not available) because
JOJO_CONFIG_FORCE_PLAINTEXT bypasses the ctypes/crypt32 path entirely.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from jojo_connectors_common import IngestError

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _make_mock_app(
    *,
    accounts: list | None = None,
    silent_result: dict | None = None,
    flow: dict | None = None,
    device_result: dict | None = None,
) -> MagicMock:
    """Return a MagicMock shaped like msal.PublicClientApplication."""
    app = MagicMock()
    app.get_accounts.return_value = accounts if accounts is not None else []
    app.acquire_token_silent.return_value = silent_result
    app.initiate_device_flow.return_value = flow or {"message": "Go to https://microsoft.com/link"}
    app.acquire_token_by_device_flow.return_value = device_result or {"access_token": "device-token"}
    return app


# ---------------------------------------------------------------------------
# test 1: cached token is returned without device-code flow
# ---------------------------------------------------------------------------


def test_msal_device_code_provider_returns_cached_token(monkeypatch, tmp_path):
    """When get_accounts() returns an account and acquire_token_silent succeeds,
    the provider returns the cached access token without starting a device flow."""
    monkeypatch.setenv("JOJO_CONFIG_FORCE_PLAINTEXT", "1")

    fake_account = {"username": "user@nurixtx.com"}
    mock_app = _make_mock_app(
        accounts=[fake_account],
        silent_result={"access_token": "cached-token-abc"},
    )

    with patch("msal.PublicClientApplication", return_value=mock_app), \
         patch("msal.SerializableTokenCache") as mock_cache_cls:
        mock_cache = MagicMock()
        mock_cache.has_state_changed = False
        mock_cache_cls.return_value = mock_cache

        from jojo_ingest.graph import msal_device_code_provider

        provider = msal_device_code_provider(cache_path=tmp_path / "cache.bin", interactive=True)
        token = provider()

    assert token == "cached-token-abc"
    mock_app.get_accounts.assert_called_once()
    mock_app.acquire_token_silent.assert_called_once()
    # No device flow should have been initiated
    mock_app.initiate_device_flow.assert_not_called()


# ---------------------------------------------------------------------------
# test 2: device-code flow starts when no cached token exists
# ---------------------------------------------------------------------------


def test_msal_device_code_provider_starts_device_flow_when_no_cache(monkeypatch, tmp_path):
    """When there are no accounts in cache, the provider initiates device-code
    flow and returns the resulting access token."""
    monkeypatch.setenv("JOJO_CONFIG_FORCE_PLAINTEXT", "1")

    mock_app = _make_mock_app(
        accounts=[],
        silent_result=None,
        flow={"message": "Open https://microsoft.com/link and enter code ABCD-1234"},
        device_result={"access_token": "fresh-device-token"},
    )

    with patch("msal.PublicClientApplication", return_value=mock_app), \
         patch("msal.SerializableTokenCache") as mock_cache_cls:
        mock_cache = MagicMock()
        mock_cache.has_state_changed = True
        mock_cache.serialize.return_value = "{}"
        mock_cache_cls.return_value = mock_cache

        from jojo_ingest.graph import msal_device_code_provider

        provider = msal_device_code_provider(cache_path=tmp_path / "cache.bin", interactive=True)
        token = provider()

    assert token == "fresh-device-token"
    mock_app.initiate_device_flow.assert_called_once()
    mock_app.acquire_token_by_device_flow.assert_called_once()


# ---------------------------------------------------------------------------
# test 3: non-interactive mode raises IngestError when no cached token
# ---------------------------------------------------------------------------


def test_msal_device_code_provider_raises_non_interactive_no_cache(monkeypatch, tmp_path):
    """When interactive=False and no cached token exists, IngestError is raised
    rather than starting an interactive device-code flow."""
    monkeypatch.setenv("JOJO_CONFIG_FORCE_PLAINTEXT", "1")

    mock_app = _make_mock_app(accounts=[], silent_result=None)

    with patch("msal.PublicClientApplication", return_value=mock_app), \
         patch("msal.SerializableTokenCache") as mock_cache_cls:
        mock_cache = MagicMock()
        mock_cache.has_state_changed = False
        mock_cache_cls.return_value = mock_cache

        from jojo_ingest.graph import msal_device_code_provider

        provider = msal_device_code_provider(cache_path=tmp_path / "cache.bin", interactive=False)
        with pytest.raises(IngestError) as exc_info:
            provider()

    assert "interactive=False" in str(exc_info.value)
    mock_app.initiate_device_flow.assert_not_called()


# ---------------------------------------------------------------------------
# test 4: cache file is written after successful device-code flow
# ---------------------------------------------------------------------------


def test_msal_device_code_provider_saves_cache_on_success(monkeypatch, tmp_path):
    """After a successful device-code login, the token cache is written to the
    specified cache_path (plaintext mode, since JOJO_CONFIG_FORCE_PLAINTEXT=1)."""
    monkeypatch.setenv("JOJO_CONFIG_FORCE_PLAINTEXT", "1")

    mock_app = _make_mock_app(
        accounts=[],
        flow={"message": "Use device code"},
        device_result={"access_token": "new-token"},
    )

    cache_file = tmp_path / "tokencache.bin"
    assert not cache_file.exists()

    with patch("msal.PublicClientApplication", return_value=mock_app), \
         patch("msal.SerializableTokenCache") as mock_cache_cls:
        mock_cache = MagicMock()
        # has_state_changed=True triggers the save path
        mock_cache.has_state_changed = True
        mock_cache.serialize.return_value = '{"AccessToken": {}}'
        mock_cache_cls.return_value = mock_cache

        from jojo_ingest.graph import msal_device_code_provider

        provider = msal_device_code_provider(cache_path=cache_file, interactive=True)
        token = provider()

    assert token == "new-token"
    # The cache file should have been written
    assert cache_file.exists()
    written = cache_file.read_text(encoding="utf-8")
    assert "AccessToken" in written


# ---------------------------------------------------------------------------
# test 5: existing cache is loaded and used for silent token acquisition
# ---------------------------------------------------------------------------


def test_msal_device_code_provider_loads_existing_cache(monkeypatch, tmp_path):
    """If a cache file already exists, the provider deserializes it and passes
    it to the MSAL app so acquire_token_silent can use it."""
    monkeypatch.setenv("JOJO_CONFIG_FORCE_PLAINTEXT", "1")

    cache_file = tmp_path / "tokencache.bin"
    # Write a minimal (empty) MSAL cache so the file exists
    cache_file.write_bytes(b"{}")

    fake_account = {"username": "cached@nurixtx.com"}
    mock_app = _make_mock_app(
        accounts=[fake_account],
        silent_result={"access_token": "loaded-from-cache"},
    )

    with patch("msal.PublicClientApplication", return_value=mock_app), \
         patch("msal.SerializableTokenCache") as mock_cache_cls:
        mock_cache = MagicMock()
        mock_cache.has_state_changed = False
        mock_cache_cls.return_value = mock_cache

        from jojo_ingest.graph import msal_device_code_provider

        provider = msal_device_code_provider(cache_path=cache_file, interactive=True)
        token = provider()

    assert token == "loaded-from-cache"
    # Verify the cache was deserialized (deserialize called with the file contents)
    mock_cache.deserialize.assert_called_once_with("{}")
    mock_app.acquire_token_silent.assert_called_once()
