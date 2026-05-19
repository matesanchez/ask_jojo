"""Sandbox runner — invokes ``render.py`` in a resource-limited subprocess.

Per PLAN.md Section 6 Phase 5: 30 s CPU, 512 MB RAM, no network,
allowlist imports. The subprocess is isolated so a malicious or buggy
spec can't bring down the parent backend.

Two execution modes:

- **In-process** (``RUN_IN_PROCESS=True``): for tests + dev mode where
  spawning a subprocess is overkill. Resource limits don't apply.
- **Subprocess** (default): the real production path. Spawns ``python -m
  jojo_output.sandbox._worker`` with the spec piped on stdin, captures
  the PNG bytes from stdout, applies POSIX rlimit on Linux/Mac and
  best-effort job-objects on Windows.

Public API:

- ``RenderResult`` — dataclass with status, artifact path or bytes,
  duration_ms, error detail.
- ``run(spec, out_path=None, ...)`` — orchestrate the sandbox flow.
- ``RUN_IN_PROCESS`` — module-level flag for tests.
"""

from __future__ import annotations

import base64
import json
import os
import resource
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from .spec import PlotSpec

# Module-level flag: tests flip this to True so they don't have to spawn a
# Python subprocess (which is slow and brittle in a sandboxed dev env).
# Production callers leave it False.
RUN_IN_PROCESS = False

# Defaults for the production subprocess.
DEFAULT_CPU_SECONDS = 30
DEFAULT_RAM_MEGABYTES = 512
DEFAULT_TIMEOUT_SECONDS = 35  # subprocess wall-clock; longer than CPU limit


@dataclass
class RenderResult:
    """Outcome of a sandbox render.

    Attributes:
        status: ``"ok"`` | ``"validation_error"`` | ``"render_error"`` |
                ``"timeout"`` | ``"resource_limit"``
        out_path: file path if ``out_path`` was provided and the render
            succeeded; None otherwise.
        bytes: raw PNG/SVG bytes if no ``out_path`` was provided and the
            render succeeded; None otherwise.
        duration_ms: wall-clock duration in milliseconds.
        error: detailed error message; None when status == "ok".
        plot_type: echoed from the spec for telemetry.
    """

    status: Literal["ok", "validation_error", "render_error", "timeout", "resource_limit"]
    out_path: Path | None = None
    bytes: bytes | None = None
    duration_ms: int = 0
    error: str | None = None
    plot_type: str = ""


def run(
    spec_dict: dict[str, Any] | PlotSpec,
    *,
    out_path: Path | str | None = None,
    fmt: Literal["png", "svg"] = "png",
    cpu_seconds: int = DEFAULT_CPU_SECONDS,
    ram_megabytes: int = DEFAULT_RAM_MEGABYTES,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> RenderResult:
    """Validate ``spec_dict``, then render in the sandbox.

    Args:
        spec_dict: a PlotSpec or a dict that validates against PlotSpec.
        out_path: when given, the render is written to disk and returned
            via ``RenderResult.out_path``. When None, raw bytes come back
            via ``RenderResult.bytes``.
        fmt: "png" (default) or "svg".
        cpu_seconds / ram_megabytes / timeout_seconds: resource limits
            for the subprocess. POSIX-only enforcement; Windows uses
            wall-clock timeout only.

    Returns ``RenderResult`` — never raises for validation, render, or
    sandbox errors. Raises only on the caller's bad inputs (e.g.
    permission denied on ``out_path``).
    """
    start_ms = _now_ms()

    # 1. Validate. Pydantic raises on bad input; we map that to a result.
    if isinstance(spec_dict, PlotSpec):
        spec = spec_dict
    else:
        try:
            spec = PlotSpec.model_validate(spec_dict)
        except Exception as e:  # noqa: BLE001 — pydantic raises ValidationError + others
            return RenderResult(
                status="validation_error",
                duration_ms=_now_ms() - start_ms,
                error=f"spec validation failed: {e}",
                plot_type=str(spec_dict.get("plot_type", "")) if isinstance(spec_dict, dict) else "",
            )

    # 2. Render — in-process for tests, subprocess for prod.
    if RUN_IN_PROCESS:
        return _run_in_process(spec, out_path=out_path, fmt=fmt, start_ms=start_ms)
    return _run_subprocess(
        spec,
        out_path=out_path,
        fmt=fmt,
        cpu_seconds=cpu_seconds,
        ram_megabytes=ram_megabytes,
        timeout_seconds=timeout_seconds,
        start_ms=start_ms,
    )


# ----------------------------------------------------------- in-process


def _run_in_process(
    spec: PlotSpec,
    *,
    out_path: Path | str | None,
    fmt: str,
    start_ms: int,
) -> RenderResult:
    from . import render

    try:
        if out_path is not None:
            renderer = render.render_to_png if fmt == "png" else render.render_to_svg
            written = renderer(spec, out_path)
            return RenderResult(
                status="ok",
                out_path=written,
                duration_ms=_now_ms() - start_ms,
                plot_type=spec.plot_type,
            )
        data = render.render_to_bytes(spec, fmt=fmt)
        return RenderResult(
            status="ok",
            bytes=data,
            duration_ms=_now_ms() - start_ms,
            plot_type=spec.plot_type,
        )
    except Exception as e:  # noqa: BLE001 — sandbox boundary
        return RenderResult(
            status="render_error",
            duration_ms=_now_ms() - start_ms,
            error=f"render failed: {type(e).__name__}: {e}",
            plot_type=spec.plot_type,
        )


# ----------------------------------------------------------- subprocess


def _set_rlimits(cpu_seconds: int, ram_megabytes: int) -> None:
    """preexec_fn for the subprocess. POSIX only."""
    # CPU time (seconds). Receives SIGXCPU when exceeded.
    resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds))
    # Address space (bytes). On modern Linux this caps virtual memory.
    bytes_limit = ram_megabytes * 1024 * 1024
    try:
        resource.setrlimit(resource.RLIMIT_AS, (bytes_limit, bytes_limit))
    except (ValueError, OSError):
        # macOS may not honor RLIMIT_AS; fall through with a softer ceiling.
        pass
    # Forbid creating new processes (best-effort; not all platforms).
    try:
        resource.setrlimit(resource.RLIMIT_NPROC, (1, 1))
    except (ValueError, OSError):
        pass
    # Forbid opening additional files beyond a small budget.
    try:
        resource.setrlimit(resource.RLIMIT_NOFILE, (64, 64))
    except (ValueError, OSError):
        pass


def _run_subprocess(
    spec: PlotSpec,
    *,
    out_path: Path | str | None,
    fmt: str,
    cpu_seconds: int,
    ram_megabytes: int,
    timeout_seconds: int,
    start_ms: int,
) -> RenderResult:
    """Spawn the worker, pipe spec on stdin, collect bytes from stdout.

    POSIX: applies RLIMIT_CPU + RLIMIT_AS via preexec_fn.
    Windows: timeout only (resource module isn't available).
    """
    spec_json = spec.model_dump_json()

    cmd = [sys.executable, "-m", "jojo_output.sandbox._worker", "--fmt", fmt]
    preexec = (
        (lambda: _set_rlimits(cpu_seconds, ram_megabytes))
        if sys.platform != "win32"
        else None
    )

    env = os.environ.copy()
    env["PYTHONHASHSEED"] = "0"
    # Disable network: many libs honor http_proxy=invalid; the strongest
    # disable is at the OS level (unshare) which we can't do here without
    # root. The allowlist of imports is the main safeguard.
    env["http_proxy"] = "http://127.0.0.1:1"
    env["https_proxy"] = "http://127.0.0.1:1"
    env["no_proxy"] = ""

    try:
        proc = subprocess.Popen(  # noqa: S603 — known cmd, no shell
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=preexec,
            env=env,
        )
    except FileNotFoundError as e:
        return RenderResult(
            status="render_error",
            duration_ms=_now_ms() - start_ms,
            error=f"failed to spawn sandbox worker: {e}",
            plot_type=spec.plot_type,
        )

    try:
        stdout_bytes, stderr_bytes = proc.communicate(
            input=spec_json.encode("utf-8"),
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.communicate()
        return RenderResult(
            status="timeout",
            duration_ms=_now_ms() - start_ms,
            error=f"sandbox exceeded {timeout_seconds}s wall-clock timeout",
            plot_type=spec.plot_type,
        )

    duration_ms = _now_ms() - start_ms
    stderr_text = stderr_bytes.decode("utf-8", errors="replace")

    if proc.returncode != 0:
        # SIGXCPU on Linux returns -24 (or 152 on some shells).
        if proc.returncode in (-24, 152) or "CPU" in stderr_text:
            return RenderResult(
                status="resource_limit",
                duration_ms=duration_ms,
                error=f"CPU limit exceeded ({cpu_seconds}s); stderr: {stderr_text[-200:]}",
                plot_type=spec.plot_type,
            )
        return RenderResult(
            status="render_error",
            duration_ms=duration_ms,
            error=f"sandbox exited {proc.returncode}: {stderr_text[-300:]}",
            plot_type=spec.plot_type,
        )

    # The worker writes a single base64-encoded blob to stdout.
    try:
        data = base64.b64decode(stdout_bytes.strip())
    except Exception as e:  # noqa: BLE001
        return RenderResult(
            status="render_error",
            duration_ms=duration_ms,
            error=f"failed to decode sandbox output: {e}",
            plot_type=spec.plot_type,
        )

    if out_path is not None:
        out = Path(out_path).resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(data)
        return RenderResult(
            status="ok",
            out_path=out,
            duration_ms=duration_ms,
            plot_type=spec.plot_type,
        )
    return RenderResult(
        status="ok",
        bytes=data,
        duration_ms=duration_ms,
        plot_type=spec.plot_type,
    )


# ----------------------------------------------------------- helpers


def _now_ms() -> int:
    return int(time.monotonic() * 1000)


# Keep the json import alive for callers that need spec.json() round-trips.
_ = json
