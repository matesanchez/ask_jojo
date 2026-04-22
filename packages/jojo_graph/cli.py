"""Stub CLI for jojo_graph.

Phase 0 scaffold. Grows into ``jojo-graph rebuild`` / ``report`` subcommands
in Phase 7a.
"""

from __future__ import annotations

import sys


def main(argv: list[str] | None = None) -> int:
    _ = argv or sys.argv[1:]
    print(
        "jojo-graph: not implemented yet (Phase 0 skeleton). "
        "Graph tab lands in Phase 7a; see PLAN.md §6 Phase 7a."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
