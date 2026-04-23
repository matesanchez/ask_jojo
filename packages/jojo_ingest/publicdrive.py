"""Public-drive connector — walks the mapped Nurix P:\\ drive.

The "Public Drive" is Nurix's org-wide shared SMB/network drive, typically
mounted as `P:\\` on Windows workstations. It's a separate, older system
from SharePoint — predates the cloud-first content strategy and still holds
a lot of historical SOPs, batch records, and protocol folders that nobody
has ported to SharePoint.

Implementation is a thin subclass of `DriveConnector`: the mount already
presents the share as a regular filesystem, so walking it is identical to
walking any local directory. The connector adds:

  - `source_type = "publicdrive"` so the manifest can tell shared-drive
    files apart from local dev-folder files later (e.g. for per-surface
    ACLs in Phase 7b).
  - Env factory `build_publicdrive_connector_from_env()` reads
    `JOJO_PUBLIC_DRIVE_PATH`, defaulting to `P:\\` on Windows (no default
    elsewhere — caller must set it). CLI + router flow through it so the
    error messages are consistent.

Performance note: `os.stat` over SMB can be slow, so scheduled runs should
always pass `--since` to let the connector skip untouched files rather than
re-statting the whole share.
"""

from __future__ import annotations

import sys

from jojo_connectors_common import IngestError
from jojo_core import config
from jojo_ingest.drive import DriveConnector

# `config.get(KEY_PUBLIC_DRIVE_PATH)` reads config.json first and falls back
# to this env var. Both surfaces work; the env var is the legacy path.
ENV_PATH = "JOJO_PUBLIC_DRIVE_PATH"
# `P:\` is the convention on Nurix Windows workstations. No default on macOS
# or Linux — the user must set the env var to wherever they've mounted the
# share (e.g. `/Volumes/Public` or `/mnt/public`).
_WINDOWS_DEFAULT = "P:\\"


class PublicDriveConnector(DriveConnector):
    """Thin subclass of DriveConnector that stamps source_type as 'publicdrive'."""

    source_type = "publicdrive"


class PublicDriveEnvError(IngestError):
    """Raised when the env-driven factory can't assemble a connector."""


def build_publicdrive_connector_from_env(
    *,
    access_level: str = "all_fte",
    path_override: str | None = None,
) -> PublicDriveConnector:
    """Assemble a PublicDriveConnector from env vars.

    Resolution order:
      1. `path_override` (CLI `--source`) if provided
      2. `$JOJO_PUBLIC_DRIVE_PATH`
      3. `P:\\` (Windows only — skipped elsewhere so we don't accidentally
         walk a non-existent path)
    """
    path = (path_override or config.get(config.KEY_PUBLIC_DRIVE_PATH, "") or "").strip()
    if not path and sys.platform.startswith("win"):
        path = _WINDOWS_DEFAULT
    if not path:
        raise PublicDriveEnvError(
            "public-drive path is not configured. Either run "
            '`jojo-core config set public_drive_path "P:\\\\"`, '
            f"set ${ENV_PATH} in the shell, or pass --source on the CLI."
        )
    try:
        return PublicDriveConnector(path, access_level=access_level)
    except IngestError as exc:
        raise PublicDriveEnvError(
            f"{ENV_PATH}={path!r}: {exc}. Is the network drive mounted and "
            "reachable?"
        ) from exc
