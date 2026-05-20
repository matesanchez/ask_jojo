"""CLI tests for jojo_lint."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml


def _make_wiki(tmp_path: Path) -> Path:
    """Build a minimal wiki with one valid page and _index.md."""
    wiki = tmp_path / "wiki"
    wiki.mkdir()
    concepts = wiki / "concepts"
    concepts.mkdir()

    fm = {
        "title": "Test Page",
        "type": "concept",
        "slug": "test-page",
        "created": "2026-01-01",
        "last_updated": "2026-04-01",
        "last_reviewed": "2026-04-01",
        "schema_version": "0.2.0",
        "confidence": "high",
        "corpus": "protein-sciences",
        "sources": [{"path": "raw/x.md", "hash": "abc", "ingested": "2026-01-01"}],
    }
    page = concepts / "test-page.md"
    page.write_text(
        f"---\n{yaml.dump(fm)}---\n\nTest page body.\n",
        encoding="utf-8",
    )

    index = wiki / "_index.md"
    index.write_text(
        "# Wiki Index\n- [[test-page|Test Page]] — `concepts/test-page.md`\n",
        encoding="utf-8",
    )
    return wiki


# ------------------------------------------------------------------ in-process CLI tests


def test_cli_main_no_args_returns_zero() -> None:
    """jojo-lint with no args prints help and exits 0."""
    from jojo_lint.cli import main

    rc = main([])
    assert rc == 0


def test_cli_check_schema_returns_zero(tmp_path: Path) -> None:
    """jojo-lint check schema --wiki <path> returns 0 and valid JSON."""
    import io
    from contextlib import redirect_stdout

    wiki = _make_wiki(tmp_path)

    buf = io.StringIO()
    from jojo_lint.cli import main

    with redirect_stdout(buf):
        rc = main(["check", "schema", "--wiki", str(wiki)])

    assert rc == 0
    output = buf.getvalue()
    parsed = json.loads(output)
    assert parsed["check_name"] == "schema"
    assert parsed["status"] == "pass"
    assert "findings" in parsed
    assert "run_at" in parsed


def test_cli_check_orphan_returns_zero(tmp_path: Path) -> None:
    wiki = _make_wiki(tmp_path)
    import io
    from contextlib import redirect_stdout

    from jojo_lint.cli import main

    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = main(["check", "orphan", "--wiki", str(wiki)])

    assert rc == 0
    output = buf.getvalue()
    parsed = json.loads(output)
    assert parsed["check_name"] == "orphan"


def test_cli_check_unknown_name_returns_nonzero(tmp_path: Path) -> None:
    from jojo_lint.cli import main

    rc = main(["check", "nonexistent-check", "--wiki", str(tmp_path)])
    assert rc != 0


def test_cli_nightly_returns_zero_on_clean_wiki(tmp_path: Path) -> None:
    """jojo-lint nightly exits 0 when no 'fail' results (warnings are OK)."""
    import io
    from contextlib import redirect_stdout

    from jojo_lint.cli import main

    wiki = _make_wiki(tmp_path)
    hist = tmp_path / "hist"

    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = main(["nightly", "--wiki", str(wiki), "--history-dir", str(hist)])

    assert rc == 0
    assert hist.exists()
    # History file should have been written
    log = hist / "lint-history.jsonl"
    assert log.exists()


def test_cli_report_empty_history(tmp_path: Path) -> None:
    from jojo_lint.cli import main

    rc = main(["report", "--history-dir", str(tmp_path)])
    assert rc == 0


def test_cli_history_is_alias_for_report(tmp_path: Path) -> None:
    from jojo_lint.cli import main

    rc = main(["history", "--history-dir", str(tmp_path)])
    assert rc == 0


def test_cli_check_weekly_stub_returns_zero(tmp_path: Path) -> None:
    """Weekly checks return api_key_required when no key — still exit 0."""
    import io
    from contextlib import redirect_stdout

    from jojo_lint.cli import main

    wiki = _make_wiki(tmp_path)
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = main(["check", "contradiction", "--wiki", str(wiki)])

    assert rc == 0
    parsed = json.loads(buf.getvalue())
    assert parsed["check_name"] == "contradiction"
    assert parsed["status"] == "api_key_required"


# ------------------------------------------------------------------ subprocess CLI test


@pytest.mark.skipif(
    not (Path(sys.executable).parent / "jojo-lint").exists()
    and not (Path(sys.executable).parent / "jojo-lint.exe").exists(),
    reason="jojo-lint entry point not installed; run with pip install -e .",
)
def test_cli_subprocess_check_schema(tmp_path: Path) -> None:
    """Subprocess invocation of jojo-lint check schema."""
    wiki = _make_wiki(tmp_path)
    result = subprocess.run(
        ["jojo-lint", "check", "schema", "--wiki", str(wiki)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    parsed = json.loads(result.stdout)
    assert parsed["check_name"] == "schema"
    assert parsed["status"] == "pass"
