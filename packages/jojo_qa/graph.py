"""Graph builder — construct ``_graph.json`` adjacency from the wiki.

The graph captures *forward* wikilinks (a page's outbound references)
combined with the existing *backward* wikilinks (``_backlinks.json``).
The result is an undirected adjacency list keyed by slug, with a
companion file at ``ask_jojo_wiki/_graph.json``.

Why we need it. ``PLAN.md`` Section 6 Phase 4 step 2 calls for "graph-
assisted navigation" — for relational questions ("what's the connection
between X and Y?"), the retrieval prompt reads ``_graph.json`` first,
finds shortest paths and shared communities between the two nodes, and
reads only the pages on those paths. Dramatically reduces tokens vs full
index reads. Building the graph deterministically (no model) is in scope
for Phase 4 today; the model-side prompt that consumes it lands with the
synthesis path on API day.

The builder is also the bridge to Phase 7a (graphify integration). The
``_graph.json`` we emit is intentionally compatible with the graphify
schema (`{"nodes": [...], "edges": [...]}`) so graphify can consume
it without translation.

Public API:

- ``WikiGraph`` — dataclass with ``nodes`` (list of slug/type/title/
  summary/corpus) and ``edges`` (list of (a, b) tuples). Edges are
  undirected; we store (min, max) so deduplication is trivial.
- ``build(wiki_root)`` — walk the wiki, extract forward wikilinks from
  bodies, merge with ``_backlinks.json``, and return a ``WikiGraph``.
- ``write(graph, wiki_root)`` — serialize to ``_graph.json``.
- ``shortest_path(graph, src, dst)`` — BFS shortest-path between two
  slugs. Returns ``None`` if disconnected.
- ``neighbors(graph, slug, hops)`` — set of slugs within ``hops`` of
  ``slug`` (1- or 2-hop neighborhood for retrieval).
"""

from __future__ import annotations

import json
import re
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from . import wikilinks
from .index_loader import IndexEntry, load_index

# Wikilink pattern for stripping [[...]] markup from body summaries.
_WIKILINK_RE = re.compile(r"\[\[(?:[^\[\]\|\n]+\|)?([^\[\]\|\n]+)\]\]")


@dataclass
class WikiGraph:
    """Undirected graph over wiki slugs.

    Attributes:
        nodes: dict slug -> metadata (``title``, ``type``, ``path``,
            ``summary``, ``corpus``).
        adjacency: dict slug -> sorted list of neighbor slugs.
        edges: list of ``(slug_a, slug_b)`` pairs with ``slug_a < slug_b``.
            Stored separately for O(1) edge listing in graphify export.
    """

    nodes: dict[str, dict[str, str]] = field(default_factory=dict)
    adjacency: dict[str, list[str]] = field(default_factory=dict)
    edges: list[tuple[str, str]] = field(default_factory=list)

    def to_json(self) -> dict[str, Any]:
        """Serialize to graphify-compatible JSON."""
        return {
            "nodes": [
                {"slug": slug, **meta}
                for slug, meta in sorted(self.nodes.items())
            ],
            "edges": [
                {"source": a, "target": b}
                for a, b in self.edges
            ],
            "adjacency": {
                slug: sorted(neighbors)
                for slug, neighbors in self.adjacency.items()
            },
            "schema_version": "0.2.0",
        }


def _read_body(wiki_root: Path, page_path: str) -> str:
    """Read a page body. Returns empty string on read error."""
    full = wiki_root / page_path
    try:
        text = full.read_text(encoding="utf-8")
    except OSError:
        return ""
    # Strip frontmatter (``---\n...\n---\n``).
    if text.startswith("---"):
        end = text.find("\n---\n", 3)
        if end != -1:
            return text[end + 5 :]
    return text


def _read_full_text(wiki_root: Path, page_path: str) -> str:
    """Read the full raw text of a page (including frontmatter)."""
    full = wiki_root / page_path
    try:
        return full.read_text(encoding="utf-8")
    except OSError:
        return ""


def _parse_frontmatter_scalar(text: str, key: str) -> str:
    """Extract a YAML scalar value from frontmatter by key.

    Handles the canonical ``key: value`` form produced by the absorb
    pipeline. Returns ``""`` when absent or when the file has no
    frontmatter block.

    This is intentionally a minimal regex parser — it does not attempt
    full YAML parsing. The absorb pipeline guarantees simple scalar
    values for ``description`` and ``corpus``.
    """
    if not text.startswith("---"):
        return ""
    end = text.find("\n---\n", 3)
    if end == -1:
        return ""
    fm_text = text[4:end]
    pattern = re.compile(
        r"^" + re.escape(key) + r"\s*:\s*(.+)$",
        re.MULTILINE,
    )
    m = pattern.search(fm_text)
    if not m:
        return ""
    value = m.group(1).strip()
    # Strip surrounding quotes if present.
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        value = value[1:-1].strip()
    return value


def _extract_summary(body: str, max_chars: int = 120) -> str:
    """Extract a one-line summary from a stripped page body.

    Algorithm:
        1. Split on newlines.
        2. Skip blank lines and lines that start with ``#`` (headings).
        3. Take the first non-empty prose line.
        4. Strip wikilink markup (``[[slug|Label]]`` -> ``Label``,
           ``[[slug]]`` -> ``slug``).
        5. Split the cleaned line on sentence boundaries (``. ``, ``? ``,
           ``! ``) and take the first sentence.
        6. Truncate to ``max_chars`` chars as a safety net for
           unusually long sentences, appending ``…`` if truncated.

    Returns ``""`` when the body has no prose content.
    """
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("#"):
            continue
        # Replace wikilink markup with the display label.
        line = _WIKILINK_RE.sub(lambda m: m.group(1), line)
        line = line.strip()
        if not line:
            continue
        # Take the first sentence (split on `. `, `? `, `! `).
        parts = re.split(r"(?<=[.!?])\s+", line, maxsplit=1)
        sentence = parts[0]
        if len(sentence) > max_chars:
            return sentence[:max_chars] + "…"
        return sentence
    return ""


def _load_backlinks(wiki_root: Path) -> dict[str, list[str]]:
    """Load ``_backlinks.json``. Returns ``{}`` on missing/invalid.

    The file's keys are page *titles* (e.g. ``"2022 DEL Screen Queue"``)
    and values are lists of *slugs* that link in. We normalize the keys
    to slugs by looking up the index. Pages whose title is not in the
    index are dropped (they would have no edges in our slug-keyed graph
    anyway).
    """
    bl_path = wiki_root / "_backlinks.json"
    if not bl_path.exists():
        return {}
    try:
        data = json.loads(bl_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    if not isinstance(data, dict):
        return {}
    return {k: list(v) for k, v in data.items() if isinstance(v, list)}


def build(wiki_root: Path | str) -> WikiGraph:
    """Walk the wiki and build the slug-keyed adjacency graph.

    Steps:
        1. Load ``_index.md`` -> list of ``IndexEntry``.
        2. For each entry, read the page body and extract forward
           wikilinks via ``wikilinks.extract``.
        3. Load ``_backlinks.json`` and add the inbound edges. Keys
           there are titles, so we resolve titles to slugs via the
           index.
        4. Deduplicate edges as ``(min, max)`` tuples.

    Edges to slugs not in the index (broken wikilinks, derived-page
    drafts, etc.) are skipped. The compile pipeline's verify step
    flags broken links separately; the graph only carries valid edges.
    """
    wiki_root = Path(wiki_root)
    entries: list[IndexEntry] = load_index(wiki_root)
    slug_to_entry = {e.slug: e for e in entries}
    title_to_slug = {e.title: e.slug for e in entries}

    graph = WikiGraph()

    # 1. Nodes from the index — read each page once to extract
    #    summary/corpus from frontmatter/body, then build forward edges.
    page_bodies: dict[str, str] = {}
    for entry in entries:
        full_text = _read_full_text(wiki_root, entry.path)
        # Prefer the ``description:`` frontmatter field; fall back to
        # the first prose line of the body.
        description = _parse_frontmatter_scalar(full_text, "description")
        if not description:
            body = _read_body(wiki_root, entry.path)
            description = _extract_summary(body)
        corpus = _parse_frontmatter_scalar(full_text, "corpus")
        graph.nodes[entry.slug] = {
            "title": entry.title,
            "type": entry.type,
            "path": entry.path,
            "summary": description,
            "corpus": corpus,
        }
        graph.adjacency.setdefault(entry.slug, [])
        # Cache the body for the forward-edge pass below.
        if full_text.startswith("---"):
            end = full_text.find("\n---\n", 3)
            page_bodies[entry.slug] = full_text[end + 5 :] if end != -1 else full_text
        else:
            page_bodies[entry.slug] = full_text

    edge_set: set[tuple[str, str]] = set()

    # 2. Forward edges from page bodies.
    for entry in entries:
        body = page_bodies.get(entry.slug, "")
        if not body:
            continue
        for ref in wikilinks.extract(body):
            target = ref.slug
            # Resolve title-form wikilinks (e.g. ``[[CBL-B Program]]``)
            # to slugs.
            if target not in slug_to_entry and target in title_to_slug:
                target = title_to_slug[target]
            if target == entry.slug or target not in slug_to_entry:
                continue
            edge_set.add(_norm_edge(entry.slug, target))

    # 3. Backward edges from _backlinks.json.
    backlinks = _load_backlinks(wiki_root)
    for title, inbound_slugs in backlinks.items():
        if title not in title_to_slug:
            continue
        target = title_to_slug[title]
        for src in inbound_slugs:
            if src == target or src not in slug_to_entry:
                continue
            edge_set.add(_norm_edge(src, target))

    # 4. Build adjacency from edge_set.
    for a, b in sorted(edge_set):
        graph.edges.append((a, b))
        graph.adjacency[a].append(b)
        graph.adjacency[b].append(a)

    # Sort and dedupe each adjacency list in place.
    for slug in graph.adjacency:
        graph.adjacency[slug] = sorted(set(graph.adjacency[slug]))

    return graph


def _norm_edge(a: str, b: str) -> tuple[str, str]:
    """Canonical undirected edge ordering: lexicographic min, max."""
    return (a, b) if a < b else (b, a)


def write(graph: WikiGraph, wiki_root: Path | str) -> Path:
    """Serialize ``graph`` to ``<wiki_root>/_graph.json``. Returns the path."""
    wiki_root = Path(wiki_root)
    out = wiki_root / "_graph.json"
    out.write_text(
        json.dumps(graph.to_json(), indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    return out


def load(wiki_root: Path | str) -> WikiGraph:
    """Load a previously-serialized ``_graph.json``. Returns empty on missing."""
    wiki_root = Path(wiki_root)
    path = wiki_root / "_graph.json"
    if not path.exists():
        return WikiGraph()
    data = json.loads(path.read_text(encoding="utf-8"))
    graph = WikiGraph()
    for node in data.get("nodes", []):
        slug = node.pop("slug")
        graph.nodes[slug] = node
    adj = data.get("adjacency", {})
    for slug, neighbors in adj.items():
        graph.adjacency[slug] = list(neighbors)
    for edge in data.get("edges", []):
        graph.edges.append((edge["source"], edge["target"]))
    return graph


# -- graph algorithms ------------------------------------------------------


def shortest_path(
    graph: WikiGraph, src: str, dst: str
) -> list[str] | None:
    """BFS shortest-path between ``src`` and ``dst``.

    Returns the path as a list of slugs (inclusive of both endpoints).
    Returns ``None`` if either endpoint is missing or the slugs are
    in different connected components.
    """
    if src == dst and src in graph.nodes:
        return [src]
    if src not in graph.nodes or dst not in graph.nodes:
        return None

    queue: deque[tuple[str, list[str]]] = deque([(src, [src])])
    visited: set[str] = {src}
    while queue:
        node, path = queue.popleft()
        for neighbor in graph.adjacency.get(node, []):
            if neighbor in visited:
                continue
            new_path = path + [neighbor]
            if neighbor == dst:
                return new_path
            visited.add(neighbor)
            queue.append((neighbor, new_path))
    return None


def neighbors(
    graph: WikiGraph, slug: str, hops: int = 1
) -> set[str]:
    """Return the set of slugs within ``hops`` BFS edges of ``slug``.

    Excludes ``slug`` itself. Returns empty set if ``slug`` is not in
    the graph or if ``hops < 1``.
    """
    if slug not in graph.nodes or hops < 1:
        return set()

    seen: dict[str, int] = {slug: 0}
    queue: deque[str] = deque([slug])
    while queue:
        node = queue.popleft()
        depth = seen[node]
        if depth == hops:
            continue
        for neighbor in graph.adjacency.get(node, []):
            if neighbor in seen:
                continue
            seen[neighbor] = depth + 1
            queue.append(neighbor)
    seen.pop(slug, None)
    return set(seen.keys())


# -- statistics ------------------------------------------------------------


def stats(graph: WikiGraph) -> dict[str, Any]:
    """Return summary stats for the graph (used by /api/ops/status)."""
    n_nodes = len(graph.nodes)
    n_edges = len(graph.edges)
    degrees = [len(adj) for adj in graph.adjacency.values()]
    orphan_count = sum(1 for d in degrees if d == 0)
    avg_degree = (sum(degrees) / n_nodes) if n_nodes else 0.0
    max_degree = max(degrees) if degrees else 0

    components = _count_components(graph)
    return {
        "node_count": n_nodes,
        "edge_count": n_edges,
        "orphan_count": orphan_count,
        "avg_degree": round(avg_degree, 2),
        "max_degree": max_degree,
        "connected_components": components,
    }


def _count_components(graph: WikiGraph) -> int:
    """Count connected components via iterative DFS."""
    seen: set[str] = set()
    components = 0
    for slug in graph.nodes:
        if slug in seen:
            continue
        components += 1
        stack: list[str] = [slug]
        while stack:
            node = stack.pop()
            if node in seen:
                continue
            seen.add(node)
            stack.extend(
                n for n in graph.adjacency.get(node, []) if n not in seen
            )
    return components
