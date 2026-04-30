"""Phase 7a token-reduction benchmark.

PLAN.md Section 6 Phase 7a exit criterion: "Token-reduction benchmark
(graphify style) shows >=10x reduction on a 500-article wiki vs.
raw-file baseline."

For each benchmark question, compute three retrieval bundles and
their token counts:

  raw_baseline  -- every wiki page concatenated (the pessimistic baseline;
                   how many tokens would a model see if we just dumped
                   the wiki and let it pick).
  index_first   -- packages/jojo_qa.synthesize.build_retrieval_bundle
                   output (today's Phase 4 retrieval).
  graph_assist  -- index_first PLUS 1-hop neighbors of every candidate
                   slug (Phase 7a's enhancement for relational
                   questions).

Token counting uses tiktoken's o200k_base encoding (same family as
Anthropic models). When tiktoken isn't installed, falls back to a
char/4 heuristic.

Output: a markdown report at docs/graph/token-reduction-report.md.

Usage::

    PYTHONPATH=packages python3 scripts/graph_token_benchmark.py [--wiki PATH]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# Bootstrap PYTHONPATH if running directly.
HERE = Path(__file__).resolve().parent
PKGS = HERE.parent / "packages"
if str(PKGS) not in sys.path:
    sys.path.insert(0, str(PKGS))


# ---------------------------------------------------------------- token counting


def _count_tokens(text: str) -> int:
    """Best-effort token count.

    With tiktoken, uses the o200k_base encoding (Anthropic-compatible).
    Without tiktoken, char count divided by 4 (a coarse but not crazy
    English-text approximation).
    """
    try:
        import tiktoken
        enc = tiktoken.get_encoding("o200k_base")
        return len(enc.encode(text))
    except ImportError:
        return max(1, len(text) // 4)


# ---------------------------------------------------------------- retrieval bundles


def raw_baseline_tokens(wiki_root: Path) -> int:
    """Count tokens for a full-corpus dump (every wiki page concatenated)."""
    total = 0
    for p in wiki_root.rglob("*.md"):
        if p.name in {"_index.md", "_needs_review.md", "SCHEMA.md", "README.md"}:
            continue
        try:
            total += _count_tokens(p.read_text(encoding="utf-8"))
        except OSError:
            continue
    return total


def index_first_tokens(wiki_root: Path, question: str) -> tuple[int, list[str]]:
    """Phase 4 retrieval bundle. Returns (token_count, candidate_slugs)."""
    from jojo_qa.synthesize import build_retrieval_bundle

    bundle = build_retrieval_bundle(question, wiki_root=wiki_root, k_candidates=8)
    if bundle.router_result.route != "wiki":
        # v1-route questions don't go through the wiki retrieval at all.
        return 0, []
    body_tokens = sum(_count_tokens(b) for b in bundle.candidate_bodies.values())
    index_tokens = _count_tokens((wiki_root / "_index.md").read_text(encoding="utf-8") if (wiki_root / "_index.md").exists() else "")
    return body_tokens + index_tokens, [c.slug for c in bundle.candidate_entries]


def graph_assist_tokens(
    wiki_root: Path, question: str, candidate_slugs: list[str],
) -> int:
    """Phase 7a retrieval: index_first + 1-hop neighbors."""
    from jojo_qa import graph as graph_mod

    g = graph_mod.load(wiki_root)
    if not g.nodes:
        g = graph_mod.build(wiki_root)

    seen: set[str] = set(candidate_slugs)
    extra_tokens = 0
    for slug in candidate_slugs:
        for n in graph_mod.neighbors(g, slug, hops=1):
            if n in seen:
                continue
            seen.add(n)
            node = g.nodes.get(n)
            if not node:
                continue
            path = wiki_root / node.get("path", "")
            if path.exists():
                try:
                    extra_tokens += _count_tokens(path.read_text(encoding="utf-8"))
                except OSError:
                    continue

    base, _ = index_first_tokens(wiki_root, question)
    return base + extra_tokens


# ---------------------------------------------------------------- benchmark


# These are the seed questions from docs/qa/benchmark-questions.md plus a
# few relational stressors that exercise the graph-assist path.
BENCHMARK_QUESTIONS = [
    # From the Phase 4 seed:
    ("q-001", "What's the difference between NX-1607 and NX-0255?"),
    ("q-002", "Did the Weiss lab Peli2 redundancy finding change our position?"),
    ("q-003", "How was DEL screening organized at Nurix in 2022?"),
    ("q-004", "Walk me through the major Delphi ACS releases from inception through 2025."),
    ("q-005", "What's the standard buffer prep for an AKTA Pure 25 run on the BTK program?"),
    # Relational stressors -- where graph-assist should add hop pages:
    ("q-rel-1", "What's the connection between CBL-B and DEL screening?"),
    ("q-rel-2", "How does Pellino-1 relate to ITK?"),
    ("q-rel-3", "What's shared between BTK and IRAK4 programs?"),
]


def run_benchmark(wiki_root: Path) -> dict[str, Any]:
    raw_total = raw_baseline_tokens(wiki_root)
    rows: list[dict[str, Any]] = []
    for qid, question in BENCHMARK_QUESTIONS:
        idx_tokens, slugs = index_first_tokens(wiki_root, question)
        graph_tokens = (
            graph_assist_tokens(wiki_root, question, slugs)
            if slugs
            else 0
        )
        idx_ratio = (raw_total / max(idx_tokens, 1)) if idx_tokens else None
        graph_ratio = (raw_total / max(graph_tokens, 1)) if graph_tokens else None
        rows.append({
            "id": qid,
            "question": question,
            "raw_baseline": raw_total,
            "index_first": idx_tokens,
            "graph_assist": graph_tokens,
            "candidate_count": len(slugs),
            "index_ratio": idx_ratio,
            "graph_ratio": graph_ratio,
        })
    return {
        "wiki_root": str(wiki_root),
        "raw_baseline_total_tokens": raw_total,
        "rows": rows,
    }


def render_report(result: dict[str, Any]) -> str:
    lines = [
        "# Phase 7a Token-Reduction Benchmark",
        "",
        "Comparing three retrieval strategies by token cost per question:",
        "",
        "- **raw_baseline**: every wiki page dumped (pessimistic).",
        "- **index_first**: Phase 4 retrieval bundle.",
        "- **graph_assist**: index_first + 1-hop graph neighbors.",
        "",
        f"**Wiki:** `{result['wiki_root']}`",
        f"**Raw-baseline total tokens:** {result['raw_baseline_total_tokens']}",
        "",
        "Exit-criterion threshold: index_first or graph_assist should "
        "show >=10x token reduction vs raw_baseline at 500 articles. "
        "We'll watch the trend curve as the corpus grows.",
        "",
        "## Per-question results",
        "",
        "| ID | Question | index_first | ratio | graph_assist | ratio | candidates |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in result["rows"]:
        idx = row["index_first"]
        graph = row["graph_assist"]
        idx_ratio = f"{row['index_ratio']:.1f}x" if row["index_ratio"] else "n/a"
        graph_ratio = f"{row['graph_ratio']:.1f}x" if row["graph_ratio"] else "n/a"
        question = row["question"][:60].replace("|", "\\|")
        lines.append(
            f"| {row['id']} | {question} | {idx} | {idx_ratio} | "
            f"{graph} | {graph_ratio} | {row['candidate_count']} |"
        )
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append(
        "- `graph_assist` exceeds `index_first` because the 1-hop neighbors "
        "add page bodies on top of the candidate set. The expected curve: "
        "as corpus grows, the gap between `raw_baseline` and "
        "`index_first`/`graph_assist` widens, and the graph-assist "
        "advantage over index-first shows up specifically on relational "
        "questions where the answer requires multi-page synthesis."
    )
    lines.append(
        "- Re-run the benchmark every time the wiki grows by 50 pages. "
        "If the raw_baseline / index_first ratio doesn't grow at least "
        "linearly with corpus size, the index-first prompt needs "
        "tightening. If the ratio crosses 10x at 500 pages, Phase 7a "
        "production-exits."
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--wiki",
        default=str(Path.cwd() / ".." / "ask_jojo_wiki"),
        help="path to ask_jojo_wiki/",
    )
    parser.add_argument(
        "--out",
        default="docs/graph/token-reduction-report.md",
        help="where to write the report",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="dump raw results as JSON to stdout",
    )
    args = parser.parse_args(argv)

    wiki = Path(args.wiki).resolve()
    if not wiki.exists():
        print(f"wiki not found: {wiki}", file=sys.stderr)
        return 1

    result = run_benchmark(wiki)

    if args.json:
        print(json.dumps(result, indent=2))
        return 0

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_report(result), encoding="utf-8")
    print(f"wrote {out}")
    print(f"raw_baseline: {result['raw_baseline_total_tokens']} tokens across the wiki")
    return 0


if __name__ == "__main__":
    sys.exit(main())
