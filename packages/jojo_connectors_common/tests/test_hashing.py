from jojo_connectors_common.hashing import canonical_sha256, stable_id


def test_canonical_sha256_is_stable_across_line_endings():
    a = canonical_sha256("hello\nworld\n")
    b = canonical_sha256("hello\r\nworld\r\n")
    c = canonical_sha256("hello\rworld\r")
    assert a == b == c


def test_canonical_sha256_strips_trailing_whitespace():
    a = canonical_sha256("line one\nline two\n")
    b = canonical_sha256("line one   \nline two\t\n")
    assert a == b


def test_canonical_sha256_adds_trailing_newline():
    a = canonical_sha256("x")
    b = canonical_sha256("x\n")
    assert a == b


def test_canonical_sha256_on_bytes_hashes_verbatim():
    # Binary content (e.g. image bytes) must not be normalized.
    raw = b"\x89PNG\r\n\x1a\n"
    assert canonical_sha256(raw) == canonical_sha256(raw)
    # And it should NOT equal the text-hash of the same bytes.
    text_hash = canonical_sha256(raw.decode("latin-1"))
    assert canonical_sha256(raw) != text_hash


def test_stable_id_is_deterministic_and_slugified():
    assert stable_id("drive", "docs/Foo Bar.docx") == "drive_docs-foo-bar-docx"
    assert stable_id("drive", "docs/Foo Bar.docx") == stable_id("drive", "docs/Foo Bar.docx")


def test_stable_id_falls_back_to_hash_when_empty_slug():
    sid = stable_id("drive", "///")
    assert sid.startswith("drive_")
    assert len(sid) > len("drive_")


# ---- entry_id length cap (added 2026-04-25 after publicdrive long-path crash)


def _deep_source_id() -> str:
    """Mimic the shape of the failing publicdrive path. Length ~340 chars,
    well over Windows MAX_PATH once the absorb prefix is added."""
    return (
        "In Vivo Pharm/Jose Gomez -public - Historical/OLD Material/"
        "Desktop 19AUG21/Papers/Desktop 24NOV20/Desktop 280820/"
        "Desktop 10JUL20/Jose Gomez Stuff/Science Literature/T-Cell/"
        "Mitochondria/T cells with dysfunctional mitochondira induce "
        "multimorbidity and premature senescence.pdf"
    )


def test_stable_id_caps_long_entry_id_under_max():
    """Without the cap, a deep SMB path produces a slug ~340 chars long
    and `target.write_text` raises EINVAL on Windows. With the cap, the
    entry_id stays at or below the budget."""
    from jojo_connectors_common.hashing import _MAX_ENTRY_ID_LEN

    sid = stable_id("publicdrive", _deep_source_id())
    assert len(sid) <= _MAX_ENTRY_ID_LEN
    assert sid.startswith("publicdrive_")


def test_stable_id_truncation_is_deterministic():
    """Re-ingesting the same source must produce the same entry_id, or
    the manifest can't detect supersedence."""
    sid1 = stable_id("publicdrive", _deep_source_id())
    sid2 = stable_id("publicdrive", _deep_source_id())
    assert sid1 == sid2


def test_stable_id_truncation_disambiguates_shared_prefix():
    """Two long source_ids sharing the same leading 200 chars must NOT
    collide post-truncation. Without the hash suffix, both would be
    truncated to the same head and the second would clobber the first
    on disk (and break manifest supersedence)."""
    base = "/".join(["very-long-folder-name-that-eats-the-budget-quickly"] * 6)
    a = stable_id("publicdrive", base + "/file-A.pdf")
    b = stable_id("publicdrive", base + "/file-B.pdf")
    assert a != b
    # And both should still be under the cap.
    from jojo_connectors_common.hashing import _MAX_ENTRY_ID_LEN

    assert len(a) <= _MAX_ENTRY_ID_LEN
    assert len(b) <= _MAX_ENTRY_ID_LEN


def test_stable_id_short_inputs_unchanged_by_cap():
    """Regression guard: the cap must not perturb existing entry_ids.

    Already-absorbed files have short slugs and must remain bit-identical
    in entry_id, otherwise re-runs would re-absorb them under new names
    and the manifest would orphan the old entries.
    """
    assert stable_id("drive", "docs/Foo Bar.docx") == "drive_docs-foo-bar-docx"
    assert stable_id("sharepoint", "Shared Documents/notes.md") == (
        "sharepoint_shared-documents-notes-md"
    )
