"""Table renderer — markdown + CSV + xlsx outputs from a structured spec.

The model authors the data structure; this renderer maps it to all
three downstream formats. The Chat tab's "Compare X and Y in a table"
flow renders markdown by default and offers CSV / xlsx download
buttons.

Public API:

- ``TableSpec`` — column-major or row-major data spec.
- ``render_markdown(spec)`` — markdown table string.
- ``render_csv(spec)`` — CSV string.
- ``render_xlsx(spec, out_path)`` — write a styled .xlsx file.
- ``render_table(spec)`` — convenience: returns dict of all three.
"""

from __future__ import annotations

import csv
import io
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator

MAX_ROWS = 1000  # render-side cap; oversized tables should pre-trim
MAX_COLS = 50


class TableSpec(BaseModel):
    """Structured table data.

    Attributes:
        columns: ordered list of column headers.
        rows: list of rows; each row is a list of cell values matching
            ``columns`` length. Cells can be str/int/float/bool/None.
        title: optional table title (rendered above the markdown table).
        footnote: optional one-line footnote (rendered below).
    """

    columns: list[str] = Field(..., min_length=1)
    rows: list[list[Any]] = Field(default_factory=list)
    title: str = ""
    footnote: str = ""

    @field_validator("columns")
    @classmethod
    def _check_cols(cls, v: list[str]) -> list[str]:
        if len(v) > MAX_COLS:
            raise ValueError(f"too many columns ({len(v)}); max is {MAX_COLS}")
        return v

    @field_validator("rows")
    @classmethod
    def _check_rows(cls, v: list[list[Any]]) -> list[list[Any]]:
        if len(v) > MAX_ROWS:
            raise ValueError(f"too many rows ({len(v)}); max is {MAX_ROWS}")
        return v


def _cell(v: Any) -> str:
    """Render one cell as a string, escaping pipe-characters in markdown."""
    if v is None:
        return ""
    s = str(v)
    return s.replace("|", "\\|")


def render_markdown(spec: TableSpec) -> str:
    """Return a GFM markdown table."""
    width = len(spec.columns)
    header = "| " + " | ".join(_cell(c) for c in spec.columns) + " |"
    sep = "| " + " | ".join("---" for _ in range(width)) + " |"
    body_rows: list[str] = []
    for row in spec.rows:
        # Pad / trim to column width.
        padded = list(row[:width]) + [""] * max(0, width - len(row))
        body_rows.append("| " + " | ".join(_cell(c) for c in padded) + " |")

    parts: list[str] = []
    if spec.title:
        parts.append(f"**{spec.title}**\n")
    parts.append(header)
    parts.append(sep)
    parts.extend(body_rows)
    if spec.footnote:
        parts.append(f"\n_{spec.footnote}_")
    return "\n".join(parts)


def render_csv(spec: TableSpec) -> str:
    """Return CSV text. Title / footnote are dropped (CSV is data only)."""
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(spec.columns)
    for row in spec.rows:
        # CSV writer handles quoting; we just need to coerce types.
        writer.writerow(["" if v is None else v for v in row])
    return buf.getvalue()


def render_xlsx(spec: TableSpec, out_path: Path | str) -> Path:
    """Write a .xlsx file with column headers bolded.

    Requires openpyxl (already in the [ingest] extra; available in any
    install that runs the existing converters).
    """
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font
    except ImportError as e:
        raise RuntimeError(
            "openpyxl is required for xlsx rendering; install via "
            "pip install -e \".[ingest]\""
        ) from e

    wb = Workbook()
    ws = wb.active
    ws.title = spec.title[:31] if spec.title else "Sheet1"  # Excel cap

    # Header row, bold.
    ws.append(list(spec.columns))
    for cell in ws[1]:
        cell.font = Font(bold=True)

    for row in spec.rows:
        ws.append(["" if v is None else v for v in row])

    out = Path(out_path).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    wb.save(out)
    return out


def render_table(spec: TableSpec) -> dict[str, str]:
    """Render markdown + csv at once; useful for the Chat tab's combined
    output. Caller passes ``out_path`` to ``render_xlsx`` separately when
    needed."""
    return {
        "markdown": render_markdown(spec),
        "csv": render_csv(spec),
    }
