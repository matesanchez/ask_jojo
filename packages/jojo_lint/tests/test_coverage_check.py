"""Tests for the weekly coverage_check (FU-20 regression guard)."""

from __future__ import annotations

import json
from pathlib import Path

from jojo_lint.checks import coverage_check
from jojo_lint import registry


def _write_queue(tmp_path: Path, lines: list[str]) -> Path:
    q = tmp_path / "queue.md"
    q.write_text("# queue\n\n" + "\n".join(lines) + "\n", encoding="utf-8")
    return q


def _knowledge_lines(n: int, category: str) -> list[str]:
    # Filenames that clearly read as scientific knowledge.
    names = [
        "publicdrive_teamfolder-cbl-b-inhibitor-potency-report-pdf",
        "publicdrive_teamfolder-turbidimetric-solubility-assay-protocol-docx",
        "publicdrive_teamfolder-nrx-0401352-purity-report-pdf",
        "publicdrive_teamfolder-btk-stability-study-results-pptx",
        "publicdrive_teamfolder-t-cell-exhaustion-checkpoint-review-pdf",
    ]
    out = []
    for i in range(n):
        out.append(f"- [x] {names[i % len(names)]}-{i}  <!-- skip: {category} -->")
    return out


def _personal_lines(n: int, category: str) -> list[str]:
    names = [
        "publicdrive_person-historical-mcat-notes-docx",
        "publicdrive_person-historical-travel-itinerary-2023-docx",
        "publicdrive_person-historical-personal-statement-grad-school-docx",
        "publicdrive_person-historical-hotel-reservation-pdf",
        "publicdrive_person-software-chromeleon-installer-msi",
    ]
    out = []
    for i in range(n):
        out.append(f"- [x] {names[i % len(names)]}-{i}  <!-- skip: {category} -->")
    return out


def test_flags_category_with_knowledge_content(tmp_path: Path) -> None:
    q = _write_queue(tmp_path, _knowledge_lines(40, "individual_user_data"))
    res = coverage_check.run(tmp_path, queue_path=q, sample_size=30)
    assert res.check_name == "coverage"
    assert res.status == "fail"
    assert any(f["severity"] == "error" and "individual_user_data" in f["message"] for f in res.findings)


def test_passes_genuinely_personal_category(tmp_path: Path) -> None:
    q = _write_queue(tmp_path, _personal_lines(40, "individual_desktop"))
    res = coverage_check.run(tmp_path, queue_path=q, sample_size=30)
    assert res.status == "pass"
    assert all(f["severity"] != "error" for f in res.findings)


def test_small_population_is_info_not_fail(tmp_path: Path) -> None:
    q = _write_queue(tmp_path, _knowledge_lines(5, "tiny_cat"))
    res = coverage_check.run(tmp_path, queue_path=q, sample_size=30, min_population=30)
    assert res.status == "pass"
    assert any(f["severity"] == "info" and "min_population" in f["message"] for f in res.findings)


def test_none_queue_path_passes_with_info(tmp_path: Path) -> None:
    res = coverage_check.run(tmp_path, queue_path=None)
    assert res.status == "pass"
    assert res.findings[0]["severity"] == "info"


def test_manifest_title_signal_used(tmp_path: Path) -> None:
    # entry_id is opaque, but manifest title carries the knowledge signal.
    lines = [f"- [x] opaque_id_{i}  <!-- skip: mixed_cat -->" for i in range(40)]
    q = _write_queue(tmp_path, lines)
    entries = {
        f"opaque_id_{i}": {
            "title": "Ablation of Cbl-b provides protection against tumors",
            "source_id": "Team/Folder/Ablation of Cbl-b.pdf",
        }
        for i in range(40)
    }
    man = tmp_path / "manifest.json"
    man.write_text(json.dumps({"entries": entries}), encoding="utf-8")
    res = coverage_check.run(tmp_path, queue_path=q, manifest_path=man, sample_size=30)
    assert res.status == "fail"


def test_registry_runs_coverage(tmp_path: Path) -> None:
    q = _write_queue(tmp_path, _knowledge_lines(40, "individual_user_data"))
    res = registry.run_check("coverage", tmp_path, queue_path=q)
    assert res.check_name == "coverage"
    assert res.status == "fail"
    assert "coverage" in registry.WEEKLY_CHECKS


def test_determinism(tmp_path: Path) -> None:
    q = _write_queue(tmp_path, _knowledge_lines(50, "cat") + _personal_lines(50, "cat2"))
    r1 = coverage_check.run(tmp_path, queue_path=q, seed=2026)
    r2 = coverage_check.run(tmp_path, queue_path=q, seed=2026)
    assert [f["message"] for f in r1.findings] == [f["message"] for f in r2.findings]


def test_mechanical_category_is_exempt(tmp_path: Path) -> None:
    # lcms_bulk_data filenames carry science tokens but are mechanical dumps.
    lines = [f"- [x] publicdrive_lcms-run-{i}-heka-report-pdf  <!-- skip: lcms_bulk_data -->" for i in range(40)]
    q = _write_queue(tmp_path, lines)
    res = coverage_check.run(tmp_path, queue_path=q)
    assert res.status == "pass"
    assert any(f["severity"] == "info" and "mechanical" in f["message"] for f in res.findings)
