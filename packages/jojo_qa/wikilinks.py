"""Wikilink extraction — pull ``[[slug]]`` and ``[[slug|label]]`` from page bodies.

The wiki uses MediaWiki-style wikilinks. The compile pipeline emits two
forms:

- ``[[slug]]`` — bare wikilink; the rendered label is the slug.
- ``[[slug|Display Label]]`` — wikilink with explicit label.

The parser also tolerates legacy ``[[Page Title]]`` (no slug; title is
the label) by preserving the raw token; the index loader's slug
normalization is a separate concern.

This module is a pure function over text. The frontend uses the same
pattern via a regex pre-process before ReactMarkdown, so the patterns
here have to stay in sync with the regex in
``src/frontend/app/(tabs)/wiki/page.tsx``.

Public API:

- ``WikilinkRef`` — dataclass with ``slug``, ``label``, ``raw``, ``position``.
- ``extract(body)`` — list of all wikilink references in the body, in
  source order, including duplicates.
- ``unique_slugs(body)`` — set of unique slugs referenced.
- ``strip(body)`` — return the body with wikilinks replaced by their
  labels (mostly for diff computation in ``qa_router.py``'s
  /api/qa/explain endpoint).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# Two patterns to give us the kind of structured match we want:
#
#   [[slug|label]]   <-- pipe-form
#   [[slug]]         <-- bare-form
#
# Order matters: the pipe-form must be tried first so the bare-form
# regex doesn't accidentally swallow a pipe-form as a slug containing
# the literal "|label" string.
#
# We disallow newlines and ``]]`` inside the slug/label to avoid runaway
# matches across paragraphs. Slugs are constrained to a sensible
# character class; labels can contain anything except ``]`` and newline.

_PIPE_RE = re.compile(
    r"\[\[(?P<slug>[^\[\]\|\n]+)\|(?P<label>[^\]\n]+)\]\]"
)
_BARE_RE = re.compile(
    r"\[\[(?P<slug>[^\[\]\|\n]+)\]\]"
)


@dataclass(frozen=True)
class WikilinkRef:
    """One wikilink reference in a page body.

    Attributes:
        slug: the link target. May be a slug (``cbl-b``) or a title
            (``CBL-B Program``); the index loader is responsible for
            resolution.
        label: the rendered label. Equal to ``slug`` for bare wikilinks.
        raw: the original raw match, e.g. ``[[cbl-b|CBL-B Program]]``.
        position: the (start, end) character indices in the source body.
    """

    slug: str
    label: str
    raw: str
    position: tuple[int, int]


def extract(body: str) -> list[WikilinkRef]:
    """Return all wikilink references in ``body`` in source order.

    Handles both ``[[slug|label]]`` and ``[[slug]]`` forms. Pipe-form
    matches take priority — a span matched by the pipe regex is masked
    out before the bare regex runs, so the bare regex can't double-match
    the same span.

    Duplicates are preserved in source order — the caller decides whether
    to deduplicate.
    """
    if not body:
        return []

    refs: list[WikilinkRef] = []
    masked = list(body)

    for m in _PIPE_RE.finditer(body):
        slug = m.group("slug").strip()
        label = m.group("label").strip()
        refs.append(
            WikilinkRef(
                slug=slug,
                label=label,
                raw=m.group(0),
                position=(m.start(), m.end()),
            )
        )
        for i in range(m.start(), m.end()):
            masked[i] = " "

    masked_text = "".join(masked)
    for m in _BARE_RE.finditer(masked_text):
        slug = m.group("slug").strip()
        refs.append(
            WikilinkRef(
                slug=slug,
                label=slug,
                raw=m.group(0),
                position=(m.start(), m.end()),
            )
        )

    refs.sort(key=lambda r: r.position[0])
    return refs


def unique_slugs(body: str) -> set[str]:
    """Return the unique set of wikilink target slugs in ``body``."""
    return {ref.slug for ref in extract(body)}


def strip(body: str) -> str:
    """Replace each wikilink with its label, leaving prose intact.

    Used for diff/explain computations where the wikilink syntax would
    otherwise generate spurious diffs.
    """
    if not body:
        return body

    # Pipe-form first: replace with label.
    out = _PIPE_RE.sub(lambda m: m.group("label").strip(), body)
    # Bare-form: replace with slug (which is the label for bare links).
    out = _BARE_RE.sub(lambda m: m.group("slug").strip(), out)
    return out
