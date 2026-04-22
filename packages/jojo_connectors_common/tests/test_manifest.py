from jojo_connectors_common.manifest import Manifest, ManifestEntry


def _entry(eid: str, sha: str, path: str | None = None) -> ManifestEntry:
    return ManifestEntry(
        id=eid,
        path=path or f"drive/{eid}.md",
        sha256=sha,
        source_type="drive",
        source_id=eid.replace("drive_", ""),
        title=eid,
    )


def test_roundtrip_through_disk(tmp_path):
    mfp = tmp_path / "manifest.json"
    m = Manifest(mfp)
    m.upsert(_entry("drive_a", "a" * 64))
    m.upsert(_entry("drive_b", "b" * 64))
    m.save()

    reloaded = Manifest.load(mfp)
    assert set(reloaded.entries) == {"drive_a", "drive_b"}
    assert reloaded.entries["drive_a"].sha256 == "a" * 64


def test_upsert_records_supersedence(tmp_path):
    m = Manifest(tmp_path / "m.json")
    e1 = _entry("drive_v1", "1" * 64)
    m.upsert(e1)
    e2 = _entry("drive_v2", "2" * 64)
    e2.supersedes = "drive_v1"
    m.upsert(e2)
    assert m.supersedence["drive_v1"] == "drive_v2"


def test_lookup_by_source_id(tmp_path):
    m = Manifest(tmp_path / "m.json")
    m.upsert(ManifestEntry(id="x", path="drive/x.md", sha256="0" * 64, source_type="drive", source_id="X"))
    m.upsert(ManifestEntry(id="y", path="drive/y.md", sha256="0" * 64, source_type="drive", source_id="Y"))
    found = m.by_source_id("drive", "X")
    assert found is not None
    assert found.id == "x"


def test_diff_against_previous(tmp_path):
    old = Manifest(tmp_path / "old.json")
    old.upsert(_entry("a", "1" * 64))
    old.upsert(_entry("b", "2" * 64))

    new = Manifest(tmp_path / "new.json")
    new.upsert(_entry("a", "1" * 64))            # unchanged
    new.upsert(_entry("b", "2b" + "b" * 62))     # changed
    new.upsert(_entry("c", "3" * 64))            # added

    diff = new.diff_against(old)
    assert diff["added"] == ["c"]
    assert diff["changed"] == ["b"]
    assert diff["removed"] == []


def test_save_is_deterministic_across_runs(tmp_path):
    m1 = Manifest(tmp_path / "a.json")
    m1.upsert(_entry("drive_z", "0" * 64))
    m1.upsert(_entry("drive_a", "1" * 64))
    m1.save()
    first = (tmp_path / "a.json").read_text()

    m2 = Manifest.load(tmp_path / "a.json")
    m2.save()
    second = (tmp_path / "a.json").read_text()

    # The `generated` timestamp differs; check only the entries block ordering.
    import json
    d1 = json.loads(first)
    d2 = json.loads(second)
    assert list(d1["entries"]) == list(d2["entries"])
    assert list(d1["entries"]) == sorted(d1["entries"])
