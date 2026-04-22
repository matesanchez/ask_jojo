"""Smoke test for jojo_lint."""

from __future__ import annotations

import jojo_lint
from jojo_lint import cli


def test_version_defined() -> None:
    assert jojo_lint.__version__ == "0.1.0"


def test_cli_stub_returns_nonzero() -> None:
    assert cli.main([]) == 1
