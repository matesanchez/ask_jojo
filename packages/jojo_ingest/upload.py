"""Upload connector — handles single-file uploads from the UI.

The Raw tab has an "Upload to raw" button. When a user drops a file, the
backend saves it to a staging directory, calls `UploadConnector.fetch()` with
the path, and the driver writes it through the same pipeline as any other
source.

Unlike drive/sharepoint, the upload connector is short-lived — one instance
per upload. It has no incremental semantics (the user just handed us a file)
and no polling.
"""

from __future__ import annotations

import logging
from collections.abc import Iterable
from datetime import datetime, timezone
from pathlib import Path

from jojo_connectors_common import Connector, IngestError, SourceEntry
from jojo_ingest.converters import ConverterNotFound, convert, is_supported

log = logging.getLogger(__name__)


class UploadConnector(Connector):
    source_type = "upload"

    def __init__(
        self,
        file_path: Path | str,
        *,
        title: str | None = None,
        author: str = "",
        access_level: str = "all_fte",
        tags: list[str] | None = None,
        source_id: str | None = None,
    ) -> None:
        self.path = Path(file_path)
        if not self.path.exists():
            raise IngestError(f"upload path does not exist: {self.path}")
        if not is_supported(self.path):
            raise IngestError(
                f"unsupported file type: {self.path.suffix} "
                f"(supported: docx, xlsx, pptx, pdf, md, txt)"
            )
        self.title = title or self.path.stem
        self.author = author
        self.access_level = access_level
        self.tags = list(tags or [])
        self.source_id = source_id or self.path.name

    def fetch(self, *, since: datetime | None = None) -> Iterable[SourceEntry]:
        # `since` is irrelevant for a one-shot upload; the user just gave us
        # the file. We honor the argument to keep the Connector interface
        # uniform but ignore its value.
        del since
        try:
            body = convert(self.path)
        except ConverterNotFound as exc:
            raise IngestError(str(exc)) from exc

        now = datetime.now(timezone.utc)
        try:
            stat = self.path.stat()
            modified = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
        except OSError:
            modified = now

        yield SourceEntry(
            source_type=self.source_type,
            source_id=self.source_id,
            source_url=f"upload://{self.source_id}",
            title=self.title,
            content=body,
            access_level=self.access_level,
            author=self.author,
            created=modified,
            modified=modified,
            tags=self.tags,
        )
