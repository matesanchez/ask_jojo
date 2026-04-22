"""Stub CLI for jojo_qa.

Phase 0 scaffold. Grows into ``jojo-qa ask "<question>"`` and diagnostic
subcommands in Phase 4.
"""

from __future__ import annotations

import sys


def main(argv: list[str] | None = None) -> int:
    _ = argv or sys.argv[1:]
    print(
        "jojo-qa: not implemented yet (Phase 0 skeleton). "
        "Q&A lands in Phase 4; see PLAN.md §6 Phase 4."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
