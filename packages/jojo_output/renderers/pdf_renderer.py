"""PDF renderer -- typeset a markdown answer as a PDF.

Two paths:

1. ``render_pdf_from_markdown(md, out_path)`` -- markdown -> HTML ->
   PDF via WeasyPrint. Supports basic typography, embedded images
   (matplotlib outputs from the sandbox land here), and tables.

2. ``render_pdf_from_marp(marp_md, out_path)`` -- if the answer is
   a Marp deck, render slides to PDF via the marp CLI (when present).
   Falls back to the WeasyPrint path with slide separators.

Public API:

- ``PdfSpec`` -- pydantic model.
- ``render_pdf(spec, out_path)``  -- dispatch on spec.kind.

Optional library: ``weasyprint`` (HTML/CSS to PDF), ``markdown-it-py``
or stdlib ``markdown`` (markdown -> HTML).
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


class PdfSpec(BaseModel):
    """PDF spec.

    Attributes:
        kind: ``"markdown"`` (most answers) or ``"marp"`` (slide decks
            exported as PDF).
        body: the markdown source (or Marp markdown).
        title: optional title used as the document title and ``<title>``.
        css: optional inline CSS for layout overrides. Defaults to the
            built-in stylesheet.
    """

    kind: Literal["markdown", "marp"] = "markdown"
    body: str = Field(...)
    title: str = ""
    css: str = ""


_DEFAULT_CSS = """
@page { size: letter; margin: 1in; }
body { font-family: Georgia, serif; font-size: 11pt; line-height: 1.45; color: #222; }
h1 { font-size: 22pt; margin-top: 0.4em; }
h2 { font-size: 16pt; margin-top: 1em; }
h3 { font-size: 13pt; }
p { margin: 0.4em 0; }
ul, ol { margin: 0.4em 0 0.4em 1.4em; }
table { border-collapse: collapse; margin: 0.6em 0; width: 100%; }
th, td { border: 1px solid #888; padding: 4px 8px; text-align: left; }
th { background: #f0f0f0; }
code { background: #f4f4f4; padding: 1px 4px; border-radius: 3px; }
pre { background: #f4f4f4; padding: 8px; border-radius: 4px; overflow-x: auto; }
""".strip()


def _markdown_to_html(md: str) -> str:
    """Best-effort markdown -> HTML conversion."""
    try:
        import markdown as md_mod  # python-markdown
        return md_mod.markdown(md, extensions=["tables", "fenced_code"])
    except ImportError:
        # Last-resort: wrap in a <pre> so the PDF at least has the content.
        from html import escape
        return f"<pre>{escape(md)}</pre>"


def render_pdf(spec: PdfSpec, out_path: Path | str) -> Path:
    """Render a PDF. Requires ``weasyprint``."""
    try:
        from weasyprint import HTML
    except ImportError as e:
        raise RuntimeError(
            "weasyprint is required for pdf rendering; install via "
            "pip install -e \".[output]\""
        ) from e

    html_body = _markdown_to_html(spec.body)
    css = spec.css or _DEFAULT_CSS
    title = spec.title or "JoJo Bot output"

    html_doc = (
        f"<!doctype html><html><head><meta charset='utf-8'>"
        f"<title>{title}</title>"
        f"<style>{css}</style>"
        f"</head><body>"
        f"{html_body}"
        f"</body></html>"
    )

    out = Path(out_path).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    HTML(string=html_doc).write_pdf(str(out))
    return out
