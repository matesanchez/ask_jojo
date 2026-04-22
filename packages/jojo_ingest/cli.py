"""`jojo-ingest` command-line entry point.

Subcommands:

    jojo-ingest sync-all --raw <path>
        Run every *implemented* connector against the given ask_jojo_raw root.
        In the local tier that's drive + upload (if files are staged).

    jojo-ingest sync <connector> --raw <path> [opts]
        Run a single connector. Fails loudly for unimplemented ones rather
        than silently skipping.

    jojo-ingest upload <file> --raw <path> [--title ... --author ...]
        One-shot: process a single file through the upload pipeline.

    jojo-ingest status --raw <path>
        Print a manifest summary (entry count, per-source breakdown,
        pending supersedence chains).

    jojo-ingest resync <connector> --raw <path>
        Force a full re-walk (no --since filter). Same output as sync, but
        deliberately ignores incremental state. Use when a connector's output
        format has changed and you want everything re-written.

All subcommands accept `--since <iso-datetime>` for incremental semantics.
The connectors that honor it (SharePoint delta queries, NurixNet seen-file)
use it to minimize traffic; drive just filters by mtime.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

from jojo_ingest.driver import IngestDriver

log = logging.getLogger("jojo_ingest")


# Connector factories — lookup by name. Map to (factory, status) where status
# is "ready" / "stub" / "needs-creds" so `status` can report honestly.
def _connector_factories() -> dict:
    from jojo_ingest.drive import DriveConnector
    from jojo_ingest.nurixnet import NurixNetConnector
    from jojo_ingest.onedrive import OneDriveConnector
    from jojo_ingest.sharepoint import SharePointConnector
    from jojo_ingest.upload import UploadConnector

    return {
        "drive": {"cls": DriveConnector, "status": "ready"},
        "upload": {"cls": UploadConnector, "status": "ready"},
        "sharepoint": {"cls": SharePointConnector, "status": "needs-creds"},
        "onedrive": {"cls": OneDriveConnector, "status": "needs-creds"},
        "nurixnet": {"cls": NurixNetConnector, "status": "needs-creds"},
    }


def _parse_since(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError as exc:
        raise SystemExit(f"invalid --since value '{value}': {exc}") from exc


def _cmd_sync(args: argparse.Namespace) -> int:
    factories = _connector_factories()
    if args.connector not in factories:
        print(f"unknown connector: {args.connector}", file=sys.stderr)
        print(f"available: {', '.join(sorted(factories))}", file=sys.stderr)
        return 2
    spec = factories[args.connector]
    if spec["status"] != "ready":
        print(
            f"connector '{args.connector}' is not ready yet "
            f"(status={spec['status']}). See packages/jojo_ingest/{args.connector}.py.",
            file=sys.stderr,
        )
        return 3
    since = _parse_since(args.since)
    cls = spec["cls"]
    if args.connector == "drive":
        if not args.source:
            print("drive connector requires --source <path>", file=sys.stderr)
            return 2
        connector = cls(args.source, access_level=args.access_level)
    else:
        connector = cls()
    driver = IngestDriver(args.raw)
    result = driver.run([connector], since=since)
    _print_result(result)
    return 0


def _cmd_sync_all(args: argparse.Namespace) -> int:
    factories = _connector_factories()
    since = _parse_since(args.since)
    connectors = []
    for name, spec in factories.items():
        if spec["status"] != "ready":
            continue
        if name == "drive":
            if not args.source:
                continue
            connectors.append(spec["cls"](args.source, access_level=args.access_level))
        elif name == "upload":
            # upload is not a batch connector; skip in sync-all
            continue
    if not connectors:
        print(
            "no ready connectors matched. Pass --source for drive, or wait for "
            "cloud connectors to come online.",
            file=sys.stderr,
        )
        return 2
    driver = IngestDriver(args.raw)
    result = driver.run(connectors, since=since)
    _print_result(result)
    return 0


def _cmd_upload(args: argparse.Namespace) -> int:
    factories = _connector_factories()
    cls = factories["upload"]["cls"]
    connector = cls(
        args.file,
        title=args.title,
        author=args.author,
        access_level=args.access_level,
        tags=args.tag or [],
    )
    driver = IngestDriver(args.raw)
    result = driver.run([connector])
    _print_result(result)
    return 0


def _cmd_resync(args: argparse.Namespace) -> int:
    # Forced re-walk: same as sync but no --since filter.
    args.since = None
    return _cmd_sync(args)


def _cmd_status(args: argparse.Namespace) -> int:
    from jojo_connectors_common import Manifest

    manifest = Manifest.load(Path(args.raw) / "manifest.json")
    by_source: dict[str, int] = {}
    for entry in manifest.entries.values():
        by_source[entry.source_type] = by_source.get(entry.source_type, 0) + 1
    out = {
        "raw_root": str(Path(args.raw).resolve()),
        "total_entries": len(manifest.entries),
        "by_source": by_source,
        "supersedence_chains": len(manifest.supersedence),
    }
    print(json.dumps(out, indent=2))
    return 0


def _print_result(result) -> None:
    summary = {
        name: {
            "added": cr.added,
            "updated": cr.updated,
            "skipped": cr.skipped,
            "errors": cr.errors,
            "failures": cr.failures,
        }
        for name, cr in result.results.items()
    }
    out = {
        "results": summary,
        "change_record": str(result.change_record_path) if result.change_record_path else None,
    }
    print(json.dumps(out, indent=2))


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="jojo-ingest", description="JoJo Bot ingest CLI")
    p.add_argument("--verbose", "-v", action="count", default=0)
    sub = p.add_subparsers(dest="command", required=True)

    s_all = sub.add_parser("sync-all", help="Run every ready connector")
    s_all.add_argument("--raw", required=True, help="ask_jojo_raw root")
    s_all.add_argument("--source", help="drive root (if including drive)")
    s_all.add_argument("--access-level", default="all_fte")
    s_all.add_argument("--since", help="ISO datetime for incremental sync")
    s_all.set_defaults(func=_cmd_sync_all)

    s = sub.add_parser("sync", help="Run one connector")
    s.add_argument("connector")
    s.add_argument("--raw", required=True)
    s.add_argument("--source", help="drive root (for drive connector)")
    s.add_argument("--access-level", default="all_fte")
    s.add_argument("--since")
    s.set_defaults(func=_cmd_sync)

    u = sub.add_parser("upload", help="Ingest a single user-supplied file")
    u.add_argument("file")
    u.add_argument("--raw", required=True)
    u.add_argument("--title")
    u.add_argument("--author", default="")
    u.add_argument("--access-level", default="all_fte")
    u.add_argument("--tag", action="append", help="Can be passed multiple times")
    u.set_defaults(func=_cmd_upload)

    r = sub.add_parser("resync", help="Force full re-walk of a connector")
    r.add_argument("connector")
    r.add_argument("--raw", required=True)
    r.add_argument("--source")
    r.add_argument("--access-level", default="all_fte")
    r.set_defaults(func=_cmd_resync)

    st = sub.add_parser("status", help="Print manifest summary")
    st.add_argument("--raw", required=True)
    st.set_defaults(func=_cmd_status)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    level = logging.WARNING
    if args.verbose == 1:
        level = logging.INFO
    elif args.verbose >= 2:
        level = logging.DEBUG
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)-5s %(name)s: %(message)s",
    )
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
