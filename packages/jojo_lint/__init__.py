"""jojo_lint — wiki lint and self-maintenance checks.

Nightly deterministic checks + weekly LLM-assisted checks (stubs when
no API key is configured). Phase 6 owns this package.

Public API:
    - ``run_nightly(wiki_root, **kwargs)`` — run all 6 nightly checks.
    - ``run_weekly(wiki_root, **kwargs)`` — run all 4 weekly checks.
    - ``run_check(name, wiki_root, **kwargs)`` — run one check by name.
    - ``CheckResult`` — dataclass for a single check's output.

Nightly checks (deterministic, no API key needed):
    schema, orphan, stub, wikilink, bloat, quote_budget

Weekly checks (LLM-assisted; return ``api_key_required`` when no key):
    contradiction, staleness, missing_articles, suggested_questions
"""

from __future__ import annotations

__version__ = "0.1.0"

from .checks.base import CheckResult
from .registry import run_check, run_nightly, run_weekly

__all__ = [
    "CheckResult",
    "run_check",
    "run_nightly",
    "run_weekly",
    "__version__",
]
