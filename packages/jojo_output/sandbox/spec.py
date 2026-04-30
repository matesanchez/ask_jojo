"""Pydantic schema for the plot spec.

The model produces a ``PlotSpec``; the renderer accepts only this shape.
Validation rejects malformed specs in the parent process before any
subprocess is spawned, so the sandbox sees only well-typed input.

Per PLAN.md Section 6 Phase 5, the contract is "data spec plus plot-type
choice" — never arbitrary code. The fields below cover the chart shapes
JoJo Bot answers will need at the start of Phase 5; add new types
deliberately, not opportunistically.

Public types:

- ``PlotType`` — Literal of supported types.
- ``PlotSpec`` — the schema. Pydantic validation enforces the contract.
- ``available_plot_types()`` — for the UI's plot-type selector.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

PlotType = Literal[
    "bar",      # vertical bar chart
    "barh",     # horizontal bar chart
    "line",     # single or multi-series line chart
    "scatter",  # 2D scatter
    "hist",     # histogram (single variable)
    "box",      # boxplot (single or grouped)
    "heatmap",  # 2D matrix as colored cells
]


def available_plot_types() -> list[PlotType]:
    """List supported plot types. UI dropdown source of truth."""
    return ["bar", "barh", "line", "scatter", "hist", "box", "heatmap"]


# Reasonable size caps. The sandbox enforces these *before* spawning the
# subprocess so a huge data array can't OOM the parent process during
# JSON parsing.

MAX_DATA_POINTS = 10_000      # series total length
MAX_SERIES = 32               # for multi-series plots
MAX_LABEL_LEN = 200           # title / axis labels


class _DataSeries(BaseModel):
    """One series in a multi-series plot."""

    label: str = Field(..., max_length=MAX_LABEL_LEN)
    x: list[float | str] = Field(default_factory=list)
    y: list[float] = Field(default_factory=list)

    @field_validator("y")
    @classmethod
    def _check_y(cls, v: list[float]) -> list[float]:
        if len(v) > MAX_DATA_POINTS:
            raise ValueError(f"y has {len(v)} points; max is {MAX_DATA_POINTS}")
        return v

    @field_validator("x")
    @classmethod
    def _check_x(cls, v: list) -> list:
        if len(v) > MAX_DATA_POINTS:
            raise ValueError(f"x has {len(v)} points; max is {MAX_DATA_POINTS}")
        return v


class PlotSpec(BaseModel):
    """The shape the model produces; the only thing the renderer accepts.

    Examples:

    Bar chart::

        PlotSpec(
            plot_type="bar",
            title="CBL-B IC50 by program",
            x_label="Program",
            y_label="IC50 (nM)",
            series=[_DataSeries(label="series-1",
                                x=["NX-1607", "NX-0255"],
                                y=[10.0, 35.0])],
        )

    Heatmap::

        PlotSpec(
            plot_type="heatmap",
            title="Connector x source-type counts",
            heatmap_matrix=[[1426, 0, 0], [0, 18111, 0], [0, 0, 99019]],
            heatmap_x_labels=["drive", "onedrive", "publicdrive"],
            heatmap_y_labels=["sharepoint", "onedrive", "publicdrive"],
        )

    The renderer dispatches on ``plot_type``; fields not relevant to the
    chosen type are simply ignored.
    """

    plot_type: PlotType
    title: str = Field("", max_length=MAX_LABEL_LEN)
    x_label: str = Field("", max_length=MAX_LABEL_LEN)
    y_label: str = Field("", max_length=MAX_LABEL_LEN)

    # Multi-series data (bar / line / scatter / box).
    series: list[_DataSeries] = Field(default_factory=list)

    # Single-variable data (hist).
    values: list[float] | None = None
    bins: int = Field(20, ge=2, le=200)

    # Heatmap-specific.
    heatmap_matrix: list[list[float]] | None = None
    heatmap_x_labels: list[str] | None = None
    heatmap_y_labels: list[str] | None = None

    # Display options.
    width_inches: float = Field(8.0, ge=2.0, le=24.0)
    height_inches: float = Field(5.0, ge=2.0, le=18.0)
    dpi: int = Field(120, ge=72, le=300)
    legend: bool = True
    grid: bool = True
    log_y: bool = False

    @field_validator("series")
    @classmethod
    def _check_series_count(cls, v: list[_DataSeries]) -> list[_DataSeries]:
        if len(v) > MAX_SERIES:
            raise ValueError(f"too many series ({len(v)}); max is {MAX_SERIES}")
        return v

    @field_validator("heatmap_matrix")
    @classmethod
    def _check_heatmap(cls, v: list[list[float]] | None) -> list[list[float]] | None:
        if v is None:
            return v
        if not v:
            raise ValueError("heatmap_matrix is empty")
        first_row_len = len(v[0])
        if first_row_len == 0:
            raise ValueError("heatmap_matrix rows are empty")
        if any(len(row) != first_row_len for row in v):
            raise ValueError("heatmap_matrix is ragged (unequal row lengths)")
        total = len(v) * first_row_len
        if total > MAX_DATA_POINTS:
            raise ValueError(f"heatmap_matrix has {total} cells; max is {MAX_DATA_POINTS}")
        return v

    @field_validator("values")
    @classmethod
    def _check_values(cls, v: list[float] | None) -> list[float] | None:
        if v is not None and len(v) > MAX_DATA_POINTS:
            raise ValueError(f"values has {len(v)} points; max is {MAX_DATA_POINTS}")
        return v
