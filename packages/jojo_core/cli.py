"""Stub CLI for jojo_core.

Phase 0 scaffold. Replaced with real subcommands (config check, worker
start, etc.) as jojo_core grows across later phases.
"""

from __future__ import annotations

import sys


def main(argv: list[str] | None = None) -> int:
    _ = argv or sys.argv[1:]
    print(
        "jojo-core: not implemented yet (Phase 0 skeleton). "
        "See ask_jojo/PLAN.md §3.3 for the planned scope."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
