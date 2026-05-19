"""Tests for ``jojo_output.sandbox.spec``.

The spec is the trust boundary: anything that's not validated here gets
rejected before the subprocess is spawned. These tests pin every
validation rule.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

# Skip the whole module when pydantic isn't installed (e.g. pre-install
# dev environments). The Phase 5 [output] extra includes pydantic via
# fastapi or directly; in the dev shell we want graceful degradation.
pytest.importorskip("pydantic")

from jojo_output.sandbox.spec import PlotSpec, available_plot_types

# -- happy paths ---------------------------------------------------------


def test_minimal_bar_spec_validates() -> None:
    spec = PlotSpec.model_validate(
        {
            "plot_type": "bar",
            "series": [{"label": "s1", "x": ["a", "b"], "y": [1.0, 2.0]}],
        }
    )
    assert spec.plot_type == "bar"
    assert len(spec.series) == 1


def test_heatmap_spec_validates() -> None:
    spec = PlotSpec.model_validate(
        {
            "plot_type": "heatmap",
            "heatmap_matrix": [[1.0, 2.0], [3.0, 4.0]],
            "heatmap_x_labels": ["a", "b"],
            "heatmap_y_labels": ["c", "d"],
        }
    )
    assert spec.heatmap_matrix == [[1.0, 2.0], [3.0, 4.0]]


def test_hist_spec_validates() -> None:
    spec = PlotSpec.model_validate({"plot_type": "hist", "values": [1.0, 2.0, 3.0]})
    assert spec.values is not None
    assert len(spec.values) == 3


# -- size limits enforced ------------------------------------------------


def test_too_many_data_points_rejected() -> None:
    with pytest.raises(Exception, match="max is 10000|y has 100001"):
        PlotSpec.model_validate(
            {
                "plot_type": "line",
                "series": [
                    {"label": "s1", "x": list(range(100_001)), "y": [0.0] * 100_001}
                ],
            }
        )


def test_too_many_series_rejected() -> None:
    series = [{"label": f"s{i}", "x": [], "y": []} for i in range(50)]
    with pytest.raises(Exception, match="too many series"):
        PlotSpec.model_validate({"plot_type": "line", "series": series})


def test_oversized_heatmap_rejected() -> None:
    matrix = [[0.0] * 200 for _ in range(200)]  # 40k cells
    with pytest.raises(Exception, match="max is 10000"):
        PlotSpec.model_validate(
            {"plot_type": "heatmap", "heatmap_matrix": matrix}
        )


def test_ragged_heatmap_rejected() -> None:
    with pytest.raises(Exception, match="ragged"):
        PlotSpec.model_validate(
            {"plot_type": "heatmap", "heatmap_matrix": [[1.0, 2.0], [3.0]]}
        )


def test_long_label_rejected() -> None:
    with pytest.raises(ValidationError):
        PlotSpec.model_validate({"plot_type": "bar", "title": "x" * 500})


# -- bad plot_type rejected ----------------------------------------------


def test_unknown_plot_type_rejected() -> None:
    with pytest.raises(ValidationError):
        PlotSpec.model_validate({"plot_type": "pie"})  # not in the literal


# -- defaults ------------------------------------------------------------


def test_defaults_reasonable() -> None:
    spec = PlotSpec(plot_type="bar")
    assert spec.width_inches == 8.0
    assert spec.height_inches == 5.0
    assert spec.dpi == 120
    assert spec.legend is True
    assert spec.grid is True
    assert spec.log_y is False
    assert spec.bins == 20


def test_dpi_clamped() -> None:
    with pytest.raises(ValidationError):
        PlotSpec(plot_type="bar", dpi=10)
    with pytest.raises(ValidationError):
        PlotSpec(plot_type="bar", dpi=10000)


# -- available_plot_types ------------------------------------------------


def test_available_plot_types_complete() -> None:
    types = available_plot_types()
    assert "bar" in types
    assert "line" in types
    assert "heatmap" in types
    assert len(types) == 7
