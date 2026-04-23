"""GraphClient unit tests — no live Graph calls.

pytest-httpx intercepts every outbound httpx request made during a test, so
we can assert on exact request shapes (URL, headers, params) and hand back
canned responses. Keeps the test suite credential-free and fast.
"""

from __future__ import annotations

import pytest

from jojo_connectors_common import IngestError
from jojo_ingest.graph import (
    GRAPH_BASE,
    GraphClient,
    GraphError,
    env_token_provider,
    normalize_site_url,
)

# ---------------------------------------------------------------- URL parsing


def test_normalize_site_url_basic():
    ref = normalize_site_url("https://nurix.sharepoint.com/sites/ProteinScience")
    assert ref.hostname == "nurix.sharepoint.com"
    assert ref.server_relative_path == "/sites/ProteinScience"


def test_normalize_site_url_strips_sitepages_home():
    ref = normalize_site_url(
        "https://nurix.sharepoint.com/sites/BiortusDiscoveryCo.Ltd/SitePages/Home.aspx"
    )
    assert ref.server_relative_path == "/sites/BiortusDiscoveryCo.Ltd"


def test_normalize_site_url_strips_trailing_slash():
    ref = normalize_site_url("https://tenant.sharepoint.com/teams/Foo/")
    assert ref.server_relative_path == "/teams/Foo"


def test_normalize_site_url_rejects_invalid():
    with pytest.raises(IngestError):
        normalize_site_url("not-a-url")


# ------------------------------------------------------------- env token provider


def test_env_token_provider_raises_when_unset(monkeypatch):
    monkeypatch.delenv("JOJO_GRAPH_ACCESS_TOKEN", raising=False)
    provider = env_token_provider()
    with pytest.raises(IngestError) as exc:
        provider()
    assert "JOJO_GRAPH_ACCESS_TOKEN" in str(exc.value)


def test_env_token_provider_returns_value(monkeypatch):
    monkeypatch.setenv("JOJO_GRAPH_ACCESS_TOKEN", "eyJ.stubbed.token")
    provider = env_token_provider()
    assert provider() == "eyJ.stubbed.token"


# -------------------------------------------------------------- GraphClient auth


def test_client_sends_bearer_token(httpx_mock):
    httpx_mock.add_response(
        url=f"{GRAPH_BASE}/me",
        json={"id": "user-123", "displayName": "Mateo"},
    )
    client = GraphClient(lambda: "TOKEN-XYZ")
    try:
        result = client.get_json("/me")
    finally:
        client.close()

    assert result == {"id": "user-123", "displayName": "Mateo"}
    req = httpx_mock.get_requests()[0]
    assert req.headers["Authorization"] == "Bearer TOKEN-XYZ"


def test_client_401_raises_graph_error_with_helpful_message(httpx_mock):
    httpx_mock.add_response(url=f"{GRAPH_BASE}/me", status_code=401, json={"error": "expired"})
    client = GraphClient(lambda: "EXPIRED")
    with pytest.raises(GraphError) as exc:
        client.get_json("/me")
    client.close()
    msg = str(exc.value).lower()
    assert "401" in msg
    assert "token" in msg


def test_client_403_raises_graph_error_with_scope_hint(httpx_mock):
    httpx_mock.add_response(
        url=f"{GRAPH_BASE}/sites/nope", status_code=403, json={"error": "forbidden"}
    )
    client = GraphClient(lambda: "TOKEN")
    with pytest.raises(GraphError) as exc:
        client.get_json("/sites/nope")
    client.close()
    assert "403" in str(exc.value)


# ------------------------------------------------------------- retry + paging


def test_client_retries_on_429(httpx_mock, monkeypatch):
    # Zero-out the sleep so the retry path is still exercised without waiting.
    import time

    monkeypatch.setattr(time, "sleep", lambda _s: None)

    httpx_mock.add_response(
        url=f"{GRAPH_BASE}/me",
        status_code=429,
        headers={"Retry-After": "1"},
        json={"error": {"code": "TooManyRequests"}},
    )
    httpx_mock.add_response(
        url=f"{GRAPH_BASE}/me", json={"id": "user-123"}
    )

    client = GraphClient(lambda: "TOKEN")
    result = client.get_json("/me")
    client.close()
    assert result == {"id": "user-123"}
    assert len(httpx_mock.get_requests()) == 2


def test_client_gives_up_after_max_retries(httpx_mock, monkeypatch):
    import time

    monkeypatch.setattr(time, "sleep", lambda _s: None)
    # Four 429s → initial + 3 retries = 4 requests → final one still 429 → GraphError.
    for _ in range(4):
        httpx_mock.add_response(
            url=f"{GRAPH_BASE}/me",
            status_code=429,
            headers={"Retry-After": "0"},
            json={},
        )

    client = GraphClient(lambda: "TOKEN")
    with pytest.raises(GraphError) as exc:
        client.get_json("/me")
    client.close()
    assert "throttled" in str(exc.value).lower()


def test_iter_collection_follows_next_link(httpx_mock):
    # Graph paginates via `@odata.nextLink`. Our iterator should follow it
    # transparently and yield items from both pages in order.
    next_url = "https://graph.microsoft.com/v1.0/next-page-token-abc"
    httpx_mock.add_response(
        url=f"{GRAPH_BASE}/sites/abc/drives",
        json={
            "value": [{"id": "drive1"}, {"id": "drive2"}],
            "@odata.nextLink": next_url,
        },
    )
    httpx_mock.add_response(
        url=next_url,
        json={"value": [{"id": "drive3"}]},
    )
    client = GraphClient(lambda: "TOKEN")
    drives = list(client.iter_collection("/sites/abc/drives"))
    client.close()
    assert [d["id"] for d in drives] == ["drive1", "drive2", "drive3"]


# ---------------------------------------------------------------- site resolution


def test_resolve_site_builds_path_style_lookup(httpx_mock):
    httpx_mock.add_response(
        url=f"{GRAPH_BASE}/sites/nurix.sharepoint.com:/sites/ProteinScience",
        json={
            "id": "nurix.sharepoint.com,site-guid,web-guid",
            "displayName": "Protein Sciences",
            "webUrl": "https://nurix.sharepoint.com/sites/ProteinScience",
        },
    )
    client = GraphClient(lambda: "TOKEN")
    site = client.resolve_site("https://nurix.sharepoint.com/sites/ProteinScience")
    client.close()
    assert site["displayName"] == "Protein Sciences"
    assert site["id"].startswith("nurix.sharepoint.com,")


def test_resolve_site_strips_sitepages_before_lookup(httpx_mock):
    # The Biortus URL the user gave us ends in SitePages/Home.aspx — the
    # lookup must target the site root, not the page.
    httpx_mock.add_response(
        url=f"{GRAPH_BASE}/sites/nurix.sharepoint.com:/sites/BiortusDiscoveryCo.Ltd",
        json={"id": "nurix.sharepoint.com,x,y", "displayName": "Biortus"},
    )
    client = GraphClient(lambda: "TOKEN")
    site = client.resolve_site(
        "https://nurix.sharepoint.com/sites/BiortusDiscoveryCo.Ltd/SitePages/Home.aspx"
    )
    client.close()
    assert site["displayName"] == "Biortus"
