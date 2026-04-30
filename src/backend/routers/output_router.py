"""Output API router — backs the Phase 5 rich-output rendering surface.

Endpoints, all deterministic today:

- ``GET  /api/output/classify-format``  — regex format classifier.
- ``GET  /api/output/plot-types``       — list supported plot types.
- ``GET  /api/output/formats``          — list supported output formats.
- ``POST /api/output/render``           — render a typed spec to bytes
                                          or a wiki/outputs/ file.
- ``POST /api/output/file-back``        — write a derived/<slug>.md or
                                          outputs/<slug>.md page from
                                          a model-authored body.
- ``GET  /api/output/list``             — list pages under wiki/outputs/.
- ``GET  /api/output/page``             — read one wiki/outputs/ page.

Implementation notes:

- Wiki root resolution mirrors ``wiki_router.py`` and ``qa_router.py``:
  ``$JOJO_WIKI_ROOT`` env var first, then ``config.json``, then sibling
  default.
- The render endpoint dispatches to ``packages/jojo_output/`` based on
  the ``format`` field. matplotlib renders go through the sandbox
  (which is in-process today; the rlimit subprocess path lights up
  in production).
- All pydantic spec validation happens at the router layer so bad
  requests fail fast with HTTP 422.
"""

from __future__ import annotations

import base64
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field, ValidationError

from jojo_core import config
from jojo_qa import format as qa_format

router = APIRouter()


# ----------------------------------------------------------- helpers


def _wiki_root() -> Path:
    default = str(Path(__file__).resolve().parents[4] / "ask_jojo_wiki")
    env_val = os.environ.get("JOJO_WIKI_ROOT")
    if env_val:
        return Path(env_val).resolve()
    return Path(config.get("wiki_root", default)).resolve()


_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9\-]*$")


def _slugify(text: str) -> str:
    """Same routine as qa_router._slugify; duplicated to keep the two
    routers independent."""
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text[:80] or "untitled"


def _today() -> str:
    return datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")


def _outputs_root(wiki_root: Path | None = None) -> Path:
    root = wiki_root if wiki_root is not None else _wiki_root()
    out = root / "outputs"
    out.mkdir(parents=True, exist_ok=True)
    return out


# ----------------------------------------------------------- format classifier


@router.get("/classify-format")
def classify_format(q: str = Query(..., min_length=1)) -> dict[str, Any]:
    """Classify ``q`` into one of the supported output formats."""
    result = qa_format.classify(q)
    return {
        "format": result.format,
        "reason": result.reason,
        "matched_keywords": list(result.matched_keywords),
        "confidence": result.confidence,
        "candidate_scores": result.candidate_scores,
    }


@router.get("/formats")
def list_formats() -> dict[str, list[str]]:
    """List supported output formats (UI dropdown source of truth)."""
    return {"formats": list(qa_format.available_formats())}


@router.get("/plot-types")
def list_plot_types() -> dict[str, list[str]]:
    """List supported matplotlib plot types."""
    try:
        from jojo_output.sandbox import available_plot_types
    except ImportError as e:
        raise HTTPException(
            status_code=503,
            detail=f"jojo_output sandbox is not installed: {e}",
        ) from e
    return {"plot_types": list(available_plot_types())}


# ----------------------------------------------------------- render


class RenderRequest(BaseModel):
    """POST /api/output/render body.

    The ``spec`` field is shape-validated against the format-specific
    pydantic model. Validation errors return HTTP 422 with the
    pydantic detail.
    """

    format: Literal[
        "markdown", "marp", "matplotlib", "plotly",
        "table", "mermaid", "docx", "pptx", "pdf",
    ]
    spec: dict[str, Any]
    out_subpath: str | None = Field(
        None,
        description="Optional path under wiki/outputs/ to write the artifact "
        "to. When absent the response carries the bytes inline (base64 for "
        "binary formats).",
    )


@router.post("/render")
def post_render(req: RenderRequest) -> dict[str, Any]:  # noqa: C901 — dispatch table
    """Render a typed spec to an artifact.

    For text formats (markdown, marp, table, mermaid) the response carries
    the rendered text inline. For binary formats (matplotlib, docx, pptx,
    pdf) it carries either a file path (when ``out_subpath`` is set) or
    base64 bytes.
    """
    fmt = req.format

    # Path-traversal guard on out_subpath.
    if req.out_subpath:
        out_root = _outputs_root()
        candidate = (out_root / req.out_subpath).resolve()
        try:
            candidate.relative_to(out_root)
        except ValueError as exc:
            raise HTTPException(
                status_code=400,
                detail="out_subpath escapes wiki/outputs/",
            ) from exc

    # Dispatch table. Each branch returns a dict shaped for the response.
    if fmt == "markdown":
        from jojo_output.renderers import MarkdownSpec, render_markdown

        spec = _validate(MarkdownSpec, req.spec)
        out = render_markdown(spec)
        return {"status": "ok", "format": "markdown", "text": out}

    if fmt == "marp":
        from jojo_output.renderers import MarpSpec, render_marp

        spec = _validate(MarpSpec, req.spec)
        out = render_marp(spec)
        return {"status": "ok", "format": "marp", "text": out}

    if fmt == "table":
        from jojo_output.renderers import TableSpec, render_table

        spec = _validate(TableSpec, req.spec)
        out = render_table(spec)
        return {
            "status": "ok",
            "format": "table",
            "markdown": out["markdown"],
            "csv": out["csv"],
        }

    if fmt == "mermaid":
        # Mermaid is just a markdown fenced block; passthrough.
        body = req.spec.get("body", "")
        if not isinstance(body, str):
            raise HTTPException(status_code=422, detail="mermaid 'body' must be a string")
        text = f"```mermaid\n{body.strip()}\n```\n"
        return {"status": "ok", "format": "mermaid", "text": text}

    if fmt == "matplotlib":
        try:
            from jojo_output.sandbox import run as sandbox_run
        except ImportError as e:
            raise HTTPException(
                status_code=503,
                detail=f"matplotlib sandbox not installed: {e}",
            ) from e
        out_path = None
        if req.out_subpath:
            out_path = _outputs_root() / req.out_subpath
        result = sandbox_run(req.spec, out_path=out_path)
        if result.status != "ok":
            raise HTTPException(
                status_code=422 if result.status == "validation_error" else 500,
                detail={
                    "status": result.status,
                    "error": result.error,
                    "duration_ms": result.duration_ms,
                },
            )
        if out_path is not None and result.out_path is not None:
            return {
                "status": "ok",
                "format": "matplotlib",
                "out_path": str(result.out_path.relative_to(_wiki_root())),
                "duration_ms": result.duration_ms,
            }
        return {
            "status": "ok",
            "format": "matplotlib",
            "bytes_b64": base64.b64encode(result.bytes or b"").decode("ascii"),
            "duration_ms": result.duration_ms,
        }

    if fmt == "docx":
        from jojo_output.renderers.docx_renderer import DocxSpec, render_docx

        spec = _validate(DocxSpec, req.spec)
        out_path = _outputs_root() / (req.out_subpath or f"{_today()}-{_slugify(spec.title or 'memo')}.docx")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            written = render_docx(spec, out_path)
        except RuntimeError as e:
            raise HTTPException(status_code=503, detail=str(e)) from e
        return {
            "status": "ok",
            "format": "docx",
            "out_path": str(written.relative_to(_wiki_root())),
        }

    if fmt == "pptx":
        from jojo_output.renderers.pptx_renderer import PptxSpec, render_pptx

        spec = _validate(PptxSpec, req.spec)
        out_path = _outputs_root() / (req.out_subpath or f"{_today()}-{_slugify(spec.title or 'deck')}.pptx")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            written = render_pptx(spec, out_path)
        except RuntimeError as e:
            raise HTTPException(status_code=503, detail=str(e)) from e
        return {
            "status": "ok",
            "format": "pptx",
            "out_path": str(written.relative_to(_wiki_root())),
        }

    if fmt == "pdf":
        from jojo_output.renderers.pdf_renderer import PdfSpec, render_pdf

        spec = _validate(PdfSpec, req.spec)
        out_path = _outputs_root() / (req.out_subpath or f"{_today()}-{_slugify(spec.title or 'output')}.pdf")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            written = render_pdf(spec, out_path)
        except RuntimeError as e:
            raise HTTPException(status_code=503, detail=str(e)) from e
        return {
            "status": "ok",
            "format": "pdf",
            "out_path": str(written.relative_to(_wiki_root())),
        }

    if fmt == "plotly":
        # Plotly is a typed spec (same shape as matplotlib); we route to a
        # plotly-specific renderer when one ships. Today, return an
        # informative 501 so the frontend can fall back to a plain
        # matplotlib render.
        raise HTTPException(
            status_code=501,
            detail="plotly renderer pending; use 'matplotlib' for now",
        )

    raise HTTPException(status_code=400, detail=f"unsupported format: {fmt}")


def _validate(model_cls: type, payload: dict[str, Any]):
    """Pydantic validation with HTTP-422 mapping."""
    try:
        return model_cls.model_validate(payload)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors()) from exc


# ----------------------------------------------------------- file-back


class FileBackRequest(BaseModel):
    """POST /api/output/file-back -- write an outputs/<slug>.md page."""

    title: str
    body: str
    output_format: str = "markdown"
    source_question: str = ""
    source_session_id: str = ""
    parent_slugs: list[str] = []
    confidence: Literal["high", "medium", "low"] = "low"
    corpus: str = "protein-sciences"
    spec: dict[str, Any] | None = None  # original typed spec (optional)


@router.post("/file-back")
def post_file_back(req: FileBackRequest) -> dict[str, Any]:
    """Write a wiki/outputs/<date>-<slug>.md page from a model answer.

    Deterministic file write; no model call. Returns the path and a
    next-step hint for the operator's commit.
    """
    slug = _slugify(req.title)
    today = _today()
    fname = f"{today}-{slug}.md"
    out_path = _outputs_root() / fname

    parent_yaml = "\n".join(f"  - {p}" for p in req.parent_slugs) or "  - (no parent slugs)"
    spec_yaml = ""
    if req.spec:
        import yaml as _yaml  # type: ignore[import-not-found]

        spec_yaml = "spec:\n" + _yaml.safe_dump(req.spec, indent=2).rstrip() + "\n"

    frontmatter = (
        "---\n"
        f"title: {req.title}\n"
        "type: output\n"
        f"slug: {today}-{slug}\n"
        f"created: {today}\n"
        f"last_updated: {today}\n"
        f"last_reviewed: {today}\n"
        "schema_version: 0.1.0\n"
        f"confidence: {req.confidence}\n"
        f"corpus: {req.corpus}\n"
        f"output_format: {req.output_format}\n"
        f"source_question: {req.source_question!r}\n"
        f"source_session_id: {req.source_session_id}\n"
        "parent_slugs:\n"
        f"{parent_yaml}\n"
        f"{spec_yaml}"
        "sources:\n"
        f"  - path: derived-from-output-rendering\n"
        f"    hash: output-{today}\n"
        f"    ingested: {today}\n"
        "---\n\n"
    )

    out_path.write_text(frontmatter + req.body, encoding="utf-8")
    rel = out_path.relative_to(_wiki_root())
    return {
        "status": "filed",
        "path": str(rel),
        "absolute_path": str(out_path),
        "slug": f"{today}-{slug}",
        "next_step": (
            f"Review {rel} in the Wiki tab and commit under the "
            f"output(<corpus>): {today}-{slug} prefix."
        ),
    }


# ----------------------------------------------------------- list / read


@router.get("/list")
def list_outputs() -> dict[str, Any]:
    """List all pages under wiki/outputs/ with frontmatter summary."""
    root = _outputs_root()
    out: list[dict[str, Any]] = []
    for p in sorted(root.glob("*.md")):
        if p.name.startswith("_"):
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except OSError:
            continue
        # Cheap frontmatter scrape (no full YAML parse to keep this fast).
        title = ""
        fmt = "markdown"
        confidence = ""
        if text.startswith("---"):
            end = text.find("\n---\n", 3)
            if end != -1:
                fm = text[4:end]
                for line in fm.splitlines():
                    if line.startswith("title:"):
                        title = line.split(":", 1)[1].strip()
                    elif line.startswith("output_format:"):
                        fmt = line.split(":", 1)[1].strip()
                    elif line.startswith("confidence:"):
                        confidence = line.split(":", 1)[1].strip()
        out.append({
            "path": str(p.relative_to(_wiki_root())),
            "slug": p.stem,
            "title": title or p.stem,
            "output_format": fmt,
            "confidence": confidence,
            "size_bytes": p.stat().st_size,
        })
    return {"total": len(out), "outputs": out}


@router.get("/page")
def get_output_page(path: str = Query(..., min_length=1)) -> dict[str, Any]:
    """Read one wiki/outputs/ page (frontmatter + body)."""
    root = _wiki_root()
    full = (root / path).resolve()
    try:
        full.relative_to(root / "outputs")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="path must be under outputs/") from exc
    if not full.exists():
        raise HTTPException(status_code=404, detail=f"not found: {path}")
    text = full.read_text(encoding="utf-8")
    return {"path": path, "body": text}
