"""Tests for the local-mount OneDrive connector.

OneDriveConnector is a thin DriveConnector subclass (see ADR 0008 — we
ingest OneDrive via the synced folder, not MS Graph, because `Files.Read.All`
isn't consented in our tenant today). The tests here cover:

  - source_type is correctly overridden to "onedrive"
  - The connector actually walks a tmp directory
  - Env factory reads JOJO_ONEDRIVE_PATH and errors helpfully when unset
  - Env factory surfaces "does the folder exist" errors with a OneDrive-
    flavored message (rather than the bare DriveConnector error)
"""

from __future__ import annotations

from pathlib import Path

import pytest

from jojo_ingest.onedrive import (
    ENV_PATH,
    OneDriveConnector,
    OneDriveEnvError,
    build_onedrive_connector_from_env,
)


@pytest.fixture
def onedrive_tree(tmp_path: Path) -> Path:
    root = tmp_path / "OneDrive - Nurix Therapeutics"
    (root / "notes").mkdir(parents=True)
    (root / "notes" / "weekly-1-on-1.md").write_text(
        "# 1:1 notes\n\nDiscuss Q2 goals.\n", encoding="utf-8"
    )
    return root


def test_source_type_is_onedrive(onedrive_tree: Path):
    conn = OneDriveConnector(onedrive_tree)
    assert conn.source_type == "onedrive"


def test_connector_walks_synced_folder(onedrive_tree: Path):
    conn = OneDriveConnector(onedrive_tree)
    entries = list(conn.fetch())
    assert len(entries) == 1
    e = entries[0]
    assert e.source_type == "onedrive"
    assert e.source_id == "notes/weekly-1-on-1.md"
    assert "1:1 notes" in e.content


def test_env_factory_requires_env_var(monkeypatch):
    monkeypatch.delenv(ENV_PATH, raising=False)
    with pytest.raises(OneDriveEnvError) as excinfo:
        build_onedrive_connector_from_env()
    assert ENV_PATH in str(excinfo.value)


def test_env_factory_reads_env_var(monkeypatch, onedrive_tree: Path):
    monkeypatch.setenv(ENV_PATH, str(onedrive_tree))
    conn = build_onedrive_connector_from_env()
    assert isinstance(conn, OneDriveConnector)
    assert conn.root == onedrive_tree.resolve()
    entries = list(conn.fetch())
    assert entries[0].source_type == "onedrive"


def test_env_factory_path_override_wins(monkeypatch, onedrive_tree: Path, tmp_path: Path):
    # Env points at something wrong; override should win.
    monkeypatch.setenv(ENV_PATH, str(tmp_path / "does-not-exist"))
    conn = build_onedrive_connector_from_env(path_override=str(onedrive_tree))
    assert conn.root == onedrive_tree.resolve()


def test_env_factory_helpful_error_when_path_missing(monkeypatch, tmp_path: Path):
    """If the env path points to nothing, we get a OneDrive-flavored error."""
    monkeypatch.setenv(ENV_PATH, str(tmp_path / "OneDrive-does-not-exist"))
    with pytest.raises(OneDriveEnvError) as excinfo:
        build_onedrive_connector_from_env()
    msg = str(excinfo.value)
    assert ENV_PATH in msg
    # Should give the operator a hint about OneDrive specifically, not just
    # "path doesn't exist" — that's the whole reason we subclass.
    assert "onedrive" in msg.lower()
