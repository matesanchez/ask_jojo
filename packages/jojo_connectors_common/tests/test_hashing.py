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
