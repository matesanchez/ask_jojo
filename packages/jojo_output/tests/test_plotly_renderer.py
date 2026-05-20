"""Tests for the Plotly HTML-fragment renderer.

Six test cases covering the main trace types, layout fields, and Pydantic
validation.  No real Plotly library is required — the renderer builds plain
Python dicts and serialises them with json.dumps.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from jojo_output.renderers.plotly_renderer import (
    PlotlySpec,
    available_plotly_themes,
    render_plotly,
)

# ---------------------------------------------------------------- bar


def test_bar_chart_renders_div_id() -> None:
    spec = PlotlySpec(
        plot_type="bar",
        title="Bar Chart",
        series=[{"label": "Group A", "x": ["x1", "x2"], "y": [1.0, 2.0]}],
    )
    html = render_plotly(spec)
    assert '<div id="plotly-' in html
    assert "Plotly.newPlot(" in html


def test_bar_chart_contains_type_bar() -> None:
    spec = PlotlySpec(
        plot_type="bar",
        series=[{"label": "a", "x": [1, 2], "y": [10, 20]}],
    )
    html = render_plotly(spec)
    assert '"type": "bar"' in html


# ---------------------------------------------------------------- line


def test_line_chart_renders_mode_lines() -> None:
    spec = PlotlySpec(
        plot_type="line",
        series=[{"label": "Series 1", "x": [0, 1, 2], "y": [0, 1, 4]}],
    )
    html = render_plotly(spec)
    assert '"mode": "lines"' in html


# ---------------------------------------------------------------- heatmap


def test_heatmap_renders_type_heatmap() -> None:
    spec = PlotlySpec(
        plot_type="heatmap",
        heatmap_matrix=[[1.0, 2.0], [3.0, 4.0]],
        heatmap_x_labels=["A", "B"],
        heatmap_y_labels=["Row1", "Row2"],
    )
    html = render_plotly(spec)
    assert '"type": "heatmap"' in html


# ---------------------------------------------------------------- pie


def test_pie_chart_renders_type_pie() -> None:
    spec = PlotlySpec(
        plot_type="pie",
        values=[30.0, 40.0, 30.0],
        labels=["alpha", "beta", "gamma"],
    )
    html = render_plotly(spec)
    assert '"type": "pie"' in html


# ---------------------------------------------------------------- histogram


def test_histogram_renders_type_histogram() -> None:
    spec = PlotlySpec(
        plot_type="histogram",
        values=[1.0, 2.0, 2.5, 3.0, 3.0, 4.0],
    )
    html = render_plotly(spec)
    assert '"type": "histogram"' in html


# ---------------------------------------------------------------- box


def test_box_renders_type_box() -> None:
    spec = PlotlySpec(
        plot_type="box",
        values=[1.0, 2.0, 3.0, 4.0, 5.0],
    )
    html = render_plotly(spec)
    assert '"type": "box"' in html


# ---------------------------------------------------------------- layout fields


def test_title_and_axis_labels_in_layout() -> None:
    spec = PlotlySpec(
        plot_type="bar",
        title="My Chart",
        x_label="X Axis",
        y_label="Y Axis",
        series=[{"label": "s", "x": [1], "y": [1]}],
    )
    html = render_plotly(spec)
    assert "My Chart" in html
    assert "X Axis" in html
    assert "Y Axis" in html


def test_unique_div_ids_per_call() -> None:
    spec = PlotlySpec(plot_type="bar")
    html1 = render_plotly(spec)
    html2 = render_plotly(spec)
    # Extract the div id from each call and confirm they differ.
    id1 = html1.split('id="')[1].split('"')[0]
    id2 = html2.split('id="')[1].split('"')[0]
    assert id1 != id2


# ---------------------------------------------------------------- validation


def test_invalid_plot_type_raises_validation_error() -> None:
    with pytest.raises(ValidationError):
        PlotlySpec(plot_type="treemap")  # type: ignore[arg-type]


def test_invalid_plot_type_unknown_string() -> None:
    with pytest.raises(ValidationError):
        PlotlySpec(plot_type="donut")  # type: ignore[arg-type]


# ---------------------------------------------------------------- themes


def test_available_plotly_themes_includes_standard() -> None:
    themes = available_plotly_themes()
    assert "plotly" in themes
    assert "plotly_dark" in themes
    assert "ggplot2" in themes
    assert len(themes) == 6


# ---------------------------------------------------------------- CDN safety


def test_script_tag_not_closed_prematurely_by_title() -> None:
    """A title containing '</script' must not break the HTML fragment."""
    spec = PlotlySpec(
        plot_type="bar",
        title="bad</script>inject",
        series=[],
    )
    html = render_plotly(spec)
    # The raw </script> closing sequence must not appear inside the
    # inline <script> block (it is escaped as <\/).
    # Count opening vs closing script tags: should be exactly 2 opens
    # (<script src=...> and <script>) and 2 closes (</script>).
    assert html.count("</script>") == 2
