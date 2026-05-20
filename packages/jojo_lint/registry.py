"""Registry — maps check names to check functions and runs suites."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from jojo_core import config as _config

from .checks import (
    bloat_check,
    contradiction_check,
    missing_articles_check,
    orphan_check,
    quote_budget_check,
    schema_check,
    staleness_check,
    stub_check,
    suggested_questions_check,
    wikilink_check,
)
from .checks.base import CheckResult

NIGHTLY_CHECKS: list[str] = [
    "schema",
    "orphan",
    "stub",
    "wikilink",
    "bloat",
    "quote_budget",
]

WEEKLY_CHECKS: list[str] = [
    "contradiction",
    "staleness",
    "missing_articles",
    "suggested_questions",
]


def _api_key() -> str | None:
    """Read the Anthropic API key from config (env-fallback enabled)."""
    return _config.get(_config.KEY_ANTHROPIC_API_KEY, None)


def run_check(name: str, wiki_root: Path | str, **kwargs: Any) -> CheckResult:
    """Run a single check by name.

    Args:
        name: check identifier, e.g. ``"schema"`` or ``"orphan"``.
        wiki_root: path to the compiled wiki repository.
        **kwargs: forwarded to the check function. Common kwargs:
            - ``api_key``: override the auto-read API key (weekly checks).
            - ``stale_days``: for ``stub`` check.
            - ``manifest_path``: for ``staleness`` / ``missing_articles``.
            - ``max_lines`` / ``max_bytes``: for ``bloat``.
            - ``max_quoted_fraction``: for ``quote_budget``.

    Raises:
        ValueError: when ``name`` is not a known check.
    """
    wiki_root = Path(wiki_root)

    if name == "schema":
        return schema_check.run(wiki_root)
    if name == "orphan":
        return orphan_check.run(wiki_root)
    if name == "stub":
        return stub_check.run(wiki_root, **{k: v for k, v in kwargs.items() if k == "stale_days"})
    if name == "wikilink":
        return wikilink_check.run(wiki_root)
    if name == "bloat":
        bloat_kw = {k: v for k, v in kwargs.items() if k in ("max_lines", "max_bytes")}
        return bloat_check.run(wiki_root, **bloat_kw)
    if name == "quote_budget":
        qb_kw = {k: v for k, v in kwargs.items() if k == "max_quoted_fraction"}
        return quote_budget_check.run(wiki_root, **qb_kw)
    if name == "contradiction":
        api_key = kwargs.get("api_key", _api_key())
        return contradiction_check.run(wiki_root, api_key=api_key)
    if name == "staleness":
        api_key = kwargs.get("api_key", _api_key())
        manifest_path = kwargs.get("manifest_path")
        return staleness_check.run(wiki_root, manifest_path=manifest_path, api_key=api_key)
    if name == "missing_articles":
        api_key = kwargs.get("api_key", _api_key())
        manifest_path = kwargs.get("manifest_path")
        return missing_articles_check.run(
            wiki_root, manifest_path=manifest_path, api_key=api_key
        )
    if name == "suggested_questions":
        api_key = kwargs.get("api_key", _api_key())
        return suggested_questions_check.run(wiki_root, api_key=api_key)

    raise ValueError(f"Unknown check: {name!r}. Known checks: {NIGHTLY_CHECKS + WEEKLY_CHECKS}")


def run_nightly(wiki_root: Path | str, **kwargs: Any) -> list[CheckResult]:
    """Run all nightly checks in order.

    Args:
        wiki_root: path to the compiled wiki repository.
        **kwargs: forwarded to individual checks (see ``run_check``).

    Returns:
        List of :class:`CheckResult` in ``NIGHTLY_CHECKS`` order.
    """
    return [run_check(name, wiki_root, **kwargs) for name in NIGHTLY_CHECKS]


def run_weekly(wiki_root: Path | str, **kwargs: Any) -> list[CheckResult]:
    """Run all weekly checks in order.

    Args:
        wiki_root: path to the compiled wiki repository.
        **kwargs: forwarded to individual checks (see ``run_check``).

    Returns:
        List of :class:`CheckResult` in ``WEEKLY_CHECKS`` order.
    """
    return [run_check(name, wiki_root, **kwargs) for name in WEEKLY_CHECKS]
