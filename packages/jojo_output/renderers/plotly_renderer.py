"""Plotly HTML-fragment renderer.

Builds a self-contained HTML snippet that renders an interactive Plotly
chart using the CDN bundle.  No ``import plotly`` — all trace and layout
dicts are plain Python dicts serialised with ``json.dumps``.

Public API:

- ``PlotlySpec``           — Pydantic model describing the chart.
- ``render_plotly(spec)``  — returns an HTML fragment string.
- ``available_plotly_themes()`` — list of valid template names.
"""

from __future__ import annotations

import json
import uuid
from typing import Any, Literal

from pydantic import BaseModel

_PLOTLY_CDN = "https://cdn.plot.ly/plotly-2.35.2.min.js"


class PlotlySpec(BaseModel):
    """Spec for the Plotly renderer.

    Attributes:
        plot_type:        Plotly trace type (mapped to Plotly trace ``type``).
        title:            Optional chart title.
        x_label:          Optional x-axis label.
        y_label:          Optional y-axis label.
        series:           List of ``{label, x, y}`` dicts for bar/line/scatter.
        heatmap_matrix:   2-D float matrix for the heatmap trace.
        heatmap_x_labels: Column labels for the heatmap.
        heatmap_y_labels: Row labels for the heatmap.
        values:           Flat list of values for histogram / box traces.
        labels:           Slice labels for pie traces.
        width_px:         Container width in pixels.
        height_px:        Container height in pixels.
        theme:            Plotly template name (``layout.template``).
    """

    plot_type: Literal["bar", "line", "scatter", "pie", "heatmap", "histogram", "box"]
    title: str | None = None
    x_label: str | None = None
    y_label: str | None = None
    series: list[dict[str, Any]] = []
    heatmap_matrix: list[list[float]] | None = None
    heatmap_x_labels: list[str] | None = None
    heatmap_y_labels: list[str] | None = None
    values: list[float] | None = None
    labels: list[str] | None = None
    width_px: int = 700
    height_px: int = 450
    theme: str = "plotly"


def available_plotly_themes() -> list[str]:
    """Return the list of supported Plotly template names."""
    return [
        "plotly",
        "plotly_white",
        "plotly_dark",
        "ggplot2",
        "seaborn",
        "simple_white",
    ]


def _build_traces(spec: PlotlySpec) -> list[dict[str, Any]]:
    """Construct the Plotly trace array from the spec."""
    pt = spec.plot_type

    if pt == "bar":
        traces = []
        for s in spec.series:
            traces.append(
                {"type": "bar", "name": s.get("label", ""), "x": s.get("x", []), "y": s.get("y", [])}
            )
        return traces or [{"type": "bar", "x": [], "y": []}]

    if pt == "line":
        traces = []
        for s in spec.series:
            traces.append(
                {
                    "type": "scatter",
                    "mode": "lines",
                    "name": s.get("label", ""),
                    "x": s.get("x", []),
                    "y": s.get("y", []),
                }
            )
        return traces or [{"type": "scatter", "mode": "lines", "x": [], "y": []}]

    if pt == "scatter":
        traces = []
        for s in spec.series:
            traces.append(
                {
                    "type": "scatter",
                    "mode": "markers",
                    "name": s.get("label", ""),
                    "x": s.get("x", []),
                    "y": s.get("y", []),
                }
            )
        return traces or [{"type": "scatter", "mode": "markers", "x": [], "y": []}]

    if pt == "pie":
        trace: dict[str, Any] = {"type": "pie"}
        if spec.values is not None:
            trace["values"] = spec.values
        if spec.labels is not None:
            trace["labels"] = spec.labels
        return [trace]

    if pt == "heatmap":
        trace = {"type": "heatmap"}
        if spec.heatmap_matrix is not None:
            trace["z"] = spec.heatmap_matrix
        if spec.heatmap_x_labels is not None:
            trace["x"] = spec.heatmap_x_labels
        if spec.heatmap_y_labels is not None:
            trace["y"] = spec.heatmap_y_labels
        return [trace]

    if pt == "histogram":
        trace = {"type": "histogram"}
        if spec.values is not None:
            trace["x"] = spec.values
        return [trace]

    if pt == "box":
        trace = {"type": "box"}
        if spec.values is not None:
            trace["y"] = spec.values
        return [trace]

    # Fallback (should not be reached — Pydantic guards the Literal).
    return []


def _build_layout(spec: PlotlySpec) -> dict[str, Any]:
    """Construct the Plotly layout dict from the spec."""
    layout: dict[str, Any] = {
        "template": spec.theme,
        "width": spec.width_px,
        "height": spec.height_px,
    }
    if spec.title:
        layout["title"] = {"text": spec.title}
    if spec.x_label:
        layout["xaxis"] = {"title": {"text": spec.x_label}}
    if spec.y_label:
        layout["yaxis"] = {"title": {"text": spec.y_label}}
    return layout


def render_plotly(spec: PlotlySpec) -> str:
    """Render ``spec`` to a self-contained HTML fragment.

    The fragment contains:
    - A ``<div>`` container sized to ``spec.width_px`` × ``spec.height_px``.
    - A ``<script>`` tag loading Plotly from CDN.
    - An inline ``<script>`` that calls ``Plotly.newPlot`` with the
      trace array and layout computed from the spec.

    Returns:
        HTML string (not a full page — intended for injection into an
        existing document or wiki page body).
    """
    uid = uuid.uuid4().hex[:8]
    div_id = f"plotly-{uid}"

    traces = _build_traces(spec)
    layout = _build_layout(spec)

    # Use json.dumps so the JS receives valid JSON (double quotes, true/false/null).
    # Replace "</script" to prevent premature tag closing inside the inline script.
    data_json = json.dumps(traces).replace("</", "<\\/")
    layout_json = json.dumps(layout).replace("</", "<\\/")

    return (
        f'<div id="{div_id}" style="width:{spec.width_px}px;height:{spec.height_px}px;"></div>\n'
        f'<script src="{_PLOTLY_CDN}" charset="utf-8"></script>\n'
        "<script>\n"
        "  (function() {\n"
        f"    var data = {data_json};\n"
        f"    var layout = {layout_json};\n"
        f'    Plotly.newPlot(\'{div_id}\', data, layout, {{responsive: true}});\n'
        "  })();\n"
        "</script>"
    )
