"""`ask_jojo_raw/manifest.json` — the mechanical source of truth.

Per PLAN.md §6 Phase 1: every raw file must be listed in the manifest with
hash, source URL, permissions, ingest date, and supersedence links. The
compile phase reads this file; the Raw tab renders it; filesystem walks
should never bypass it.

Keeping the manifest a plain JSON file (not a database) is deliberate — it
diffs cleanly, committers can eyeball changes, and the Phase 7b shared server
migration doesn't need a schema migration step.

Manifest shape:

    {
      "schema_version": "0.1.0",
      "generated": "2026-04-22T19:15:00+00:00",
      "entries": {
        "<entry-id>": {
          "path": "drive/some-file.md",
          "sha256": "...",
          "source_type": "drive",
          ...
        },
        ...
      },
      "supersedence": {
        "<old-entry-id>": "<new-entry-id>",
        ...
      }
    }
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "0.1.0"


@dataclass(slots=True)
class ManifestEntry:
    id: str
    path: str           # Repo-relative POSIX path (e.g. "drive/x.md")
    sha256: str
    source_type: str
    source_url: str = ""
    source_id: str = ""
    title: str = ""
    access_level: str = "all_fte"
    fetched: str = ""
    size_bytes: int = 0
    redacted_fields: list[str] = field(default_factory=list)
    supersedes: str | None = None   # entry-id that this one replaces

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class Manifest:
    """In-memory view of `manifest.json` with idempotent update semantics.

    Typical usage:

        manifest = Manifest.load(raw_root / "manifest.json")
        existing = manifest.get(entry.id)
        if existing and existing.sha256 == entry.sha256:
            return  # no-op, content unchanged
        if existing:
            entry.supersedes = existing.id
        manifest.upsert(entry)
        manifest.save()
    """

    def __init__(
        self,
        path: Path,
        entries: dict[str, ManifestEntry] | None = None,
        supersedence: dict[str, str] | None = None,
    ) -> None:
        self.path = path
        self.entries: dict[str, ManifestEntry] = dict(entries or {})
        self.supersedence: dict[str, str] = dict(supersedence or {})

    # ------------------------------------------------------------------ IO
    @classmethod
    def load(cls, path: Path | str) -> Manifest:
        p = Path(path)
        if not p.exists():
            return cls(p)
        data = json.loads(p.read_text(encoding="utf-8"))
        entries_raw = data.get("entries", {})
        entries: dict[str, ManifestEntry] = {}
        for entry_id, fields in entries_raw.items():
            entries[entry_id] = ManifestEntry(
                id=entry_id,
                path=fields["path"],
                sha256=fields["sha256"],
                source_type=fields.get("source_type", ""),
                source_url=fields.get("source_url", ""),
                source_id=fields.get("source_id", ""),
                title=fields.get("title", ""),
                access_level=fields.get("access_level", "all_fte"),
                fetched=fields.get("fetched", ""),
                size_bytes=fields.get("size_bytes", 0),
                redacted_fields=list(fields.get("redacted_fields", []) or []),
                supersedes=fields.get("supersedes"),
            )
        return cls(p, entries=entries, supersedence=dict(data.get("supersedence", {})))

    def save(self) -> None:
        out = {
            "schema_version": SCHEMA_VERSION,
            "generated": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "entries": {
                eid: {k: v for k, v in e.to_dict().items() if k != "id"}
                for eid, e in sorted(self.entries.items())
            },
            "supersedence": dict(sorted(self.supersedence.items())),
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(out, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    # ------------------------------------------------------------------ queries
    def get(self, entry_id: str) -> ManifestEntry | None:
        return self.entries.get(entry_id)

    def by_source_id(self, source_type: str, source_id: str) -> ManifestEntry | None:
        for entry in self.entries.values():
            if entry.source_type == source_type and entry.source_id == source_id:
                return entry
        return None

    def by_source(self, source_type: str) -> list[ManifestEntry]:
        return [e for e in self.entries.values() if e.source_type == source_type]

    # ------------------------------------------------------------------ mutation
    def upsert(self, entry: ManifestEntry) -> None:
        if entry.supersedes:
            self.supersedence[entry.supersedes] = entry.id
        self.entries[entry.id] = entry

    def remove(self, entry_id: str) -> bool:
        return self.entries.pop(entry_id, None) is not None

    def diff_against(self, other: Manifest) -> dict[str, list[str]]:
        """Summarize changes from `other` → `self`. Used by incremental sync."""
        added = sorted(set(self.entries) - set(other.entries))
        removed = sorted(set(other.entries) - set(self.entries))
        changed = sorted(
            eid
            for eid in self.entries
            if eid in other.entries and self.entries[eid].sha256 != other.entries[eid].sha256
        )
        return {"added": added, "removed": removed, "changed": changed}
