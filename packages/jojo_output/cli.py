"""Stub CLI for jojo_output.

Phase 0 scaffold. Grows in Phase 5.
"""

from __future__ import annotations

import sys


def main(argv: list[str] | None = None) -> int:
    _ = argv or sys.argv[1:]
    print(
        "jojo-output: not implemented yet (Phase 0 skeleton). "
        "Rich outputs land in Phase 5; see PLAN.md §6 Phase 5."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
