"""Allow ``python -m jojo_ingest`` as an alternative to the ``jojo-ingest``
console script. Useful when the entry-point shim isn't on PATH — typically
on Windows when pip installs to a user-scripts directory that wasn't added
to PATH. Less fragile than relying on the PATH entry; used by
``ops/validation/Run-ValidationSyncAll.ps1`` for that reason.
"""

from __future__ import annotations

import sys

from jojo_ingest.cli import main

if __name__ == "__main__":
    sys.exit(main())
