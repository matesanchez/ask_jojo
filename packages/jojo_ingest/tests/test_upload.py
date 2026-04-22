from pathlib import Path

import pytest

from jojo_connectors_common import IngestError, Manifest
from jojo_ingest.driver import IngestDriver
from jojo_ingest.upload import UploadConnector


def test_upload_pipes_single_file(tmp_path: Path):
    src = tmp_path / "notes.md"
    src.write_text("# Upload Test\n\nShort body.\n", encoding="utf-8")
    raw = tmp_path / "ask_jojo_raw"

    conn = UploadConnector(src, title="Upload Test", author="Mateo", tags=["adhoc"])
    result = IngestDriver(raw).run([conn])

    cr = result.results["upload"]
    assert cr.added == 1
    manifest = Manifest.load(raw / "manifest.json")
    assert len(manifest.entries) == 1
    entry = next(iter(manifest.entries.values()))
    assert entry.source_type == "upload"
    assert entry.title == "Upload Test"


def test_upload_rejects_unsupported(tmp_path: Path):
    bad = tmp_path / "image.psd"
    bad.write_bytes(b"\x00\x00\x00\x00")
    with pytest.raises(IngestError):
        UploadConnector(bad)


def test_upload_missing_path_raises(tmp_path: Path):
    with pytest.raises(IngestError):
        UploadConnector(tmp_path / "does-not-exist.md")
