"""Unit tests for the thread-based watchdog helper.

These are deliberately short-timeout tests so the suite stays fast.
"""

from __future__ import annotations

import time

import pytest

from jojo_ingest._watchdog import WatchdogTimeout, run_with_timeout


def test_run_with_timeout_returns_result():
    assert run_with_timeout(lambda: 42, timeout_s=1.0) == 42


def test_run_with_timeout_propagates_exceptions():
    def boom():
        raise RuntimeError("kaboom")

    with pytest.raises(RuntimeError, match="kaboom"):
        run_with_timeout(boom, timeout_s=1.0)


def test_run_with_timeout_raises_on_deadline():
    def slow():
        time.sleep(0.5)
        return "too late"

    with pytest.raises(WatchdogTimeout) as exc:
        run_with_timeout(slow, timeout_s=0.05, label="slow-call")
    assert "slow-call" in str(exc.value)


def test_run_with_timeout_is_timeout_error_subclass():
    # Callers that only care about "some timeout happened" should be
    # able to catch TimeoutError and still match.
    def slow():
        time.sleep(0.2)

    with pytest.raises(TimeoutError):
        run_with_timeout(slow, timeout_s=0.01)


def test_run_with_timeout_rejects_nonpositive_timeout():
    with pytest.raises(ValueError):
        run_with_timeout(lambda: None, timeout_s=0)


def test_run_with_timeout_passes_args_and_kwargs():
    assert run_with_timeout(lambda a, b, *, c: a + b + c, 1, 2, timeout_s=1.0, c=3) == 6
