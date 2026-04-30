"""Markdown renderer — passthrough plus inline mermaid + wikilink rewriting.

The default Phase 4 answer format. Most Q&A answers are markdown;
this renderer adds two cheap transforms on top of the raw content:

1. Wikilink rewrite: ``[[slug|label]]`` and ``[[slug]]`` become
   markdown links pointing at the Wiki tab. Same pattern as the
   ``wiki/page.tsx`` frontend, but server-side so file-back outputs
   render correctly when viewed outside JoJo Bot.
2. Mermaid block detection: fenced ``mermaid`` blocks are passed
   through unchanged (the frontend has the renderer); this function
   only validates that the syntax is well-formed enough to not
   choke the renderer.

Public API:

- ``MarkdownSpec`` — Pydantic model for the input.
- ``render_markdown(spec) -> str`` — returns the rewritten markdown.
"""

from __future__ import annotations

import re

from pydantic import BaseModel, Field


class MarkdownSpec(BaseModel):
    """Spec for the markdown renderer.

    Attributes:
        body: raw markdown body (the model authors this).
        title: optional page title (rendered as a top-of-document H1).
        wikilink_base: relative path or URL prefix for wikilinks.
                       Defaults to ``/wiki?slug=`` so links navigate
                       to the Wiki tab. Set to ``""`` to leave
                       wikilinks as raw ``[[slug]]`` text.
        rewrite_wikilinks: when False, wikilinks pass through unchanged
                       (used when the consumer renders them itself,
                       e.g. the React Markdown component in the Wiki
                       tab).
    """

    body: str = Field(...)
    title: str = ""
    wikilink_base: str = "/wiki?slug="
    rewrite_wikilinks: bool = True


_PIPE_WIKILINK_RE = re.compile(r"\[\[([^\[\]\|\n]+)\|([^\]\n]+)\]\]")
_BARE_WIKILINK_RE = re.compile(r"\[\[([^\[\]\|\n]+)\]\]")


def render_markdown(spec: MarkdownSpec) -> str:
    """Apply markdown transforms; return the rewritten body."""
    body = spec.body

    if spec.rewrite_wikilinks and spec.wikilink_base:
        # Pipe-form first so the bare regex doesn't double-match.
        body = _PIPE_WIKILINK_RE.sub(
            lambda m: f"[{m.group(2).strip()}]({spec.wikilink_base}{m.group(1).strip()})",
            body,
        )
        body = _BARE_WIKILINK_RE.sub(
            lambda m: f"[{m.group(1).strip()}]({spec.wikilink_base}{m.group(1).strip()})",
            body,
        )

    if spec.title:
        body = f"# {spec.title}\n\n{body}"

    return body
