"""`ask_jojo_raw/manifest.json` — the mechanical source of truth.

Per PLAN.md §6 Phase 1: every raw file must be listed in the manifest with
hash, source URL, permissions, ingest date, and supersedence links. The
compile phase reads this file; the Raw tab renders it; filesystem walks
should never bypass it.

Keeping the manifest plain JSON (not a database) is deliberate — it diffs
cleanly, committers can eyeball changes, and the Phase 7b shared server
migration doesn't need a schema migration step.

**Split format** (auto-selected when entry count ≥ SPLIT_THRESHOLD):

    manifest.json          ← tiny routing stub (<1 KB)
    manifest_onedrive.json ← entries for source_type "onedrive"
    manifest_publicdrive.json
    manifest_sharepoint.json
    …

The stub shape:

    {
      "schema_version": "0.1.0",
      "generated": "2026-04-22T19:15:00+00:00",
      "format": "split",
      "parts": ["manifest_onedrive.json", "manifest_publicdrive.json", ...],
      "total_entries": 139370,
      "supersedence": {...}
    }

``Manifest.load()`` detects ``"format": "split"`` and transparently merges
all parts so callers see a unified in-memory object.  ``Manifest.save()``
switches to split format automatically once entry count ≥ SPLIT_THRESHOLD.

**Unified format** (small manifests / tests):

    {
      "schema_version": "0.1.0",
      "generated": "2026-04-22T19:15:00+00:00",
      "entries": { "<entry-id>": { ... }, ... },
      "supersedence": { ... }
    }
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "0.1.0"

# When the total entry count reaches this threshold, save() writes split files
# instead of a single manifest.json.  Keeps each file well under GitHub's
# 100 MB limit.  Tests use tiny manifests (< 100 entries) and are unaffected.
SPLIT_THRESHOLD = 10_000


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
    def _parse_entries(cls, entries_raw: dict) -> dict[str, ManifestEntry]:
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
        return entries

    @classmethod
    def load(cls, path: Path | str) -> Manifest:
        """Load a manifest from *path*.

        Handles both formats transparently:

        - **Unified** — single ``manifest.json`` with an ``entries`` key.
        - **Split** — ``manifest.json`` routing stub (``"format": "split"``)
          plus per-source ``manifest_{source_type}.json`` files in the same
          directory.  All parts are merged into a single in-memory object.
        """
        p = Path(path)
        if not p.exists():
            return cls(p)
        data = json.loads(p.read_text(encoding="utf-8"))

        if data.get("format") == "split":
            # Split format: load each part file and merge.
            entries: dict[str, ManifestEntry] = {}
            for part_name in data.get("parts", []):
                part_path = p.parent / part_name
                if not part_path.exists():
                    continue
                part_data = json.loads(part_path.read_text(encoding="utf-8"))
                entries.update(cls._parse_entries(part_data.get("entries", {})))
            return cls(
                p,
                entries=entries,
                supersedence=dict(data.get("supersedence", {})),
            )

        # Unified format.
        entries = cls._parse_entries(data.get("entries", {}))
        return cls(p, entries=entries, supersedence=dict(data.get("supersedence", {})))

    def save(self) -> None:
        """Persist the manifest to disk.

        Writes split format (stub + per-source files) when
        ``len(self.entries) >= SPLIT_THRESHOLD``; unified JSON otherwise.
        This keeps every file well under GitHub's 100 MB limit while
        leaving small test manifests as single files.
        """
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if len(self.entries) >= SPLIT_THRESHOLD:
            self._save_split()
        else:
            self._save_unified()

    def _save_unified(self) -> None:
        out = {
            "schema_version": SCHEMA_VERSION,
            "generated": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "entries": {
                eid: {k: v for k, v in e.to_dict().items() if k != "id"}
                for eid, e in sorted(self.entries.items())
            },
            "supersedence": dict(sorted(self.supersedence.items())),
        }
        self.path.write_text(
            json.dumps(out, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    def _save_split(self) -> None:
        """Write per-source-type part files + a small routing stub."""
        generated = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

        # Group entries by source_type.
        by_src: dict[str, dict[str, ManifestEntry]] = {}
        for eid, entry in self.entries.items():
            by_src.setdefault(entry.source_type, {})[eid] = entry

        # Write one file per source type.
        for src, src_entries in sorted(by_src.items()):
            part_out = {
                "schema_version": SCHEMA_VERSION,
                "generated": generated,
                "source_type": src,
                "entries": {
                    eid: {k: v for k, v in e.to_dict().items() if k != "id"}
                    for eid, e in sorted(src_entries.items())
                },
            }
            part_path = self.path.parent / f"manifest_{src}.json"
            part_path.write_text(
                json.dumps(part_out, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

        # Write the routing stub.
        stub = {
            "schema_version": SCHEMA_VERSION,
            "generated": generated,
            "format": "split",
            "parts": sorted(f"manifest_{s}.json" for s in by_src),
            "total_entries": len(self.entries),
            "supersedence": dict(sorted(self.supersedence.items())),
        }
        self.path.write_text(
            json.dumps(stub, indent=2, ensure_ascii=False) + "\n",
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
