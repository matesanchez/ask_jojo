"""Content hashing and stable-ID generation.

The raw layer's immutability guarantee depends on stable hashes. Every raw file
records the canonical SHA256 of its content; the wiki's citations embed these
hashes so a compile-time check can verify the source hasn't moved under us.

`canonical_sha256` normalizes line endings and trailing whitespace before
hashing so a file that round-trips through a text editor (CRLF → LF, trailing
newline added) still hashes identically. Without this, idempotency breaks the
first time a user opens a raw file on Windows.
"""

from __future__ import annotations

import hashlib
import re

_TRAILING_WS = re.compile(r"[ \t]+$", re.MULTILINE)


def canonical_sha256(content: str | bytes) -> str:
    """Return the SHA256 hex of content after light canonicalization.

    - bytes: hashed as-is (binary content must stay bit-identical).
    - str:  CRLF → LF, trailing whitespace per line stripped, single trailing
            newline enforced. Matches what git's `core.autocrlf=false` + most
            editors produce.
    """
    if isinstance(content, bytes):
        return hashlib.sha256(content).hexdigest()
    normalized = content.replace("\r\n", "\n").replace("\r", "\n")
    normalized = _TRAILING_WS.sub("", normalized)
    if not normalized.endswith("\n"):
        normalized += "\n"
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def stable_id(source_type: str, source_id: str) -> str:
    """Return a stable, filesystem-safe id for (source_type, source_id).

    The id is used as the raw file stem (`<source_type>_<slug>.md`). Keeping it
    deterministic means re-ingesting the same source produces the same filename
    — the manifest can detect supersedence instead of seeing two orphans.
    """
    slug = re.sub(r"[^a-zA-Z0-9\-]+", "-", source_id).strip("-").lower()
    if not slug:
        slug = hashlib.sha1(source_id.encode("utf-8")).hexdigest()[:16]
    return f"{source_type}_{slug}"
