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
from collections.abc import Iterable

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
    """DriveConnector subclass for the Nurix P:\\ share.

    Beyond stamping `source_type = "publicdrive"`, this connector ships a
    baseline ignore set tuned to the P:\\ drive's known-noisy subtrees.
    These belong here (in connector code) rather than in the source's
    own `.jojoignore` because:

      - operators don't have write permission at the share root, and
      - a `.jojoignore` at P:\\ would also affect any other tooling that
        respects gitignore files; the prune is ingest-specific.

    Patterns ship as defaults; an operator can layer additional patterns
    via the `extra_ignore_patterns=` kwarg or negate a builtin with a
    `!`-rule in the source-root `.jojoignore` if circumstances change.

    The current builtins target instrument-output formats whose contents
    are binary blobs the converters cannot read, and which produce
    millions of files per directory. Without the prune, the walker
    descends into them indefinitely (this was the root cause of the
    24-hour publicdrive runs that watchdog-killed at 1440 minutes
    without ever yielding a usable file once they entered the
    Analytical Chemistry/Data_LCMS-AUTO subtree on 2026-04-25).
    """

    source_type = "publicdrive"

    # Conservative starter set — file an issue if a real prune-target
    # gets caught, or pass `extra_ignore_patterns=` from a CLI flag.
    #
    #   *.D/        Agilent ChemStation per-injection directories. Each
    #               one contains hundreds of binary chromatogram files
    #               (DA.M, *.bin, *.UV, ...) the converters can't read.
    #   *.d/        Same as above; lowercase variant seen on a few older
    #               Bruker/MestReNova-derived directories.
    #   Data_LCMS-AUTO/
    #               Bulk auto-runs of LC/MS data. Usually a parent of many
    #               *.D directories, but pruning at this level is cheaper
    #               than per-injection because we never descend at all.
    #   WellImages/
    #               Well-plate imaging output (HighContent / plate-reader
    #               instrument runs). Each WellImages directory contains a
    #               numeric-ID tree
    #                   WellImages/<run>/plateID_<n>/batchID_<m>/wellNum_<k>/...
    #               with thousands of small binary image files per leaf.
    #               The 2026-04-27 publicdrive walk timed out at hour 24
    #               inside Whistler/Diligence visit/WellImages/... before
    #               reaching every top-level folder alphabetically after
    #               'Whistler' (Wortman / X* / Y* / Z*). Pruning at the
    #               WellImages level is enough — we don't need separate
    #               plateID_/batchID_/wellNum_ rules because the parent
    #               prune stops the descent before any of those are seen.
    _BUILTIN_IGNORE_PATTERNS: tuple[str, ...] = (
        "*.D/",
        "*.d/",
        "Data_LCMS-AUTO/",
        "WellImages/",
    )


class PublicDriveEnvError(IngestError):
    """Raised when the env-driven factory can't assemble a connector."""


def build_publicdrive_connector_from_env(
    *,
    access_level: str = "all_fte",
    path_override: str | None = None,
    include_extensions: Iterable[str] | None = None,
    extra_ignore_patterns: Iterable[str] | None = None,
    progress_interval_s: float | None = None,
) -> PublicDriveConnector:
    """Assemble a PublicDriveConnector from env vars.

    Resolution order:
      1. `path_override` (CLI `--source`) if provided
      2. `$JOJO_PUBLIC_DRIVE_PATH`
      3. `P:\\` (Windows only — skipped elsewhere so we don't accidentally
         walk a non-existent path)

    `include_extensions` is plumbed straight through to DriveConnector. The
    P: drive's ~50 TB is mostly raw instrument output; the typical operator
    cut is `{"docx","pptx","pdf"}` to grab just the institutional knowledge.

    `progress_interval_s` overrides the connector's heartbeat cadence. None
    (the default) keeps DriveConnector's own default; pass 0 (or negative)
    to silence the heartbeat entirely.
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
    # Only forward progress_interval_s when the caller actually set it; this
    # keeps the DriveConnector default authoritative when the CLI flag is
    # absent rather than overriding it with a sentinel.
    extra: dict[str, float] = {}
    if progress_interval_s is not None:
        extra["progress_interval_s"] = progress_interval_s
    try:
        return PublicDriveConnector(
            path,
            access_level=access_level,
            include_extensions=include_extensions,
            extra_ignore_patterns=extra_ignore_patterns,
            **extra,
        )
    except IngestError as exc:
        raise PublicDriveEnvError(
            f"{ENV_PATH}={path!r}: {exc}. Is the network drive mounted and "
            "reachable?"
        ) from exc
