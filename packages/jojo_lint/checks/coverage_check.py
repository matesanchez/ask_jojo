"""Coverage check — flags skip categories that still hide knowledge content.

This is the durable regression guard for the FU-20 finding: the Phase 2 absorb
pass categorically skipped person-named folders (``departed_individual``,
``individual_user_data``, ...) that in fact held real organizational knowledge.

For each skip category in the compile queue, this check samples ``sample_size``
entries (deterministically, by ``seed``) and applies a content-vs-folder-name
heuristic to estimate how much of the category is actually knowledge-bearing.
A category whose sampled knowledge fraction exceeds ``threshold`` is flagged:
the categorical skip is too coarse and the category needs entry-level review.

Categories that are legitimately mechanical/bulk and identifiable by path alone
(LCMS dumps, caches, supersession bookkeeping) are exempt from the gate, per
FU-20 recommendation #2 ("keep an exception list for clearly mechanical signals").

Runs **weekly** (sampling every night is wasteful). No model calls — the
heuristic is deterministic — so it has no ``api_key_required`` path.
"""

from __future__ import annotations

import json
import random
import re
import time
from datetime import datetime, timezone
from pathlib import Path

from .base import CheckResult

# Skip line in queue.md, e.g. "- [x] <entry_id>  <!-- skip: departed_individual -->"
_SKIP_RE = re.compile(r"^- \[[ xX]\] (\S+)\s+<!-- skip: ([a-z_]+) -->")

# Knowledge signals evaluated against the *document basename + title* only,
# never the folder path (the folder path is what produced the original false
# skips — a science-named folder made every personal file look like science).
_NRX_RE = re.compile(r"\bn[rx]x?-?\d{3,}", re.I)
_PROTOCOL_KW = (
    "protocol", "assay", "-method", "methods-", "workflow", "sop", "procedure",
    "characterization", "purity", "quantitation", "quant-", "stability",
    "solubility", "ksol", "tfa-analysis", "titration", "calibration", "qc-",
)
_SCIENCE_KW = (
    "cbl", "btk", "itk", "tyk2", "irak4", "zap-70", "zap70", "pellino", "peli",
    "skp2", "cdc34", "crbn", "cereblon", "protac", "degrader", "t-cell", "tcell",
    "cd8", "cd4", "treg", "checkpoint", "ctla", "pd-1", "pd1", "tumor", "immuno",
    "antibody", "elisa", "western", "flow-cytometry", "facs", "kinetic", "biacore",
    "spr", "crispr", "rna-seq", "ngs", "lcms", "mass-spec", "chromatography",
    "hplc", "uplc", "degradation", "ubiquit", "e3-ligase", "ligase", "screen",
    "binding", "potency", "ic50", "pharmacolog", "in-vivo", "in-vitro", "compound",
    "inhibitor", "mechanism", "pathway", "expression", "purification", "adme",
)
_PERSONAL_KW = (
    "mcat", "resume", "personal-statement", "grad-school", "medical-school",
    "application", "transcript", "cover-letter", "travel", "itinerary", "hotel",
    "reservation", "lecture-notes", "homework", "syllabus", "invoice", "receipt",
    "passport", "vacation", "recipe",
)
_SOFTWARE_KW = (
    "installer", "-setup-", "chromeleon", "openlab", "flowjo", "chimerax",
    ".msi", "redistributable", "vcredist", "uninstall",
)

# Skip categories that are legitimately mechanical/bulk and are correctly
# identifiable by path alone (FU-20 recommendation #2: keep an exception list
# for clearly mechanical signals). These are exempt from the coverage gate —
# they contain science tokens but are data dumps / caches / supersession
# bookkeeping, not narrative knowledge that belongs on a wiki page.
_MECHANICAL_CATEGORY_SUBSTRINGS = (
    "lcms", "bulk", "compute_output", "instrument_data", "instrument_dump",
    "instrument_backup", "software_cache", "cache", "dump", "qc_evidence",
    "superseded", "duplicate", "iterative", "low_signal", "cro_",
    "_record_no_wiki", "not_wiki", "no_wiki_narrative", "residual", "project_archive",
)


def _is_mechanical_category(category: str) -> bool:
    return any(sub in category for sub in _MECHANICAL_CATEGORY_SUBSTRINGS)


def _is_knowledge(entry_id: str, entry: dict | None) -> bool:
    """Heuristic: does this entry look like knowledge content (not personal/software)?"""
    title = (entry or {}).get("title", "") or ""
    src = (entry or {}).get("source_id", "") or ""
    basename = src.split("/")[-1].lower() if src else entry_id.lower()
    signal = basename + " " + title.lower()

    if any(k in entry_id.lower() for k in _SOFTWARE_KW):
        return False
    science = any(k in signal for k in _SCIENCE_KW) or bool(_NRX_RE.search(signal))
    if any(k in signal for k in _PERSONAL_KW) and not science:
        return False
    if science:
        return True
    if any(k in signal for k in _PROTOCOL_KW):
        return True
    # PDFs with no decisive signal are most often literature -> count as knowledge.
    return basename.endswith(".pdf") or entry_id.lower().endswith("-pdf")


def _load_manifest(manifest_path: Path | None) -> dict:
    if not manifest_path:
        return {}
    p = Path(manifest_path)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8")).get("entries", {})
    except (OSError, json.JSONDecodeError):
        return {}


def run(
    wiki_root: Path | str,
    queue_path: Path | str | None = None,
    manifest_path: Path | str | None = None,
    sample_size: int = 30,
    seed: int = 2026,
    threshold: float = 0.15,
    min_population: int = 30,
) -> CheckResult:
    """Sample each non-mechanical skip category and flag those over threshold.

    Args:
        wiki_root: accepted for interface consistency; unused (coverage is a
            corpus/queue property, not a wiki-page property).
        queue_path: path to ``docs/compile/queue.md``. If ``None``, the check
            returns ``pass`` with an informational finding (nothing to sample).
        manifest_path: optional ``ask_jojo_raw/manifest.json`` for title/source_id
            signal. Without it the heuristic falls back to the entry_id alone.
        sample_size: entries sampled per category (default 30).
        seed: RNG seed for deterministic sampling.
        threshold: max tolerated knowledge fraction before a category is flagged.
        min_population: categories smaller than this are reported as info, not failed.

    Returns:
        CheckResult(check_name="coverage"). Status ``"fail"`` if any non-exempt
        category exceeds the threshold, else ``"pass"``.
    """
    start = time.monotonic()
    findings: list[dict] = []

    if queue_path is None:
        return CheckResult(
            check_name="coverage",
            status="pass",
            findings=[{"slug": "-", "message": "no queue_path provided; nothing to sample", "severity": "info"}],
            run_at=datetime.now(tz=timezone.utc).isoformat(),
            duration_ms=int((time.monotonic() - start) * 1000),
        )

    queue_path = Path(queue_path)
    entries = _load_manifest(Path(manifest_path) if manifest_path else None)

    populations: dict[str, list[str]] = {}
    try:
        for line in queue_path.read_text(encoding="utf-8", errors="replace").splitlines():
            m = _SKIP_RE.match(line)
            if m:
                populations.setdefault(m.group(2), []).append(m.group(1))
    except OSError:
        return CheckResult(
            check_name="coverage",
            status="warn",
            findings=[{"slug": "-", "message": f"could not read queue at {queue_path}", "severity": "warn"}],
            run_at=datetime.now(tz=timezone.utc).isoformat(),
            duration_ms=int((time.monotonic() - start) * 1000),
        )

    rng = random.Random(seed)
    failed = False
    for category, ids in sorted(populations.items()):
        if _is_mechanical_category(category):
            findings.append({
                "slug": category,
                "message": f"'{category}' is a mechanical/bulk skip category (exempt from coverage gate)",
                "severity": "info",
            })
            continue
        if len(ids) < min_population:
            findings.append({
                "slug": category,
                "message": f"population {len(ids)} < min_population {min_population}; skipped sampling",
                "severity": "info",
            })
            continue
        sample = rng.sample(ids, min(sample_size, len(ids)))
        knowledge = sum(1 for eid in sample if _is_knowledge(eid, entries.get(eid)))
        frac = knowledge / len(sample)
        if frac > threshold:
            failed = True
            findings.append({
                "slug": category,
                "message": (
                    f"skip category '{category}' (population {len(ids)}) sampled "
                    f"{knowledge}/{len(sample)} = {frac:.0%} knowledge content "
                    f"(> {threshold:.0%}); categorical skip too coarse — needs entry-level review"
                ),
                "severity": "error",
            })
        else:
            findings.append({
                "slug": category,
                "message": f"'{category}' sampled {frac:.0%} knowledge (<= {threshold:.0%}); ok",
                "severity": "info",
            })

    return CheckResult(
        check_name="coverage",
        status="fail" if failed else "pass",
        findings=findings,
        run_at=datetime.now(tz=timezone.utc).isoformat(),
        duration_ms=int((time.monotonic() - start) * 1000),
    )
