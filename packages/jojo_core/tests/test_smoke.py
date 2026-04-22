"""Smoke test for jojo_core. Keeps pytest green on the empty package.

Replaced with real tests as jojo_core gains implementation.
"""

from __future__ import annotations

import jojo_core
from jojo_core import cli


def test_version_defined() -> None:
    assert jojo_core.__version__ == "0.1.0"


def test_cli_stub_returns_nonzero() -> None:
    # Phase 0 stub must return a non-zero exit code so that anything
    # that accidentally depends on a real implementation fails loudly.
    assert cli.main([]) == 1
