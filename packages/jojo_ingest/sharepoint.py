"""SharePoint connector — walks configured sites via MS Graph.

Design (see ADR 0005 for the eventual service-account posture, ADR 0007 for
the three-path auth strategy and the delegated-token dev mode this uses
today):

  1. Take a list of SharePoint site URLs (e.g.
     `https://nurix.sharepoint.com/sites/ProteinScience`) + a `GraphClient`.
  2. For each site, resolve it to a Graph site ID, then walk every drive
     (document library) rooted at that site.
  3. For each drive item that looks like a knowledge file (supported
     extension, under the size limit), download it, hand it to the
     file-type converter, and emit a `SourceEntry`.
  4. Any item that's a folder gets recursed into. Office lock files (`~$…`)
     and SharePoint internals (Forms/) are filtered at the name level before
     any download happens.

The connector doesn't know or care about auth — it gets a token-providing
`GraphClient` from the caller. That lets the same code serve Path A
(pasted delegated token), Path B (MSAL device-code flow), and Path C
(client-credentials service account) without branching.

Incremental sync: V1 walks every item and relies on the driver's SHA256
hash check to deduplicate on re-runs. That's O(all-items-in-site) per
sync. Phase 1c swaps this for Graph's `/drives/{id}/root/delta` endpoint
which returns only changes since the last delta token — order-of-magnitude
cheaper for scheduled runs. Delta isn't here yet because it needs a
delta-token store, which we don't have a home for until Phase 3.

Access level: SharePoint ACLs are non-trivial (group membership,
inheritance, sharing links). We punt on per-item ACL resolution for V1 and
take a single `access_level` parameter that applies to every item this
connector ingests — typically `"all_fte"`. Phase 7b will replace this with
a per-item ACL readout via the item's `permissions` relationship.
"""

from __future__ import annotations

import logging
import tempfile
from collections.abc import Iterable, Iterator
from datetime import datetime
from pathlib import Path
from typing import Any

from jojo_connectors_common import Connector, IngestError, SourceEntry
from jojo_core import config
from jojo_ingest.converters import ConverterNotFound, convert, is_supported
from jojo_ingest.graph import GraphClient, SiteRef, env_token_provider, normalize_site_url

log = logging.getLogger(__name__)

# Skip names that come out of SharePoint but aren't knowledge content. These
# match against the bare item name (not the path), so "Forms" matches any
# folder literally named "Forms" (SharePoint's system folder).
_SKIP_NAMES: set[str] = {"Forms", "_private", "_catalogs"}
_SKIP_PREFIXES: tuple[str, ...] = ("~$",)   # Office lock files


class SharePointConnector(Connector):
    source_type = "sharepoint"

    def __init__(
        self,
        site_urls: list[str],
        *,
        client: GraphClient,
        access_level: str = "all_fte",
        max_size_mb: int = 50,
        owns_client: bool = False,
    ) -> None:
        if not site_urls:
            raise IngestError("SharePointConnector: site_urls must contain at least one URL")
        self.site_refs: list[SiteRef] = [normalize_site_url(u) for u in site_urls]
        self.client = client
        self.access_level = access_level
        self.max_bytes = max_size_mb * 1024 * 1024
        self._owns_client = owns_client

    # ------------------------------------------------------------------ fetch
    def fetch(self, *, since: datetime | None = None) -> Iterable[SourceEntry]:
        for ref in self.site_refs:
            try:
                yield from self._fetch_site(ref, since=since)
            except IngestError as exc:
                # One bad site shouldn't poison the others — log and move on.
                log.warning("skipping site %s: %s", ref.original_url, exc)
                continue

    def close(self) -> None:
        if self._owns_client:
            self.client.close()

    # ----------------------------------------------------------- per-site walk
    def _fetch_site(self, ref: SiteRef, *, since: datetime | None) -> Iterator[SourceEntry]:
        site = self.client.resolve_site(ref.original_url)
        site_id = site["id"]
        site_display = site.get("displayName") or site.get("name") or ref.server_relative_path
        log.info("walking site: %s (%s)", site_display, ref.server_relative_path)

        # A single SharePoint site can host multiple document libraries
        # (Drives in Graph terms). Walk every drive so we don't miss the
        # "Chemistry" library sitting next to the default "Documents".
        for drive in self.client.iter_collection(f"/sites/{site_id}/drives"):
            drive_id = drive["id"]
            drive_name = drive.get("name") or "Documents"
            yield from self._walk_drive(
                ref=ref,
                site_id=site_id,
                site_display=site_display,
                drive_id=drive_id,
                drive_name=drive_name,
                item_id="root",
                path_prefix=drive_name,
                since=since,
            )

    def _walk_drive(
        self,
        *,
        ref: SiteRef,
        site_id: str,
        site_display: str,
        drive_id: str,
        drive_name: str,
        item_id: str,
        path_prefix: str,
        since: datetime | None,
    ) -> Iterator[SourceEntry]:
        # Graph's children endpoint for root vs. a specific folder has two
        # different path shapes — handle both.
        if item_id == "root":
            children_path = f"/drives/{drive_id}/root/children"
        else:
            children_path = f"/drives/{drive_id}/items/{item_id}/children"

        for item in self.client.iter_collection(children_path):
            name = item.get("name") or ""
            if self._should_skip_name(name):
                continue
            if "folder" in item:
                yield from self._walk_drive(
                    ref=ref,
                    site_id=site_id,
                    site_display=site_display,
                    drive_id=drive_id,
                    drive_name=drive_name,
                    item_id=item["id"],
                    path_prefix=f"{path_prefix}/{name}",
                    since=since,
                )
                continue
            if "file" not in item:
                # Could be a OneNote notebook or something else — skip.
                continue
            entry = self._build_entry(
                item=item,
                ref=ref,
                site_id=site_id,
                site_display=site_display,
                drive_id=drive_id,
                drive_name=drive_name,
                path_prefix=path_prefix,
                since=since,
            )
            if entry is not None:
                yield entry

    # ------------------------------------------------------------ per-file build
    def _build_entry(
        self,
        *,
        item: dict[str, Any],
        ref: SiteRef,
        site_id: str,
        site_display: str,
        drive_id: str,
        drive_name: str,
        path_prefix: str,
        since: datetime | None,
    ) -> SourceEntry | None:
        name = item["name"]
        ext = Path(name).suffix.lower().lstrip(".")
        if not is_supported(name):
            log.debug("unsupported ext, skipping: %s", name)
            return None
        size = int(item.get("size") or 0)
        if size > self.max_bytes:
            log.info("skipping %s: %d bytes > max_size %d", name, size, self.max_bytes)
            return None
        modified = _parse_iso(item.get("lastModifiedDateTime"))
        created = _parse_iso(item.get("createdDateTime"))
        if since is not None and modified is not None and modified < since:
            return None

        # Prefer the pre-signed downloadUrl when Graph gives us one (avoids a
        # second auth round-trip); otherwise fall back to the /content endpoint.
        download_url = item.get("@microsoft.graph.downloadUrl")
        if download_url:
            blob = self.client.download_bytes(download_url)
        else:
            blob = self.client.download_bytes(f"/drives/{drive_id}/items/{item['id']}/content")

        # Converters take a Path, so we materialize bytes to a NamedTemp with
        # the real extension preserved. The converter dispatches on suffix.
        try:
            with tempfile.NamedTemporaryFile(suffix=f".{ext}" if ext else "", delete=False) as tmp:
                tmp.write(blob)
                tmp_path = Path(tmp.name)
            try:
                body = convert(tmp_path)
            except ConverterNotFound:
                return None
            except Exception as exc:  # noqa: BLE001
                log.warning("failed to convert %s: %s", name, exc)
                return None
            finally:
                try:
                    tmp_path.unlink()
                except OSError:
                    pass
        except OSError as exc:
            log.warning("tempfile failure for %s: %s", name, exc)
            return None

        source_id = f"{site_display}/{path_prefix}/{name}"
        # item.webUrl is the browsable URL; item.id the stable Graph ID.
        source_url = item.get("webUrl") or (
            f"{_origin(ref)}{ref.server_relative_path}/{path_prefix}/{name}"
        )
        author = _extract_author(item)

        return SourceEntry(
            source_type=self.source_type,
            source_id=source_id,
            source_url=source_url,
            title=Path(name).stem,
            content=body,
            access_level=self.access_level,
            author=author,
            created=created,
            modified=modified,
            tags=[],
            extra={
                "graph_item_id": item["id"],
                "graph_drive_id": drive_id,
                "graph_site_id": site_id,
                "site_display": site_display,
                "drive_name": drive_name,
            },
        )

    # ---------------------------------------------------------------- helpers
    @staticmethod
    def _should_skip_name(name: str) -> bool:
        if not name:
            return True
        if name in _SKIP_NAMES:
            return True
        return any(name.startswith(p) for p in _SKIP_PREFIXES)


# ------------------------------------------------------------ tiny utils


def _parse_iso(s: str | None) -> datetime | None:
    if not s:
        return None
    # Graph returns ISO-8601 with a trailing 'Z'. datetime.fromisoformat can't
    # handle 'Z' until 3.11 — normalize to +00:00 for 3.10 compat.
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None


def _extract_author(item: dict[str, Any]) -> str:
    """Pick a display-name string out of Graph's createdBy/lastModifiedBy block."""
    for key in ("lastModifiedBy", "createdBy"):
        block = item.get(key) or {}
        user = block.get("user") or {}
        name = user.get("displayName") or user.get("email")
        if name:
            return str(name)
    return ""


def _origin(ref: SiteRef) -> str:
    """Reconstruct the scheme+host for the site's URL (for fallback webUrl construction)."""
    # original_url is guaranteed to start with http(s):// per normalize_site_url.
    from urllib.parse import urlparse

    p = urlparse(ref.original_url)
    return f"{p.scheme}://{p.netloc}"


# ----------------------------------------------------------- env-driven factory


# Comma-separated list of SharePoint site URLs to ingest. Set in the user's
# environment (or CLI flag) rather than committed anywhere — the list is
# tenant-specific.
ENV_SITES = "JOJO_SHAREPOINT_SITES"
ENV_TOKEN = "JOJO_GRAPH_ACCESS_TOKEN"


class SharePointEnvError(IngestError):
    """Raised when the env-driven factory can't assemble a connector.

    Separate class so the CLI + router can map it to an actionable 400
    instead of the generic 500 that bare IngestError would produce.
    """


def build_sharepoint_connector_from_env(
    *,
    access_level: str = "all_fte",
    max_size_mb: int = 50,
    site_urls_override: list[str] | None = None,
    token_override: str | None = None,
) -> SharePointConnector:
    """Assemble a ready-to-run SharePointConnector from env vars.

    Both the CLI (`jojo-ingest sync sharepoint`) and the backend router
    (`POST /api/ingest/sync/sharepoint`) call into here, so the
    "what env vars do I need" UX is consistent across surfaces. If
    anything's missing we raise `SharePointEnvError` with a message that
    names the exact env var to set.

    Passing `site_urls_override` or `token_override` skips the env lookup
    for that piece — useful for one-off CLI invocations that don't want to
    pollute the shell.
    """
    # Resolve site list. Reads config.json (`sharepoint_sites`) first and
    # falls back to $JOJO_SHAREPOINT_SITES; either is accepted.
    if site_urls_override:
        site_urls = list(site_urls_override)
    else:
        raw = (config.get(config.KEY_SHAREPOINT_SITES, "") or "").strip()
        if not raw:
            raise SharePointEnvError(
                "SharePoint site list is not configured. Run "
                '`jojo-core config set sharepoint_sites "https://nurix.sharepoint.com/sites/ProteinScience,'
                'https://nurix.sharepoint.com/sites/NurixNet"` '
                f"or set ${ENV_SITES} in the shell."
            )
        site_urls = [s.strip() for s in raw.split(",") if s.strip()]
    if not site_urls:
        raise SharePointEnvError(f"{ENV_SITES} was set but parsed to an empty list")

    # Resolve token. env_token_provider reads config.json first (via
    # config.get) and falls back to the env var, so scheduled runs pick up
    # tokens rotated via `jojo-core config set graph_access_token ...`.
    if token_override:
        token_provider = lambda: token_override   # noqa: E731 — trivial closure
    else:
        token_provider = env_token_provider(ENV_TOKEN)
        # Eagerly check so we fail fast before any Graph call.
        try:
            token_provider()
        except IngestError as exc:
            raise SharePointEnvError(str(exc)) from exc

    client = GraphClient(token_provider)
    return SharePointConnector(
        site_urls,
        client=client,
        access_level=access_level,
        max_size_mb=max_size_mb,
        owns_client=True,   # we built the client, we're responsible for closing it
    )
