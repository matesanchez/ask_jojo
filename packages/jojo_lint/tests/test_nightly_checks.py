"""Tests for the six nightly deterministic lint checks."""

from __future__ import annotations

from pathlib import Path

from jojo_lint.checks import (
    bloat_check,
    orphan_check,
    quote_budget_check,
    schema_check,
    stub_check,
    wikilink_check,
)

# ------------------------------------------------------------------ helpers

def _write_page(
    wiki_root: Path,
    subdir: str,
    filename: str,
    frontmatter: dict,
    body: str = "",
) -> Path:
    """Write a minimal wiki page with frontmatter."""
    import yaml

    d = wiki_root / subdir
    d.mkdir(parents=True, exist_ok=True)
    page = d / filename
    fm_text = yaml.dump(frontmatter, default_flow_style=False)
    page.write_text(f"---\n{fm_text}---\n\n{body}", encoding="utf-8")
    return page


def _make_valid_frontmatter(slug: str, **overrides: object) -> dict:
    """Return a minimal valid frontmatter dict."""
    fm: dict = {
        "title": f"Title for {slug}",
        "type": "concept",
        "slug": slug,
        "created": "2026-01-01",
        "last_updated": "2026-04-01",
        "last_reviewed": "2026-04-01",
        "schema_version": "0.2.0",
        "confidence": "high",
        "corpus": "protein-sciences",
        "sources": [{"path": "raw/test.md", "hash": "abc123", "ingested": "2026-01-01"}],
    }
    fm.update(overrides)
    return fm


def _make_index(wiki_root: Path, slugs: list[str]) -> None:
    """Write a minimal ``_index.md`` listing the given slugs."""
    lines = ["# Wiki Index\n"]
    for slug in slugs:
        lines.append(f"- [[{slug}|{slug}]] — `concepts/{slug}.md`\n")
    (wiki_root / "_index.md").write_text("".join(lines), encoding="utf-8")


# ------------------------------------------------------------------ schema_check

class TestSchemaCheck:
    def test_pass_on_valid_page(self, tmp_path: Path) -> None:
        fm = _make_valid_frontmatter("valid-slug")
        _write_page(tmp_path, "concepts", "valid-slug.md", fm)
        result = schema_check.run(tmp_path)
        assert result.status == "pass"
        assert result.findings == []

    def test_warn_on_missing_title(self, tmp_path: Path) -> None:
        fm = _make_valid_frontmatter("no-title")
        del fm["title"]
        _write_page(tmp_path, "concepts", "no-title.md", fm)
        result = schema_check.run(tmp_path)
        # Status is "warn" (not "fail") so nightly runs exit 0 even on real wiki.
        # Individual findings still have severity "error".
        assert result.status == "warn"
        errors = [f for f in result.findings if f["severity"] == "error"]
        assert any("missing field: title" in f["message"] for f in errors)

    def test_warn_on_output_type_missing_output_format(self, tmp_path: Path) -> None:
        fm = _make_valid_frontmatter("my-output", type="output")
        # output_format is NOT present
        _write_page(tmp_path, "outputs", "my-output.md", fm)
        result = schema_check.run(tmp_path)
        assert result.status == "warn"
        assert any("output_format" in f["message"] for f in result.findings)

    def test_pass_on_output_type_with_output_format(self, tmp_path: Path) -> None:
        fm = _make_valid_frontmatter("my-output", type="output", output_format="markdown")
        _write_page(tmp_path, "outputs", "my-output.md", fm)
        result = schema_check.run(tmp_path)
        assert result.status == "pass"

    def test_excludes_index_and_schema_files(self, tmp_path: Path) -> None:
        """_index.md and SCHEMA.md must not appear as findings."""
        # _index.md with no frontmatter
        (tmp_path / "_index.md").write_text("# Index\n", encoding="utf-8")
        (tmp_path / "SCHEMA.md").write_text("# Schema\n", encoding="utf-8")
        result = schema_check.run(tmp_path)
        assert result.status == "pass"

    def test_multiple_missing_fields(self, tmp_path: Path) -> None:
        fm = {"slug": "partial"}  # missing almost everything
        _write_page(tmp_path, "concepts", "partial.md", fm)
        result = schema_check.run(tmp_path)
        assert result.status == "warn"
        assert len(result.findings) >= 5

    def test_check_result_has_required_fields(self, tmp_path: Path) -> None:
        result = schema_check.run(tmp_path)
        assert result.check_name == "schema"
        assert result.run_at  # non-empty
        assert result.duration_ms >= 0


# ------------------------------------------------------------------ orphan_check

class TestOrphanCheck:
    def test_pass_when_all_pages_indexed(self, tmp_path: Path) -> None:
        _write_page(tmp_path, "concepts", "a.md", _make_valid_frontmatter("a"))
        _make_index(tmp_path, ["a"])
        result = orphan_check.run(tmp_path)
        assert result.status == "pass"

    def test_warn_on_orphan_page(self, tmp_path: Path) -> None:
        _write_page(tmp_path, "concepts", "orphan.md", _make_valid_frontmatter("orphan"))
        _make_index(tmp_path, [])  # empty index
        result = orphan_check.run(tmp_path)
        assert result.status == "warn"
        assert any("orphan" in f["slug"] for f in result.findings)
        assert all(f["severity"] == "warn" for f in result.findings)

    def test_no_false_positives_when_indexed(self, tmp_path: Path) -> None:
        _write_page(tmp_path, "concepts", "indexed.md", _make_valid_frontmatter("indexed"))
        _make_index(tmp_path, ["indexed"])
        result = orphan_check.run(tmp_path)
        slugs = [f["slug"] for f in result.findings]
        assert "indexed" not in slugs

    def test_pass_when_no_index_exists(self, tmp_path: Path) -> None:
        """Without _index.md, every page is orphan — should still return warn, not crash."""
        _write_page(tmp_path, "concepts", "x.md", _make_valid_frontmatter("x"))
        result = orphan_check.run(tmp_path)
        # All pages are orphan when no index exists
        assert result.status in ("pass", "warn")


# ------------------------------------------------------------------ stub_check

class TestStubCheck:
    def test_warn_on_stale_low_confidence_page(self, tmp_path: Path) -> None:
        fm = _make_valid_frontmatter("stale-low", confidence="low", last_updated="2025-01-01")
        _write_page(tmp_path, "concepts", "stale-low.md", fm)
        result = stub_check.run(tmp_path, stale_days=60)
        assert result.status == "warn"
        assert any("stale-low" in f["slug"] for f in result.findings)

    def test_pass_on_high_confidence_page(self, tmp_path: Path) -> None:
        fm = _make_valid_frontmatter("fresh-high", confidence="high", last_updated="2025-01-01")
        _write_page(tmp_path, "concepts", "fresh-high.md", fm)
        result = stub_check.run(tmp_path, stale_days=60)
        assert result.status == "pass"

    def test_pass_on_recent_low_confidence_page(self, tmp_path: Path) -> None:
        fm = _make_valid_frontmatter("fresh-low", confidence="low", last_updated="2026-05-01")
        _write_page(tmp_path, "concepts", "fresh-low.md", fm)
        result = stub_check.run(tmp_path, stale_days=60)
        # 2026-05-01 is within 60 days of 2026-05-19
        assert result.status == "pass"

    def test_finding_message_mentions_days(self, tmp_path: Path) -> None:
        fm = _make_valid_frontmatter("stale-page", confidence="low", last_updated="2025-01-01")
        _write_page(tmp_path, "concepts", "stale-page.md", fm)
        result = stub_check.run(tmp_path, stale_days=30)
        assert result.findings
        assert "days" in result.findings[0]["message"]


# ------------------------------------------------------------------ wikilink_check

class TestWikilinkCheck:
    def test_pass_on_valid_wikilinks(self, tmp_path: Path) -> None:
        _write_page(tmp_path, "concepts", "a.md", _make_valid_frontmatter("a"))
        _write_page(tmp_path, "concepts", "b.md", _make_valid_frontmatter("b"), body="See [[a]].")
        result = wikilink_check.run(tmp_path)
        assert result.status == "pass"

    def test_warn_on_broken_wikilink(self, tmp_path: Path) -> None:
        _write_page(
            tmp_path, "concepts", "page.md",
            _make_valid_frontmatter("page"),
            body="See [[nonexistent-slug]].",
        )
        result = wikilink_check.run(tmp_path)
        # Status is "warn" so nightly runs exit 0 even on the real wiki.
        # Individual findings still carry severity "error".
        assert result.status == "warn"
        assert any("nonexistent-slug" in f["message"] for f in result.findings)
        assert all(f["severity"] == "error" for f in result.findings)

    def test_warn_on_duplicate_slug(self, tmp_path: Path) -> None:
        _write_page(tmp_path, "concepts", "dup1.md", _make_valid_frontmatter("dup"))
        _write_page(tmp_path, "methods", "dup2.md", _make_valid_frontmatter("dup"))
        result = wikilink_check.run(tmp_path)
        assert result.status == "warn"
        dup_findings = [f for f in result.findings if f.get("message") == "duplicate slug"]
        assert dup_findings
        assert dup_findings[0]["slug"] == "dup"

    def test_passes_on_anchor_wikilinks(self, tmp_path: Path) -> None:
        """[[slug#section]] should resolve to 'slug'."""
        _write_page(tmp_path, "concepts", "a.md", _make_valid_frontmatter("a"))
        _write_page(
            tmp_path, "concepts", "b.md",
            _make_valid_frontmatter("b"),
            body="See [[a#overview]].",
        )
        result = wikilink_check.run(tmp_path)
        assert result.status == "pass"

    def test_passes_on_pipe_wikilinks(self, tmp_path: Path) -> None:
        """[[slug|label]] should resolve to 'slug'."""
        _write_page(tmp_path, "concepts", "a.md", _make_valid_frontmatter("a"))
        _write_page(
            tmp_path, "concepts", "b.md",
            _make_valid_frontmatter("b"),
            body="See [[a|the A page]].",
        )
        result = wikilink_check.run(tmp_path)
        assert result.status == "pass"


# ------------------------------------------------------------------ bloat_check

class TestBloatCheck:
    def test_pass_on_small_page(self, tmp_path: Path) -> None:
        fm = _make_valid_frontmatter("small")
        _write_page(tmp_path, "concepts", "small.md", fm, body="Short page.\n")
        result = bloat_check.run(tmp_path)
        assert result.status == "pass"

    def test_warn_on_oversize_page(self, tmp_path: Path) -> None:
        fm = _make_valid_frontmatter("big")
        big_body = "line\n" * 1001  # 1001 lines
        _write_page(tmp_path, "concepts", "big.md", fm, body=big_body)
        result = bloat_check.run(tmp_path, max_lines=1000)
        assert result.status == "warn"
        assert any("big" in f["slug"] for f in result.findings)

    def test_warn_on_oversize_bytes(self, tmp_path: Path) -> None:
        fm = _make_valid_frontmatter("fatbytes")
        # Generate content that exceeds 51200 bytes
        fat_body = "x" * 52000
        _write_page(tmp_path, "concepts", "fatbytes.md", fm, body=fat_body)
        result = bloat_check.run(tmp_path, max_bytes=51200)
        assert result.status == "warn"

    def test_finding_message_contains_counts(self, tmp_path: Path) -> None:
        fm = _make_valid_frontmatter("bigpage")
        big_body = "line\n" * 1001
        _write_page(tmp_path, "concepts", "bigpage.md", fm, body=big_body)
        result = bloat_check.run(tmp_path, max_lines=1000)
        assert result.findings
        msg = result.findings[0]["message"]
        assert "lines" in msg
        assert "bytes" in msg


# ------------------------------------------------------------------ quote_budget_check

class TestQuoteBudgetCheck:
    def test_pass_on_no_blockquotes(self, tmp_path: Path) -> None:
        fm = _make_valid_frontmatter("plain")
        _write_page(tmp_path, "concepts", "plain.md", fm, body="No quotes here.\n")
        result = quote_budget_check.run(tmp_path)
        assert result.status == "pass"

    def test_warn_on_high_blockquote_fraction_page(self, tmp_path: Path) -> None:
        fm = _make_valid_frontmatter("quoty")
        # 4 blockquote lines out of 5 total = 80% > 30% threshold
        body = "> quote 1\n> quote 2\n> quote 3\n> quote 4\nnormal line\n"
        _write_page(tmp_path, "concepts", "quoty.md", fm, body=body)
        result = quote_budget_check.run(tmp_path)
        assert result.status == "warn"
        assert any("quoty" in f["slug"] for f in result.findings)

    def test_warn_on_global_exceeded(self, tmp_path: Path) -> None:
        # Create two pages: one with heavy blockquotes to push global fraction over 20%
        fm1 = _make_valid_frontmatter("heavily-quoted")
        body1 = "\n".join(["> q" for _ in range(20)] + ["normal" for _ in range(5)])
        _write_page(tmp_path, "concepts", "heavily-quoted.md", fm1, body=body1)

        result = quote_budget_check.run(tmp_path, max_quoted_fraction=0.20)
        assert result.status == "warn"

    def test_pass_on_low_blockquote_fraction(self, tmp_path: Path) -> None:
        fm = _make_valid_frontmatter("mostly-prose")
        # 1 blockquote out of 10 lines = 10% < 30% per-page and 20% global
        body = "> one quote\n" + "line\n" * 9
        _write_page(tmp_path, "concepts", "mostly-prose.md", fm, body=body)
        result = quote_budget_check.run(tmp_path, max_quoted_fraction=0.20)
        assert result.status == "pass"
