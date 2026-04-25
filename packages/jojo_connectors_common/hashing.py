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

# Cap on the entire entry_id ("<source_type>_<slug>") so the resulting
# raw filename stays under Windows MAX_PATH (260) on the typical Nurix
# install. Math (taken from mdelosrios's box, 2026-04-25):
#   "C:\Users\mdelosrios\Claude_Local\jojo_bot_v2.0\ask_jojo\"    56
#   "ask_jojo_raw\publicdrive\"                                  25
#   "<entry_id>.md"                                              cap + 3
# Cap = 160 gives 56 + 25 + 160 + 3 = 244 — comfortably under 260
# without depending on Windows long-path support being enabled. Bumping
# the cap risks reintroducing the EINVAL absorb crash on Jose Gomez's
# desktop-of-desktops T-cell paper trail; lowering further makes
# already-readable filenames opaque without a real benefit.
_MAX_ENTRY_ID_LEN = 160
_HASH_SUFFIX_LEN = 10  # 10 hex chars of sha1 — 40 bits, collision-safe at our scale


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

    When the slug-from-source_id would push the entry_id past
    `_MAX_ENTRY_ID_LEN`, the slug is truncated and a stable
    sha1-derived suffix is appended. This was added 2026-04-25 after a
    publicdrive walk on a deeply-nested SMB share started raising
    OSError [Errno 22] on absorb because the resulting raw filename
    exceeded Windows MAX_PATH. Truncate-with-hash keeps the algorithm
    deterministic (same source_id always yields same entry_id) and
    collision-safe (the hash disambiguates two long paths sharing a
    common prefix).
    """
    slug = re.sub(r"[^a-zA-Z0-9\-]+", "-", source_id).strip("-").lower()
    if not slug:
        slug = hashlib.sha1(source_id.encode("utf-8")).hexdigest()[:16]
    entry_id = f"{source_type}_{slug}"
    if len(entry_id) <= _MAX_ENTRY_ID_LEN:
        return entry_id
    # Reserve room for the joining "-" plus the hash suffix. The joining
    # "-" is added explicitly so the tail is recognizable as a hash and
    # not a slug fragment (the rstrip("-") prevents "...--<hash>").
    suffix = hashlib.sha1(source_id.encode("utf-8")).hexdigest()[:_HASH_SUFFIX_LEN]
    head_budget = _MAX_ENTRY_ID_LEN - len(source_type) - 1 - 1 - _HASH_SUFFIX_LEN
    head = slug[:head_budget].rstrip("-")
    return f"{source_type}_{head}-{suffix}"
