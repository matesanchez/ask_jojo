"""Converter dispatch by file extension.

New formats: add an entry to `CONVERTERS`, implement `convert(path) -> str`
in a sibling module. The text tier (.md / .txt) is the fallback — any file
whose extension isn't mapped but whose bytes decode as UTF-8 is treated as
plain text. Binary files with unknown extensions raise `ConverterNotFound`
and the caller decides what to do (skip, store-as-binary, flag for review).
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path


class ConverterNotFound(Exception):
    """Raised when no converter matches a file's extension and it isn't text."""


# Extension (lowercase, no dot) → converter callable returning a markdown string.
CONVERTERS: dict[str, Callable[[Path], str]] = {}


def _register(ext: str, fn: Callable[[Path], str]) -> None:
    CONVERTERS[ext.lower().lstrip(".")] = fn


def is_supported(path: Path | str) -> bool:
    """Return True if the extension has a dedicated converter *or* is plain text."""
    ext = Path(path).suffix.lower().lstrip(".")
    return ext in CONVERTERS or ext in {"md", "markdown", "txt", "text", ""}


def convert(path: Path | str) -> str:
    """Convert a file to markdown. Raises ConverterNotFound if unsupported."""
    p = Path(path)
    ext = p.suffix.lower().lstrip(".")
    if ext in CONVERTERS:
        return CONVERTERS[ext](p)
    if ext in {"md", "markdown", "txt", "text", ""}:
        from jojo_ingest.converters.text_convert import convert_text

        return convert_text(p)
    raise ConverterNotFound(f"No converter for extension '.{ext}' ({p})")


# Lazy registration — import modules on first dispatch so missing optional
# deps don't break the common import path.
def _install_registry() -> None:
    from jojo_ingest.converters.docx_convert import convert_docx
    from jojo_ingest.converters.pdf_convert import convert_pdf
    from jojo_ingest.converters.pptx_convert import convert_pptx
    from jojo_ingest.converters.xlsx_convert import convert_xlsx

    _register("docx", convert_docx)
    _register("pptx", convert_pptx)
    _register("xlsx", convert_xlsx)
    _register("pdf", convert_pdf)


_install_registry()
