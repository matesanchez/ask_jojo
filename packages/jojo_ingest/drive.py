"""Local-path / SMB drive connector.

Walks a root directory and emits one `SourceEntry` per readable file. The
`.jojoignore` at the root (if any) filters the walk -- default ignores cover
Office lock files, OS junk, and common build directories.

SMB paths work too: pass `\\\\server\\share\\folder` (Windows) or a mounted
`/mnt/smb/share` (Linux/macOS). The connector treats them as ordinary
filesystem paths; the only quirk is that `os.stat` can be slow over SMB, so
`--incremental --since <iso>` is strongly recommended for scheduled runs.

Hang resilience (FU-9): every blocking filesystem call -- `iterdir`,
`stat`, and the per-file `convert` hand-off -- is routed through
`jojo_ingest._watchdog.run_with_timeout`. If a call doesn't return within
its timeout, the walker logs the path and moves on. Without this guard a
single torn-down SMB session can deadlock the whole run (the symptom from
the April 22 soak: 12h wall-clock, zero additions, zero errors).

Files whose extension has a dedicated converter (docx/xlsx/pptx/pdf) round-
trip through that converter. Anything else that decodes as text falls back
to the text converter. Binary files with unknown extensions are skipped and
logged. Files larger than `max_size_mb` (default 50 MB) are skipped before
the converter ever opens them -- this matches the SharePoint connector's
default and keeps a random 4 GB CAD file on P:\\ from exploding the walker.
"""

from __future__ import annotations

import logging
from collections.abc import Iterable, Iterator
from datetime import datetime, timezone
from pathlib import Path

from jojo_connectors_common import (
    Connector,
    IngestError,
    JojoIgnore,
    SourceEntry,
)
from jojo_ingest._watchdog import WatchdogTimeout, run_with_timeout
from jojo_ingest.converters import ConverterNotFound, convert, is_supported

log = logging.getLogger(__name__)

# Defaults picked to match operational experience:
#   - 30s is longer than any healthy SMB scandir in our testing (median < 1s,
#     p99 < 5s) but short enough that a stuck subtree doesn't eat hours.
#   - 10s covers a cold-cache stat over SMB with plenty of slack; longer than
#     that and something is wrong.
#   - 120s for convert covers pathological xlsx/pdf files; beyond that
#     something is hung (fitz on a corrupt PDF, openpyxl on shared-string
#     weirdness) and we'd rather skip than wait.
_DEFAULT_LISTDIR_TIMEOUT_S = 30.0
_DEFAULT_STAT_TIMEOUT_S = 10.0
_DEFAULT_CONVERT_TIMEOUT_S = 120.0


class DriveConnector(Connector):
    source_type = "drive"

    def __init__(
        self,
        root: Path | str,
        *,
        access_level: str = "all_fte",
        ignore: JojoIgnore | None = None,
        max_size_mb: int = 50,
        listdir_timeout_s: float = _DEFAULT_LISTDIR_TIMEOUT_S,
        stat_timeout_s: float = _DEFAULT_STAT_TIMEOUT_S,
        convert_timeout_s: float = _DEFAULT_CONVERT_TIMEOUT_S,
    ) -> None:
        self.root = Path(root).resolve()
        if not self.root.exists():
            raise IngestError(f"drive root does not exist: {self.root}")
        self.access_level = access_level
        self.ignore = ignore or JojoIgnore.from_file(self.root / ".jojoignore")
        self.max_bytes = max_size_mb * 1024 * 1024
        self.listdir_timeout_s = listdir_timeout_s
        self.stat_timeout_s = stat_timeout_s
        self.convert_timeout_s = convert_timeout_s

    def fetch(self, *, since: datetime | None = None) -> Iterable[SourceEntry]:
        yield from self._walk(self.root, since=since)

    def _walk(self, directory: Path, *, since: datetime | None) -> Iterator[SourceEntry]:
        try:
            children = run_with_timeout(
                lambda: sorted(directory.iterdir(), key=lambda p: p.name),
                timeout_s=self.listdir_timeout_s,
                label=f"iterdir({directory})",
            )
        except PermissionError:
            log.warning("permission denied, skipping: %s", directory)
            return
        except WatchdogTimeout as exc:
            # This is the FU-9 case: SMB session torn down, iterdir never
            # returns. Daemon thread is abandoned; the walker moves on.
            log.warning("listdir timed out on %s, skipping subtree: %s", directory, exc)
            return
        except OSError as exc:
            # Broader I/O failure at the directory level -- most commonly a
            # transient SMB blip on the public P: drive. Typical errnos:
            #   WinError 59 ("unexpected network error")
            #   WinError 64 ("network name no longer available")
            #   WinError 67 ("network name cannot be found")
            #   WinError 1231 ("network location cannot be reached")
            # Log loudly but keep walking -- one bad subtree is never worth
            # losing the entire run's worth of already-yielded entries.
            log.warning("I/O error listing %s, skipping subtree: %s", directory, exc)
            return
        for entry in children:
            rel = entry.relative_to(self.root).as_posix()
            if entry.is_dir():
                if self.ignore.match(rel, is_dir=True):
                    continue
                yield from self._walk(entry, since=since)
                continue
            if self.ignore.match(rel, is_dir=False):
                continue
            if not is_supported(entry):
                log.info("unsupported extension, skipping: %s", rel)
                continue
            stat = self._safe_stat(entry)
            if stat is None:
                continue
            if stat.st_size > self.max_bytes:
                log.info(
                    "skipping %s: %d bytes > max_size %d",
                    rel, stat.st_size, self.max_bytes,
                )
                continue
            if since is not None:
                mtime = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
                if mtime < since:
                    continue
            se = self._build_entry(entry, rel, stat=stat)
            if se is not None:
                yield se

    def _safe_stat(self, path: Path):
        """Stat a single path with a watchdog timeout. Returns None on failure.

        Over SMB an `os.stat` on a handle whose session was torn down can
        block indefinitely. We route every stat through the watchdog so
        the walker never gets stuck on one file.
        """
        try:
            return run_with_timeout(
                path.stat,
                timeout_s=self.stat_timeout_s,
                label=f"stat({path})",
            )
        except WatchdogTimeout as exc:
            log.warning("stat timed out on %s, skipping: %s", path, exc)
            return None
        except OSError as exc:
            log.warning("stat failed on %s, skipping: %s", path, exc)
            return None

    def _build_entry(self, path: Path, rel: str, *, stat=None) -> SourceEntry | None:
        try:
            body = run_with_timeout(
                convert,
                path,
                timeout_s=self.convert_timeout_s,
                label=f"convert({rel})",
            )
        except ConverterNotFound:
            return None
        except WatchdogTimeout as exc:
            # A converter that never returns is either pegged on a
            # corrupt file or stuck inside a C extension we can't
            # interrupt. Skip and move on.
            log.warning("convert timed out on %s, skipping: %s", path, exc)
            return None
        except Exception as exc:  # noqa: BLE001 -- one bad file must not stop the walk
            log.warning("failed to convert %s: %s", path, exc)
            return None
        if stat is None:
            stat = self._safe_stat(path)
        if stat is not None:
            modified = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
            created = datetime.fromtimestamp(stat.st_ctime, tz=timezone.utc)
        else:
            modified = None
            created = None
        return SourceEntry(
            source_type=self.source_type,
            source_id=rel,
            source_url=path.as_uri(),
            title=path.stem,
            content=body,
            access_level=self.access_level,
            author="",
            created=created,
            modified=modified,
            tags=[],
        )
