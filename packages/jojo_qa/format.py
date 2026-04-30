"""Format classifier — picks the output format for a question.

PLAN.md Section 6 Phase 5: "the query-router's pre-pass classifier
also picks format, with heuristics: 'explain X' -> markdown; 'slides
for X' -> Marp; 'plot X vs Y' -> matplotlib; 'compare X and Y in a
table' -> markdown table; 'diagram the relationships' -> mermaid."

Same shape as ``router.py``: regex backstop today, Haiku classifier
on API day, regex stays as the safety net. The regex is the spec.

The classifier is *parallel* to the route classifier (v1 vs wiki),
not nested under it. A question can be (route=wiki, format=marp) or
(route=v1, format=markdown). v1-route questions skip format detection
and inherit the v1.0 system's default response shape (which today
is plain markdown).

Public API:

- ``Format``        — Literal type of the supported formats.
- ``FormatResult``  — dataclass with ``format``, ``reason``,
                      ``matched_keywords``, ``confidence``.
- ``classify(question)`` — returns FormatResult.
- ``available_formats()`` — list of supported formats (for the UI's
                      format selector dropdown).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Literal

# ---------------------------------------------------------------- formats

Format = Literal[
    "markdown",  # default; explanatory prose
    "marp",      # Marp slide deck
    "matplotlib",  # static chart (PNG)
    "plotly",    # interactive chart (HTML fragment)
    "table",     # markdown table (toggle to CSV / xlsx)
    "mermaid",   # inline mermaid diagram
    "docx",      # Word document
    "pptx",      # PowerPoint deck (non-Marp; structured slides)
    "pdf",       # PDF (typeset answer)
]


def available_formats() -> list[Format]:
    """List of supported formats. Used by the UI's format selector."""
    return [
        "markdown",
        "marp",
        "matplotlib",
        "plotly",
        "table",
        "mermaid",
        "docx",
        "pptx",
        "pdf",
    ]


# ------------------------------------------------------- pattern definitions

# Each pattern is a tuple of (compiled regex, format, reason, base score).
# Higher base score wins on ties. Order in the list is significant only for
# tie-breaking inside the same score bucket.
#
# Reasoning behind the scores:
#   10 = explicit format keyword in the question (e.g. "as a PDF")
#    8 = strong intent verb ("plot", "diagram", "make slides")
#    6 = format implied by structure ("compare X and Y in a table")
#    4 = soft hint ("show me a chart of")
#    2 = fallback (markdown gets every question that didn't trip a stronger
#        pattern, score 1)


_PATTERNS: list[tuple[re.Pattern[str], Format, str, int]] = [
    # --- Marp / slides --------------------------------------------------
    (re.compile(r"\b(make|create|generate|produce|prepare)\s+(\w+\s+)?slides?\b", re.IGNORECASE),
     "marp", "explicit slide-creation verb", 10),
    (re.compile(r"\bslide\s*deck\b|\bdeck\s+(for|about|comparing)\b", re.IGNORECASE),
     "marp", "deck keyword", 9),
    (re.compile(r"\bpresent(ation)?\s+on\b", re.IGNORECASE),
     "marp", "presentation phrasing", 7),

    # --- matplotlib / charts --------------------------------------------
    # Allow any words (with hyphens) between the verb and the comparator
    # so multi-token Y-axes like "Plot CBL-B IC50 vs concentration" match.
    # Cap at 6 tokens (~40 chars) to avoid runaway matches across sentences.
    (re.compile(r"\b(plot|chart|graph)\s+(?:[\w-]+\s+){1,6}(vs|versus|over|by)\b", re.IGNORECASE),
     "matplotlib", "plot X vs Y idiom", 10),
    (re.compile(r"\b(make|generate|create)\s+(a\s+)?(chart|plot|histogram|scatter)\b", re.IGNORECASE),
     "matplotlib", "explicit chart-creation verb", 9),
    (re.compile(r"\b(visuali[sz]e|show me)\s+(the\s+)?(distribution|trend|relationship)\b", re.IGNORECASE),
     "matplotlib", "visualization phrasing", 7),

    # --- plotly (interactive charts; explicit only) ---------------------
    (re.compile(r"\binteractive\s+(chart|plot|graph|visuali[sz]ation)\b", re.IGNORECASE),
     "plotly", "interactive chart keyword", 9),
    (re.compile(r"\bplotly\b", re.IGNORECASE),
     "plotly", "plotly explicit", 10),

    # --- table -----------------------------------------------------------
    (re.compile(r"\bcompare\s+\w+\s+and\s+\w+\s+(in|as)\s+(a\s+)?table\b", re.IGNORECASE),
     "table", "explicit compare-as-table", 10),
    (re.compile(r"\bin\s+(a\s+)?table\b", re.IGNORECASE),
     "table", "in a table", 8),
    (re.compile(r"\bside[-\s]?by[-\s]?side\b", re.IGNORECASE),
     "table", "side-by-side comparison", 6),

    # --- mermaid ---------------------------------------------------------
    (re.compile(r"\b(diagram|flowchart|sequence\s+diagram|state\s+diagram)\b", re.IGNORECASE),
     "mermaid", "diagram keyword", 9),
    (re.compile(r"\bmermaid\b", re.IGNORECASE),
     "mermaid", "mermaid explicit", 10),

    # --- docx ------------------------------------------------------------
    (re.compile(r"\b(memo|report|letter|brief)\b(?!.*\b(slide|deck|table|chart|plot)\b)", re.IGNORECASE),
     "docx", "memo/report keyword (word-document idioms)", 8),
    (re.compile(r"\bword\s+(doc|document)\b|\.docx?\b|\bin\s+word\b", re.IGNORECASE),
     "docx", "word-document keyword", 10),

    # --- pptx (PowerPoint; non-Marp structured slides) -------------------
    (re.compile(r"\bpowerpoint\b|\.pptx?\b", re.IGNORECASE),
     "pptx", "powerpoint keyword", 10),

    # --- pdf -------------------------------------------------------------
    (re.compile(r"\b(as\s+)?a?\s*pdf\b|\bpdf\s+(of|version|export)\b", re.IGNORECASE),
     "pdf", "pdf keyword", 10),

    # --- markdown (explicit) ---------------------------------------------
    (re.compile(r"\b(in\s+markdown|as\s+markdown|\.md\b)\b", re.IGNORECASE),
     "markdown", "markdown explicit", 10),
]

# Default fallback: every question that doesn't trip a stronger pattern
# gets ``markdown`` with score 1. Markdown is the explanatory-prose format
# scientists expect when they ask "what is X?"


# ---------------------------------------------------------------- result type


@dataclass(frozen=True)
class FormatResult:
    """Output of ``classify``.

    Attributes:
        format: one of the values in ``available_formats()``.
        reason: short human-readable explanation, suitable for UI tooltip.
        matched_keywords: tuple of substrings from the question that
            triggered the chosen format.
        confidence: ``"high"`` if score >= 8, ``"medium"`` for 4-7,
            ``"low"`` for the markdown fallback.
        candidate_scores: dict ``format -> highest score`` so the UI can
            show second-best alternatives in a dropdown.
    """

    format: Format
    reason: str
    matched_keywords: tuple[str, ...] = field(default_factory=tuple)
    confidence: Literal["high", "medium", "low"] = "medium"
    candidate_scores: dict[Format, int] = field(default_factory=dict)


# ---------------------------------------------------------------- public API


def classify(question: str) -> FormatResult:
    """Classify ``question`` into one of the supported output formats.

    Default is ``markdown`` (explanatory prose). Explicit format keywords
    (e.g. "as a PDF", "in a table") win with high confidence. Soft hints
    win with medium confidence. Empty or all-whitespace questions return
    markdown with low confidence.
    """
    if not question or not question.strip():
        return FormatResult(
            format="markdown",
            reason="empty question — defaulting to markdown",
            confidence="low",
        )

    # Score each pattern; track the best per format and the best overall.
    scores: dict[Format, int] = {}
    matched: dict[Format, list[str]] = {}
    reasons: dict[Format, str] = {}

    for pattern, fmt, reason, base in _PATTERNS:
        m = pattern.search(question)
        if m:
            score = base
            if score > scores.get(fmt, 0):
                scores[fmt] = score
                reasons[fmt] = reason
            matched.setdefault(fmt, []).append(m.group(0))

    # Default fallback: markdown at score 1.
    scores.setdefault("markdown", 1)
    reasons.setdefault("markdown", "no explicit format keyword — defaulting to markdown")

    # Pick the highest score; tie-breaks deterministic by format-list order.
    best_fmt: Format = "markdown"
    best_score = 0
    for fmt in available_formats():
        if scores.get(fmt, 0) > best_score:
            best_fmt = fmt
            best_score = scores[fmt]

    # Confidence bucketing.
    if best_score >= 8:
        confidence: Literal["high", "medium", "low"] = "high"
    elif best_score >= 4:
        confidence = "medium"
    else:
        confidence = "low"

    return FormatResult(
        format=best_fmt,
        reason=reasons[best_fmt],
        matched_keywords=tuple(matched.get(best_fmt, [])),
        confidence=confidence,
        candidate_scores=dict(scores),
    )
