"""Base `Connector` interface every ingest source implements.

Design notes (read before adding a connector):

- A connector's job is to *fetch and normalize*, not to decide policy. The
  redaction pass, the manifest write, and the on-disk layout are handled by
  the shared ingest driver so all connectors behave identically downstream.

- Connectors yield `SourceEntry` objects. The driver turns each entry into a
  raw .md file (frontmatter + body), runs redaction, updates the manifest,
  and emits a change record.

- Idempotency is enforced at the driver level via SHA256 comparison. A
  connector doesn't need to track what it has already ingested — it can
  re-emit the same entry on every run and the driver will skip writes that
  don't change content.

- `--incremental` / `--since` is advisory. Connectors that can filter on the
  source side (SharePoint delta queries) should; connectors that can't
  (local drive walker) are free to yield every entry and let the hash check
  deduplicate.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


class IngestError(Exception):
    """Raised by connectors when a source can't be fetched.

    Non-fatal — the driver logs and moves on. Use for per-entry failures
    (single file unreadable, auth refused for one item). For connector-wide
    failures (wrong credentials, source offline) raise a subclass or let
    the underlying exception propagate; the driver will mark the connector
    as failed in the Ops tab.
    """


@dataclass(slots=True)
class SourceEntry:
    """One logical unit of source content.

    The `content` field is the normalized markdown body (no frontmatter — the
    driver adds it). `body_bytes` is populated when the original is binary
    and no markdown normalization is available yet (e.g. an image); callers
    can decide whether to fall back to filesystem storage.
    """

    source_type: str
    source_id: str              # Stable identifier on the source side (URL, file path, item-id)
    source_url: str
    title: str
    content: str                # Markdown body
    access_level: str = "all_fte"
    author: str = ""
    created: datetime | None = None
    modified: datetime | None = None
    language: str = "en"
    tags: list[str] = field(default_factory=list)
    body_bytes: bytes | None = None   # Optional: original bytes for binary-only sources
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ConnectorResult:
    """Summary of one connector's run — surfaced in the Ops tab."""

    source_type: str
    added: int = 0
    updated: int = 0
    skipped: int = 0
    errors: int = 0
    failures: list[str] = field(default_factory=list)


class Connector(ABC):
    """Abstract base. Every connector subclasses this and implements `fetch`."""

    source_type: str = ""   # Override in subclass; must match SourceType enum value

    @abstractmethod
    def fetch(self, *, since: datetime | None = None) -> Iterable[SourceEntry]:
        """Yield `SourceEntry` objects for this connector.

        - `since`: optional cutoff for incremental sync. Connectors that can
          honor it should; others should yield everything and rely on the
          driver's hash check for deduplication.
        """

    def close(self) -> None:  # noqa: B027 — optional hook, default is intentionally a no-op
        """Release any held resources (Graph SDK clients, browser contexts).

        Default is a no-op. Connectors that hold clients, HTTP pools, or
        browser contexts override this to release them.
        """
