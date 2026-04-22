"""Local-path / SMB drive connector.

Walks a root directory and emits one `SourceEntry` per readable file. The
`.jojoignore` at the root (if any) filters the walk — default ignores cover
Office lock files, OS junk, and common build directories.

SMB paths work too: pass `\\\\server\\share\\folder` (Windows) or a mounted
`/mnt/smb/share` (Linux/macOS). The connector treats them as ordinary
filesystem paths; the only quirk is that `os.stat` can be slow over SMB, so
`--incremental --since <iso>` is strongly recommended for scheduled runs.

Files whose extension has a dedicated converter (docx/xlsx/pptx/pdf) round-
trip through that converter. Anything else that decodes as text falls back
to the text converter. Binary files with unknown extensions are skipped and
logged.
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
from jojo_ingest.converters import ConverterNotFound, convert, is_supported

log = logging.getLogger(__name__)


class DriveConnector(Connector):
    source_type = "drive"

    def __init__(
        self,
        root: Path | str,
        *,
        access_level: str = "all_fte",
        ignore: JojoIgnore | None = None,
    ) -> None:
        self.root = Path(root).resolve()
        if not self.root.exists():
            raise IngestError(f"drive root does not exist: {self.root}")
        self.access_level = access_level
        self.ignore = ignore or JojoIgnore.from_file(self.root / ".jojoignore")

    def fetch(self, *, since: datetime | None = None) -> Iterable[SourceEntry]:
        yield from self._walk(self.root, since=since)

    def _walk(self, directory: Path, *, since: datetime | None) -> Iterator[SourceEntry]:
        try:
            children = sorted(directory.iterdir(), key=lambda p: p.name)
        except PermissionError:
            log.warning("permission denied, skipping: %s", directory)
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
            if since is not None:
                try:
                    mtime = datetime.fromtimestamp(entry.stat().st_mtime, tz=timezone.utc)
                except OSError:
                    continue
                if mtime < since:
                    continue
            se = self._build_entry(entry, rel)
            if se is not None:
                yield se

    def _build_entry(self, path: Path, rel: str) -> SourceEntry | None:
        try:
            body = convert(path)
        except ConverterNotFound:
            return None
        except Exception as exc:  # noqa: BLE001 — one bad file must not stop the walk
            log.warning("failed to convert %s: %s", path, exc)
            return None
        try:
            stat = path.stat()
            modified = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
            created = datetime.fromtimestamp(stat.st_ctime, tz=timezone.utc)
        except OSError:
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
