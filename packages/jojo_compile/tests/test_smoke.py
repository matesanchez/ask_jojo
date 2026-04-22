"""Smoke test for jojo_compile."""

from __future__ import annotations

import jojo_compile
from jojo_compile import cli


def test_version_defined() -> None:
    assert jojo_compile.__version__ == "0.1.0"


def test_cli_stub_returns_nonzero() -> None:
    assert cli.main([]) == 1
