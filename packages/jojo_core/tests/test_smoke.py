"""Smoke test for jojo_core package + CLI.

Covers the trivial surface area (version, parser wiring). Deeper CLI
behavior is exercised in ``test_cli.py``.
"""

from __future__ import annotations

import pytest

import jojo_core
from jojo_core import cli


def test_version_defined() -> None:
    assert jojo_core.__version__ == "0.1.0"


def test_cli_no_args_prints_help_and_exits_nonzero(
    capsys: pytest.CaptureFixture[str],
) -> None:
    # argparse exits with SystemExit(2) when a required subcommand is omitted.
    with pytest.raises(SystemExit) as exc:
        cli.main([])
    assert exc.value.code == 2


def test_cli_version_subcommand(capsys: pytest.CaptureFixture[str]) -> None:
    rc = cli.main(["version"])
    out = capsys.readouterr().out.strip()
    assert rc == 0
    assert out == jojo_core.__version__
