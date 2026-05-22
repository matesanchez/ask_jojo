"""QA API router — backs the Chat tab in the JoJo Bot frontend.

The Chat tab is the user-facing surface for Phase 4 Q&A. Most endpoints
are deterministic and serve real responses today; the synthesis
endpoints are feature-flagged on ``config.get("anthropic_api_key")``
per ``ADR 0011``. When the API key is absent, ``POST /api/qa/query``
returns the ``api_key_required`` shape with the retrieval bundle
attached so the UI can render a Cowork-handoff modal.

Endpoint map:

- ``GET  /api/qa/route``        — regex router classification (?q=).
- ``GET  /api/qa/index``        — full ``_index.md`` parsed.
- ``GET  /api/qa/retrieve``     — assemble the retrieval bundle (?q=, ?k=).
- ``GET  /api/qa/path``         — BFS shortest path (?from=&to=).
- ``GET  /api/qa/graph``        — graph stats summary.
- ``GET  /api/qa/qmd-status``   — qmd activation status.
- ``GET  /api/qa/misses``       — recent miss-log summary.
- ``POST /api/qa/query``        — feature-flagged synthesis.
- ``POST /api/qa/explain``      — feature-flagged citation-trace.
- ``POST /api/qa/file-back``    — write a derived/<date>-<slug>.md page.

Implementation notes:

- Wiki root is read via ``_wiki_root()`` (env var first, then config,
  then sibling-of-cwd default — same pattern as raw_router/wiki_router).
- The synthesis endpoints use the canonical ``api_key_required`` shape
  from ``jojo_qa.synthesize`` so the Chat tab and Wiki tab edit modal
  share the same UI conventions.
- ``POST /api/qa/file-back`` writes deterministically (no model call) —
  the body comes from the caller (e.g. Cowork session pasted answer).
"""

from __future__ import annotations

import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from jojo_core import config
from jojo_qa import (
    graph as graph_mod,
)
from jojo_qa import (
    index_loader,
    miss_log,
    qmd_activation,
    synthesize,
)
from jojo_qa import (
    router as qa_router,
)

router = APIRouter()

# ------------------------------------------------------------- config helpers


def _wiki_root() -> Path:
    """Resolve the wiki root each request — mirrors raw_router/wiki_router."""
    default = str(Path(__file__).resolve().parents[4] / "ask_jojo_wiki")
    env_val = os.environ.get("JOJO_WIKI_ROOT")
    if env_val:
        return Path(env_val).resolve()
    return Path(config.get("wiki_root", default)).resolve()


def _manifest_path() -> Path | None:
    """Resolve the manifest path. Returns None if it doesn't exist."""
    raw_root = config.get("raw_root", None)
    if raw_root:
        p = Path(raw_root).resolve() / "manifest.json"
    else:
        p = _wiki_root().parent / "ask_jojo_raw" / "manifest.json"
    return p if p.exists() else None


_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9\-]*$")


def _validate_slug(slug: str) -> str:
    """Reject slugs that don't conform to wiki naming. Used by /path."""
    if not _SLUG_RE.match(slug):
        raise HTTPException(status_code=400, detail=f"invalid slug: {slug!r}")
    return slug


def _slugify(text: str) -> str:
    """Cheap slugifier for file-back destination paths.

    Lowercase, replace whitespace and punctuation with hyphens, collapse
    runs, trim leading/trailing hyphens. Truncates to 80 chars.
    """
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text[:80] or "untitled"


# ------------------------------------------------------------- request models


class QueryRequest(BaseModel):
    """Body for ``POST /api/qa/query``."""

    question: str
    depth: str = "sonnet"  # "sonnet" | "opus"
    route_hint: str | None = None  # "v1" | "wiki" | None


class ExplainRequest(BaseModel):
    """Body for ``POST /api/qa/explain``."""

    question: str
    answer_slugs: list[str]


class FileBackRequest(BaseModel):
    """Body for ``POST /api/qa/file-back``.

    Writes a derived/<date>-<slug>.md page into the wiki repo. The
    body is the markdown the caller wants persisted (typically a Cowork
    session's answer). The endpoint adds frontmatter and writes the
    file; it does not commit (the operator commits after review).
    """

    title: str
    body: str
    slug: str | None = None  # auto-derived from title if absent
    corpus: str = "protein-sciences"
    sources: list[dict[str, str]] | None = None
    confidence: str = "low"


class MissLogRequest(BaseModel):
    """Body for ``POST /api/qa/misses``."""

    question: str
    route: str = "wiki"
    reason: str = "no-candidates"
    raw_entries: list[str] = []
    candidate_slugs: list[str] = []
    session_id: str = ""


# ------------------------------------------------------------- deterministic endpoints


@router.get("/route")
def get_route(q: str = Query(..., min_length=1)) -> dict[str, Any]:
    """Classify ``q`` into ``v1`` or ``wiki``. Pure-regex; no model call."""
    result = qa_router.classify(q)
    return {
        "route": result.route,
        "reason": result.reason,
        "matched_keywords": list(result.matched_keywords),
        "override_matched": result.override_matched,
    }


@router.get("/index")
def get_index() -> dict[str, Any]:
    """Return the parsed ``_index.md`` as a list of entries."""
    entries = index_loader.load_index(_wiki_root())
    return {
        "total": len(entries),
        "entries": [
            {
                "slug": e.slug,
                "title": e.title,
                "type": e.type,
                "path": e.path,
            }
            for e in entries
        ],
    }


@router.get("/retrieve")
def get_retrieve(
    q: str = Query(..., min_length=1),
    k: int = Query(8, ge=1, le=20),
    include_neighbors: bool = Query(True),
) -> dict[str, Any]:
    """Build the retrieval bundle for ``q``.

    Pure deterministic plumbing: regex router + ``_index.md`` ranking
    + 1-hop graph neighborhood + raw-fallback search. No model call.
    The Chat tab uses this for the api-key-required path; the
    synthesis path uses it as the bundle on API day.
    """
    bundle = synthesize.build_retrieval_bundle(
        q,
        wiki_root=_wiki_root(),
        manifest_path=_manifest_path(),
        k_candidates=k,
        include_neighbors=include_neighbors,
    )
    return bundle.to_dict()


@router.get("/path")
def get_path(
    src: str = Query(..., alias="from", description="source slug"),
    dst: str = Query(..., alias="to", description="destination slug"),
) -> dict[str, Any]:
    """BFS shortest path between two wiki slugs."""
    _validate_slug(src)
    _validate_slug(dst)
    g = graph_mod.load(_wiki_root())
    if not g.nodes:
        g = graph_mod.build(_wiki_root())
    path = graph_mod.shortest_path(g, src, dst)
    if path is None:
        return {"path": None, "hops": None, "reason": "disconnected or missing slug"}
    return {"path": path, "hops": len(path) - 1}


@router.get("/graph")
def get_graph_stats() -> dict[str, Any]:
    """Return the graph stats summary (nodes/edges/components/avg_degree)."""
    g = graph_mod.load(_wiki_root())
    if not g.nodes:
        g = graph_mod.build(_wiki_root())
    return graph_mod.stats(g)


@router.get("/qmd-status")
def get_qmd_status() -> dict[str, Any]:
    """Return qmd activation status (triggers, current values, reason)."""
    return qmd_activation.status_summary(wiki_root=_wiki_root())


@router.get("/misses")
def get_misses(window_days: int = Query(14, ge=1, le=365)) -> dict[str, Any]:
    """Recent miss-log summary."""
    return miss_log.summary(window_days=window_days)


@router.post("/misses")
def post_miss(req: MissLogRequest) -> dict[str, Any]:
    """Append one miss-log entry. Used by Cowork sessions and the Chat tab."""
    log_path = miss_log.append(
        req.question,
        route=req.route,
        reason=req.reason,
        raw_entries=req.raw_entries,
        candidate_slugs=req.candidate_slugs,
        session_id=req.session_id,
    )
    return {"status": "logged", "path": str(log_path)}


# ------------------------------------------------------------- feature-flagged synthesis


@router.post("/query")
def post_query(req: QueryRequest) -> dict[str, Any]:
    """Synthesize an answer to ``req.question``.

    Today: returns the ``api_key_required`` shape with the retrieval
    bundle attached when ``anthropic_api_key`` is absent in config.
    On API day: calls Sonnet 4.6 (or Opus 4.6 if depth='opus') and
    returns the synthesized answer.

    The retrieval bundle in the no-key response is the same shape a
    Cowork session consumes today (see ADR 0011 + docs/qa/qa-prompt.md).
    """
    if req.depth not in ("sonnet", "opus"):
        raise HTTPException(
            status_code=400,
            detail="depth must be 'sonnet' or 'opus'",
        )
    if req.route_hint not in (None, "v1", "wiki"):
        raise HTTPException(
            status_code=400,
            detail="route_hint must be 'v1' or 'wiki'",
        )

    # Cast types narrowly so static checkers stay happy.
    depth: Any = req.depth
    route_hint: Any = req.route_hint

    return synthesize.answer(
        req.question,
        wiki_root=_wiki_root(),
        manifest_path=_manifest_path(),
        depth=depth,
        route_hint=route_hint,
    )


@router.post("/explain")
def post_explain(req: ExplainRequest) -> dict[str, Any]:
    """Trace the citation chain for an answer.

    Today: deterministic. Returns the wikilink graph between the cited
    slugs and the candidate-rank scores for each. The model-side
    explanation lands when the API key does.
    """
    g = graph_mod.load(_wiki_root())
    if not g.nodes:
        g = graph_mod.build(_wiki_root())

    pairs: list[dict[str, Any]] = []
    for i, src in enumerate(req.answer_slugs):
        for dst in req.answer_slugs[i + 1 :]:
            path = graph_mod.shortest_path(g, src, dst)
            pairs.append(
                {
                    "from": src,
                    "to": dst,
                    "path": path,
                    "hops": (len(path) - 1) if path else None,
                }
            )

    api_key = config.get("anthropic_api_key", None)
    return {
        "status": "ok",
        "model_explanation": bool(api_key),
        "message": (
            "Citation graph ready."
            if api_key
            else "Citation graph computed. Add an API key in Settings for model-side explanations."
        ),
        "question": req.question,
        "graph_pairs": pairs,
    }


# ------------------------------------------------------------- file-back


@router.post("/file-back")
def post_file_back(req: FileBackRequest) -> dict[str, Any]:
    """Write a ``ask_jojo_wiki/derived/<date>-<slug>.md`` page.

    Deterministic file write. The caller (Chat tab "File this" button
    or a Cowork session) supplies the body; this endpoint adds
    frontmatter and writes the file. No git commit — the operator
    reviews and commits separately.

    Path traversal guard: the slug is sanitized via ``_slugify`` so
    callers cannot escape the ``derived/`` directory.
    """
    wiki_root = _wiki_root()
    derived = wiki_root / "derived"
    derived.mkdir(parents=True, exist_ok=True)

    slug = _slugify(req.slug or req.title)
    today = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
    fname = f"{today}-{slug}.md"
    out_path = derived / fname

    # Frontmatter per SCHEMA.md Section 3.
    sources_yaml = ""
    if req.sources:
        for s in req.sources:
            path = s.get("path", "")
            hash_val = s.get("hash", "")
            ingested = s.get("ingested", today)
            sources_yaml += f"  - path: {path}\n    hash: {hash_val}\n    ingested: {ingested}\n"
    else:
        sources_yaml = (
            f"  - path: derived-from-cowork-session\n"
            f"    hash: cowork-{today}\n"
            f"    ingested: {today}\n"
        )

    frontmatter = (
        "---\n"
        f"title: {req.title}\n"
        "type: derived\n"
        f"slug: {slug}\n"
        f"created: {today}\n"
        f"last_updated: {today}\n"
        f"last_reviewed: {today}\n"
        "schema_version: 0.1.0\n"
        f"confidence: {req.confidence}\n"
        f"corpus: {req.corpus}\n"
        "sources:\n"
        f"{sources_yaml}"
        "---\n\n"
    )

    out_path.write_text(frontmatter + req.body, encoding="utf-8")
    rel = out_path.relative_to(wiki_root)
    return {
        "status": "filed",
        "path": rel.as_posix(),
        "absolute_path": str(out_path),
        "slug": slug,
        "next_step": (
            "Review the page in the Wiki tab and commit it under the "
            "qa(<corpus>): <slug> filed under derived/ prefix per ADR 0011."
        ),
    }
