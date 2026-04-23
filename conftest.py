"""Top-level pytest conftest.

Redirects ``jojo_core.config`` to a throwaway file for the whole session so
tests can never accidentally read or write the operator's real
``%APPDATA%\\JojoBot\\config.json``. Also forces plaintext mode so DPAPI
calls are never made during the test run (tests that specifically exercise
the DPAPI code path monkey-patch the primitives themselves).

This is a safety net, not the primary mechanism: individual test modules
can still override the path via their own fixtures.
"""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True, scope="session")
def _isolate_jojo_config(tmp_path_factory: pytest.TempPathFactory):
    """Point jojo_core.config at a session-local tmp file."""
    try:
        from jojo_core import config
    except ImportError:
        # jojo_core isn't on sys.path in every test context (e.g. if we ever
        # run just src/backend tests against an uninstalled package).
        yield
        return
    tmp_root = tmp_path_factory.mktemp("jojo_config")
    config.set_config_path_for_tests(tmp_root / "config.json")
    import os
    os.environ["JOJO_CONFIG_FORCE_PLAINTEXT"] = "1"
    yield
    config.set_config_path_for_tests(None)
