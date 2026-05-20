"""CLI for jojo_qa.

Subcommands:

    jojo-qa route <question>            Run the regex router; print result.
    jojo-qa retrieve <question>         Build and print the retrieval bundle.
    jojo-qa graph rebuild               Build _graph.json from wiki + backlinks.
    jojo-qa graph stats                 Print graph stats (nodes/edges/components).
    jojo-qa graph path <src> <dst>      BFS shortest-path between two slugs.
    jojo-qa qmd status                  Print qmd activation status.
    jojo-qa qmd activate                Force-activate qmd (writes config flag).
    jojo-qa qmd deactivate              Force-deactivate qmd.
    jojo-qa misses summary              Print recent miss-log summary.

The synthesis subcommand (``jojo-qa ask``) is intentionally not wired
yet; it returns ``api_key_required`` until FU-10 lands. See
``synthesize.answer`` and ADR 0011.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from jojo_core import config

from . import graph as graph_mod
from . import miss_log, qmd_activation, router, synthesize


def _wiki_root(args: argparse.Namespace) -> Path:
    """Resolve wiki root from CLI flag, config, or sibling-of-cwd default."""
    if getattr(args, "wiki", None):
        return Path(args.wiki).resolve()
    val = config.get("wiki_root", None)
    if val:
        return Path(val).resolve()
    # Default: ../ask_jojo_wiki sibling of the cwd.
    return (Path.cwd() / ".." / "ask_jojo_wiki").resolve()


def _manifest(args: argparse.Namespace) -> Path | None:
    """Resolve manifest path from CLI flag, config, or sibling default."""
    if getattr(args, "manifest", None):
        return Path(args.manifest).resolve()
    val = config.get("raw_root", None)
    if val:
        p = Path(val).resolve() / "manifest.json"
        return p if p.exists() else None
    p = (Path.cwd() / ".." / "ask_jojo_raw" / "manifest.json").resolve()
    return p if p.exists() else None


# -- command handlers ----------------------------------------------------


def cmd_route(args: argparse.Namespace) -> int:
    result = router.classify(args.question)
    out = {
        "route": result.route,
        "reason": result.reason,
        "matched_keywords": list(result.matched_keywords),
        "override_matched": result.override_matched,
    }
    print(json.dumps(out, indent=2))
    return 0


def cmd_retrieve(args: argparse.Namespace) -> int:
    bundle = synthesize.build_retrieval_bundle(
        args.question,
        wiki_root=_wiki_root(args),
        manifest_path=_manifest(args),
        k_candidates=args.k,
    )
    payload = bundle.to_dict()
    if not args.full:
        # Trim bodies; preserve summary.
        payload["candidate_bodies"] = {
            slug: f"<{len(body)} chars>" for slug, body in payload["candidate_bodies"].items()
        }
    print(json.dumps(payload, indent=2))
    return 0


def cmd_graph_rebuild(args: argparse.Namespace) -> int:
    wiki_root = _wiki_root(args)
    g = graph_mod.build(wiki_root)
    out = graph_mod.write(g, wiki_root)
    print(f"wrote {out}")
    print(json.dumps(graph_mod.stats(g), indent=2))
    return 0


def cmd_graph_stats(args: argparse.Namespace) -> int:
    wiki_root = _wiki_root(args)
    g = graph_mod.load(wiki_root)
    if not g.nodes:
        # Build on the fly if not yet serialized.
        g = graph_mod.build(wiki_root)
    print(json.dumps(graph_mod.stats(g), indent=2))
    return 0


def cmd_graph_path(args: argparse.Namespace) -> int:
    wiki_root = _wiki_root(args)
    g = graph_mod.load(wiki_root)
    if not g.nodes:
        g = graph_mod.build(wiki_root)
    path = graph_mod.shortest_path(g, args.src, args.dst)
    if path is None:
        print(json.dumps({"path": None, "reason": "disconnected or missing"}))
        return 1
    print(json.dumps({"path": path, "hops": len(path) - 1}, indent=2))
    return 0


def cmd_qmd_status(args: argparse.Namespace) -> int:
    summary = qmd_activation.status_summary(wiki_root=_wiki_root(args))
    print(json.dumps(summary, indent=2))
    return 0


def cmd_qmd_activate(args: argparse.Namespace) -> int:
    _ = args
    qmd_activation.activate()
    print("qmd_active=True (written to config.json)")
    return 0


def cmd_qmd_deactivate(args: argparse.Namespace) -> int:
    _ = args
    qmd_activation.deactivate()
    print("qmd_active=False (written to config.json)")
    return 0


def cmd_misses_summary(args: argparse.Namespace) -> int:
    _ = args
    print(json.dumps(miss_log.summary(), indent=2))
    return 0


# -- argparse plumbing ---------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="jojo-qa", description=__doc__)
    p.add_argument("--wiki", help="path to ask_jojo_wiki/ (overrides config)")
    p.add_argument("--manifest", help="path to ask_jojo_raw/manifest.json")

    sub = p.add_subparsers(dest="cmd", required=True)

    p_route = sub.add_parser("route", help="run the regex router")
    p_route.add_argument("question")
    p_route.set_defaults(func=cmd_route)

    p_retr = sub.add_parser("retrieve", help="build the retrieval bundle")
    p_retr.add_argument("question")
    p_retr.add_argument("-k", type=int, default=8, help="top-k candidates")
    p_retr.add_argument("--full", action="store_true", help="include page bodies in output")
    p_retr.set_defaults(func=cmd_retrieve)

    p_graph = sub.add_parser("graph", help="graph operations")
    g_sub = p_graph.add_subparsers(dest="graph_cmd", required=True)

    g_build = g_sub.add_parser("rebuild", help="rebuild _graph.json")
    g_build.set_defaults(func=cmd_graph_rebuild)

    g_stats = g_sub.add_parser("stats", help="print graph stats")
    g_stats.set_defaults(func=cmd_graph_stats)

    g_path = g_sub.add_parser("path", help="BFS shortest path")
    g_path.add_argument("src")
    g_path.add_argument("dst")
    g_path.set_defaults(func=cmd_graph_path)

    p_qmd = sub.add_parser("qmd", help="qmd activation operations")
    q_sub = p_qmd.add_subparsers(dest="qmd_cmd", required=True)

    q_status = q_sub.add_parser("status", help="print qmd activation status")
    q_status.set_defaults(func=cmd_qmd_status)

    q_act = q_sub.add_parser("activate", help="force qmd activation")
    q_act.set_defaults(func=cmd_qmd_activate)

    q_deact = q_sub.add_parser("deactivate", help="force qmd deactivation")
    q_deact.set_defaults(func=cmd_qmd_deactivate)

    p_misses = sub.add_parser("misses", help="miss-log operations")
    m_sub = p_misses.add_subparsers(dest="misses_cmd", required=True)
    m_sum = m_sub.add_parser("summary", help="print miss-log summary")
    m_sum.set_defaults(func=cmd_misses_summary)

    return p


def main(argv: list[str] | None = None) -> int:
    try:
        args = _build_parser().parse_args(argv)
    except SystemExit:
        return 1
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
