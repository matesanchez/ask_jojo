"""SharePoint connector — stub pending MS Graph app registration.

When the IT ticket lands (see `docs/ADR/0005-jojo-bot-service-account.md`
Phase 7b plan) this file gets filled in with:

  1. msgraph-core client built from `azure.identity.DefaultAzureCredential` or
     a device-code flow for local-first mode (per ADR 0004).
  2. Site/drive/item traversal: `/sites/{site-id}/drives/{drive-id}/root/children`
     recursively. Use `$expand=children(...)` and `$delta` on subsequent runs.
  3. Per-file conversion via `jojo_ingest.converters.convert()` after downloading
     the binary to a temp path.
  4. ACL readout from the item's `permissions` relationship → `access_level`
     mapped via `packages/jojo_connectors_common/acl.py` (TODO: write this module
     when we know the shape of Nurix's SharePoint permissions).
  5. Rate-limit handling: 429 / 503 with exponential backoff, honor
     `Retry-After` header, stagger across sites.

Required scopes (app-only token): `Files.Read.All`, `Sites.Read.All`.
Secrets live under `%APPDATA%\\JojoBot\\config.json` (DPAPI-encrypted per
ADR 0004).

Until credentials arrive, instantiating this connector raises NotImplementedError.
Interface-conformance tests assert the class exists, matches `source_type`,
and fails loudly rather than silently.
"""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime

from jojo_connectors_common import Connector, SourceEntry


class SharePointConnector(Connector):
    source_type = "sharepoint"

    def __init__(
        self,
        *,
        tenant_id: str = "",
        client_id: str = "",
        client_secret: str = "",
        site_ids: list[str] | None = None,
    ) -> None:
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.site_ids = list(site_ids or [])

    def fetch(self, *, since: datetime | None = None) -> Iterable[SourceEntry]:
        raise NotImplementedError(
            "SharePoint connector is not wired yet. Blocked on MS Graph app "
            "registration (IT ticket). See packages/jojo_ingest/sharepoint.py "
            "docstring for the implementation plan."
        )
