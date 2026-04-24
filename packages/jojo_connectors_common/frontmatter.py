"""YAML frontmatter for raw files.

PLAN.md §6 Phase 1 lists the mandatory fields:
  id, source_type, source_url, source_id, title, author, created, modified,
  fetched, sha256, language, access_level, tags, redacted_fields.

This module owns their serialization, parsing, and validation. The absorb
pipeline (Phase 2) relies on these fields being exactly as specified — any
drift here propagates silently into the wiki. Prefer adding new optional
fields with clear defaults over renaming existing ones.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

import yaml

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)\Z", re.DOTALL)


class SourceType(str, Enum):
    """Closed set of source-system identifiers. Extend with care — Phase 2 readers match against these exact strings."""

    SHAREPOINT = "sharepoint"
    ONEDRIVE = "onedrive"
    PUBLICDRIVE = "publicdrive"
    DRIVE = "drive"
    NURIXNET = "nurixnet"
    UPLOAD = "upload"
    # Stretch connectors, reserved so they land predictably:
    TEAMS = "teams"
    BENCHLING = "benchling"
    ASANA = "asana"


class AccessLevel(str, Enum):
    """Who is allowed to see this entry in downstream layers.

    Mapped to the permission badges in the Raw tab and to per-user scope
    checks in Phase 7b (shared server). `all_fte` is the widest — anyone with
    a Nurix login. Narrower levels carry an `acl:` list in the frontmatter.
    """

    PUBLIC = "public"          # Nurix public-facing content (rare for raw)
    ALL_FTE = "all_fte"         # Any Nurix employee
    DEPARTMENT = "department"   # Scoped to one department (acl: lists the dept)
    RESTRICTED = "restricted"   # Case-by-case (acl: lists users/groups)


FRONTMATTER_FIELDS: tuple[str, ...] = (
    "id",
    "source_type",
    "source_url",
    "source_id",
    "title",
    "author",
    "created",
    "modified",
    "fetched",
    "sha256",
    "language",
    "access_level",
    "tags",
    "redacted_fields",
)


@dataclass(slots=True)
class RawFrontmatter:
    """Typed view of a raw-file frontmatter block.

    Use `.to_yaml()` to produce the canonical block written at the top of a
    raw .md file, or `build_frontmatter(...)` for the dict form the manifest
    records alongside. Any additional vendor-specific fields go in `extra`.
    """

    id: str
    source_type: SourceType
    source_url: str
    source_id: str
    title: str
    sha256: str
    access_level: AccessLevel = AccessLevel.ALL_FTE
    author: str = ""
    created: str | None = None
    modified: str | None = None
    fetched: str | None = None
    language: str = "en"
    tags: list[str] = field(default_factory=list)
    redacted_fields: list[str] = field(default_factory=list)
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "id": self.id,
            "source_type": self.source_type.value,
            "source_url": self.source_url,
            "source_id": self.source_id,
            "title": self.title,
            "author": self.author,
            "created": self.created,
            "modified": self.modified,
            "fetched": self.fetched or _now_iso(),
            "sha256": self.sha256,
            "language": self.language,
            "access_level": self.access_level.value,
            "tags": list(self.tags),
            "redacted_fields": list(self.redacted_fields),
        }
        data.update(self.extra)
        return data

    def to_yaml(self) -> str:
        """Render as a `---\\n…\\n---\\n` block ready to prepend to body."""
        body = yaml.safe_dump(
            self.to_dict(),
            sort_keys=False,
            default_flow_style=False,
            allow_unicode=True,
        )
        return f"---\n{body}---\n"


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def build_frontmatter(
    *,
    entry_id: str,
    source_type: SourceType | str,
    source_url: str,
    source_id: str,
    title: str,
    sha256: str,
    access_level: AccessLevel | str = AccessLevel.ALL_FTE,
    author: str = "",
    created: str | None = None,
    modified: str | None = None,
    fetched: str | None = None,
    language: str = "en",
    tags: list[str] | None = None,
    redacted_fields: list[str] | None = None,
    extra: dict[str, Any] | None = None,
) -> RawFrontmatter:
    """Helper for connectors — coerces string enums to their typed form."""
    return RawFrontmatter(
        id=entry_id,
        source_type=SourceType(source_type) if isinstance(source_type, str) else source_type,
        source_url=source_url,
        source_id=source_id,
        title=title,
        sha256=sha256,
        access_level=(
            AccessLevel(access_level) if isinstance(access_level, str) else access_level
        ),
        author=author,
        created=created,
        modified=modified,
        fetched=fetched,
        language=language,
        tags=list(tags or []),
        redacted_fields=list(redacted_fields or []),
        extra=dict(extra or {}),
    )


def split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Split a raw file into (frontmatter-dict, body-str).

    Returns ({}, text) if no frontmatter block is found — the caller can then
    decide whether that's a legitimate plain-markdown file or a corrupted
    raw entry that needs flagging.
    """
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return {}, text
    fm_raw, body = match.groups()
    data = yaml.safe_load(fm_raw) or {}
    if not isinstance(data, dict):
        return {}, text
    return data, body


def parse_frontmatter(text: str) -> RawFrontmatter | None:
    """Parse a raw file's frontmatter into a typed RawFrontmatter."""
    data, _ = split_frontmatter(text)
    if not data:
        return None
    missing = [f for f in ("id", "source_type", "source_id", "sha256", "title") if f not in data]
    if missing:
        raise ValueError(f"Frontmatter missing required fields: {missing}")
    extra = {k: v for k, v in data.items() if k not in FRONTMATTER_FIELDS}
    return RawFrontmatter(
        id=data["id"],
        source_type=SourceType(data["source_type"]),
        source_url=data.get("source_url", ""),
        source_id=data["source_id"],
        title=data["title"],
        sha256=data["sha256"],
        access_level=AccessLevel(data.get("access_level", AccessLevel.ALL_FTE.value)),
        author=data.get("author", ""),
        created=data.get("created"),
        modified=data.get("modified"),
        fetched=data.get("fetched"),
        language=data.get("language", "en"),
        tags=list(data.get("tags") or []),
        redacted_fields=list(data.get("redacted_fields") or []),
        extra=extra,
    )
