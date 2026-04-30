"""jojo_qa — question answering over the compiled wiki.

Phase 4 lives here. Six deterministic modules ship the load-bearing
plumbing; the model-call path lands in ``synthesize.py`` once the
Anthropic API key is provisioned (see FU-10 in ``docs/follow-ups.md``
and ``docs/ADR/0011-qa-via-cowork-while-api-pending.md``).

Public API (deterministic, available today):
    - ``router.classify(question)`` — regex-driven query router.
    - ``index_loader.load_index(wiki_root)`` — parse ``_index.md`` into
      a slug -> metadata map.
    - ``wikilinks.extract(body)`` — return outbound ``[[slug]]`` and
      ``[[slug|label]]`` references from a page body.
    - ``graph.build(wiki_root)`` — construct ``_graph.json`` adjacency
      from ``_backlinks.json`` plus body-link extraction.
    - ``graph.shortest_path(graph, src, dst)`` — BFS path between two
      slugs, used by the relational-question retrieval prompt.
    - ``raw_fallback.search(manifest, query, k)`` — substring search
      over manifest titles and paths; returns top-k entry IDs.
    - ``miss_log.append(query, reason, raw_entries)`` — append-only
      JSONL log of retrieval misses; the next absorb pass reads this.

Synthesis (feature-flagged, pending FU-10):
    - ``synthesize.answer(question, retrieval_bundle)`` — returns the
      ``api_key_required`` shape until the model client is wired.

Activation (qmd dormant until tripped):
    - ``qmd_activation.should_activate(...)`` — threshold check per
      PLAN.md Section 6 Phase 4 step 5. ``qmd`` is installed as a
      dormant runtime dependency in ``pyproject.toml [qa]``; the
      activation switch flips when ``_index.md`` crosses 200 pages
      or when the miss log shows sustained retrieval misses.
"""

__version__ = "0.1.0"
