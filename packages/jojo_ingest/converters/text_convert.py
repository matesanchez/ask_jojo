"""Text / markdown passthrough converter.

Decodes with a fallback chain so a Windows-encoded .txt doesn't blow up the
ingest. If every decoding fails, raises UnicodeDecodeError — the connector
will log it and mark the entry as errored.
"""

from __future__ import annotations

from pathlib import Path

_ENCODINGS: tuple[str, ...] = ("utf-8-sig", "utf-8", "cp1252", "latin-1")


def convert_text(path: Path) -> str:
    raw = path.read_bytes()
    for enc in _ENCODINGS:
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    # Last resort — latin-1 decodes any byte stream.
    return raw.decode("latin-1", errors="replace")
