"""Tests for the AST guard.

Most malicious patterns are caught here. The tests are intentionally
exhaustive on the bad-cases side: false positives are recoverable,
false negatives are sandbox escapes.
"""

from __future__ import annotations

import pytest

from jojo_output.sandbox.ast_guard import (
    ALLOWED_IMPORTS,
    UnsafeASTError,
    check_safe,
)


# -- allowed --------------------------------------------------------------


def test_allow_numpy_import() -> None:
    check_safe("import numpy as np")


def test_allow_matplotlib_pyplot() -> None:
    check_safe("import matplotlib.pyplot as plt")


def test_allow_pandas_import() -> None:
    check_safe("import pandas as pd")


def test_allow_seaborn() -> None:
    check_safe("import seaborn as sns")


def test_allow_simple_arithmetic() -> None:
    check_safe("x = 1 + 2 * 3")


def test_allow_function_def() -> None:
    check_safe("def f(x):\n    return x * 2")


# -- banned imports -------------------------------------------------------


@pytest.mark.parametrize(
    "src",
    [
        "import os",
        "import subprocess",
        "import socket",
        "import urllib.request",
        "import requests",
        "from os import system",
        "from subprocess import Popen",
        "import sys",  # not in ALLOWED_IMPORTS
    ],
)
def test_banned_imports_rejected(src: str) -> None:
    with pytest.raises(UnsafeASTError, match="disallowed"):
        check_safe(src)


def test_star_imports_rejected() -> None:
    with pytest.raises(UnsafeASTError, match="star"):
        check_safe("from numpy import *")


# -- banned name lookups --------------------------------------------------


@pytest.mark.parametrize(
    "src",
    [
        "eval('1+1')",
        "exec('print(1)')",
        "compile('1+1', '<s>', 'eval')",
        "open('/etc/passwd')",
        "input()",
        "globals()",
        "__import__('os')",
        "getattr(x, 'y')",
    ],
)
def test_banned_names_rejected(src: str) -> None:
    with pytest.raises(UnsafeASTError, match="disallowed"):
        check_safe(src)


# -- banned attribute access ----------------------------------------------


@pytest.mark.parametrize(
    "src",
    [
        "x.__class__",
        "x.__bases__",
        "x.__subclasses__()",
        "x.__globals__",
        "x.__builtins__",
        "x.__dict__",
        "(()).__class__.__bases__",  # the classic sandbox escape
    ],
)
def test_banned_attrs_rejected(src: str) -> None:
    with pytest.raises(UnsafeASTError, match="disallowed"):
        check_safe(src)


# -- syntax errors propagate --------------------------------------------


def test_syntax_error_wrapped() -> None:
    with pytest.raises(UnsafeASTError, match="syntax"):
        check_safe("def x(:")


# -- ALLOWED_IMPORTS public API ------------------------------------------


def test_allowed_imports_set_is_immutable() -> None:
    """ALLOWED_IMPORTS should be a frozenset so callers can't mutate it."""
    assert isinstance(ALLOWED_IMPORTS, frozenset)
    with pytest.raises(AttributeError):
        ALLOWED_IMPORTS.add("os")  # type: ignore[attr-defined]


# -- Phase 5 review issue #E.1: dangerous module names in scope ----------


@pytest.mark.parametrize(
    "src",
    [
        "@os.path.join\ndef f(): pass",            # decorator using os
        "x = sys.argv",                             # direct sys lookup
        "subprocess.run(['ls'])",                   # direct subprocess
        "y = pathlib.Path('/etc/passwd')",          # pathlib name lookup
        "shutil.rmtree('/')",                        # shutil
        "z = pickle.loads(blob)",                    # pickle
        "ctypes.CDLL('libc.so.6')",                  # ctypes
    ],
)
def test_dangerous_module_names_blocked(src: str) -> None:
    """Module names like os / sys / subprocess can't appear as Name
    lookups even if they're somehow in scope without an import.
    Belt-and-suspenders for the import-side allowlist."""
    with pytest.raises(UnsafeASTError, match="disallowed"):
        check_safe(src)
