"""CLI for jojo_finetune — Phase 8: fine-tune dataset generation + training + eval.

Commands:

    jojo-finetune generate-dataset [--wiki-root PATH] [--output PATH]
                                   [--n INT] [--dry-run]

    jojo-finetune train --backend {bedrock|hf|dry-run}
                        [--dataset PATH] [--base-model STR]

    jojo-finetune eval --model MODEL_ID
                       --backend {bedrock|hf|synthesis}
                       [--benchmark PATH] [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from jojo_core import config

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------

_DEFAULT_WIKI_ROOT = Path("../ask_jojo_wiki").resolve()
_DEFAULT_DATASET = Path("data/finetune/v1.jsonl")
_DEFAULT_BENCHMARK = Path("data/finetune/benchmark.jsonl")
_DEFAULT_N = 100


# ---------------------------------------------------------------------------
# Helper: resolve wiki root
# ---------------------------------------------------------------------------


def _wiki_root(args: argparse.Namespace) -> Path:
    raw = getattr(args, "wiki_root", None)
    if raw:
        return Path(raw).resolve()
    val = config.get("wiki_root", None)
    if val:
        return Path(val).resolve()
    return _DEFAULT_WIKI_ROOT


# ---------------------------------------------------------------------------
# Sub-command handlers
# ---------------------------------------------------------------------------


def cmd_generate_dataset(args: argparse.Namespace) -> int:
    from jojo_finetune.dataset import generate_dataset

    wiki_root = _wiki_root(args)
    output = Path(args.output).resolve() if args.output else _DEFAULT_DATASET.resolve()
    n = args.n
    dry_run = args.dry_run

    try:
        examples = generate_dataset(wiki_root, output, n=n, dry_run=dry_run)
    except (ValueError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(
        json.dumps(
            {
                "status": "ok",
                "output": str(output),
                "records_written": len(examples),
                "dry_run": dry_run,
            },
            indent=2,
        )
    )
    return 0


def cmd_train(args: argparse.Namespace) -> int:
    from jojo_finetune.train import get_backend

    dataset = Path(args.dataset).resolve() if args.dataset else _DEFAULT_DATASET.resolve()
    base_model = args.base_model or ""

    try:
        backend = get_backend(args.backend)
    except (ValueError, ImportError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    # For real backends, use their default base model when none is given.
    if not base_model:
        if hasattr(backend, "DEFAULT_BASE_MODEL"):
            base_model = backend.DEFAULT_BASE_MODEL  # type: ignore[attr-defined]

    try:
        job = backend.submit(dataset, base_model)
    except (ValueError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(dict(job), indent=2))
    return 0


def cmd_eval(args: argparse.Namespace) -> int:
    from jojo_finetune.eval import run_eval

    benchmark = (
        Path(args.benchmark).resolve() if args.benchmark else _DEFAULT_BENCHMARK.resolve()
    )

    try:
        report = run_eval(
            args.model,
            args.backend,
            benchmark,
            dry_run=args.dry_run,
        )
    except (ValueError, FileNotFoundError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    # Print report without per-question details to keep output scannable.
    summary = {k: v for k, v in report.items() if k != "results"}
    summary["sample_results"] = report["results"][:3]
    print(json.dumps(summary, indent=2))
    return 0


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="jojo-finetune",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    # generate-dataset
    p_gen = sub.add_parser(
        "generate-dataset",
        help="Generate synthetic fine-tune training examples from the wiki.",
    )
    p_gen.add_argument("--wiki-root", dest="wiki_root", help="Path to ask_jojo_wiki/")
    p_gen.add_argument("--output", help="Destination .jsonl path")
    p_gen.add_argument(
        "--n", type=int, default=_DEFAULT_N, help="Number of examples to generate"
    )
    p_gen.add_argument(
        "--dry-run",
        dest="dry_run",
        action="store_true",
        help="Produce deterministic examples without API calls",
    )
    p_gen.set_defaults(func=cmd_generate_dataset)

    # train
    p_train = sub.add_parser(
        "train",
        help="Submit a fine-tune training job.",
    )
    p_train.add_argument(
        "--backend",
        required=True,
        choices=["bedrock", "hf", "dry-run"],
        help="Training backend",
    )
    p_train.add_argument("--dataset", help="Path to training .jsonl file")
    p_train.add_argument("--base-model", dest="base_model", help="Base model identifier")
    p_train.set_defaults(func=cmd_train)

    # eval
    p_eval = sub.add_parser(
        "eval",
        help="Evaluate a model against the benchmark.",
    )
    p_eval.add_argument("--model", required=True, help="Model ID to evaluate")
    p_eval.add_argument(
        "--backend",
        required=True,
        choices=["bedrock", "hf", "synthesis", "dry-run"],
        help="Eval backend",
    )
    p_eval.add_argument("--benchmark", help="Path to benchmark .jsonl file")
    p_eval.add_argument(
        "--dry-run",
        dest="dry_run",
        action="store_true",
        help="Use fixed dummy responses; no API calls",
    )
    p_eval.set_defaults(func=cmd_eval)

    return p


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    """Entry point for the ``jojo-finetune`` console script."""
    args = _build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
