"""DOCX → markdown via `mammoth`.

Mammoth preserves headings, lists, and basic table structure out of the box.
Custom style-map entries handle Nurix-specific heading conventions; add more
here as we discover styles that don't round-trip cleanly.

Images embedded in the .docx are deliberately discarded at this stage —
Phase 1 stores the original file path in the manifest, and a Phase 2
enhancement will extract and link images into `ask_jojo_raw/<source>/assets/`.
"""

from __future__ import annotations

from pathlib import Path

import mammoth

# Default style-map additions. Extend as needed.
_STYLE_MAP = """
p[style-name='Title'] => h1:fresh
p[style-name='Subtitle'] => h2:fresh
p[style-name='Heading 1'] => h1:fresh
p[style-name='Heading 2'] => h2:fresh
p[style-name='Heading 3'] => h3:fresh
p[style-name='Heading 4'] => h4:fresh
p[style-name='Quote'] => blockquote:fresh
""".strip()


def convert_docx(path: Path) -> str:
    with path.open("rb") as fh:
        result = mammoth.convert_to_markdown(fh, style_map=_STYLE_MAP)
    # mammoth returns a Result(value, messages) — we ignore warnings here,
    # but a future hook could surface them into the ingest log.
    return result.value
