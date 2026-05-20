"""CLI for jojo_graph.

Subcommands:

  jojo-graph rebuild      build graph artifacts (graphify or fallback).
  jojo-graph stats        print summary stats.
  jojo-graph report       print path to GRAPH_REPORT.md.
  jojo-graph html         print path to graph.html.
  jojo-graph available    print 'graphify' | 'fallback'.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from jojo_core import config

from . import builder


def _wiki_root(args: argparse.Namespace) -> Path:
    if getattr(args, "wiki", None):
        return Path(args.wiki).resolve()
    val = config.get("wiki_root", None)
    if val:
        return Path(val).resolve()
    return (Path.cwd() / ".." / "ask_jojo_wiki").resolve()


def cmd_rebuild(args: argparse.Namespace) -> int:
    wiki = _wiki_root(args)
    artifacts = builder.rebuild(wiki)
    print(json.dumps({
        "graph_html": str(artifacts.graph_html),
        "graph_json": str(artifacts.graph_json),
        "graph_report": str(artifacts.graph_report),
        "used_fallback": artifacts.used_fallback,
        "node_count": artifacts.node_count,
        "edge_count": artifacts.edge_count,
    }, indent=2))
    return 0


def cmd_stats(args: argparse.Namespace) -> int:
    print(json.dumps(builder.stats(_wiki_root(args)), indent=2))
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    print(builder.report_path(_wiki_root(args)))
    return 0


def cmd_html(args: argparse.Namespace) -> int:
    print(builder.html_path(_wiki_root(args)))
    return 0


def cmd_available(args: argparse.Namespace) -> int:
    _ = args
    print("graphify" if builder.is_graphify_available() else "fallback")
    return 0


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="jojo-graph", description=__doc__)
    p.add_argument("--wiki", help="path to ask_jojo_wiki/")
    sub = p.add_subparsers(dest="cmd", required=True)

    s_rebuild = sub.add_parser("rebuild", help="build graph artifacts")
    s_rebuild.set_defaults(func=cmd_rebuild)

    s_stats = sub.add_parser("stats", help="print stats")
    s_stats.set_defaults(func=cmd_stats)

    s_report = sub.add_parser("report", help="GRAPH_REPORT.md path")
    s_report.set_defaults(func=cmd_report)

    s_html = sub.add_parser("html", help="graph.html path")
    s_html.set_defaults(func=cmd_html)

    s_avail = sub.add_parser("available", help="check graphify availability")
    s_avail.set_defaults(func=cmd_available)

    return p


def main(argv: list[str] | None = None) -> int:
    try:
        args = _build_parser().parse_args(argv)
    except SystemExit:
        return 1
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
