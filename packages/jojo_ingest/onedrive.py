"""OneDrive connector — reads the synced OneDrive folder from local disk.

See ADR 0008 for the full decision record. Short version: the Nurix tenant
doesn't currently allow the delegated `Files.Read.All` scope to be consented
without admin approval, so the MS-Graph-over-Sites path (what SharePoint
uses) isn't usable for OneDrive today. Meanwhile the desktop OneDrive client
already syncs the same content to a regular folder on the operator's
machine — so for V1 we just walk that folder like any other filesystem.

This is purely a `DriveConnector` with a different `source_type`. No new
traversal logic, no new converter logic; the only connector-level specifics
are:

  - `source_type = "onedrive"` so the manifest can tell OneDrive files
    apart from arbitrary drive paths later.
  - Env factory `build_onedrive_connector_from_env()` reads
    `JOJO_ONEDRIVE_PATH` (typically `C:\\Users\\<user>\\OneDrive - Nurix
    Therapeutics`). CLI + router both flow through it so the "what do I
    need to set" UX is consistent.

When the tenant opens up `Files.Read.All` — or when we ship the service-
account app registration in Phase 7b — we can swap this for a Graph-based
implementation without touching callers: same `source_type`, same
`SourceEntry` shape. The env factory would change what it builds; the
ingest pipeline wouldn't notice.
"""

from __future__ import annotations

import os

from jojo_connectors_common import IngestError
from jojo_ingest.drive import DriveConnector

# Env var — point at the root of your synced OneDrive folder. On Windows this
# is typically under `C:\Users\<user>\OneDrive - Nurix Therapeutics`; on
# macOS under `~/Library/CloudStorage/OneDrive-NurixTherapeutics`.
ENV_PATH = "JOJO_ONEDRIVE_PATH"


class OneDriveConnector(DriveConnector):
    """Thin subclass of DriveConnector that stamps source_type as 'onedrive'."""

    source_type = "onedrive"


class OneDriveEnvError(IngestError):
    """Raised when the env-driven factory can't assemble a connector.

    Separate class so the CLI + router can map it to an actionable 400
    rather than the generic 500 a bare IngestError would produce.
    """


def build_onedrive_connector_from_env(
    *,
    access_level: str = "all_fte",
    path_override: str | None = None,
) -> OneDriveConnector:
    """Assemble a OneDriveConnector from env vars.

    `path_override` (or `--source` on the CLI) wins over the env var; useful
    for one-off invocations that shouldn't pollute the shell environment.
    """
    path = (path_override or os.environ.get(ENV_PATH, "")).strip()
    if not path:
        raise OneDriveEnvError(
            f"{ENV_PATH} is not set. Point it at the local OneDrive sync "
            "folder, e.g. "
            'JOJO_ONEDRIVE_PATH="C:\\Users\\mdelosrios\\OneDrive - Nurix Therapeutics". '
            "You can also pass --source on the CLI to override."
        )
    try:
        return OneDriveConnector(path, access_level=access_level)
    except IngestError as exc:
        # DriveConnector raises when the root doesn't exist; translate so the
        # caller gets a OneDrive-flavored error message naming the env var.
        raise OneDriveEnvError(
            f"{ENV_PATH}={path!r}: {exc}. Is OneDrive signed in and syncing?"
        ) from exc
