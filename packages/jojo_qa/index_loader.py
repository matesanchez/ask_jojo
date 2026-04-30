"""Index loader — parse ``ask_jojo_wiki/_index.md`` into a slug -> metadata map.

The index file is the canonical catalog of every wiki page. The compile
pipeline rebuilds it on every checkpoint per ``schema/CLAUDE.md`` Section 3,
and the wiki tab + Q&A retrieval read it on every request.

The index format (per current ``ask_jojo_wiki/_index.md``):

    # Wiki Index
    Total pages: 138

    ## Concept

    - [[slug-a|Title A]] — `concepts/slug-a.md`
    - [[slug-b|Title B]] — `concepts/slug-b.md`

    ## Decision

    - [[slug-c|Title C]] — `decisions/slug-c.md`

The parser is permissive about whitespace and case, but the format above
is what the compile pipeline produces today. ``aliases`` are not on the
index — they live in each page's frontmatter and require a per-page read
for fuzzy matching. The retrieval bundle either reads frontmatter
on-demand or relies on the index alone, depending on the question.

Public API:

- ``IndexEntry`` — dataclass for one page.
- ``load_index(wiki_root)`` — parse ``_index.md`` into a list of
  ``IndexEntry``.
- ``index_by_slug(entries)`` — convert to a slug -> entry dict.
- ``rank_candidates(entries, question, k=8)`` — substring-overlap scoring
  for picking the top-k candidates for a question.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

# Index entry format. Two backtick-or-not forms; we match the canonical
# pattern produced by the compile pipeline today and degrade gracefully
# on whitespace / quoting variants.
#
# Canonical: ``- [[slug|Title]] — `path/to.md` ``
# Tolerant: any wikilink + path-in-backticks combination.

_INDEX_LINE_RE = re.compile(
    r"^\s*-\s*"                     # bullet
    r"\[\[(?P<slug>[^|\]]+)"        # wikilink slug
    r"(?:\|(?P<title>[^\]]+))?\]\]"  # optional pipe-label
    r"\s*[—\-]\s*"                  # em-dash or hyphen separator
    r"`(?P<path>[^`]+)`",           # path in backticks
    re.UNICODE,
)

# "## Concept" -> "Concept" -> normalized "concept".
_TYPE_HEADER_RE = re.compile(r"^##\s+(?P<type>[A-Za-z][A-Za-z0-9\- ]*)\s*$")


@dataclass(frozen=True)
class IndexEntry:
    """One page in the wiki index.

    Attributes:
        slug: the wikilink slug, e.g. ``cbl-b``.
        title: human-readable page title, e.g. ``CBL-B Program``.
        path: relative path under ``ask_jojo_wiki/``, e.g.
            ``programs/cbl-b.md``.
        type: page type derived from the index's section header,
            e.g. ``program``, ``target``, ``decision``. Lowercased.
        aliases: alias list from the page's frontmatter (empty when
            the entry was loaded without enrichment). Used by
            ``rank_candidates`` to surface pages whose body content
            matches the question even when the title/slug do not.
        tags: tag list from the page's frontmatter (empty when
            unenriched).
    """

    slug: str
    title: str
    path: str
    type: str
    aliases: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()

    @property
    def directory(self) -> str:
        """Top-level directory containing the page."""
        return self.path.split("/", 1)[0] if "/" in self.path else ""


# Frontmatter list-field regex: matches lines like ``aliases: [a, b, c]``
# (inline) or the YAML block-list form ``aliases:\n  - a\n  - b``.
_FM_LIST_INLINE_RE = re.compile(
    r"^(?P<key>aliases|tags)\s*:\s*\[(?P<items>[^\]]*)\]\s*$",
    re.MULTILINE,
)


def _parse_frontmatter_lists(body: str, key: str) -> tuple[str, ...]:
    """Extract a YAML list field (``aliases`` or ``tags``) from frontmatter.

    Handles both inline ``key: [a, b, c]`` and block ``key:\\n  - a\\n  - b``.
    Returns a tuple of stripped string values; empty tuple when absent or
    malformed. The parser is permissive on purpose; the absorb pipeline
    is the source of truth for valid frontmatter, this is best-effort.
    """
    if not body.startswith("---"):
        return ()
    end = body.find("\n---", 3)
    if end == -1:
        return ()
    fm_text = body[4:end]

    # Inline form: key: [a, b, c]
    for m in _FM_LIST_INLINE_RE.finditer(fm_text):
        if m.group("key") == key:
            items = m.group("items")
            return tuple(s.strip().strip('"').strip("'") for s in items.split(",") if s.strip())

    # Block form: key:\n  - a\n  - b
    lines = fm_text.splitlines()
    for i, line in enumerate(lines):
        stripped = line.lstrip()
        if stripped.startswith(f"{key}:") and stripped.rstrip().endswith(":"):
            collected: list[str] = []
            for sub in lines[i + 1 :]:
                if sub.startswith("  - "):
                    val = sub[4:].strip().strip('"').strip("'")
                    if val:
                        collected.append(val)
                elif sub and not sub.startswith(" "):
                    break
            return tuple(collected)
    return ()


def _enrich_from_page(wiki_root: Path, entry: IndexEntry) -> IndexEntry:
    """Read the page's frontmatter and return an enriched entry copy.

    Pulls ``aliases`` and ``tags`` from the YAML frontmatter. Returns
    the original entry if the page is unreadable.
    """
    try:
        body = (wiki_root / entry.path).read_text(encoding="utf-8")
    except OSError:
        return entry
    aliases = _parse_frontmatter_lists(body, "aliases")
    tags = _parse_frontmatter_lists(body, "tags")
    if not aliases and not tags:
        return entry
    return IndexEntry(
        slug=entry.slug,
        title=entry.title,
        path=entry.path,
        type=entry.type,
        aliases=aliases,
        tags=tags,
    )


def load_index(
    wiki_root: Path | str,
    *,
    enrich: bool = False,
) -> list[IndexEntry]:
    """Parse ``<wiki_root>/_index.md`` into a list of entries.

    Skips empty sections. Tolerant of whitespace; strict about the
    bullet+wikilink+path pattern (lines that don't match are silently
    ignored, since the index file may contain prose between sections).

    When ``enrich=True``, each entry gets its ``aliases`` and ``tags``
    populated from the page's YAML frontmatter (one extra disk read
    per page). The ranker scores against these fields so a question
    like "Peli2 redundancy" surfaces ``programs/pellino-1.md`` via
    its aliases without needing to scan body content. At the current
    138-page scale this adds < 100 ms; cache or skip when corpus
    grows beyond a few thousand pages.
    """
    wiki_root = Path(wiki_root)
    index_path = wiki_root / "_index.md"
    if not index_path.exists():
        return []

    text = index_path.read_text(encoding="utf-8")
    entries: list[IndexEntry] = []
    current_type = ""

    for raw_line in text.splitlines():
        type_m = _TYPE_HEADER_RE.match(raw_line)
        if type_m:
            current_type = type_m.group("type").strip().lower()
            continue
        line_m = _INDEX_LINE_RE.match(raw_line)
        if line_m and current_type:
            slug = line_m.group("slug").strip()
            title = (line_m.group("title") or slug).strip()
            path = line_m.group("path").strip()
            entries.append(
                IndexEntry(
                    slug=slug,
                    title=title,
                    path=path,
                    type=current_type,
                )
            )

    if enrich:
        entries = [_enrich_from_page(wiki_root, e) for e in entries]

    return entries


def index_by_slug(entries: Iterable[IndexEntry]) -> dict[str, IndexEntry]:
    """Convert ``entries`` to a dict keyed by slug. Last-write wins on collision.

    Emits a warning per collision so callers know data is being shadowed.
    Use ``entries_by_slug_grouped`` when you need *all* entries that
    share a slug (e.g. when both the program and target page exist).
    """
    import warnings

    out: dict[str, IndexEntry] = {}
    seen: dict[str, IndexEntry] = {}
    for e in entries:
        if e.slug in seen and seen[e.slug] != e:
            prior = seen[e.slug]
            warnings.warn(
                f"slug collision: {e.slug!r} appears as both "
                f"type={prior.type!r} (path={prior.path!r}) and "
                f"type={e.type!r} (path={e.path!r}); last-write wins "
                f"(see ask_jojo/docs/follow-ups.md FU-12)",
                stacklevel=2,
            )
        seen[e.slug] = e
        out[e.slug] = e
    return out


def entries_by_slug_grouped(
    entries: Iterable[IndexEntry],
) -> dict[str, list[IndexEntry]]:
    """Like ``index_by_slug`` but preserves all entries that share a slug.

    Use this when you need to surface both the program and target page
    for slugs like ``pellino-1`` until FU-12's rename lands.
    """
    out: dict[str, list[IndexEntry]] = {}
    for e in entries:
        out.setdefault(e.slug, []).append(e)
    return out


# -- retrieval scoring -----------------------------------------------------


def _tokenize(text: str) -> set[str]:
    """Cheap tokenizer: lowercased word-boundary tokens, length >= 2."""
    return {
        t for t in re.findall(r"[A-Za-z0-9][A-Za-z0-9\-]+", text.lower())
        if len(t) >= 2
    }


def _score(entry: IndexEntry, q_tokens: set[str]) -> int:
    """Score one entry against the question's token set.

    Heuristic:
        - Each token in the slug counts 3 (high signal — slugs are short).
        - Each token in the title counts 2 (medium signal).
        - Each token in an alias counts 2 (medium signal — aliases are
          curated synonyms).
        - Each token in the type counts 1 (low signal — many entries
          share types).
        - Each token in a tag counts 1 (low signal).

    Tokens are matched as full-token equality after the cheap tokenizer.
    A token in the question that does not appear in any field scores 0.

    Alias / tag tokens come from frontmatter and are populated only when
    the index was loaded with ``enrich=True``. Unenriched entries score
    against slug + title + type only (preserving prior behavior).
    """
    slug_tokens = _tokenize(entry.slug)
    title_tokens = _tokenize(entry.title)
    type_tokens = _tokenize(entry.type)
    alias_tokens: set[str] = set()
    for a in entry.aliases:
        alias_tokens |= _tokenize(a)
    tag_tokens: set[str] = set()
    for t in entry.tags:
        tag_tokens |= _tokenize(t)

    score = 0
    for tok in q_tokens:
        if tok in slug_tokens:
            score += 3
        if tok in title_tokens:
            score += 2
        if tok in alias_tokens:
            score += 2
        if tok in type_tokens:
            score += 1
        if tok in tag_tokens:
            score += 1
    return score


def rank_candidates(
    entries: Iterable[IndexEntry],
    question: str,
    k: int = 8,
) -> list[IndexEntry]:
    """Return the top-``k`` candidate entries for ``question``.

    Stable sort: ties broken by the order in which entries appear in
    the input iterable (which, for ``load_index``, is index-file order).

    A candidate with score 0 is excluded — better to return fewer
    candidates than to return irrelevant ones. The retrieval bundle's
    consumer is expected to fall back to the raw-search path if the
    candidate list is empty.
    """
    q_tokens = _tokenize(question)
    if not q_tokens:
        return []

    scored: list[tuple[int, int, IndexEntry]] = []
    for i, entry in enumerate(entries):
        s = _score(entry, q_tokens)
        if s > 0:
            # Negate the index for stable sort (lower index wins on tie).
            scored.append((-s, i, entry))

    scored.sort()
    return [e for _, _, e in scored[:k]]
