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


# ----- built-in ignore patterns -----------------------------------------
# Added 2026-04-27 after the publicdrive walker spent 24 hours descending
# into Agilent ChemStation `*.D/` directories on the Nurix P:\ share. The
# operator can't add the prune to a `.jojoignore` at the share root (no
# write permission, and a file there would also affect every other tool
# that reads gitignore patterns), so PublicDriveConnector ships its own
# baseline. These tests pin that contract.


def test_publicdrive_prunes_agilent_chemstation_dirs(tmp_path: Path):
    """An Agilent .D directory must be skipped before the walker enters it.

    Reproduces the 2026-04-25 stall: a healthy folder containing a .D
    instrument-output sibling. Without the builtin prune the walker
    descends into the .D and pays SMB stat time on every binary inside.
    """
    root = tmp_path / "public"
    real = root / "Analytical/HT Purification"
    real.mkdir(parents=True)
    (real / "method-2024.md").write_text("# real doc\n", encoding="utf-8")
    # The .D directory the prune must skip. Files inside use a supported
    # extension (.md) so we know the test would fail loudly if the
    # walker entered the .D — i.e. the test's negative claim is real,
    # not just an artifact of converter rejection.
    inj = real / "065-D3B-G6-ELN-119-1737-0047.D"
    inj.mkdir()
    (inj / "should-not-be-found.md").write_text("instrument noise\n", encoding="utf-8")

    conn = PublicDriveConnector(root)
    names = sorted(e.source_id for e in conn.fetch())
    # Only the top-level .md survives. The .D contents must NOT appear,
    # even though they have a supported extension — the prune happens
    # at directory-entry time, before the walker descends.
    assert names == ["Analytical/HT Purification/method-2024.md"]


def test_publicdrive_prunes_data_lcms_auto_dir(tmp_path: Path):
    """`Data_LCMS-AUTO/` is a known parent of many .D dirs; pruning at this
    level is cheaper than per-injection."""
    root = tmp_path / "public"
    base = root / "Analytical/HT Purification"
    base.mkdir(parents=True)
    (base / "report.md").write_text("# report\n", encoding="utf-8")
    auto = base / "Data_LCMS-AUTO/20240415_session"
    auto.mkdir(parents=True)
    (auto / "junk.md").write_text("instrument log line\n", encoding="utf-8")

    conn = PublicDriveConnector(root)
    names = sorted(e.source_id for e in conn.fetch())
    # Only the report at the top level. Anything under Data_LCMS-AUTO/ pruned.
    assert "Analytical/HT Purification/report.md" in names
    assert not any("Data_LCMS-AUTO" in n for n in names)


def test_publicdrive_extra_ignore_patterns_layer_on_top(tmp_path: Path):
    """Operator-supplied `extra_ignore_patterns` add to (don't replace) the
    builtins. This is the seam for one-off prunes like
    `extra_ignore_patterns=["ARCHIVE (moved to sharepoint)/"]`.
    """
    root = tmp_path / "public"
    (root / "real").mkdir(parents=True)
    (root / "real" / "doc.md").write_text("# real", encoding="utf-8")
    (root / "ARCHIVE (moved to sharepoint)").mkdir()
    (root / "ARCHIVE (moved to sharepoint)" / "old.md").write_text("dup", encoding="utf-8")
    inj = root / "real/065.D"
    inj.mkdir()
    (inj / "junk.md").write_text("inst", encoding="utf-8")

    conn = PublicDriveConnector(
        root, extra_ignore_patterns=["ARCHIVE (moved to sharepoint)/"]
    )
    names = sorted(e.source_id for e in conn.fetch())
    # builtin .D prune still active AND operator extra also active.
    assert names == ["real/doc.md"]


def test_publicdrive_extra_ignore_can_negate_builtin(tmp_path: Path):
    """Safety valve: an operator can `!`-rule a builtin pattern back in for
    a specific run if they actually want that subtree."""
    root = tmp_path / "public"
    inj = root / "065.D"
    inj.mkdir(parents=True)
    (inj / "report.md").write_text("# data", encoding="utf-8")

    # Default: pruned.
    default = PublicDriveConnector(root)
    assert list(default.fetch()) == []

    # With an explicit `!` rule, the .D dir is walked.
    opted_in = PublicDriveConnector(root, extra_ignore_patterns=["!*.D/"])
    names = sorted(e.source_id for e in opted_in.fetch())
    assert names == ["065.D/report.md"]


def test_publicdrive_factory_forwards_extra_ignore_patterns(monkeypatch, tmp_path: Path):
    """The env-driven factory must thread `extra_ignore_patterns` through to
    the connector — otherwise the CLI surface can't expose it."""
    root = tmp_path / "public"
    inj = root / "065.D"
    inj.mkdir(parents=True)
    (inj / "report.md").write_text("# data", encoding="utf-8")

    monkeypatch.setenv(ENV_PATH, str(root))
    # Ask the factory to UN-prune .D for this run.
    conn = build_publicdrive_connector_from_env(extra_ignore_patterns=["!*.D/"])
    names = sorted(e.source_id for e in conn.fetch())
    assert names == ["065.D/report.md"]


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
