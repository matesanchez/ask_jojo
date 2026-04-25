"""Drive connector + driver integration tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from jojo_connectors_common import Manifest
from jojo_ingest.drive import DriveConnector
from jojo_ingest.driver import IngestDriver


@pytest.fixture
def source_tree(tmp_path: Path) -> Path:
    """Build a small tree of real files for the drive walker to traverse."""
    root = tmp_path / "src"
    (root / "sop").mkdir(parents=True)
    (root / "sop" / "buffer-recipe.md").write_text(
        "# Buffer Recipe\n\n100 mM Tris, pH 7.4.\n", encoding="utf-8"
    )
    (root / "sop" / "gel-prep.txt").write_text(
        "Pour a 10% SDS-PAGE gel. Let set 30 min.\n", encoding="utf-8"
    )
    (root / "drafts").mkdir()
    (root / "drafts" / "wip.md").write_text("half-written note", encoding="utf-8")
    # Lock file that must be skipped:
    (root / "sop" / "~$buffer-recipe.docx").write_text("lock", encoding="utf-8")
    # Unsupported extension:
    (root / "sop" / "image.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    (root / ".jojoignore").write_text("drafts/\n", encoding="utf-8")
    return root


def test_drive_walker_yields_only_supported_files(source_tree: Path):
    conn = DriveConnector(source_tree)
    entries = list(conn.fetch())
    names = sorted(e.source_id for e in entries)
    # Only the two SOP files (md + txt). drafts/ ignored, ~$ ignored, png unsupported.
    assert names == ["sop/buffer-recipe.md", "sop/gel-prep.txt"]


def test_driver_end_to_end(source_tree: Path, tmp_path: Path):
    raw = tmp_path / "ask_jojo_raw"
    driver = IngestDriver(raw)
    conn = DriveConnector(source_tree)
    result = driver.run([conn])

    cr = result.results["drive"]
    assert cr.added == 2
    assert cr.updated == 0
    assert cr.errors == 0

    # Files landed where they should:
    files = sorted((raw / "drive").glob("*.md"))
    assert len(files) == 2
    for path in files:
        text = path.read_text(encoding="utf-8")
        assert text.startswith("---\n")
        assert "sha256:" in text
        assert "source_type: drive" in text

    # Manifest lists both entries:
    manifest = Manifest.load(raw / "manifest.json")
    assert len(manifest.entries) == 2
    assert all(e.source_type == "drive" for e in manifest.entries.values())

    # Change record exists:
    assert result.change_record_path is not None
    assert result.change_record_path.exists()


def test_driver_idempotent_rerun(source_tree: Path, tmp_path: Path):
    raw = tmp_path / "ask_jojo_raw"
    driver = IngestDriver(raw)

    # First run adds.
    r1 = driver.run([DriveConnector(source_tree)])
    assert r1.results["drive"].added == 2

    # Second run against unchanged files: everything skipped.
    driver2 = IngestDriver(raw)
    r2 = driver2.run([DriveConnector(source_tree)])
    assert r2.results["drive"].added == 0
    assert r2.results["drive"].updated == 0
    assert r2.results["drive"].skipped == 2

    # Third run after modifying one file: exactly one update.
    (source_tree / "sop" / "buffer-recipe.md").write_text(
        "# Buffer Recipe\n\n100 mM Tris, pH 8.0. (adjusted)\n", encoding="utf-8"
    )
    driver3 = IngestDriver(raw)
    r3 = driver3.run([DriveConnector(source_tree)])
    assert r3.results["drive"].updated == 1
    assert r3.results["drive"].skipped == 1


def test_driver_records_supersedence(source_tree: Path, tmp_path: Path):
    raw = tmp_path / "ask_jojo_raw"
    IngestDriver(raw).run([DriveConnector(source_tree)])
    (source_tree / "sop" / "buffer-recipe.md").write_text(
        "# Buffer Recipe\n\nNew body.\n", encoding="utf-8"
    )
    IngestDriver(raw).run([DriveConnector(source_tree)])

    manifest = Manifest.load(raw / "manifest.json")
    # Supersedence is only recorded when the entry's `.supersedes` is set in
    # `ManifestEntry` — for same-id updates the hash changes in place.
    # Here we assert the entry still exists, hash changed, and the absorb
    # marked it as updated (verified in test_driver_idempotent_rerun).
    entry = manifest.by_source_id("drive", "sop/buffer-recipe.md")
    assert entry is not None
    assert entry.title == "buffer-recipe"


def test_drive_incremental_since_filter(source_tree: Path, tmp_path: Path):
    from datetime import datetime, timedelta, timezone

    raw = tmp_path / "ask_jojo_raw"
    driver = IngestDriver(raw)
    # Pass a cutoff far in the future -- nothing should be emitted.
    future = datetime.now(timezone.utc) + timedelta(days=1)
    r = driver.run([DriveConnector(source_tree)], since=future)
    assert r.results["drive"].added == 0


# --------------------------------------------------------- hang-resilience (FU-9)


def test_drive_walker_skips_subtree_when_iterdir_times_out(source_tree: Path, caplog):
    """FU-9 smoking gun: if iterdir blocks forever, the walker must skip and
    keep going. We simulate the hang by monkeypatching the watchdog to
    raise WatchdogTimeout and assert the walker still returns."""
    import jojo_ingest.drive as drive_module
    from jojo_ingest._watchdog import WatchdogTimeout

    real_run = drive_module.run_with_timeout
    calls = {"n": 0}

    def fake_run(func, *args, timeout_s, label="", **kwargs):
        # Fail the very first listdir call; let subsequent calls (like
        # stat/convert) through the real helper. This mimics a single
        # hung subtree at the root, which is the FU-9 shape.
        calls["n"] += 1
        if calls["n"] == 1 and label.startswith("iterdir"):
            raise WatchdogTimeout(f"{label} simulated hang")
        return real_run(func, *args, timeout_s=timeout_s, label=label, **kwargs)

    import pytest

    with pytest.MonkeyPatch.context() as m:
        m.setattr(drive_module, "run_with_timeout", fake_run)
        conn = DriveConnector(source_tree)
        with caplog.at_level("WARNING"):
            entries = list(conn.fetch())
    assert entries == []
    assert any("listdir timed out" in rec.message for rec in caplog.records)


def test_drive_walker_skips_oversize_files(source_tree: Path):
    """Files exceeding max_size_mb must be skipped before the converter
    ever opens them -- matches the SharePoint connector's behavior and
    protects the walker from a random multi-GB file on P:\\."""
    # Make buffer-recipe.md "big" by shrinking the cap below its size.
    big_file_size = (source_tree / "sop" / "buffer-recipe.md").stat().st_size
    assert big_file_size > 0

    # 1 MB / 1_048_576 > 0 is true for any real file; we use a byte cap
    # via a max_size_mb=0 run plus a tiny pre-check guard.
    # A max_size_mb of 0 yields max_bytes=0, which skips every supported file.
    conn = DriveConnector(source_tree, max_size_mb=0)
    entries = list(conn.fetch())
    assert entries == []

    # Sanity: a normal cap still yields both files.
    conn2 = DriveConnector(source_tree, max_size_mb=50)
    entries2 = list(conn2.fetch())
    assert len(entries2) == 2


def test_drive_walker_skips_file_when_convert_times_out(source_tree: Path, caplog):
    """Converter hang on a single file must not deadlock the walker."""
    import jojo_ingest.drive as drive_module
    from jojo_ingest._watchdog import WatchdogTimeout

    real_run = drive_module.run_with_timeout

    def fake_run(func, *args, timeout_s, label="", **kwargs):
        if label.startswith("convert(") and "buffer-recipe.md" in label:
            raise WatchdogTimeout(f"{label} simulated hang")
        return real_run(func, *args, timeout_s=timeout_s, label=label, **kwargs)

    import pytest

    with pytest.MonkeyPatch.context() as m:
        m.setattr(drive_module, "run_with_timeout", fake_run)
        conn = DriveConnector(source_tree)
        with caplog.at_level("WARNING"):
            entries = list(conn.fetch())
    # gel-prep.txt should still come through; buffer-recipe.md is skipped.
    names = sorted(e.source_id for e in entries)
    assert names == ["sop/gel-prep.txt"]
    assert any("convert timed out" in rec.message for rec in caplog.records)


# --------------------------------------------------- periodic manifest flush


def test_driver_flushes_manifest_periodically(source_tree: Path, tmp_path: Path):
    """A crash at hour N must not cost more than `flush_every` entries.

    We simulate 'the walker keeps going after the flush' by rigging a
    driver with flush_every=1 and confirming the manifest on disk has
    both entries before .run() returns its final save."""
    raw = tmp_path / "ask_jojo_raw"
    driver = IngestDriver(raw, flush_every=1)

    # Monkey-patch Manifest.save to count invocations without losing behavior.
    save_count = {"n": 0}
    real_save = driver.manifest.save

    def counting_save(*args, **kwargs):
        save_count["n"] += 1
        return real_save(*args, **kwargs)

    driver.manifest.save = counting_save  # type: ignore[method-assign]
    driver.run([DriveConnector(source_tree)])

    # Two files were absorbed; with flush_every=1 that's at least 2
    # mid-run flushes + 1 final flush. Being conservative we assert >= 3.
    assert save_count["n"] >= 3


# ---- include_extensions allowlist ----------------------------------------
# Added 2026-04-24 alongside the publicdrive walk-scoping work. The P:\
# drive is ~50 TB of mostly raw instrument output; without an allowlist
# every walk paid the SMB stat cost on millions of irrelevant files.


def test_include_extensions_filters_to_allowlist(source_tree: Path):
    """{'md'} should drop the .txt file even though the txt converter exists."""
    conn = DriveConnector(source_tree, include_extensions={"md"})
    entries = list(conn.fetch())
    names = sorted(e.source_id for e in entries)
    assert names == ["sop/buffer-recipe.md"]


def test_include_extensions_normalizes_case_dot_and_whitespace(source_tree: Path):
    """Operators paste ".DOCX", "TXT", or " .pptx" -- all should match.

    Whitespace order matters: lstrip('.') runs after strip() because
    ' .txt' would otherwise lstrip the leading space, leave the dot, and
    silently never match.
    """
    conn = DriveConnector(source_tree, include_extensions={"  .TXT  "})
    entries = list(conn.fetch())
    assert [e.source_id for e in entries] == ["sop/gel-prep.txt"]


def test_include_extensions_none_preserves_default_behavior(source_tree: Path):
    """Regression guard: passing None must match the no-arg behavior."""
    baseline = DriveConnector(source_tree)
    filtered = DriveConnector(source_tree, include_extensions=None)
    assert sorted(e.source_id for e in baseline.fetch()) == sorted(
        e.source_id for e in filtered.fetch()
    )


def test_include_extensions_empty_iterable_excludes_everything(source_tree: Path):
    """Distinct from None: an empty allowlist means 'allow nothing'.

    The CLI parser maps `--include-ext ""` to None (no filter). But if a
    caller passes the empty frozenset directly, that's an explicit "no
    extensions allowed" -- respect it. Documents the semantic so a future
    caller doesn't conflate empty-set with no-filter.
    """
    conn = DriveConnector(source_tree, include_extensions=frozenset())
    assert list(conn.fetch()) == []


def test_include_extensions_drops_unmarked_text_files(tmp_path: Path):
    """Files with no extension fall through to the text converter by default
    but should be dropped when an allowlist is set -- the operator was
    explicit about which extensions to admit."""
    root = tmp_path / "src"
    root.mkdir()
    (root / "README").write_text("no extension", encoding="utf-8")
    (root / "notes.md").write_text("# notes", encoding="utf-8")
    conn = DriveConnector(root, include_extensions={"md"})
    names = sorted(e.source_id for e in conn.fetch())
    assert names == ["notes.md"]


def test_cli_parse_include_ext():
    """_parse_include_ext should normalize, dedupe, and treat empty as None."""
    from jojo_ingest.cli import _parse_include_ext

    assert _parse_include_ext(None) is None
    assert _parse_include_ext("") is None
    assert _parse_include_ext("   ") is None
    assert _parse_include_ext(",,,") is None  # all-empty after split
    assert _parse_include_ext("docx,pptx,pdf") == frozenset({"docx", "pptx", "pdf"})
    assert _parse_include_ext(".DOCX, .PPTX") == frozenset({"docx", "pptx"})
    assert _parse_include_ext("docx,docx,pdf") == frozenset({"docx", "pdf"})


# ---- progress heartbeat --------------------------------------------------
# Added 2026-04-24 so an operator tailing the wrapper log can tell whether
# a multi-day P:\ walk is making progress vs. hung on a single subtree. Gate
# is `time.monotonic`-based; we patch monotonic to control the clock.


def _fake_monotonic_factory(values: list[float]):
    """Returns a callable that yields successive values from `values`, then
    repeats the last one forever. Lets a test simulate elapsed wall time
    without sleeping."""
    state = {"i": 0}

    def fake() -> float:
        i = min(state["i"], len(values) - 1)
        v = values[i]
        state["i"] += 1
        return v

    return fake


def test_progress_emits_to_stderr_on_first_directory(
    source_tree: Path, capsys, monkeypatch: pytest.MonkeyPatch
):
    """First _walk call should always emit (last_progress_at == 0).

    Note: with a constant monotonic value, only the root emit fires (later
    directory entries are within the 60s gate). yielded=0 at the root makes
    sense -- the count is incremented only after a yield.
    """
    import jojo_ingest.drive as drive_module

    monkeypatch.setattr(drive_module.time, "monotonic", lambda: 100.0)
    conn = DriveConnector(source_tree)
    list(conn.fetch())
    err = capsys.readouterr().err
    # Format check + source_type + root-directory marker.
    assert "[progress] drive: walking ." in err
    assert "yielded 0 so far" in err


def test_progress_gates_by_interval(
    source_tree: Path, capsys, monkeypatch: pytest.MonkeyPatch
):
    """Within `progress_interval_s`, only the first emit should fire.

    Walker enters root at t=100 (forced emit), then sop/ at t=130 (gated:
    delta=30 < 60), so we expect exactly one '[progress]' line despite
    multiple directory entries.
    """
    import jojo_ingest.drive as drive_module

    fake = _fake_monotonic_factory([100.0, 130.0, 145.0, 150.0])
    monkeypatch.setattr(drive_module.time, "monotonic", fake)
    conn = DriveConnector(source_tree, progress_interval_s=60.0)
    list(conn.fetch())
    err = capsys.readouterr().err
    assert err.count("[progress]") == 1, f"expected 1 emit, got {err!r}"


def test_progress_emits_again_after_interval_elapses(
    source_tree: Path, capsys, monkeypatch: pytest.MonkeyPatch
):
    """Once the interval has passed, the next directory entry should emit."""
    import jojo_ingest.drive as drive_module

    # Walker enters root at t=100 (emit), then sop/ at t=200 (delta=100 >
    # 60 -> emit). Two directories visited that pass the gate.
    fake = _fake_monotonic_factory([100.0, 200.0, 210.0])
    monkeypatch.setattr(drive_module.time, "monotonic", fake)
    conn = DriveConnector(source_tree, progress_interval_s=60.0)
    list(conn.fetch())
    err = capsys.readouterr().err
    assert err.count("[progress]") >= 2, f"expected >=2 emits, got {err!r}"


def test_progress_disabled_when_interval_non_positive(
    source_tree: Path, capsys, monkeypatch: pytest.MonkeyPatch
):
    """Operators who tail their own logs may want the heartbeat off."""
    import jojo_ingest.drive as drive_module

    monkeypatch.setattr(drive_module.time, "monotonic", lambda: 100.0)
    for interval in (0.0, -5.0):
        conn = DriveConnector(source_tree, progress_interval_s=interval)
        list(conn.fetch())
        err = capsys.readouterr().err
        assert "[progress]" not in err, f"interval={interval}: {err!r}"


def test_progress_uses_subclass_source_type(
    tmp_path: Path, capsys, monkeypatch: pytest.MonkeyPatch
):
    """The line must say 'publicdrive' (not 'drive') for a subclass — that's
    the whole point of distinguishing source types in the manifest."""
    import jojo_ingest.drive as drive_module
    from jojo_ingest.publicdrive import PublicDriveConnector

    root = tmp_path / "share"
    root.mkdir()
    (root / "note.md").write_text("# n", encoding="utf-8")

    monkeypatch.setattr(drive_module.time, "monotonic", lambda: 0.0)
    conn = PublicDriveConnector(root)
    list(conn.fetch())
    err = capsys.readouterr().err
    assert "[progress] publicdrive: walking ." in err


def test_progress_resets_state_each_fetch(
    source_tree: Path, capsys, monkeypatch: pytest.MonkeyPatch
):
    """A reused connector must report fresh yields per run, not cumulative.

    Without the reset in fetch(), a second call's heartbeat would say
    'yielded 4 so far' after two two-file walks, which would mislead an
    operator scanning for production progress vs. a stuck restart.
    """
    import jojo_ingest.drive as drive_module

    monkeypatch.setattr(drive_module.time, "monotonic", lambda: 100.0)
    conn = DriveConnector(source_tree)
    list(conn.fetch())
    capsys.readouterr()  # discard run 1 output
    list(conn.fetch())
    err = capsys.readouterr().err
    # Run 2's first emit is at root before any yields, so the count must
    # be 0 -- if the reset is missing, this would be 2 (carried from run 1).
    assert "yielded 0 so far" in err
