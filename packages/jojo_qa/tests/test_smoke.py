"""Smoke test for jojo_qa."""

from __future__ import annotations

import jojo_qa
from jojo_qa import cli


def test_version_defined() -> None:
    assert jojo_qa.__version__ == "0.1.0"


def test_cli_stub_returns_nonzero() -> None:
    assert cli.main([]) == 1
