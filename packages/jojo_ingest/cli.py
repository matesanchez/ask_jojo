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

from jojo_core import config
from jojo_ingest.driver import IngestDriver

log = logging.getLogger("jojo_ingest")


# Connector factories — lookup by name. Map to (factory, status) where status
# is "ready" / "needs-token" / "needs-path" so `status` can report honestly.
# Note: NurixNet intentionally not listed — it's a SharePoint site (part of
# the SharePoint connector's site list), not a separate connector.
def _connector_factories() -> dict:
    from jojo_ingest.drive import DriveConnector
    from jojo_ingest.onedrive import OneDriveConnector
    from jojo_ingest.publicdrive import PublicDriveConnector
    from jojo_ingest.sharepoint import SharePointConnector
    from jojo_ingest.upload import UploadConnector

    # config.get() consults config.json first, then the env var, so the
    # status matches whichever surface the operator is using.
    sharepoint_status = (
        "ready"
        if config.get(config.KEY_GRAPH_ACCESS_TOKEN)
        and config.get(config.KEY_SHAREPOINT_SITES)
        else "needs-token"
    )
    # OneDrive + public drive come out of local mounts (ADR 0008) — they're
    # "ready" as soon as the operator points either the env var or config.json
    # at their synced folder.
    onedrive_status = "ready" if config.get(config.KEY_ONEDRIVE_PATH) else "needs-path"
    publicdrive_status = (
        "ready" if config.get(config.KEY_PUBLIC_DRIVE_PATH) else "needs-path"
    )

    return {
        "drive": {"cls": DriveConnector, "status": "ready"},
        "upload": {"cls": UploadConnector, "status": "ready"},
        "sharepoint": {"cls": SharePointConnector, "status": sharepoint_status},
        "onedrive": {"cls": OneDriveConnector, "status": onedrive_status},
        "publicdrive": {"cls": PublicDriveConnector, "status": publicdrive_status},
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
        # Don't block env-driven connectors on the env-var check if the user
        # passed the equivalent CLI override — `--sites` substitutes for
        # JOJO_SHAREPOINT_SITES, `--source` substitutes for JOJO_ONEDRIVE_PATH
        # / JOJO_PUBLIC_DRIVE_PATH.
        overrides_present = (
            (args.connector == "sharepoint" and args.sites)
            or (args.connector in ("onedrive", "publicdrive") and args.source)
        )
        if not overrides_present:
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
    elif args.connector == "sharepoint":
        from jojo_ingest.sharepoint import (
            SharePointEnvError,
            build_sharepoint_connector_from_env,
        )

        sites = args.sites.split(",") if args.sites else None
        try:
            connector = build_sharepoint_connector_from_env(
                access_level=args.access_level,
                site_urls_override=sites,
                token_override=args.access_token,
            )
        except SharePointEnvError as exc:
            print(f"sharepoint connector cannot start: {exc}", file=sys.stderr)
            return 3
    elif args.connector == "onedrive":
        from jojo_ingest.onedrive import (
            OneDriveEnvError,
            build_onedrive_connector_from_env,
        )

        try:
            connector = build_onedrive_connector_from_env(
                access_level=args.access_level,
                path_override=args.source,
            )
        except OneDriveEnvError as exc:
            print(f"onedrive connector cannot start: {exc}", file=sys.stderr)
            return 3
    elif args.connector == "publicdrive":
        from jojo_ingest.publicdrive import (
            PublicDriveEnvError,
            build_publicdrive_connector_from_env,
        )

        try:
            connector = build_publicdrive_connector_from_env(
                access_level=args.access_level,
                path_override=args.source,
            )
        except PublicDriveEnvError as exc:
            print(f"publicdrive connector cannot start: {exc}", file=sys.stderr)
            return 3
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
        elif name == "sharepoint":
            from jojo_ingest.sharepoint import build_sharepoint_connector_from_env

            connectors.append(
                build_sharepoint_connector_from_env(access_level=args.access_level)
            )
        elif name == "onedrive":
            from jojo_ingest.onedrive import build_onedrive_connector_from_env

            connectors.append(
                build_onedrive_connector_from_env(access_level=args.access_level)
            )
        elif name == "publicdrive":
            from jojo_ingest.publicdrive import build_publicdrive_connector_from_env

            connectors.append(
                build_publicdrive_connector_from_env(access_level=args.access_level)
            )
    if not connectors:
        print(
            "no ready connectors matched. Pass --source for drive, or "
            "configure sharepoint / onedrive / publicdrive via "
            "`jojo-core config set ...` (graph_access_token, sharepoint_sites, "
            "onedrive_path, public_drive_path) or their JOJO_* env-var "
            "equivalents.",
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
    s.add_argument(
        "--source",
        help=(
            "Filesystem root. Required for 'drive'; optional override for "
            "'onedrive' (default: $JOJO_ONEDRIVE_PATH) and 'publicdrive' "
            "(default: $JOJO_PUBLIC_DRIVE_PATH, or 'P:\\' on Windows)."
        ),
    )
    s.add_argument("--access-level", default="all_fte")
    s.add_argument("--since")
    s.add_argument(
        "--sites",
        help=(
            "Comma-separated SharePoint site URLs (for sharepoint connector). "
            "Overrides JOJO_SHAREPOINT_SITES env var."
        ),
    )
    s.add_argument(
        "--access-token",
        help=(
            "Bearer token for the sharepoint connector (Path A). Overrides "
            "JOJO_GRAPH_ACCESS_TOKEN. Prefer the env var for non-one-shot runs."
        ),
    )
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
