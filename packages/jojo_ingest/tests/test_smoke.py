"""Smoke test for jojo_ingest."""

from __future__ import annotations

import pytest

import jojo_ingest
from jojo_ingest import cli


def test_version_defined() -> None:
    assert jojo_ingest.__version__ == "0.1.0"


def test_cli_without_command_errors() -> None:
    # argparse exits with SystemExit(2) on missing required subcommand.
    with pytest.raises(SystemExit):
        cli.main([])


def test_cli_status_on_empty_raw(tmp_path, capsys) -> None:
    import json

    rc = cli.main(["status", "--raw", str(tmp_path)])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["total_entries"] == 0
    assert out["by_source"] == {}
