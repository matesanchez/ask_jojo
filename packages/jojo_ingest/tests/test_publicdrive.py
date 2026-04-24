"""Tests for the public-drive connector (the P:\\ network drive on Windows).

Same shape as test_onedrive — PublicDriveConnector is a DriveConnector
subclass with source_type 'publicdrive' and an env-driven factory reading
JOJO_PUBLIC_DRIVE_PATH. See ADR 0008.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from jojo_ingest.publicdrive import (
    ENV_PATH,
    PublicDriveConnector,
    PublicDriveEnvError,
    build_publicdrive_connector_from_env,
)


@pytest.fixture
def pdrive_tree(tmp_path: Path) -> Path:
    root = tmp_path / "public"
    (root / "sops").mkdir(parents=True)
    (root / "sops" / "autoclave-procedure.md").write_text(
        "# Autoclave\n\nRun at 121 C for 20 min.\n", encoding="utf-8"
    )
    (root / "sops" / "gel-running.txt").write_text(
        "Use 1x TBE buffer.\n", encoding="utf-8"
    )
    return root


def test_source_type_is_publicdrive(pdrive_tree: Path):
    conn = PublicDriveConnector(pdrive_tree)
    assert conn.source_type == "publicdrive"


def test_connector_walks_mounted_drive(pdrive_tree: Path):
    conn = PublicDriveConnector(pdrive_tree)
    entries = list(conn.fetch())
    names = sorted(e.source_id for e in entries)
    assert names == ["sops/autoclave-procedure.md", "sops/gel-running.txt"]
    assert all(e.source_type == "publicdrive" for e in entries)


def test_env_factory_requires_env_var_on_non_windows(monkeypatch):
    """On macOS/Linux, no env var means we error — there's no sensible default."""
    monkeypatch.delenv(ENV_PATH, raising=False)
    monkeypatch.setattr("sys.platform", "linux")
    with pytest.raises(PublicDriveEnvError) as excinfo:
        build_publicdrive_connector_from_env()
    assert ENV_PATH in str(excinfo.value)


def test_env_factory_reads_env_var(monkeypatch, pdrive_tree: Path):
    monkeypatch.setenv(ENV_PATH, str(pdrive_tree))
    conn = build_publicdrive_connector_from_env()
    assert isinstance(conn, PublicDriveConnector)
    assert conn.root == pdrive_tree.resolve()


def test_env_factory_path_override_wins(monkeypatch, pdrive_tree: Path, tmp_path: Path):
    monkeypatch.setenv(ENV_PATH, str(tmp_path / "does-not-exist"))
    conn = build_publicdrive_connector_from_env(path_override=str(pdrive_tree))
    assert conn.root == pdrive_tree.resolve()


def test_env_factory_helpful_error_when_path_missing(monkeypatch, tmp_path: Path):
    monkeypatch.setenv(ENV_PATH, str(tmp_path / "publicdrive-not-mounted"))
    with pytest.raises(PublicDriveEnvError) as excinfo:
        build_publicdrive_connector_from_env()
    msg = str(excinfo.value)
    assert ENV_PATH in msg
    assert "mounted" in msg.lower() or "reachable" in msg.lower()


def test_source_type_round_trips_through_frontmatter(pdrive_tree: Path):
    """Regression: 2026-04-24 P-drive run blew up because the SourceType enum
    didn't include 'publicdrive', so every absorb raised ValueError. The
    connector-level `source_type == "publicdrive"` check above was passing,
    but the driver's `build_frontmatter(source_type=...)` call wasn't covered.
    Lock in the round-trip so any future connector that ships a stamp
    string the enum doesn't know about fails loudly here, not in prod.
    """
    from jojo_connectors_common.frontmatter import SourceType, build_frontmatter

    assert SourceType("publicdrive") is SourceType.PUBLICDRIVE
    conn = PublicDriveConnector(pdrive_tree)
    entries = list(conn.fetch())
    assert entries, "fixture should yield at least one entry"
    sample = entries[0]
    fm = build_frontmatter(
        entry_id="x",
        source_type=sample.source_type,
        source_url="file:///x",
        source_id=sample.source_id,
        title="x",
        sha256="0" * 64,
    )
    assert fm.source_type is SourceType.PUBLICDRIVE
