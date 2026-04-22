"""jojo_ingest — source connectors for ``ask_jojo_raw/``.

Owns the SharePoint / OneDrive / NurixNet / Drive / upload connectors plus
the shared driver that runs them against an `ask_jojo_raw/` directory.

Connector status as of Phase 1 (local tier):

  - drive      : ready — walks a local/SMB path
  - upload     : ready — single-file UI uploads
  - sharepoint : stub — blocked on MS Graph app registration (IT ticket)
  - onedrive   : stub — blocked on same IT ticket
  - nurixnet   : stub — blocked on VPN access + Playwright environment
"""

__version__ = "0.1.0"

from jojo_ingest.driver import DriverResult, IngestDriver

__all__ = ["DriverResult", "IngestDriver"]
