"""CLI entry point for jojo-lint.

Subcommands:
    nightly   [--wiki <path>] [--history-dir <path>]
    weekly    [--wiki <path>] [--history-dir <path>]
    check <name> [--wiki <path>]
    report    [--days N] [--history-dir <path>]
    history   [--days N] [--history-dir <path>]
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def _default_wiki_root() -> Path:
    """Resolve the wiki root from env or sibling-of-cwd default."""
    env_val = os.environ.get("JOJO_WIKI_ROOT")
    if env_val:
        return Path(env_val).resolve()
    # Default: sibling of the project root
    cwd = Path.cwd()
    candidate = cwd.parent / "ask_jojo_wiki"
    if candidate.exists():
        return candidate
    return cwd / "ask_jojo_wiki"


def _default_history_dir() -> Path:
    """Resolve the history dir from env or platform default."""
    env_val = os.environ.get("JOJO_LINT_HISTORY_DIR")
    if env_val:
        return Path(env_val).resolve()
    return Path.home() / "AppData" / "Local" / "JojoBot" / "lint-history"


def _print_results_summary(results: list) -> None:  # type: ignore[type-arg]
    """Print a human-readable summary of check results."""
    for r in results:
        status_icon = {"pass": "[OK]", "warn": "[WARN]", "fail": "[FAIL]"}.get(
            r.status, f"[{r.status.upper()}]"
        )
        finding_count = len(r.findings)
        print(
            f"  {status_icon:8s} {r.check_name:<20s}"
            f" {finding_count} finding(s)"
            f"  ({r.duration_ms} ms)"
        )
        if finding_count and finding_count <= 5:
            for f in r.findings:
                sev = f.get("severity", "?")
                slug = f.get("slug", "?")
                msg = f.get("message", "")
                print(f"             [{sev}] {slug}: {msg}")
        elif finding_count > 5:
            for f in r.findings[:3]:
                sev = f.get("severity", "?")
                slug = f.get("slug", "?")
                msg = f.get("message", "")
                print(f"             [{sev}] {slug}: {msg}")
            print(f"             ... and {finding_count - 3} more")


def _cmd_nightly(args: list[str]) -> int:
    """Run nightly checks."""
    import argparse

    p = argparse.ArgumentParser(prog="jojo-lint nightly")
    p.add_argument("--wiki", default=None, help="Path to wiki root")
    p.add_argument("--history-dir", default=None, help="History directory")
    ns = p.parse_args(args)

    wiki_root = Path(ns.wiki).resolve() if ns.wiki else _default_wiki_root()
    history_dir = Path(ns.history_dir).resolve() if ns.history_dir else _default_history_dir()

    from .history import append_run
    from .registry import run_nightly

    print(f"jojo-lint nightly -- wiki: {wiki_root}")
    results = run_nightly(wiki_root)
    _print_results_summary(results)
    append_run("nightly", results, history_dir=history_dir)

    if any(r.status == "fail" for r in results):
        print("\nResult: FAIL (one or more checks failed)")
        return 1
    print("\nResult: OK")
    return 0


def _cmd_weekly(args: list[str]) -> int:
    """Run weekly checks."""
    import argparse

    p = argparse.ArgumentParser(prog="jojo-lint weekly")
    p.add_argument("--wiki", default=None, help="Path to wiki root")
    p.add_argument("--history-dir", default=None, help="History directory")
    ns = p.parse_args(args)

    wiki_root = Path(ns.wiki).resolve() if ns.wiki else _default_wiki_root()
    history_dir = Path(ns.history_dir).resolve() if ns.history_dir else _default_history_dir()

    from .history import append_run
    from .registry import run_weekly

    print(f"jojo-lint weekly -- wiki: {wiki_root}")
    results = run_weekly(wiki_root)
    _print_results_summary(results)
    append_run("weekly", results, history_dir=history_dir)

    if any(r.status == "fail" for r in results):
        print("\nResult: FAIL (one or more checks failed)")
        return 1
    print("\nResult: OK")
    return 0


def _cmd_check(args: list[str]) -> int:
    """Run a single check and print JSON to stdout."""
    import argparse

    p = argparse.ArgumentParser(prog="jojo-lint check")
    p.add_argument("name", help="Check name (e.g. schema, orphan, stub)")
    p.add_argument("--wiki", default=None, help="Path to wiki root")
    ns = p.parse_args(args)

    wiki_root = Path(ns.wiki).resolve() if ns.wiki else _default_wiki_root()

    from .registry import run_check

    try:
        result = run_check(ns.name, wiki_root)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(result.to_dict(), indent=2))
    return 0


def _cmd_report(args: list[str]) -> int:
    """Print a summary table of recent runs."""
    import argparse

    p = argparse.ArgumentParser(prog="jojo-lint report")
    p.add_argument("--days", type=int, default=30, help="Look-back window in days")
    p.add_argument("--history-dir", default=None, help="History directory")
    ns = p.parse_args(args)

    history_dir = Path(ns.history_dir).resolve() if ns.history_dir else _default_history_dir()

    from .history import load_runs

    runs = load_runs(days=ns.days, history_dir=history_dir)
    if not runs:
        print(f"No runs found in the last {ns.days} days.")
        return 0

    print(f"{'run_at':30s} {'scope':8s} {'checks':6s} {'fail':5s} {'warn':5s}")
    print("-" * 60)
    for run in runs:
        results = run.get("results", [])
        fail = sum(1 for r in results if r.get("status") == "fail")
        warn = sum(1 for r in results if r.get("status") == "warn")
        print(
            f"{run.get('run_at', '')[:29]:30s}"
            f" {run.get('scope', ''):8s}"
            f" {len(results):6d}"
            f" {fail:5d}"
            f" {warn:5d}"
        )
    return 0


def _cmd_history(args: list[str]) -> int:
    """Alias for report."""
    return _cmd_report(args)


def main(argv: list[str] | None = None) -> int:
    """Entry point for ``jojo-lint``."""
    args = argv if argv is not None else sys.argv[1:]

    if not args:
        print(
            "Usage: jojo-lint <command> [options]\n"
            "Commands: nightly, weekly, check <name>, report, history\n"
            "Run 'jojo-lint <command> --help' for details."
        )
        return 0

    cmd = args[0]
    rest = args[1:]

    dispatch = {
        "nightly": _cmd_nightly,
        "weekly": _cmd_weekly,
        "check": _cmd_check,
        "report": _cmd_report,
        "history": _cmd_history,
    }

    handler = dispatch.get(cmd)
    if handler is None:
        print(f"Unknown command: {cmd!r}", file=sys.stderr)
        print("Available commands: " + ", ".join(dispatch.keys()), file=sys.stderr)
        return 1

    return handler(rest)


if __name__ == "__main__":
    sys.exit(main())
