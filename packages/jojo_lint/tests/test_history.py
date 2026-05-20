"""Tests for jojo_lint.history — append, load, and metrics roundtrip."""

from __future__ import annotations

from pathlib import Path

from jojo_lint import history
from jojo_lint.checks.base import CheckResult


def _make_result(check_name: str, status: str = "pass", n_findings: int = 0) -> CheckResult:
    from datetime import datetime, timezone

    findings = [
        {"slug": f"slug-{i}", "message": "test finding", "severity": "warn"}
        for i in range(n_findings)
    ]
    return CheckResult(
        check_name=check_name,
        status=status,
        findings=findings,
        run_at=datetime.now(tz=timezone.utc).isoformat(),
        duration_ms=10,
    )


class TestAppendAndLoad:
    def test_append_creates_file(self, tmp_path: Path) -> None:
        results = [_make_result("schema"), _make_result("orphan")]
        history.append_run("nightly", results, history_dir=tmp_path)
        log = tmp_path / "lint-history.jsonl"
        assert log.exists()

    def test_append_writes_valid_json(self, tmp_path: Path) -> None:
        import json

        results = [_make_result("schema")]
        history.append_run("nightly", results, history_dir=tmp_path)
        log = tmp_path / "lint-history.jsonl"
        lines = [ln for ln in log.read_text(encoding="utf-8").splitlines() if ln.strip()]
        assert len(lines) == 1
        record = json.loads(lines[0])
        assert record["scope"] == "nightly"
        assert "run_at" in record
        assert len(record["results"]) == 1

    def test_multiple_appends(self, tmp_path: Path) -> None:
        history.append_run("nightly", [_make_result("schema")], history_dir=tmp_path)
        history.append_run("nightly", [_make_result("orphan")], history_dir=tmp_path)
        log = tmp_path / "lint-history.jsonl"
        lines = [ln for ln in log.read_text(encoding="utf-8").splitlines() if ln.strip()]
        assert len(lines) == 2

    def test_load_runs_empty_when_no_file(self, tmp_path: Path) -> None:
        runs = history.load_runs(history_dir=tmp_path)
        assert runs == []

    def test_load_runs_returns_all_recent(self, tmp_path: Path) -> None:
        history.append_run("nightly", [_make_result("schema")], history_dir=tmp_path)
        history.append_run("weekly", [_make_result("contradiction")], history_dir=tmp_path)
        runs = history.load_runs(days=30, history_dir=tmp_path)
        assert len(runs) == 2

    def test_load_runs_filters_by_scope(self, tmp_path: Path) -> None:
        history.append_run("nightly", [_make_result("schema")], history_dir=tmp_path)
        history.append_run("weekly", [_make_result("contradiction")], history_dir=tmp_path)
        nightly_runs = history.load_runs(scope="nightly", history_dir=tmp_path)
        assert len(nightly_runs) == 1
        assert nightly_runs[0]["scope"] == "nightly"

    def test_load_runs_most_recent_first(self, tmp_path: Path) -> None:
        history.append_run("nightly", [_make_result("schema")], history_dir=tmp_path)
        history.append_run("nightly", [_make_result("orphan")], history_dir=tmp_path)
        runs = history.load_runs(scope="nightly", history_dir=tmp_path)
        assert len(runs) == 2
        assert runs[0]["run_at"] >= runs[1]["run_at"]

    def test_roundtrip_preserves_findings(self, tmp_path: Path) -> None:

        results = [_make_result("stub", status="warn", n_findings=3)]
        history.append_run("nightly", results, history_dir=tmp_path)
        runs = history.load_runs(scope="nightly", history_dir=tmp_path)
        assert len(runs) == 1
        loaded_results = runs[0]["results"]
        assert len(loaded_results) == 1
        assert loaded_results[0]["check_name"] == "stub"
        assert loaded_results[0]["status"] == "warn"
        assert len(loaded_results[0]["findings"]) == 3


class TestMetricsSeries:
    def test_empty_series_when_no_history(self, tmp_path: Path) -> None:
        series = history.metrics_series(days=30, history_dir=tmp_path)
        assert series == []

    def test_series_has_required_keys(self, tmp_path: Path) -> None:
        results = [
            _make_result("schema"),
            _make_result("orphan", status="warn", n_findings=2),
            _make_result("stub", status="warn", n_findings=1),
            _make_result("wikilink"),
            _make_result("bloat"),
            _make_result("quote_budget"),
        ]
        history.append_run("nightly", results, history_dir=tmp_path)
        series = history.metrics_series(days=30, history_dir=tmp_path)
        assert len(series) == 1
        entry = series[0]
        assert "run_at" in entry
        assert "orphan_count" in entry
        assert "avg_confidence_score" in entry
        assert "stale_count" in entry
        assert "wikilink_error_count" in entry

    def test_series_counts_orphans(self, tmp_path: Path) -> None:
        results = [
            _make_result("orphan", status="warn", n_findings=5),
        ]
        history.append_run("nightly", results, history_dir=tmp_path)
        series = history.metrics_series(days=30, history_dir=tmp_path)
        assert series[0]["orphan_count"] == 5

    def test_series_counts_stale(self, tmp_path: Path) -> None:
        results = [
            _make_result("stub", status="warn", n_findings=3),
        ]
        history.append_run("nightly", results, history_dir=tmp_path)
        series = history.metrics_series(days=30, history_dir=tmp_path)
        assert series[0]["stale_count"] == 3
