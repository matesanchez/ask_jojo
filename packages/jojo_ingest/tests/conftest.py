"""Test isolation fixtures for jojo_ingest tests.

Redirects all jojo_core.config I/O to a per-test temp file so tests that
call config.get() for JOJO_ONEDRIVE_PATH, JOJO_GRAPH_ACCESS_TOKEN, etc. are
not affected by values in the developer's real %APPDATA%\\JojoBot\\config.json.
"""

from __future__ import annotations

import pytest

from jojo_core import config


@pytest.fixture(autouse=True)
def _isolated_config(tmp_path, monkeypatch):
    monkeypatch.setenv("JOJO_CONFIG_FORCE_PLAINTEXT", "1")
    config.set_config_path_for_tests(tmp_path / "config.json")
    yield
    config.set_config_path_for_tests(None)
