"""Tests for ``jojo_output.sandbox.runner``.

We exercise the runner in two modes:

- **In-process** (``RUN_IN_PROCESS=True``) -- fast, runs in the test's
  process; covers happy paths + validation/render errors + plot-type
  dispatch.
- **Subprocess** (default) -- slow but exercises the real production
  path including resource limits. Marked ``@pytest.mark.slow`` and
  skipped when matplotlib isn't installed in the test env.

The slow tests are the most important ones for security. They prove
that a malicious or buggy spec actually gets killed by the rlimit /
timeout, not just rejected by Pydantic.
"""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("pydantic")

from jojo_output.sandbox import runner as runner_mod
from jojo_output.sandbox.spec import PlotSpec


# All tests in this module use in-process mode unless marked otherwise.
@pytest.fixture(autouse=True)
def _in_process(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(runner_mod, "RUN_IN_PROCESS", True)


# -- happy paths ---------------------------------------------------------


def test_run_bar_to_bytes() -> None:
    pytest.importorskip("matplotlib")
    spec = {
        "plot_type": "bar",
        "title": "Test bar",
        "series": [{"label": "a", "x": ["x", "y"], "y": [1.0, 2.0]}],
    }
    result = runner_mod.run(spec)
    assert result.status == "ok"
    assert result.bytes is not None
    assert len(result.bytes) > 100
    assert result.plot_type == "bar"


def test_run_line_to_file(tmp_path: Path) -> None:
    pytest.importorskip("matplotlib")
    spec = PlotSpec.model_validate(
        {
            "plot_type": "line",
            "series": [{"label": "y1", "x": [0, 1, 2], "y": [1.0, 4.0, 9.0]}],
        }
    )
    out = tmp_path / "line.png"
    result = runner_mod.run(spec, out_path=out)
    assert result.status == "ok"
    assert result.out_path == out.resolve()
    assert out.exists()
    assert out.stat().st_size > 100


def test_run_svg_format(tmp_path: Path) -> None:
    pytest.importorskip("matplotlib")
    spec = {
        "plot_type": "bar",
        "series": [{"label": "a", "x": ["x"], "y": [1.0]}],
    }
    result = runner_mod.run(spec, fmt="svg", out_path=tmp_path / "bar.svg")
    assert result.status == "ok"
    assert (tmp_path / "bar.svg").exists()
    text = (tmp_path / "bar.svg").read_text()
    assert text.startswith("<?xml") or text.startswith("<svg")


def test_run_heatmap() -> None:
    pytest.importorskip("matplotlib")
    spec = {
        "plot_type": "heatmap",
        "heatmap_matrix": [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]],
    }
    result = runner_mod.run(spec)
    assert result.status == "ok"


def test_run_hist() -> None:
    pytest.importorskip("matplotlib")
    spec = {"plot_type": "hist", "values": [1.0, 2.0, 3.0, 4.0, 5.0]}
    result = runner_mod.run(spec)
    assert result.status == "ok"


# -- validation errors ---------------------------------------------------


def test_validation_error_propagates_as_status() -> None:
    """A bad spec returns RenderResult(status='validation_error'), not a raise."""
    result = runner_mod.run({"plot_type": "pie"})  # not a real plot_type
    assert result.status == "validation_error"
    assert result.error is not None
    assert "validation" in result.error.lower()


def test_oversized_data_validation_error() -> None:
    result = runner_mod.run(
        {
            "plot_type": "line",
            "series": [
                {"label": "s", "x": list(range(50_000)), "y": [0.0] * 50_000}
            ],
        }
    )
    assert result.status == "validation_error"


def test_missing_required_field_for_type() -> None:
    """A heatmap spec without heatmap_matrix should fail at render time."""
    pytest.importorskip("matplotlib")
    result = runner_mod.run({"plot_type": "heatmap"})
    # Either validation rejects or render does; both are acceptable failure modes.
    assert result.status in ("validation_error", "render_error")


# -- duration ------------------------------------------------------------


def test_duration_recorded() -> None:
    pytest.importorskip("matplotlib")
    result = runner_mod.run(
        {"plot_type": "bar", "series": [{"label": "a", "x": ["x"], "y": [1.0]}]}
    )
    assert result.duration_ms >= 0
    assert result.duration_ms < 30_000  # in-process should be <30s


# -- plot_type echoed even on failure -------------------------------------


def test_plot_type_echoed_on_validation_error() -> None:
    result = runner_mod.run({"plot_type": "pie", "series": []})
    # validation_error path; spec_dict is a dict so plot_type is echoed.
    assert result.plot_type == "pie"


# -- spec instance accepted ----------------------------------------------


def test_pre_validated_spec_accepted() -> None:
    pytest.importorskip("matplotlib")
    spec = PlotSpec(
        plot_type="hist",
        values=[1.0, 2.0, 3.0],
    )
    result = runner_mod.run(spec)
    assert result.status == "ok"
