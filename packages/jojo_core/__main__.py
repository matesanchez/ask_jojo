"""Allow ``python -m jojo_core`` as an alternative to the ``jojo-core``
console script. Same PATH-independence rationale as ``jojo_ingest.__main__``:
on Windows setups where pip's Scripts directory isn't on PATH, the entry-point
shim is unreachable but ``python -m`` always works.
"""

from __future__ import annotations

import sys

from jojo_core.cli import main

if __name__ == "__main__":
    sys.exit(main())
