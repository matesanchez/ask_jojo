"""SharePointConnector end-to-end tests against a mocked Graph API.

We stub out every Graph response the connector issues — site resolution,
drive listing, children listing, content download — and assert the
connector emits well-formed `SourceEntry` objects for exactly the items
we expect. Covers:

  - Site resolution → drive walk → recursion into subfolders.
  - Filtering: `~$` lock files, SharePoint `Forms/` system folder,
    unsupported extensions, over-size items, pre-`since` modifications.
  - SourceEntry field population: title, source_id, author, modified,
    extras (graph_item_id / drive_id / site_id) propagated.
  - Graceful failure: a bad site gets logged and skipped without poisoning
    the other configured sites.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from jojo_connectors_common import IngestError
from jojo_ingest.driver import IngestDriver
from jojo_ingest.graph import GRAPH_BASE, GraphClient
from jojo_ingest.sharepoint import SharePointConnector

# ---------------------------------------------------------- fixtures & helpers

SITE_URL = "https://nurix.sharepoint.com/sites/ProteinScience"
SITE_PATH_LOOKUP = f"{GRAPH_BASE}/sites/nurix.sharepoint.com:/sites/ProteinScience"
SITE_ID = "nurix.sharepoint.com,siteguid,webguid"
DRIVE_ID = "b!drivetoken"


@pytest.fixture
def client():
    c = GraphClient(lambda: "TOKEN-TEST")
    yield c
    c.close()


def _file_item(
    name: str,
    *,
    item_id: str = "item-auto",
    size: int = 512,
    modified: str = "2026-04-10T12:00:00Z",
    created: str = "2026-04-01T09:00:00Z",
    author: str = "Mateo de los Rios",
    content: bytes = b"# Body\n\nHello world.\n",
) -> dict:
    # Shape matches Graph's drive-item JSON (minimum fields our code touches).
    return {
        "id": item_id,
        "name": name,
        "size": size,
        "lastModifiedDateTime": modified,
        "createdDateTime": created,
        "webUrl": f"https://nurix.sharepoint.com/sites/ProteinScience/Documents/{name}",
        "file": {"mimeType": "text/markdown"},
        "lastModifiedBy": {"user": {"displayName": author, "email": f"{author.lower()}@nurixtx.com"}},
        "@microsoft.graph.downloadUrl": f"https://nurix-cdn.example/{item_id}",
        "_content": content,   # internal marker — not part of Graph; used by the mock setup
    }


def _folder_item(name: str, *, item_id: str = "folder-auto", child_count: int = 1) -> dict:
    return {
        "id": item_id,
        "name": name,
        "folder": {"childCount": child_count},
    }


def _json_safe(items: list[dict]) -> list[dict]:
    """Strip private underscore-prefixed fields (like `_content`) before JSON-serializing."""
    return [{k: v for k, v in it.items() if not k.startswith("_")} for it in items]


def _register_site_drives(httpx_mock, *, drives=None, site_url=SITE_URL, site_id=SITE_ID):
    httpx_mock.add_response(
        url=SITE_PATH_LOOKUP,
        json={"id": site_id, "displayName": "Protein Sciences", "webUrl": site_url},
    )
    httpx_mock.add_response(
        url=f"{GRAPH_BASE}/sites/{site_id}/drives",
        json={"value": drives or [{"id": DRIVE_ID, "name": "Documents"}]},
    )


def _register_children(httpx_mock, drive_id: str, folder_id: str, children: list[dict]):
    if folder_id == "root":
        url = f"{GRAPH_BASE}/drives/{drive_id}/root/children"
    else:
        url = f"{GRAPH_BASE}/drives/{drive_id}/items/{folder_id}/children"
    httpx_mock.add_response(url=url, json={"value": _json_safe(children)})


def _register_downloads(httpx_mock, items: list[dict]):
    for item in items:
        httpx_mock.add_response(url=item["@microsoft.graph.downloadUrl"], content=item["_content"])


# ---------------------------------------------------------------- init tests


def test_connector_rejects_empty_site_urls(client):
    with pytest.raises(IngestError):
        SharePointConnector([], client=client)


def test_connector_source_type_is_sharepoint(client):
    conn = SharePointConnector([SITE_URL], client=client)
    assert conn.source_type == "sharepoint"


# ------------------------------------------------------------- end-to-end walk


def test_walk_yields_entries_for_supported_files(httpx_mock, client):
    _register_site_drives(httpx_mock)
    md_file = _file_item("recipe.md", item_id="file-md", content=b"# Recipe\n\nBody.\n")
    txt_file = _file_item("notes.txt", item_id="file-txt", content=b"plain text.\n")
    _register_children(httpx_mock, DRIVE_ID, "root", [md_file, txt_file])
    _register_downloads(httpx_mock, [md_file, txt_file])

    conn = SharePointConnector([SITE_URL], client=client)
    entries = list(conn.fetch())

    assert len(entries) == 2
    titles = sorted(e.title for e in entries)
    assert titles == ["notes", "recipe"]
    md = next(e for e in entries if e.title == "recipe")
    assert md.source_type == "sharepoint"
    assert "Protein Sciences" in md.source_id
    assert md.author == "Mateo de los Rios"
    assert md.extra["graph_item_id"] == "file-md"
    assert md.extra["graph_drive_id"] == DRIVE_ID
    assert md.extra["site_display"] == "Protein Sciences"


def test_walk_recurses_into_folders(httpx_mock, client):
    _register_site_drives(httpx_mock)
    folder = _folder_item("SOPs", item_id="folder-sop")
    top_file = _file_item("top.md", item_id="top", content=b"# Top\n")
    nested_file = _file_item("nested.md", item_id="nested", content=b"# Nested\n")
    _register_children(httpx_mock, DRIVE_ID, "root", [folder, top_file])
    _register_children(httpx_mock, DRIVE_ID, "folder-sop", [nested_file])
    _register_downloads(httpx_mock, [top_file, nested_file])

    conn = SharePointConnector([SITE_URL], client=client)
    entries = list(conn.fetch())
    assert len(entries) == 2
    nested = next(e for e in entries if e.title == "nested")
    # Folder segments land in source_id so supersedence + frontmatter match the tree.
    assert "SOPs" in nested.source_id


def test_walk_skips_lock_files_and_system_folders(httpx_mock, client):
    _register_site_drives(httpx_mock)
    real = _file_item("good.md", item_id="good", content=b"# Good\n")
    lock = _file_item("~$draft.docx", item_id="lock", content=b"lockfile")
    forms = _folder_item("Forms", item_id="forms-folder")
    _register_children(httpx_mock, DRIVE_ID, "root", [real, lock, forms])
    _register_downloads(httpx_mock, [real])   # lock + Forms must NOT be downloaded

    conn = SharePointConnector([SITE_URL], client=client)
    entries = list(conn.fetch())
    assert [e.title for e in entries] == ["good"]


def test_walk_skips_unsupported_extensions(httpx_mock, client):
    _register_site_drives(httpx_mock)
    good = _file_item("notes.md", item_id="good", content=b"# Notes\n")
    # No download URL registered for the unsupported file — if our skip logic
    # regresses and tries to download it, the mock will raise.
    img = _file_item("logo.png", item_id="img", content=b"\x89PNG...")
    _register_children(httpx_mock, DRIVE_ID, "root", [good, img])
    _register_downloads(httpx_mock, [good])

    conn = SharePointConnector([SITE_URL], client=client)
    entries = list(conn.fetch())
    assert [e.title for e in entries] == ["notes"]


def test_walk_respects_since_filter(httpx_mock, client):
    _register_site_drives(httpx_mock)
    old = _file_item("old.md", item_id="old", modified="2026-01-01T00:00:00Z", content=b"# Old\n")
    new = _file_item("new.md", item_id="new", modified="2026-04-15T00:00:00Z", content=b"# New\n")
    _register_children(httpx_mock, DRIVE_ID, "root", [old, new])
    _register_downloads(httpx_mock, [new])   # `old` falls below the cutoff before download

    conn = SharePointConnector([SITE_URL], client=client)
    cutoff = datetime(2026, 3, 1, tzinfo=timezone.utc)
    entries = list(conn.fetch(since=cutoff))
    assert [e.title for e in entries] == ["new"]


def test_walk_skips_oversize_files(httpx_mock, client):
    _register_site_drives(httpx_mock)
    small = _file_item("small.md", item_id="small", size=1024, content=b"# Small\n")
    huge = _file_item(
        "video.md",
        item_id="huge",
        size=200 * 1024 * 1024,   # 200 MB — over the 50 MB default
        content=b"...",
    )
    _register_children(httpx_mock, DRIVE_ID, "root", [small, huge])
    _register_downloads(httpx_mock, [small])   # huge must not be downloaded

    conn = SharePointConnector([SITE_URL], client=client, max_size_mb=50)
    entries = list(conn.fetch())
    assert [e.title for e in entries] == ["small"]


def test_bad_site_logged_and_skipped(httpx_mock, caplog):
    # One site 404s (wrong URL, user revoked access, etc.) — the connector
    # should log a warning and move on to the next configured site.
    good_url = SITE_URL
    bad_url = "https://nurix.sharepoint.com/sites/GhostSite"

    httpx_mock.add_response(
        url=f"{GRAPH_BASE}/sites/nurix.sharepoint.com:/sites/GhostSite",
        status_code=404,
        json={"error": {"code": "itemNotFound"}},
    )
    _register_site_drives(httpx_mock, site_url=good_url)
    md = _file_item("doc.md", item_id="only", content=b"# Doc\n")
    _register_children(httpx_mock, DRIVE_ID, "root", [md])
    _register_downloads(httpx_mock, [md])

    client = GraphClient(lambda: "TOKEN")
    conn = SharePointConnector([bad_url, good_url], client=client)
    with caplog.at_level("WARNING"):
        entries = list(conn.fetch())
    client.close()

    assert [e.title for e in entries] == ["doc"]
    assert any("GhostSite" in rec.message for rec in caplog.records)


# ------------------------------------------------------- IngestDriver integration


def test_driver_ingests_sharepoint_entries_into_manifest(httpx_mock, client, tmp_path: Path):
    # Full pipeline: SharePointConnector → IngestDriver → raw .md + manifest
    # gets a real entry on disk. This is the closest we get to end-to-end
    # without a live Graph token.
    _register_site_drives(httpx_mock)
    md = _file_item("buffer.md", item_id="file-buf", content=b"# Buffer\n\n100 mM Tris.\n")
    _register_children(httpx_mock, DRIVE_ID, "root", [md])
    _register_downloads(httpx_mock, [md])

    raw = tmp_path / "ask_jojo_raw"
    driver = IngestDriver(raw)
    conn = SharePointConnector([SITE_URL], client=client)
    result = driver.run([conn])

    cr = result.results["sharepoint"]
    assert cr.added == 1
    assert cr.errors == 0
    # Raw markdown landed with frontmatter pointing at sharepoint.
    files = list((raw / "sharepoint").glob("*.md"))
    assert len(files) == 1
    text = files[0].read_text(encoding="utf-8")
    assert "source_type: sharepoint" in text
    assert "sha256:" in text

    # Re-run is a no-op (idempotency check).
    _register_site_drives(httpx_mock)
    _register_children(httpx_mock, DRIVE_ID, "root", [md])
    _register_downloads(httpx_mock, [md])
    conn2 = SharePointConnector([SITE_URL], client=client)
    r2 = IngestDriver(raw).run([conn2])
    assert r2.results["sharepoint"].skipped == 1
    assert r2.results["sharepoint"].added == 0


# --------------------------------------------------------- sanity: since-after-all


def test_since_after_everything_yields_nothing(httpx_mock, client):
    _register_site_drives(httpx_mock)
    md = _file_item("doc.md", modified="2026-01-01T00:00:00Z", content=b"# Old\n")
    _register_children(httpx_mock, DRIVE_ID, "root", [md])
    # No download should happen — cutoff rejects before we fetch content.
    conn = SharePointConnector([SITE_URL], client=client)
    future = datetime.now(timezone.utc) + timedelta(days=365)
    entries = list(conn.fetch(since=future))
    assert entries == []
