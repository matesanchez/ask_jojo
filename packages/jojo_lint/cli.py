"""Stub CLI for jojo_lint.

Phase 0 scaffold. Grows into ``jojo-lint nightly`` / ``weekly`` /
``check <name>`` subcommands in Phase 6.
"""

from __future__ import annotations

import sys


def main(argv: list[str] | None = None) -> int:
    _ = argv or sys.argv[1:]
    print(
        "jojo-lint: not implemented yet (Phase 0 skeleton). "
        "Lint checks land in Phase 6; see PLAN.md §6 Phase 6."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
