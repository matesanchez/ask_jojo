"""Raw-source fallback retrieval — substring search over the manifest.

When the wiki coverage for a question is insufficient (no candidate
pages match, or candidates exist but the answer requires reading raw
files), the retrieval pipeline falls through to ``raw_fallback.search``.
The function reads ``ask_jojo_raw/manifest.json`` and scores each entry
against the query's tokens, returning the top-k entry IDs the eventual
synthesis pass should read.

This is the *deterministic* half of the raw-fallback path. The model-side
decision ("did the wiki have enough coverage?") lands with the synthesis
prompt on API day; today, the Cowork session decides and triggers
``search`` directly.

Public API:

- ``RawHit`` — dataclass with ``entry_id``, ``title``, ``source_type``,
  ``score``.
- ``search(manifest_path, query, k=10)`` — top-k matches.
- ``score_entry(entry, q_tokens)`` — public for CLI testing.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class RawHit:
    """One hit from raw-fallback search.

    Attributes:
        entry_id: the manifest key, e.g.
            ``sharepoint_protein-science-documents-...``
        title: best-effort human-readable title; falls back to the
            entry_id if the manifest entry has no ``title`` field.
        source_type: ``onedrive``, ``sharepoint``, ``publicdrive``, or
            ``drive``. Matches the connector identifier used in
            ``raw_router.py``.
        score: integer score from ``score_entry``. Higher is better.
        path: relative path within ``ask_jojo_raw/``. Useful for
            display in the UI's miss-fallback dropdown.
    """

    entry_id: str
    title: str
    source_type: str
    score: int
    path: str


def _tokenize(text: str) -> set[str]:
    """Same tokenizer as ``index_loader._tokenize`` for consistency.

    Also yields consecutive hyphen-joined sub-tokens so that a query
    token like "cbl-b" matches within a longer token like "cbl-b-team".
    """
    tokens: set[str] = set()
    for tok in re.findall(r"[A-Za-z0-9][A-Za-z0-9\-]+", text.lower()):
        if len(tok) < 2:
            continue
        tokens.add(tok)
        if "-" in tok:
            parts = [p for p in tok.split("-") if p]
            for part in parts:
                if len(part) >= 2:
                    tokens.add(part)
            for i in range(len(parts) - 1):
                sub = parts[i] + "-" + parts[i + 1]
                if len(sub) >= 2:
                    tokens.add(sub)
    return tokens


def score_entry(entry: dict[str, Any], q_tokens: set[str]) -> int:
    """Score one manifest entry against the question's tokens.

    Heuristic:
        - title token: +3
        - source_url token: +2 (the SharePoint/OneDrive path often
          carries the topic word — e.g. ``cbl-aacr-2019-aacr-abstract``)
        - tags / metadata.tags token: +1
    """
    if not q_tokens:
        return 0
    title = str(entry.get("title", "")).lower()
    source_url = str(entry.get("source_url", "")).lower()
    path = str(entry.get("path", "")).lower()
    tags_field = entry.get("tags") or entry.get("metadata", {}).get("tags") or []
    if isinstance(tags_field, str):
        tags_text = tags_field.lower()
    else:
        tags_text = " ".join(str(t) for t in tags_field).lower()

    title_tokens = _tokenize(title)
    url_tokens = _tokenize(source_url + " " + path)
    tag_tokens = _tokenize(tags_text)

    score = 0
    for tok in q_tokens:
        if tok in title_tokens:
            score += 3
        if tok in url_tokens:
            score += 2
        if tok in tag_tokens:
            score += 1
    return score


def search(
    manifest_path: Path | str,
    query: str,
    k: int = 10,
) -> list[RawHit]:
    """Return the top-``k`` raw-entry hits for ``query``.

    Reads the manifest from disk every call. The manifest is small
    enough at current scale (~140k entries) that this is cheap; a
    cache layer can be added later if the latency budget needs it.
    """
    manifest_path = Path(manifest_path)
    if not manifest_path.exists():
        return []

    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []

    entries = data.get("entries") or {}
    if not isinstance(entries, dict):
        return []

    q_tokens = _tokenize(query)
    if not q_tokens:
        return []

    scored: list[tuple[int, int, RawHit]] = []
    for i, (entry_id, entry) in enumerate(entries.items()):
        if not isinstance(entry, dict):
            continue
        s = score_entry(entry, q_tokens)
        if s > 0:
            scored.append(
                (
                    -s,
                    i,
                    RawHit(
                        entry_id=entry_id,
                        title=str(entry.get("title", entry_id)),
                        source_type=str(entry.get("source_type", "unknown")),
                        score=s,
                        path=str(entry.get("path", "")),
                    ),
                )
            )

    scored.sort()
    return [h for _, _, h in scored[:k]]
