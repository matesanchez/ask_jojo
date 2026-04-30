"""Marp renderer — produces Marp markdown from a typed slide spec.

The actual SVG carousel render happens in the frontend Web Worker
(per PLAN.md Section 6 Phase 5). This server-side renderer's job is to
take a structured slide spec from the model and emit the Marp-flavored
markdown the worker consumes.

Marp markdown is regular markdown with special directives. The shape:

    ---
    marp: true
    theme: default
    paginate: true
    ---

    # Slide 1 title

    Slide 1 body.

    ---

    # Slide 2 title

    - bullet
    - bullet

Public API:

- ``MarpSpec`` — Pydantic model for the deck.
- ``Slide``    — Pydantic model for one slide.
- ``render_marp(spec) -> str`` — produces the Marp markdown.

The frontend Web Worker (``src/frontend/lib/marp/worker.ts``)
converts the markdown to an array of SVG strings.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

MAX_SLIDES = 60
MAX_BULLETS = 16


class Slide(BaseModel):
    """One slide.

    Attributes:
        title: slide title (rendered as H1 in Marp).
        body: free-form markdown body. May contain inline lists,
            code blocks, images, mermaid blocks. Ignored when
            ``bullets`` is non-empty.
        bullets: bullet list (rendered as a markdown ``- `` list).
        notes: speaker notes (rendered in Marp's ``<!-- comment -->``
            syntax).
        layout: optional Marp layout directive (``cover``, ``two-cols``,
            etc.). Falls back to default layout if absent.
    """

    title: str = Field("", max_length=200)
    body: str = ""
    bullets: list[str] = Field(default_factory=list)
    notes: str = ""
    layout: Literal["", "cover", "two-cols", "section"] = ""

    @field_validator("bullets")
    @classmethod
    def _check_bullets(cls, v: list[str]) -> list[str]:
        if len(v) > MAX_BULLETS:
            raise ValueError(f"too many bullets ({len(v)}); max is {MAX_BULLETS}")
        return v


class MarpSpec(BaseModel):
    """A complete deck spec.

    Attributes:
        title: deck title (used for the cover slide if no slide #1 has
            a layout='cover').
        theme: Marp theme. Defaults to ``default``; ``gaia`` and
            ``uncover`` are also built in. Custom themes require
            registering them in the Web Worker.
        paginate: show page numbers.
        slides: ordered slides.
    """

    title: str = ""
    theme: Literal["default", "gaia", "uncover"] = "default"
    paginate: bool = True
    slides: list[Slide] = Field(default_factory=list)

    @field_validator("slides")
    @classmethod
    def _check_slides(cls, v: list[Slide]) -> list[Slide]:
        if len(v) > MAX_SLIDES:
            raise ValueError(f"too many slides ({len(v)}); max is {MAX_SLIDES}")
        return v


def _slide_to_md(slide: Slide) -> str:
    parts: list[str] = []
    if slide.layout:
        parts.append(f"<!-- _class: {slide.layout} -->\n")
    if slide.title:
        parts.append(f"# {slide.title}\n")
    if slide.bullets:
        for b in slide.bullets:
            parts.append(f"- {b}")
        parts.append("")
    elif slide.body:
        parts.append(slide.body)
        parts.append("")
    if slide.notes:
        # Marp speaker-note syntax.
        parts.append(f"<!-- {slide.notes} -->")
    return "\n".join(parts)


def render_marp(spec: MarpSpec) -> str:
    """Return the Marp-flavored markdown ready for the Web Worker."""
    front = (
        "---\n"
        "marp: true\n"
        f"theme: {spec.theme}\n"
        f"paginate: {'true' if spec.paginate else 'false'}\n"
        "---\n\n"
    )
    if not spec.slides:
        if spec.title:
            return front + f"# {spec.title}\n\n_(empty deck)_\n"
        return front + "_(empty deck)_\n"

    parts: list[str] = [front]

    # Optional cover slide if no slides have layout='cover' and a title is set.
    has_cover = any(s.layout == "cover" for s in spec.slides)
    if spec.title and not has_cover:
        parts.append("<!-- _class: cover -->\n")
        parts.append(f"# {spec.title}\n")
        parts.append("\n---\n\n")

    parts.append("\n---\n\n".join(_slide_to_md(s) for s in spec.slides))
    return "".join(parts)
