"""Stub CLI for jojo_compile.

Phase 0 scaffold. Grows into ``jojo-compile absorb`` / ``plan`` / ``verify``
/ ``reorganize`` subcommands in Phase 2.
"""

from __future__ import annotations

import sys


def main(argv: list[str] | None = None) -> int:
    _ = argv or sys.argv[1:]
    print(
        "jojo-compile: not implemented yet (Phase 0 skeleton). "
        "Absorb loop lands in Phase 2; see PLAN.md §6 Phase 2."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
