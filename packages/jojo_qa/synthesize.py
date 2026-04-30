"""Synthesis pass — feature-flagged Sonnet/Opus call.

This module is the single place the Anthropic API client lives. Today
it returns the ``api_key_required`` shape that ``qa_router.py``'s
``POST /api/qa/query`` uses to nudge the UI to show the retrieval
bundle and a "run this in a Cowork session" hint.

When the API key lands (FU-10 in ``docs/follow-ups.md``):

    1. Add ``"anthropic_api_key"`` to ``jojo_core.config.SECRET_KEYS``
       (one-line edit in ``packages/jojo_core/config.py``).
    2. Implement ``_call_model`` below: ``anthropic.Anthropic(api_key=...)``,
       Sonnet 4.6 by default, Opus 4.6 when ``depth="opus"``.
    3. Flip ``API_KEY_REQUIRED_RESPONSE`` to ``answer(...)`` in the live
       path of ``qa_router.py``.

Per ``ADR 0011`` the prompt that the model receives is the contents of
``docs/qa/qa-prompt.md``'s SESSION PROMPT block. The retrieval bundle
is the same shape Cowork sessions consume today, so the prompt and
bundle stay invariant on API day; only the trigger changes.

Public API:

- ``RetrievalBundle`` — dataclass aggregating router result, candidate
  slugs, page bodies, graph neighborhood, and raw fallback hits.
- ``build_retrieval_bundle(...)`` — assemble the bundle.
- ``answer(question, *, depth='sonnet')`` — feature-flagged. Returns
  the ``api_key_required`` shape today; Sonnet/Opus call on API day.
- ``API_KEY_REQUIRED_RESPONSE`` — the canonical shape for the no-key
  path. Imported by ``qa_router.py`` so the wire format stays in sync.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Literal

from jojo_core import config

from . import graph as graph_mod
from . import index_loader, raw_fallback
from .index_loader import IndexEntry
from .router import Route, RouterResult, classify

Depth = Literal["sonnet", "opus"]


# Shape returned when the API key is not configured. ``qa_router.py``
# returns this with HTTP 200 so the UI can render a nudge instead of an
# error. Keep this in sync with the Phase 3 ``POST /api/wiki/edit``
# precedent.
API_KEY_REQUIRED_RESPONSE: dict[str, Any] = {
    "status": "api_key_required",
    "message": (
        "JoJo can synthesize a model-driven answer once the Anthropic "
        "API key is configured. In the meantime, paste the retrieval "
        "bundle below into a Cowork session running docs/qa/qa-prompt.md "
        "or open the question in the Chat tab's Cowork-handoff modal."
    ),
}


@dataclass
class RetrievalBundle:
    """The paste-in payload for a Cowork session (or the prompt input on
    API day).

    Attributes:
        question: the user question, verbatim.
        router_result: deterministic route decision (regex backstop).
        candidate_entries: top-k index entries chosen for first-pass
            reading.
        candidate_bodies: dict slug -> body text for each candidate.
            Trimmed to ``max_body_chars`` per page if long.
        graph_neighborhood: 1-hop neighbors of each candidate slug.
            Empty for ``v1`` route.
        raw_fallback_hits: top-k raw-entry hits for the same query.
            Used when the wiki coverage is suspected to be insufficient.
        wiki_root: absolute path of the wiki repo (for citation
            resolution).
    """

    question: str
    router_result: RouterResult
    candidate_entries: list[IndexEntry] = field(default_factory=list)
    candidate_bodies: dict[str, str] = field(default_factory=dict)
    graph_neighborhood: dict[str, list[str]] = field(default_factory=dict)
    raw_fallback_hits: list[dict[str, Any]] = field(default_factory=list)
    wiki_root: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Serialize to JSON-friendly shape for the API response."""
        return {
            "question": self.question,
            "router": {
                "route": self.router_result.route,
                "reason": self.router_result.reason,
                "matched_keywords": list(self.router_result.matched_keywords),
                "override_matched": self.router_result.override_matched,
            },
            "candidates": [
                {
                    "slug": e.slug,
                    "title": e.title,
                    "type": e.type,
                    "path": e.path,
                }
                for e in self.candidate_entries
            ],
            "candidate_bodies": self.candidate_bodies,
            "graph_neighborhood": self.graph_neighborhood,
            "raw_fallback_hits": self.raw_fallback_hits,
            "wiki_root": self.wiki_root,
        }


def build_retrieval_bundle(
    question: str,
    *,
    wiki_root: Path,
    manifest_path: Path | None = None,
    k_candidates: int = 8,
    k_raw: int = 5,
    max_body_chars: int = 8000,
    include_neighbors: bool = True,
    route_hint: Route | None = None,
) -> RetrievalBundle:
    """Assemble the retrieval bundle for a question.

    Args:
        question: raw question string.
        wiki_root: path to ``ask_jojo_wiki/``.
        manifest_path: optional path to ``ask_jojo_raw/manifest.json``
            for raw-fallback search. If absent, ``raw_fallback_hits``
            stays empty.
        k_candidates: max candidate pages to include in the bundle.
        k_raw: max raw-entry hits to include.
        max_body_chars: truncate page bodies to this many chars to
            keep the bundle small. Tail is kept (most recent additions
            are typically appended in the wiki).
        include_neighbors: whether to include 1-hop graph neighbors.
        route_hint: operator-provided route override. If absent, the
            regex classifier runs.
    """
    if route_hint is not None:
        # Trust the hint; fabricate a RouterResult that says so.
        rr = RouterResult(
            route=route_hint,
            reason=f"operator-provided route hint: {route_hint}",
        )
    else:
        rr = classify(question)

    if rr.route == "v1":
        # No wiki retrieval for v1-route questions; the bundle is just
        # the routing slip.
        return RetrievalBundle(
            question=question,
            router_result=rr,
            wiki_root=str(wiki_root),
        )

    entries = index_loader.load_index(wiki_root, enrich=True)
    candidates = index_loader.rank_candidates(entries, question, k=k_candidates)

    bodies: dict[str, str] = {}
    for entry in candidates:
        full = wiki_root / entry.path
        try:
            text = full.read_text(encoding="utf-8")
        except OSError:
            continue
        if max_body_chars and len(text) > max_body_chars:
            text = text[:max_body_chars] + "\n\n... (truncated for bundle size)"
        bodies[entry.slug] = text

    neighborhood: dict[str, list[str]] = {}
    if include_neighbors and candidates:
        graph = graph_mod.load(wiki_root)
        if graph.nodes:
            for entry in candidates:
                neighborhood[entry.slug] = sorted(
                    graph_mod.neighbors(graph, entry.slug, hops=1)
                )

    raw_hits: list[dict[str, Any]] = []
    if manifest_path is not None and Path(manifest_path).exists():
        for hit in raw_fallback.search(manifest_path, question, k=k_raw):
            raw_hits.append(asdict(hit))

    return RetrievalBundle(
        question=question,
        router_result=rr,
        candidate_entries=candidates,
        candidate_bodies=bodies,
        graph_neighborhood=neighborhood,
        raw_fallback_hits=raw_hits,
        wiki_root=str(wiki_root),
    )


def answer(
    question: str,
    *,
    wiki_root: Path,
    manifest_path: Path | None = None,
    depth: Depth = "sonnet",
    route_hint: Route | None = None,
) -> dict[str, Any]:
    """Synthesize an answer to ``question``.

    Today: returns the ``api_key_required`` shape with the retrieval
    bundle attached, so the UI / Cowork handoff can pick it up.

    On API day: calls Sonnet 4.6 (or Opus 4.6 if ``depth='opus'``)
    with the prompt from ``docs/qa/qa-prompt.md`` and the bundle as
    user-message context, then returns the synthesized answer.
    """
    bundle = build_retrieval_bundle(
        question,
        wiki_root=wiki_root,
        manifest_path=manifest_path,
        route_hint=route_hint,
    )

    api_key = config.get("anthropic_api_key", None)
    if not api_key:
        out = dict(API_KEY_REQUIRED_RESPONSE)
        out["retrieval_bundle"] = bundle.to_dict()
        out["depth"] = depth
        return out

    # API key present -> live synthesis.
    return _call_model(question, bundle, depth=depth, api_key=api_key)


def _call_model(
    question: str,
    bundle: RetrievalBundle,
    *,
    depth: Depth,
    api_key: str,
) -> dict[str, Any]:
    """Call Anthropic Messages API. Stub today; lands with FU-10.

    The implementation is intentionally a single function so the API-day
    edit is small: import ``anthropic``, build the messages payload,
    return the parsed answer. Until then it returns ``not_implemented``
    so a misconfigured environment surfaces a clear error.
    """
    # Suppress unused warnings - parameters are part of the future-day signature.
    _ = (question, bundle, depth, api_key)
    return {
        "status": "not_implemented",
        "message": (
            "synthesize._call_model is the API-day stub. The retrieval "
            "bundle and prompt are ready; flip this function to call "
            "anthropic.Anthropic(api_key=api_key).messages.create(...) "
            "with the prompt from docs/qa/qa-prompt.md. See FU-10."
        ),
    }
