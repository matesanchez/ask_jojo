"""Fixed plotting functions — the only Python the sandbox runs.

The model produces a ``PlotSpec`` (validated by ``spec.py``); this
module dispatches on ``spec.plot_type`` and calls a fixed matplotlib
function. There is no eval, no exec, no LLM-authored Python anywhere
in this path.

Public API:

- ``render_to_png(spec, out_path)`` — render a PlotSpec to a PNG file.
- ``render_to_svg(spec, out_path)`` — same, SVG.
- ``render_to_bytes(spec, fmt='png')`` — in-memory render for
                                          response-streaming endpoints.

Imports are deliberately limited to numpy + matplotlib + (optionally)
pandas + seaborn. plotly is handled by a sibling renderer that
returns HTML rather than a PNG; the matplotlib path is the one that
runs in the resource-limited subprocess.
"""

from __future__ import annotations

import io
from pathlib import Path
from typing import Any

# Import matplotlib inside functions so the module can be imported (and
# tests collected) on systems where matplotlib isn't installed yet.
# Real renders fail with a clear ImportError.


def _import_matplotlib():
    try:
        import matplotlib
        matplotlib.use("Agg")  # non-interactive backend; no display required
        import matplotlib.pyplot as plt
        return matplotlib, plt
    except ImportError as e:
        raise RuntimeError(
            "matplotlib is required for sandbox rendering. "
            "Install via: pip install -e \".[output]\""
        ) from e


def _render_bar(plt: Any, spec: Any, horizontal: bool) -> None:
    if not spec.series:
        raise ValueError("bar plot requires at least one series")
    width = 0.8 / max(len(spec.series), 1)
    for i, s in enumerate(spec.series):
        # Numeric x positions for grouped bars.
        positions = [j + i * width for j in range(len(s.x))]
        if horizontal:
            plt.barh(positions, s.y, height=width, label=s.label)
        else:
            plt.bar(positions, s.y, width=width, label=s.label)
    # Labels: use the first series' x as tick labels.
    first = spec.series[0]
    tick_positions = [j + (len(spec.series) - 1) * width / 2 for j in range(len(first.x))]
    if horizontal:
        plt.yticks(tick_positions, first.x)
    else:
        plt.xticks(tick_positions, first.x, rotation=30, ha="right")


def _render_line(plt: Any, spec: Any) -> None:
    if not spec.series:
        raise ValueError("line plot requires at least one series")
    for s in spec.series:
        plt.plot(s.x, s.y, label=s.label, marker="o" if len(s.x) <= 50 else "")


def _render_scatter(plt: Any, spec: Any) -> None:
    if not spec.series:
        raise ValueError("scatter plot requires at least one series")
    for s in spec.series:
        # Coerce string x values to indices for scatter (matplotlib is fine
        # with mixed types but axis labels get noisy).
        xs = list(range(len(s.x))) if s.x and isinstance(s.x[0], str) else s.x
        plt.scatter(xs, s.y, label=s.label, alpha=0.7)


def _render_hist(plt: Any, spec: Any) -> None:
    if not spec.values:
        raise ValueError("hist plot requires `values`")
    plt.hist(spec.values, bins=spec.bins)


def _render_box(plt: Any, spec: Any) -> None:
    if not spec.series:
        raise ValueError("box plot requires at least one series")
    data = [s.y for s in spec.series]
    labels = [s.label for s in spec.series]
    plt.boxplot(data, labels=labels)


def _render_heatmap(plt: Any, spec: Any) -> None:
    if not spec.heatmap_matrix:
        raise ValueError("heatmap requires `heatmap_matrix`")
    import numpy as np
    arr = np.array(spec.heatmap_matrix)
    im = plt.imshow(arr, aspect="auto", cmap="viridis")
    if spec.heatmap_x_labels:
        plt.xticks(range(arr.shape[1]), spec.heatmap_x_labels, rotation=30, ha="right")
    if spec.heatmap_y_labels:
        plt.yticks(range(arr.shape[0]), spec.heatmap_y_labels)
    plt.colorbar(im)


_RENDERERS = {
    "bar":     lambda plt, spec: _render_bar(plt, spec, horizontal=False),
    "barh":    lambda plt, spec: _render_bar(plt, spec, horizontal=True),
    "line":    _render_line,
    "scatter": _render_scatter,
    "hist":    _render_hist,
    "box":     _render_box,
    "heatmap": _render_heatmap,
}


def _render_to_buffer(spec: Any, fmt: str) -> bytes:
    matplotlib, plt = _import_matplotlib()
    fig = plt.figure(figsize=(spec.width_inches, spec.height_inches), dpi=spec.dpi)
    try:
        renderer = _RENDERERS.get(spec.plot_type)
        if renderer is None:
            raise ValueError(f"unsupported plot_type: {spec.plot_type!r}")
        renderer(plt, spec)

        if spec.title:
            plt.title(spec.title)
        if spec.x_label:
            plt.xlabel(spec.x_label)
        if spec.y_label:
            plt.ylabel(spec.y_label)
        if spec.legend and (spec.series or spec.plot_type == "scatter"):
            plt.legend()
        if spec.grid:
            plt.grid(True, alpha=0.3)
        if spec.log_y:
            plt.yscale("log")
        plt.tight_layout()

        buf = io.BytesIO()
        fig.savefig(buf, format=fmt)
        return buf.getvalue()
    finally:
        plt.close(fig)


def render_to_png(spec: Any, out_path: Path | str) -> Path:
    """Render ``spec`` to ``out_path`` as PNG. Returns the absolute path."""
    out = Path(out_path).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(_render_to_buffer(spec, "png"))
    return out


def render_to_svg(spec: Any, out_path: Path | str) -> Path:
    out = Path(out_path).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(_render_to_buffer(spec, "svg"))
    return out


def render_to_bytes(spec: Any, fmt: str = "png") -> bytes:
    """In-memory render. Returns the raw bytes for the chosen format."""
    if fmt not in ("png", "svg"):
        raise ValueError(f"unsupported format: {fmt!r}; use 'png' or 'svg'")
    return _render_to_buffer(spec, fmt)
