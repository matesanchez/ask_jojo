"""matplotlib / Plotly sandbox for Phase 5 rich outputs.

PLAN.md Section 6 Phase 5 contract:
  "LLM generates a data spec plus a plot-type choice, and a fixed
  Python function actually draws the chart. We never run arbitrary
  LLM code. The sandboxed subprocess has resource limits (30s CPU,
  512 MB RAM), no network, bind-mounted working dir erased per run,
  allowlist imports (numpy, pandas, matplotlib, seaborn, plotly).
  Anything else fails closed."

This package is the *deterministic* half of that contract. The model
produces a typed JSON spec (validated against ``spec.PlotSpec``); a
fixed Python function in ``render.py`` maps the spec to matplotlib
or Plotly calls; ``runner.py`` runs the render in a subprocess with
resource limits. ``ast_guard.py`` is a belt-and-suspenders check for
any future "user-pasted custom plot" escape hatch.

Public API:

- ``PlotSpec``       — Pydantic schema for the data spec.
- ``RenderResult``   — return type with status + artifact path / data
                       + error detail.
- ``run(spec, ...)`` — orchestrate the full sandbox flow.
- ``available_plot_types()`` — for the UI's plot-type selector.

The model never calls ``run`` directly; it returns a ``PlotSpec``
that the synthesis path passes to ``run``. Spec validation, AST
checking, and resource limits all happen in the parent process
before the subprocess is spawned.
"""

from .spec import (
    PlotSpec,
    PlotType,
    available_plot_types,
)
from .runner import RenderResult, run

__all__ = [
    "PlotSpec",
    "PlotType",
    "RenderResult",
    "available_plot_types",
    "run",
]
