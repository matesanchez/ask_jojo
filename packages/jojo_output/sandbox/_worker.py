"""Sandbox worker — runs inside the resource-limited subprocess.

Reads a PlotSpec JSON from stdin, calls ``render.render_to_bytes``,
writes base64-encoded bytes to stdout. Imports are deliberately the
minimum needed; new dependencies don't slip in via this path.

Invocation::

    python -m jojo_output.sandbox._worker --fmt png

Stdin: PlotSpec JSON.
Stdout: base64-encoded PNG (or SVG).
Stderr: errors only (otherwise silent).

Exit codes:
  0       - success
  64      - bad command-line args
  65      - bad input JSON
  66      - render error
  -24     - CPU limit (SIGXCPU on POSIX)
"""

from __future__ import annotations

import argparse
import base64
import json
import sys


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--fmt", default="png", choices=["png", "svg"])
    args = p.parse_args()

    raw = sys.stdin.buffer.read()
    if not raw:
        print("empty stdin (expected PlotSpec JSON)", file=sys.stderr)
        return 65
    try:
        payload = json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError as e:
        print(f"invalid JSON on stdin: {e}", file=sys.stderr)
        return 65

    # Validate inside the worker too (defense in depth).
    from jojo_output.sandbox.spec import PlotSpec
    try:
        spec = PlotSpec.model_validate(payload)
    except Exception as e:  # noqa: BLE001
        print(f"spec validation failed: {e}", file=sys.stderr)
        return 65

    from jojo_output.sandbox.render import render_to_bytes
    try:
        data = render_to_bytes(spec, fmt=args.fmt)
    except Exception as e:  # noqa: BLE001
        print(f"render failed: {type(e).__name__}: {e}", file=sys.stderr)
        return 66

    sys.stdout.buffer.write(base64.b64encode(data))
    sys.stdout.buffer.write(b"\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
