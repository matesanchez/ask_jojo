"""Microsoft Graph HTTP wrapper used by the SharePoint + OneDrive connectors.

Why a thin httpx wrapper instead of `msgraph-core` / `msgraph-sdk`:

  - Those SDKs are heavy (tens of MB of generated code), hard to mock, and
    churn fast. We need exactly three call shapes (paged JSON GET, single
    JSON GET, raw byte download). httpx handles that in ~200 lines, tests
    cleanly with `pytest-httpx`, and doesn't pin us to a specific SDK
    generator.
  - The interesting complexity is auth, paging, throttling, and the
    `/sites/{hostname}:{path}` site-resolution dance — none of which the SDK
    simplifies meaningfully.

Auth abstraction: the client takes a `TokenProvider`, which is any callable
returning a bearer token string when invoked. That lets us swap three
credential flows behind one interface:

  - Path A (today): `env_token_provider()` returns whatever was pasted into
    `JOJO_GRAPH_ACCESS_TOKEN`. ~60 min token lifetime, human-in-the-loop.
  - Path B (next): `msal_device_code_provider()` wraps an MSAL
    `PublicClientApplication` with token caching to disk.
  - Path C (eventual): `msal_client_credentials_provider()` wraps a
    `ConfidentialClientApplication` with a cert/secret. Requires a real app
    registration with admin-consented app permissions.

Throttling: Graph returns 429 + `Retry-After` seconds. We honor the header
and retry up to 3 times with a capped backoff. Beyond that we raise so the
driver can mark the connector as failed rather than spinning forever.
"""

from __future__ import annotations

import logging
import os
import time
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote, urlparse

import httpx

from jojo_connectors_common import IngestError

log = logging.getLogger(__name__)

# Callable returning a bearer token. Re-invoked on every request so providers
# that refresh tokens transparently (MSAL) stay fresh; the env-var provider
# just re-reads each call.
TokenProvider = Callable[[], str]

GRAPH_BASE = "https://graph.microsoft.com/v1.0"
DEFAULT_TIMEOUT = 30.0
MAX_RETRIES = 3


# ---------------------------------------------------------------- auth providers


def env_token_provider(var: str = "JOJO_GRAPH_ACCESS_TOKEN") -> TokenProvider:
    """Path A auth: read a Graph Explorer-issued bearer token.

    Token is re-read on every call so rotating the source (env var or
    config.json) takes effect immediately without restarting the process.

    When ``var`` is the default "JOJO_GRAPH_ACCESS_TOKEN", we read via
    ``jojo_core.config.get(KEY_GRAPH_ACCESS_TOKEN)``, which checks
    config.json first and falls back to the env var. Scheduled runs pick
    up tokens rotated via ``jojo-core config set graph_access_token ...``
    without needing a shell env export. Non-default ``var`` names keep
    the legacy env-only behavior (useful in tests).
    """
    from jojo_core import config

    def _get() -> str:
        if var == "JOJO_GRAPH_ACCESS_TOKEN":
            tok = (config.get(config.KEY_GRAPH_ACCESS_TOKEN, "") or "").strip()
        else:
            tok = os.environ.get(var, "").strip()
        if not tok:
            raise IngestError(
                f"Graph access token is not configured. Either run "
                f'`jojo-core config set graph_access_token "eyJ..."`, '
                f"set ${var} in the shell (paste from Graph Explorer's "
                "Access token tab), or switch to MSAL device-code auth."
            )
        return tok

    return _get


# ---------------------------------------------------------------- site resolution


@dataclass(slots=True, frozen=True)
class SiteRef:
    """Parsed SharePoint site URL ready to feed to Graph's path-style lookup.

    Graph resolves sites via `/sites/{hostname}:{server-relative-path}` which
    needs the pieces separated — not the raw URL. `normalize_site_url` does
    that split + tolerates trailing page-level paths like `/SitePages/Home.aspx`
    or a stray trailing slash.
    """

    hostname: str
    server_relative_path: str   # always starts with "/", no trailing slash
    original_url: str


def normalize_site_url(site_url: str) -> SiteRef:
    """Parse a SharePoint site URL into a SiteRef.

    Examples:
      https://nurix.sharepoint.com/sites/ProteinScience
      → SiteRef("nurix.sharepoint.com", "/sites/ProteinScience", ...)

      https://nurix.sharepoint.com/sites/Biortus/SitePages/Home.aspx
      → SiteRef("nurix.sharepoint.com", "/sites/Biortus", ...)  # page URL stripped

      https://tenant.sharepoint.com/teams/Foo/
      → SiteRef("tenant.sharepoint.com", "/teams/Foo", ...)  # trailing / stripped
    """
    parsed = urlparse(site_url.strip())
    if not parsed.scheme.startswith("http") or not parsed.netloc:
        raise IngestError(f"not a valid SharePoint site URL: {site_url!r}")
    path = parsed.path.rstrip("/") or "/"
    # Strip anything from /SitePages/ or /Shared%20Documents/ onward — we want
    # the site root, the drive walk finds libraries from there.
    lowered = path.lower()
    for marker in ("/sitepages/", "/shared documents/", "/shared%20documents/"):
        idx = lowered.find(marker)
        if idx > 0:
            path = path[:idx]
            break
    if not path.startswith("/"):
        path = "/" + path
    return SiteRef(hostname=parsed.netloc, server_relative_path=path, original_url=site_url)


# ------------------------------------------------------------------- Graph client


class GraphError(IngestError):
    """Raised for non-retryable Graph errors (401, 403, 404, schema surprises)."""


class GraphClient:
    """Small, test-friendly Graph v1.0 HTTP wrapper.

    Lifetime: build one per ingest run, pass to each connector that needs it,
    `close()` when done. Connectors don't share state through the client —
    it's stateless beyond the underlying httpx session.
    """

    def __init__(
        self,
        token_provider: TokenProvider,
        *,
        base_url: str = GRAPH_BASE,
        client: httpx.Client | None = None,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self._token = token_provider
        self._base = base_url.rstrip("/")
        # Allow a pre-built client (tests use pytest-httpx's mock transport).
        self._client = client or httpx.Client(timeout=timeout, follow_redirects=True)
        self._owns_client = client is None

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    # --------------------------------------------------------- low-level request
    def _request(
        self,
        method: str,
        path_or_url: str,
        *,
        params: dict[str, Any] | None = None,
        stream: bool = False,
    ) -> httpx.Response:
        url = path_or_url if path_or_url.startswith("http") else self._base + path_or_url
        for attempt in range(MAX_RETRIES + 1):
            token = self._token()
            headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
            try:
                if stream:
                    # Graph returns a 302 to a pre-signed CDN URL for content
                    # downloads. httpx's follow_redirects=True handles the
                    # redirect; Authorization is stripped on redirect per
                    # httpx's default, which is actually what we want (the
                    # CDN URL is already signed).
                    req = self._client.build_request(method, url, params=params, headers=headers)
                    resp = self._client.send(req)
                else:
                    resp = self._client.request(method, url, params=params, headers=headers)
            except httpx.TransportError as exc:
                # Transport-level failure before we got any HTTP response back.
                # Covers httpx.ConnectError (e.g. WinError 10054 "connection
                # forcibly closed"), ReadTimeout, RemoteProtocolError, etc.
                # The corporate network + Graph's pre-signed CDN URLs seem to
                # drop idle TLS connections occasionally; a short backoff and
                # retry almost always succeeds.
                if attempt >= MAX_RETRIES:
                    raise GraphError(
                        f"Graph transport error after {MAX_RETRIES + 1} attempts for "
                        f"{method} {url}: {exc.__class__.__name__}: {exc}"
                    ) from exc
                delay = min(2.0**attempt, 30.0)
                log.warning(
                    "Graph transport error (%s: %s). Sleeping %.1fs then retrying (attempt %d/%d).",
                    exc.__class__.__name__, exc, delay, attempt + 1, MAX_RETRIES,
                )
                time.sleep(delay)
                continue
            if resp.status_code == 429 or resp.status_code == 503:
                if attempt >= MAX_RETRIES:
                    break
                delay = _parse_retry_after(resp.headers.get("Retry-After"), attempt)
                log.warning("Graph throttled (%s). Sleeping %.1fs then retrying.", resp.status_code, delay)
                time.sleep(delay)
                continue
            if resp.status_code == 401:
                # 401 on Graph has two common causes and the remediation differs:
                #   (a) token lifetime exceeded (~60 min) -- rotate the token
                #   (b) token lacks the scope the endpoint requires -- e.g.
                #       SharePoint site resolution needs Sites.Read.All, which
                #       Graph Explorer does NOT consent to by default. A fresh
                #       token that still 401s on every site is almost always
                #       this case. Fix: Graph Explorer -> Modify permissions ->
                #       consent to Sites.Read.All, sign out + back in, re-mint.
                # We don't parse WWW-Authenticate here (Graph's format is
                # inconsistent across endpoints); caller gets both hypotheses.
                raise GraphError(
                    f"Graph returned 401 Unauthorized for {method} {url}. "
                    "Either the token has expired (~60-min lifetime -- paste "
                    "a fresh one) OR it lacks the scope this endpoint requires "
                    "(e.g. Sites.Read.All for SharePoint sites). Decode the "
                    "token at https://jwt.ms and inspect the 'scp' claim to "
                    "tell the two apart."
                )
            if resp.status_code == 403:
                raise GraphError(
                    f"Graph returned 403 Forbidden for {method} {url}. "
                    "Token lacks the required scope, or you don't have read "
                    "access to that site/drive/item."
                )
            return resp
        raise GraphError(
            f"Graph throttled {MAX_RETRIES} times in a row for {method} {url}. Giving up."
        )

    # -------------------------------------------------------------- json helpers
    def get_json(self, path: str, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        resp = self._request("GET", path, params=params)
        if resp.status_code == 404:
            raise GraphError(f"Graph 404 for {path}. Resource doesn't exist or isn't visible to you.")
        if resp.status_code >= 400:
            raise GraphError(f"Graph {resp.status_code} for {path}: {resp.text[:300]}")
        return resp.json()

    def iter_collection(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> Iterator[dict[str, Any]]:
        """Yield every item in an OData collection, following `@odata.nextLink`.

        Works for `/sites/{id}/drives`, `/drives/{id}/root/children`,
        `/drives/{id}/root/delta`, anything that returns `{value: [...], @odata.nextLink: ...}`.
        """
        page = self.get_json(path, params=params)
        while True:
            yield from page.get("value", [])
            next_link = page.get("@odata.nextLink")
            if not next_link:
                return
            page = self.get_json(next_link)

    # -------------------------------------------------------- content download
    def download_bytes(self, content_url_or_path: str) -> bytes:
        """Download a drive item's content as raw bytes.

        Accepts either a Graph path (`/drives/{id}/items/{id}/content`) or an
        already-resolved `@microsoft.graph.downloadUrl` (which is a pre-signed
        URL pointing at the SharePoint CDN, not a Graph endpoint).
        """
        resp = self._request("GET", content_url_or_path, stream=True)
        if resp.status_code >= 400:
            raise GraphError(
                f"Graph content download failed ({resp.status_code}) for {content_url_or_path}"
            )
        return resp.content

    # ------------------------------------------------------ site resolution
    def resolve_site(self, site_url: str) -> dict[str, Any]:
        """Resolve a SharePoint site URL to its Graph site record.

        Uses the path-style lookup: `/sites/{hostname}:{server-relative-path}`.
        Returns the full site object; caller typically just needs `["id"]`.
        """
        ref = normalize_site_url(site_url)
        # Graph expects the path as-is (no URL-encoding of the leading `:`),
        # but we do encode any spaces or non-ASCII in the server-relative path.
        encoded_path = quote(ref.server_relative_path, safe="/")
        path = f"/sites/{ref.hostname}:{encoded_path}"
        return self.get_json(path)


# ----------------------------------------------------------------- internals


def _parse_retry_after(header: str | None, attempt: int) -> float:
    """Parse `Retry-After` (seconds or HTTP-date). Fall back to exp backoff."""
    if header:
        try:
            return float(header)
        except ValueError:
            pass  # HTTP-date form is rare in Graph; fall through to backoff.
    return min(2.0**attempt, 30.0)
