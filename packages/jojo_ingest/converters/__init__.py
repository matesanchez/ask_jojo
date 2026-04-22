"""File-format → markdown converters used by all connectors.

Dispatch lives in `dispatch.convert()`. Each converter returns a markdown
string; binary-only content (images, videos) returns an empty body and the
caller decides whether to keep the file or skip it.

The goal is "good enough to absorb" — we do NOT round-trip formatting
perfectly. Headings, lists, tables, and paragraph breaks must survive;
visual styling (colors, fonts, margins) is out of scope.
"""

from jojo_ingest.converters.dispatch import (
    CONVERTERS,
    ConverterNotFound,
    convert,
    is_supported,
)

__all__ = ["CONVERTERS", "ConverterNotFound", "convert", "is_supported"]
