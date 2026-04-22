"""Phase 1 exit-criterion smoke test.

Per PLAN.md §6 Phase 1 exit criteria:

  - Ingest a corpus of at least 100 documents via the drive connector.
  - Every ingested file has valid frontmatter and a manifest entry.
  - Re-running produces zero work (idempotent).
  - A change record exists for the initial run.

This test is the proof that the whole pipe — walker → converter →
redaction → hash → manifest → raw write → change record — holds
together end-to-end, not just per-unit. It's slow-ish (builds 100+
real files on disk) but still runs in well under a second.
"""

from __future__ import annotations

import random
from pathlib import Path

from jojo_connectors_common import Manifest, split_frontmatter
from jojo_ingest.drive import DriveConnector
from jojo_ingest.driver import IngestDriver

# Fixed seed so failures reproduce.
_RNG = random.Random(20260422)

_TXT_TEMPLATES = [
    "# {title}\n\nProcedure details for {title}. Tris buffer at pH {ph}.\n",
    "# {title}\n\n- Step 1: align instrument\n- Step 2: load sample\n- Step 3: read at {nm} nm\n",
    "Notes on {title}.\n\nRun at {nm} nm, hold pH {ph} throughout.\n",
]


def _seed_corpus(root: Path, n_files: int = 120) -> None:
    """Build n_files across 8 subdirectories to exercise the walker."""
    subdirs = ["sop", "protocols", "recipes", "qc", "instruments", "drafts", "stability", "pharma"]
    for i in range(n_files):
        sub = subdirs[i % len(subdirs)]
        ext = ".md" if i % 2 == 0 else ".txt"
        target = root / sub / f"doc-{i:03d}{ext}"
        target.parent.mkdir(parents=True, exist_ok=True)
        tmpl = _TXT_TEMPLATES[i % len(_TXT_TEMPLATES)]
        target.write_text(
            tmpl.format(title=f"Doc {i:03d}", ph=_RNG.choice([7.0, 7.4, 8.0]), nm=_RNG.randint(260, 600)),
            encoding="utf-8",
        )
    # Add known noise that should be filtered out: one ignored folder + one
    # lock file + one unsupported binary.
    (root / "drafts" / "~$half-done.docx").write_text("lock", encoding="utf-8")
    (root / "logo.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 32)
    (root / ".jojoignore").write_text("drafts/\n", encoding="utf-8")


def test_phase1_exit_criterion(tmp_path: Path) -> None:
    source = tmp_path / "protein-sciences"
    raw = tmp_path / "ask_jojo_raw"
    _seed_corpus(source, n_files=120)

    # How many files should survive filtering? 120 with every other a .md/.txt,
    # but drafts/ (every 8th subdir × 120/8 = 15 files) get ignored.
    expected = 120 - (120 // 8)  # 15 drafts files are ignored

    # ---------------- first run: adds everything
    driver = IngestDriver(raw)
    conn = DriveConnector(source)
    r1 = driver.run([conn])
    cr1 = r1.results["drive"]
    assert cr1.added == expected, f"expected {expected} added, got {cr1.added}"
    assert cr1.updated == 0
    assert cr1.errors == 0
    assert r1.change_record_path is not None and r1.change_record_path.exists()

    # At least 100 — the PLAN exit criterion.
    assert cr1.added >= 100

    # ---------------- manifest has a row per file with frontmatter present
    manifest = Manifest.load(raw / "manifest.json")
    assert len(manifest.entries) == expected
    written = sorted((raw / "drive").glob("*.md"))
    assert len(written) == expected

    # Spot-check 10 random files for well-formed frontmatter.
    sample = _RNG.sample(written, 10)
    for path in sample:
        full = path.read_text(encoding="utf-8")
        fm, body = split_frontmatter(full)
        assert fm, f"{path.name} missing frontmatter"
        # Required fields per PLAN.md §6 Phase 1.
        assert fm["source_type"] == "drive"
        assert len(fm["sha256"]) == 64
        assert fm["access_level"] in {"public", "all_fte", "department", "restricted"}
        assert fm["id"]
        assert fm["title"]
        assert body.strip(), f"{path.name} has empty body"

    # ---------------- second run: idempotent (zero work)
    r2 = IngestDriver(raw).run([DriveConnector(source)])
    cr2 = r2.results["drive"]
    assert cr2.added == 0
    assert cr2.updated == 0
    assert cr2.skipped == expected
    # No change record emitted because nothing changed.
    assert r2.change_record_path is None

    # ---------------- third run after editing 5 files: exactly 5 updated
    targets = sorted(source.rglob("doc-*.md"))[:5]
    for t in targets:
        t.write_text(t.read_text(encoding="utf-8") + "\n(update)\n", encoding="utf-8")
    r3 = IngestDriver(raw).run([DriveConnector(source)])
    cr3 = r3.results["drive"]
    assert cr3.updated == 5
    assert cr3.added == 0
    assert cr3.errors == 0
    assert cr3.skipped == expected - 5


def test_phase1_exit_criterion_access_level_respected(tmp_path: Path) -> None:
    """Custom access_level on the connector propagates into frontmatter + manifest."""
    source = tmp_path / "src"
    (source / "sop").mkdir(parents=True)
    (source / "sop" / "restricted.md").write_text("# R\n\nBody.\n", encoding="utf-8")
    raw = tmp_path / "ask_jojo_raw"

    IngestDriver(raw).run([DriveConnector(source, access_level="restricted")])
    manifest = Manifest.load(raw / "manifest.json")
    entry = next(iter(manifest.entries.values()))
    assert entry.access_level == "restricted"

    written = list((raw / "drive").glob("*.md"))[0].read_text(encoding="utf-8")
    fm, _ = split_frontmatter(written)
    assert fm["access_level"] == "restricted"
