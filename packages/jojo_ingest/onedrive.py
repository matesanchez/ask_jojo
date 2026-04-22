"""OneDrive connector — stub pending MS Graph app registration.

Same backend as SharePoint (MS Graph), different scopes and different
traversal root. The production implementation will share most of its code
with sharepoint.py via a `packages/jojo_ingest/_msgraph.py` helper module.

Required scopes: `Files.Read` (user scope). Device-code flow on first run,
refresh-token caching via DPAPI afterwards.

Because OneDrive is per-user, privacy model differs from SharePoint:
`access_level` should be `restricted` by default with `acl` listing the user
whose OneDrive was crawled. The absorb pipeline later decides whether the
entry is wiki-worthy at all — a lot of OneDrive content is personal.
"""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime

from jojo_connectors_common import Connector, SourceEntry


class OneDriveConnector(Connector):
    source_type = "onedrive"

    def __init__(self, *, client_id: str = "", user_upn: str = "") -> None:
        self.client_id = client_id
        self.user_upn = user_upn

    def fetch(self, *, since: datetime | None = None) -> Iterable[SourceEntry]:
        raise NotImplementedError(
            "OneDrive connector is not wired yet. Blocked on MS Graph app "
            "registration (same IT ticket as SharePoint). See "
            "packages/jojo_ingest/onedrive.py docstring for the plan."
        )
