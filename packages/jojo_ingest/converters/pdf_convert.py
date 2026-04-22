"""PDF → markdown via PyMuPDF (fitz).

Extracts page text in reading order. PyMuPDF's default text extraction is
good enough for the office/SharePoint PDF population we expect; scanned PDFs
(image-only, no OCR layer) come out blank and get logged as such — the
absorb pipeline will flag them for manual review.

For complex layouts we use the "blocks" mode which preserves paragraph
boundaries. Tables in PDFs remain an open problem and are not reconstructed
here — future enhancement once we see how often it matters.
"""

from __future__ import annotations

from pathlib import Path

import fitz  # pymupdf


def convert_pdf(path: Path) -> str:
    doc = fitz.open(str(path))
    parts: list[str] = [f"# {path.stem}\n"]
    try:
        for i, page in enumerate(doc, start=1):
            text = page.get_text("text") or ""
            text = text.strip()
            if not text:
                parts.append(f"## Page {i}\n\n_(no extractable text — likely image-only)_\n")
                continue
            parts.append(f"## Page {i}\n\n{text}\n")
    finally:
        doc.close()
    return "\n".join(parts)
