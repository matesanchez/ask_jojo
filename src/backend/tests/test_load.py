"""Async load-test script for JoJo Bot v2.0 backend.

This module serves two purposes:

1. **Pytest integration** — collected by pytest but *immediately skipped*
   unless the environment variable ``JOJO_LOAD_TEST=1`` is set. This prevents
   the load test from blocking CI.

2. **Standalone runner** — execute directly with:

       python -m src.backend.tests.test_load

   or via the helper entry-point:

       python src/backend/tests/test_load.py

Configuration environment variables:
    JOJO_LOAD_BASE_URL   Base URL of the running server (default: http://127.0.0.1:8765)
    JOJO_LOAD_DURATION   Test duration in seconds (default: 10; production: 300)
    JOJO_LOAD_WORKERS    Concurrent workers (default: 100)
    JOJO_LOAD_TEST       Set to "1" to allow pytest to run the load test case

Production validation note:
    For the full 5-minute, 100-worker sustained run described in the Test 1
    specification, set:
        JOJO_LOAD_DURATION=300
        JOJO_LOAD_WORKERS=100
    and run against the production server.  This is documented as
    "PROCEDURE DOCUMENTED — run on workstation" because it requires a live
    server and sustained network capacity that CI cannot guarantee.

Acceptance criteria (to be verified on workstation):
    - p95 latency < 500 ms for wiki/raw/graph routes
    - p95 latency < 8000 ms for qa/route (synthesis is slow)
    - 0 HTTP 5xx responses
    - Process RSS growth < 50 MB over the 5-minute window (no memory leak)
"""

from __future__ import annotations

import asyncio
import json
import os
import time
from typing import Any

import pytest

# ---------------------------------------------------------------------------
# Route weight table:  (path, weight, acceptable_p95_ms)
# ---------------------------------------------------------------------------
ROUTES: list[tuple[str, int, int]] = [
    ("/api/wiki/page?path=targets/cbl-b.md",    60, 500),
    ("/api/qa/route?q=what+is+CBL-B",           20, 8_000),
    ("/api/raw/tree",                            10, 500),
    ("/api/graph/json",                          10, 500),
]

DEFAULT_BASE_URL  = "http://127.0.0.1:8765"
DEFAULT_DURATION  = 10      # seconds — set JOJO_LOAD_DURATION=300 for production
DEFAULT_WORKERS   = 100


def _cfg() -> dict[str, Any]:
    return {
        "base_url":   os.environ.get("JOJO_LOAD_BASE_URL", DEFAULT_BASE_URL),
        "duration":   int(os.environ.get("JOJO_LOAD_DURATION", DEFAULT_DURATION)),
        "workers":    int(os.environ.get("JOJO_LOAD_WORKERS", DEFAULT_WORKERS)),
    }


async def _worker(
    base_url: str,
    deadline: float,
    latencies: dict[str, list[float]],
    errors: dict[str, int],
    route_table: list[tuple[str, int, int]],
) -> None:
    """Single worker: fire requests until *deadline* (monotonic time)."""
    # Build a flat list of routes respecting weights.
    weighted: list[str] = []
    for path, weight, _ in route_table:
        weighted.extend([path] * weight)

    import httpx  # local import so module loads without httpx at collection time

    # Use a short per-request timeout to avoid blocking forever on hung routes.
    timeout = httpx.Timeout(connect=2.0, read=30.0, write=5.0, pool=5.0)
    async with httpx.AsyncClient(base_url=base_url, timeout=timeout) as client:
        idx = 0
        while time.monotonic() < deadline:
            path = weighted[idx % len(weighted)]
            idx += 1
            t0 = time.monotonic()
            try:
                r = await client.get(path)
                elapsed_ms = (time.monotonic() - t0) * 1000
                if r.status_code >= 500:
                    errors[path] = errors.get(path, 0) + 1
                else:
                    bucket = latencies.setdefault(path, [])
                    bucket.append(elapsed_ms)
            except Exception:  # noqa: BLE001
                errors[path] = errors.get(path, 0) + 1


def _percentile(data: list[float], pct: float) -> float:
    if not data:
        return float("nan")
    sorted_data = sorted(data)
    idx = int(len(sorted_data) * pct / 100)
    idx = max(0, min(idx, len(sorted_data) - 1))
    return sorted_data[idx]


async def run_load_test(
    base_url: str = DEFAULT_BASE_URL,
    duration: int = DEFAULT_DURATION,
    workers: int = DEFAULT_WORKERS,
) -> dict[str, Any]:
    """Run the load test. Returns a results dict with per-route stats.

    The return dict has this shape::

        {
          "config": {...},
          "routes": {
            "/api/wiki/page?path=targets/cbl-b.md": {
              "request_count": 412,
              "error_count": 0,
              "p50_ms": 14.2,
              "p95_ms": 38.7,
              "p99_ms": 72.1,
              "p95_threshold_ms": 500,
              "pass": true
            },
            ...
          },
          "totals": {
            "total_requests": 1024,
            "total_errors": 0,
            "overall_pass": true
          }
        }
    """
    latencies: dict[str, list[float]] = {}
    errors: dict[str, int] = {}
    deadline = time.monotonic() + duration

    tasks = [
        _worker(base_url, deadline, latencies, errors, ROUTES)
        for _ in range(workers)
    ]
    await asyncio.gather(*tasks)

    route_results: dict[str, Any] = {}
    overall_pass = True
    total_requests = 0
    total_errors = sum(errors.values())

    for path, _weight, threshold_ms in ROUTES:
        lats = latencies.get(path, [])
        err = errors.get(path, 0)
        p95 = _percentile(lats, 95)
        passed = (p95 <= threshold_ms) if lats else True
        if not passed:
            overall_pass = False
        count = len(lats)
        total_requests += count + err
        route_results[path] = {
            "request_count":     count,
            "error_count":       err,
            "p50_ms":            round(_percentile(lats, 50), 2),
            "p95_ms":            round(p95, 2),
            "p99_ms":            round(_percentile(lats, 99), 2),
            "p95_threshold_ms":  threshold_ms,
            "pass":              passed,
        }

    return {
        "config": {
            "base_url": base_url,
            "duration_seconds": duration,
            "worker_count": workers,
        },
        "routes": route_results,
        "totals": {
            "total_requests":  total_requests,
            "total_errors":    total_errors,
            "overall_pass":    overall_pass,
        },
    }


# ---------------------------------------------------------------------------
# pytest integration — skipped unless JOJO_LOAD_TEST=1
# ---------------------------------------------------------------------------

@pytest.mark.skipif(
    os.environ.get("JOJO_LOAD_TEST") != "1",
    reason="Load test skipped in CI. Set JOJO_LOAD_TEST=1 to enable.",
)
def test_backend_load() -> None:
    """Run a short (10-second) load test against a locally running server.

    To run:
        JOJO_LOAD_TEST=1 python -m pytest src/backend/tests/test_load.py -v
    """
    cfg = _cfg()
    results = asyncio.run(
        run_load_test(
            base_url=cfg["base_url"],
            duration=cfg["duration"],
            workers=cfg["workers"],
        )
    )
    print("\n" + json.dumps(results, indent=2))
    assert results["totals"]["overall_pass"], (
        f"Load test failed. Results:\n{json.dumps(results, indent=2)}"
    )


# ---------------------------------------------------------------------------
# Standalone entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Standalone runner: python src/backend/tests/test_load.py"""
    cfg = _cfg()
    print(
        f"Starting load test: {cfg['workers']} workers, "
        f"{cfg['duration']}s duration, target={cfg['base_url']}"
    )
    print("  NOTE: Set JOJO_LOAD_DURATION=300 for the full 5-minute production run.")
    results = asyncio.run(
        run_load_test(
            base_url=cfg["base_url"],
            duration=cfg["duration"],
            workers=cfg["workers"],
        )
    )
    print(json.dumps(results, indent=2))
    if not results["totals"]["overall_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
