"""CLI for jojo_core.

Exposes ``jojo-core config`` subcommands for inspecting and editing
``%APPDATA%\\JojoBot\\config.json`` (DPAPI-encrypted on Windows, plaintext
elsewhere per ``jojo_core.config``):

    jojo-core config path                 -- print where config.json lives
    jojo-core config show                 -- print all keys (secrets masked)
    jojo-core config show --unmask        -- print all keys without masking
    jojo-core config get <key>            -- print one key's value
    jojo-core config set <key> <value>    -- store a value
    jojo-core config delete <key>         -- remove a key
    jojo-core config migrate-from-env     -- copy JOJO_* env vars into config

Additional top-level commands (phase-1 packaging pass):

    jojo-core version                     -- print package version

Other subcommands land as jojo_core grows (logging setup, Anthropic
client factory, worker control).
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

import jojo_core
from jojo_core import config


def _cmd_config_path(_: argparse.Namespace) -> int:
    print(config.config_path())
    return 0


def _cmd_config_show(args: argparse.Namespace) -> int:
    data = config.load()
    if not data:
        print(f"(empty -- no config at {config.config_path()})")
        return 0
    width = max(len(k) for k in data.keys())
    for key in sorted(data.keys()):
        value = data[key]
        if not args.unmask and key in config.SECRET_KEYS:
            display = config.mask(value)
        else:
            display = value
        print(f"{key:<{width}}  {display}")
    return 0


def _cmd_config_get(args: argparse.Namespace) -> int:
    value = config.get(args.key, env_fallback=not args.no_env)
    if value is None:
        print(f"(unset) {args.key}", file=sys.stderr)
        return 1
    print(value)
    return 0


def _cmd_config_set(args: argparse.Namespace) -> int:
    if args.key not in config.ENV_MAP:
        known = ", ".join(sorted(config.ENV_MAP.keys()))
        print(f"[error] unknown key {args.key!r}. Known keys: {known}", file=sys.stderr)
        return 2
    if args.key in config.SECRET_KEYS and not config._use_dpapi():
        print(
            f"[warning] writing a secret ({args.key}) on a platform without DPAPI. "
            f"The value will be stored as plaintext in {config.config_path()}. "
            f"Set JOJO_CONFIG_FORCE_PLAINTEXT=1 to silence this warning.",
            file=sys.stderr,
        )
    config.set(args.key, args.value)
    print(f"[ok] set {args.key}")
    return 0


def _cmd_config_delete(args: argparse.Namespace) -> int:
    if config.delete(args.key):
        print(f"[ok] deleted {args.key}")
        return 0
    print(f"(not set) {args.key}", file=sys.stderr)
    return 1


def _cmd_config_migrate(args: argparse.Namespace) -> int:
    migrated = config.migrate_from_env(overwrite=args.overwrite)
    if not migrated:
        print("(no-op -- no matching JOJO_* env vars are set, or all keys already configured)")
        return 0
    for key in migrated:
        print(f"[ok] migrated {key} from ${config.ENV_MAP[key]}")
    print(f"\nWrote {len(migrated)} key(s) to {config.config_path()}")
    return 0


def _cmd_version(_: argparse.Namespace) -> int:
    print(jojo_core.__version__)
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="jojo-core",
        description="JoJo Bot core utilities. Primary subcommand is 'config'.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # config
    p_config = sub.add_parser("config", help="Inspect / edit config.json")
    p_config_sub = p_config.add_subparsers(dest="subcommand", required=True)

    p_path = p_config_sub.add_parser("path", help="Print the config.json location")
    p_path.set_defaults(func=_cmd_config_path)

    p_show = p_config_sub.add_parser("show", help="Print all keys (secrets masked)")
    p_show.add_argument(
        "--unmask",
        action="store_true",
        help="Show secret values in full instead of masking them.",
    )
    p_show.set_defaults(func=_cmd_config_show)

    p_get = p_config_sub.add_parser("get", help="Print the value for <key>")
    p_get.add_argument("key")
    p_get.add_argument(
        "--no-env",
        action="store_true",
        help="Don't fall back to the matching environment variable.",
    )
    p_get.set_defaults(func=_cmd_config_get)

    p_set = p_config_sub.add_parser("set", help="Store a value for <key>")
    p_set.add_argument("key")
    p_set.add_argument("value")
    p_set.set_defaults(func=_cmd_config_set)

    p_del = p_config_sub.add_parser("delete", help="Remove <key> from config.json")
    p_del.add_argument("key")
    p_del.set_defaults(func=_cmd_config_delete)

    p_mig = p_config_sub.add_parser(
        "migrate-from-env",
        help="Copy every set JOJO_* env var into config.json",
    )
    p_mig.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite keys already present in config.json (default: skip).",
    )
    p_mig.set_defaults(func=_cmd_config_migrate)

    # version
    p_ver = sub.add_parser("version", help="Print the jojo_core package version")
    p_ver.set_defaults(func=_cmd_version)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
