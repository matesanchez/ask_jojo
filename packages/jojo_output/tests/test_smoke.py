"""Smoke test for jojo_output."""

from __future__ import annotations

import jojo_output
from jojo_output import cli


def test_version_defined() -> None:
    assert jojo_output.__version__ == "0.1.0"


def test_cli_stub_returns_nonzero() -> None:
    assert cli.main([]) == 1
