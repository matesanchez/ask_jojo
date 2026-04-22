"""Shared ingest driver — turns SourceEntry objects into raw files on disk.

Every connector produces `SourceEntry` dicts. The driver:

  1. Runs the body through the redaction pass.
  2. Computes a canonical SHA256.
  3. Consults the manifest — no-op on unchanged content, supersedence on
     changed content, new entry otherwise.
  4. Writes the raw .md with frontmatter + body to the correct subdirectory.
  5. Updates the manifest.
  6. Appends to a `_changes/<yyyy-mm-dd>.json` record for Phase 2 consumption.

Keeping this in one place is what makes the "same pipeline for every
connector" invariant true — connectors stay small, the policy lives here.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from jojo_connectors_common import (
    Connector,
    ConnectorResult,
    Manifest,
    ManifestEntry,
    SourceEntry,
    build_frontmatter,
    canonical_sha256,
    redact_pii,
    stable_id,
)


@dataclass(slots=True)
class DriverResult:
    results: dict[str, ConnectorResult] = field(default_factory=dict)
    change_record_path: Path | None = None


class IngestDriver:
    """Runs one or more connectors against an `ask_jojo_raw/` directory."""

    def __init__(self, raw_root: Path | str) -> None:
        self.raw_root = Path(raw_root)
        self.raw_root.mkdir(parents=True, exist_ok=True)
        self.manifest = Manifest.load(self.raw_root / "manifest.json")

    # ------------------------------------------------------------------ core
    def run(
        self,
        connectors: list[Connector],
        *,
        since: datetime | None = None,
    ) -> DriverResult:
        changes: dict[str, list[str]] = {"added": [], "updated": [], "removed": [], "skipped": []}
        result = DriverResult()
        for connector in connectors:
            cr = ConnectorResult(source_type=connector.source_type)
            try:
                for entry in connector.fetch(since=since):
                    outcome = self._absorb(entry)
                    if outcome == "added":
                        cr.added += 1
                        changes["added"].append(entry.source_id)
                    elif outcome == "updated":
                        cr.updated += 1
                        changes["updated"].append(entry.source_id)
                    elif outcome == "skipped":
                        cr.skipped += 1
                    else:
                        cr.errors += 1
                        cr.failures.append(entry.source_id)
            finally:
                connector.close()
            result.results[connector.source_type] = cr
        self.manifest.save()
        if any(changes[k] for k in ("added", "updated", "removed")):
            result.change_record_path = self._write_change_record(changes)
        return result

    # ------------------------------------------------------------------ internals
    def _absorb(self, entry: SourceEntry) -> str:
        """Process one SourceEntry. Returns 'added' / 'updated' / 'skipped' / 'error'."""
        try:
            red = redact_pii(entry.content)
            body = red.content
            sha = canonical_sha256(body)
            entry_id = stable_id(entry.source_type, entry.source_id)
            existing = self.manifest.get(entry_id)

            if existing and existing.sha256 == sha:
                return "skipped"

            rel_dir = entry.source_type
            rel_path = f"{rel_dir}/{entry_id}.md"
            target = self.raw_root / rel_path

            frontmatter = build_frontmatter(
                entry_id=entry_id,
                source_type=entry.source_type,
                source_url=entry.source_url,
                source_id=entry.source_id,
                title=entry.title or entry.source_id,
                sha256=sha,
                author=entry.author,
                created=_fmt(entry.created),
                modified=_fmt(entry.modified),
                language=entry.language,
                access_level=entry.access_level,
                tags=entry.tags,
                redacted_fields=red.redacted_fields,
                extra=entry.extra,
            )
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(frontmatter.to_yaml() + body + ("\n" if not body.endswith("\n") else ""), encoding="utf-8")

            manifest_entry = ManifestEntry(
                id=entry_id,
                path=rel_path,
                sha256=sha,
                source_type=entry.source_type,
                source_url=entry.source_url,
                source_id=entry.source_id,
                title=entry.title or entry.source_id,
                access_level=entry.access_level,
                fetched=_fmt(datetime.now(timezone.utc)),
                size_bytes=target.stat().st_size,
                redacted_fields=red.redacted_fields,
                supersedes=existing.id if existing else None,
            )
            self.manifest.upsert(manifest_entry)
            return "updated" if existing else "added"
        except Exception:
            # The caller tracks error counts; we swallow to avoid taking down
            # the whole run because of one bad file. A production build would
            # log the traceback to `_changes/<date>.errors.json`.
            return "error"

    def _write_change_record(self, changes: dict[str, list[str]]) -> Path:
        date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        out_dir = self.raw_root / "_changes"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{date}.json"
        existing: dict = {}
        if out_path.exists():
            existing = json.loads(out_path.read_text(encoding="utf-8"))
        for k, v in changes.items():
            existing.setdefault(k, []).extend(v)
        # Deduplicate while preserving order.
        for k in existing:
            seen: set[str] = set()
            deduped: list[str] = []
            for sid in existing[k]:
                if sid not in seen:
                    deduped.append(sid)
                    seen.add(sid)
            existing[k] = deduped
        existing["generated"] = _fmt(datetime.now(timezone.utc))
        out_path.write_text(
            json.dumps(existing, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        return out_path


def _fmt(dt: datetime | None) -> str:
    if dt is None:
        return ""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.replace(microsecond=0).isoformat()
