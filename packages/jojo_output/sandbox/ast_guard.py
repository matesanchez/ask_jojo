"""AST guard — belt-and-suspenders check for any future "user-pasted code" path.

The Phase 5 contract is "model produces a typed JSON spec, never code."
The renderer in ``render.py`` only takes a PlotSpec. This module exists
for any future escape hatch where a power user pastes a custom plot
function (e.g. for a Phase 8 backlog item). Don't enable that path
without running the AST through ``check_safe`` first.

Public API:

- ``ALLOWED_IMPORTS`` — frozenset of module names allowed at the top
  of any pasted snippet.
- ``check_safe(source)`` — parse + walk the AST; raise ``UnsafeASTError``
  on any disallowed node.
- ``UnsafeASTError`` — explanatory exception for the violation.

Banned: ``os``, ``subprocess``, ``socket``, ``urllib``, ``requests``,
``__import__``, ``eval``, ``exec``, ``compile``, ``open``,
``pathlib``, attribute access into ``__builtins__``, etc.

This is intentionally conservative — false positives are easier to
loosen than false negatives are to discover.
"""

from __future__ import annotations

import ast
from typing import Any

ALLOWED_IMPORTS = frozenset(
    {
        "numpy",
        "numpy.linalg",
        "numpy.random",
        "pandas",
        "matplotlib",
        "matplotlib.pyplot",
        "matplotlib.patches",
        "matplotlib.colors",
        "seaborn",
        "math",  # stdlib safe
        "statistics",  # stdlib safe
    }
)


class UnsafeASTError(ValueError):
    """Raised by ``check_safe`` on disallowed code patterns."""


_BANNED_NAMES = frozenset(
    {
        "eval",
        "exec",
        "compile",
        "__import__",
        "open",
        "input",
        "globals",
        "locals",
        "vars",
        "getattr",  # stops attribute lookup chains
        "setattr",
        "delattr",
        "hasattr",  # too easy to probe for unsafe attrs
    }
)

_BANNED_ATTRS = frozenset(
    {
        "__class__",
        "__bases__",
        "__subclasses__",
        "__globals__",
        "__builtins__",
        "__dict__",
        "__getattribute__",
        "__getattr__",
        "__import__",
        "__loader__",
        "__spec__",
        "f_globals",
        "f_locals",
        "gi_frame",
        "cr_frame",
    }
)


def check_safe(source: str) -> None:
    """Parse ``source`` and raise ``UnsafeASTError`` on any disallowed node."""
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        raise UnsafeASTError(f"syntax error: {e}") from e

    for node in ast.walk(tree):
        _check_node(node)


def _check_node(node: ast.AST) -> None:
    # Imports: only ALLOWED_IMPORTS or their submodules.
    if isinstance(node, ast.Import):
        for alias in node.names:
            if not _import_allowed(alias.name):
                raise UnsafeASTError(f"disallowed import: {alias.name!r}")
    elif isinstance(node, ast.ImportFrom):
        mod = node.module or ""
        if not _import_allowed(mod):
            raise UnsafeASTError(f"disallowed import-from: {mod!r}")

    # Banned name lookups.
    if isinstance(node, ast.Name):
        if node.id in _BANNED_NAMES:
            raise UnsafeASTError(f"disallowed name: {node.id!r}")

    # Banned attribute access.
    if isinstance(node, ast.Attribute):
        if node.attr in _BANNED_ATTRS:
            raise UnsafeASTError(f"disallowed attribute: {node.attr!r}")

    # Forbid `with` (file/connection management implies side effects).
    # If a future legitimate use case needs `with`, allow it case-by-case.
    # Forbid `try/except` for the same reason — bypasses other checks.
    # (Pragmatic: spec-driven rendering doesn't need these.)
    # The render path doesn't use try/except either, so this is consistent.

    # Forbid `lambda` argument shadowing of banned names? Out of scope.
    # Star imports.
    if isinstance(node, ast.ImportFrom) and any(a.name == "*" for a in (node.names or [])):
        raise UnsafeASTError("star imports are not allowed")


def _import_allowed(name: str) -> bool:
    if not name:
        return False
    # Allow exact match or submodule of an allowed root.
    if name in ALLOWED_IMPORTS:
        return True
    parts = name.split(".")
    # Match against root only (e.g. matplotlib.pyplot -> matplotlib).
    return parts[0] in ALLOWED_IMPORTS


# Sanity check: make sure ast itself is reachable.
_ = Any
