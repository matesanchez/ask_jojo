"""Query router — classifies a question as ``v1`` (legacy AKTA path) or ``wiki``.

The router has two layers, in priority order:

1. **Regex backstop** — deterministic, fast, and the contract per
   ``PLAN.md`` Section 6 Phase 4 ("a cheap Haiku pre-pass classifies each
   question. If it matches ``\\bakta|unicorn|chromatograph|purif|buffer``
   and similar protein-purification keywords, the query goes to v1.0's
   RAG pipeline.").

2. **Wiki-override list** — phrases where the regex would mis-route (e.g.
   "buffer for the SIAH1 DEL screen" contains ``buffer`` but is a
   wiki-domain question). Override patterns are explicit and tested.

The Haiku-classifier optimization slots in *front* of these two layers on
API day, with the regex as a safety net (regex first, classifier when the
regex result is ambiguous). The classifier is optional; the regex is
the spec. See ``ADR 0011`` for the rationale.

Public API:

- ``classify(question, *, overrides=None) -> RouterResult``
- ``RouterResult`` — dataclass with ``route``, ``reason``, ``matched_keywords``.

Hint: callers that already know the route (operator override) should pass
``hint`` through unchanged and trust the operator. ``classify`` is for
the case where the route is unknown.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Literal

# -- v1 trigger keywords (regex word-boundary, case-insensitive) ----------
#
# Source of truth for the spec: PLAN.md Section 6 Phase 4 ("Legacy AKTA routing")
# and ADR 0011 ("Routing rules").
#
# Order is significant only for ``matched_keywords`` reporting; routing
# itself is a single match-any check. Keep the list pure ASCII to avoid
# the CP1252 / PowerShell-5.1 trap on any future port to a .ps1 doc
# generator (see feedback memory).

V1_KEYWORDS: tuple[str, ...] = (
    "akta",
    "unicorn",
)

# Only the legacy v1.0 AKTA/UNICORN chromatography SYSTEM routes to v1.
# General protein-science terms (purification, buffer, chromatography) were
# removed 2026-06-05: the v2 wiki now holds extensive Protein Sciences SOP
# content on exactly those topics, so questions about them must be answered
# from the wiki rather than deflected to the legacy system.
_STEM_KEYWORDS: frozenset[str] = frozenset()

_V1_PATTERN: re.Pattern[str] = re.compile(
    "|".join(
        r"\b" + re.escape(k) + ("" if k in _STEM_KEYWORDS else r"\b")
        for k in V1_KEYWORDS
    ),
    re.IGNORECASE,
)

# -- wiki-override list ----------------------------------------------------
#
# Phrases that *would* match the v1 regex but are wiki-domain on
# inspection. Each entry is a (compiled) regex; if any entry matches the
# question, the route flips to ``wiki`` regardless of the v1 match.
#
# Add entries here as Cowork sessions surface routing edge cases (per
# ADR 0011's prompt-tightening loop). Each entry should have a paired
# regression test in ``test_router.py``.
#
# Note: this is a *small* list by design. The Haiku classifier on API
# day will subsume most of these; the override list only carries the
# cases where the regex's recall on the v1 trigger is wrong by spec.

DEFAULT_WIKI_OVERRIDES: tuple[str, ...] = (
    # "buffer for the SIAH1 DEL screen" — buffer keyword on a DEL-screen
    # question routes wiki, not v1. The relevant wiki page is
    # decisions/q4-2022-screening-budget or methods/del-buffer-stability-testing.
    r"\bbuffer\b.*\bdel\b",
    r"\bdel\b.*\bbuffer\b",
    # SEC-MALS questions: chromatograph keyword on the wiki's
    # methods/sec-mals page is wiki-domain when the question is about
    # *analysis* rather than *operation*.
    r"\bsec[-\s]?mals\b",
)

_WIKI_OVERRIDE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(p, re.IGNORECASE) for p in DEFAULT_WIKI_OVERRIDES
]


# -- public types ----------------------------------------------------------

Route = Literal["v1", "wiki"]


@dataclass(frozen=True)
class RouterResult:
    """The output of ``classify``.

    Attributes:
        route: ``"v1"`` (legacy AKTA path) or ``"wiki"`` (default).
        reason: short human-readable explanation, suitable for the UI's
            route badge tooltip.
        matched_keywords: the v1 keywords that matched, if any.
        override_matched: True iff a wiki-override regex matched.
    """

    route: Route
    reason: str
    matched_keywords: tuple[str, ...] = field(default_factory=tuple)
    override_matched: bool = False


# -- public API ------------------------------------------------------------


def classify(
    question: str,
    *,
    overrides: Iterable[str] | None = None,
) -> RouterResult:
    """Classify ``question`` into ``v1`` or ``wiki``.

    The default route is ``wiki``; the ``v1`` route requires a v1-keyword
    match that is *not* overridden by a wiki-override pattern.

    Args:
        question: the user question, raw string.
        overrides: optional iterable of regex strings that override v1
            matches and route the question to ``wiki``. Defaults to
            ``DEFAULT_WIKI_OVERRIDES``. Pass ``[]`` (empty list) to
            disable overrides — useful for unit tests of the raw regex.

    Returns:
        ``RouterResult`` with the route, the reason, the matched
        keywords (if any), and whether an override fired.
    """
    if not question or not question.strip():
        return RouterResult(
            route="wiki",
            reason="empty question — defaulting to wiki",
        )

    # 1. Find any v1 keyword matches. This is the spec; if no v1 keyword
    #    matches, route is unambiguously wiki.
    matches = tuple(
        m.group(0).lower() for m in _V1_PATTERN.finditer(question)
    )
    if not matches:
        return RouterResult(
            route="wiki",
            reason="no v1 trigger keyword matched",
        )

    # 2. Check overrides. If an override matches, the wiki path wins
    #    regardless of the v1 keyword.
    if overrides is None:
        override_patterns = _WIKI_OVERRIDE_PATTERNS
    else:
        override_patterns = [re.compile(p, re.IGNORECASE) for p in overrides]

    for pattern in override_patterns:
        if pattern.search(question):
            return RouterResult(
                route="wiki",
                reason=(
                    f"v1 keyword(s) {matches} matched, but wiki-override "
                    f"pattern '{pattern.pattern}' won"
                ),
                matched_keywords=matches,
                override_matched=True,
            )

    # v1 routing retired (2026-06-05): v2 is the single, all-encompassing
    # knowledge surface. Even when legacy AKTA/UNICORN keywords match, the
    # route stays "wiki" -- nothing is deflected to the legacy system.
    # matched_keywords is still reported for the UI badge / debugging.
    return RouterResult(
        route="wiki",
        reason=(
            f"answered from the wiki (legacy keyword(s) {', '.join(matches)} no longer deflect)"
            if matches else "answered from the wiki"
        ),
        matched_keywords=matches,
    )


def matched_keywords(question: str) -> tuple[str, ...]:
    """Return the v1 keywords matched in ``question``.

    Convenience for callers that want the raw match list without the
    routing decision (e.g. UI debug strip).
    """
    if not question:
        return ()
    return tuple(m.group(0).lower() for m in _V1_PATTERN.finditer(question))
