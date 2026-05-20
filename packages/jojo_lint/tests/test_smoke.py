"""Smoke tests for jojo_lint."""

from __future__ import annotations

import jojo_lint
from jojo_lint.checks.base import CheckResult


def test_version_defined() -> None:
    assert jojo_lint.__version__ == "0.1.0"


def test_run_check_returns_check_result(tmp_path) -> None:
    """run_check("schema", ...) returns a CheckResult even on an empty wiki."""
    # Provide an empty wiki root — schema check should return pass with no findings.
    result = jojo_lint.run_check("schema", tmp_path)
    assert isinstance(result, CheckResult)
    assert result.check_name == "schema"
    assert result.status in ("pass", "warn", "fail", "api_key_required")
    assert isinstance(result.findings, list)
    assert isinstance(result.run_at, str)
