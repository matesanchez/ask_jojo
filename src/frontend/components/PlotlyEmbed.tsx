"use client";

/**
 * PlotlyEmbed -- safely renders a Plotly HTML fragment inside an iframe.
 *
 * The fragment (from POST /api/output/render) typically contains a
 * <div id="plotly-..."> and a <script> that calls Plotly.newPlot(). Running
 * it inside a sandboxed iframe prevents script access to the parent document
 * while still letting Plotly's own scripts execute.
 *
 * sandbox="allow-scripts":
 *   - Allows the embedded <script> to run (Plotly initialisation).
 *   - Denies same-origin access, form submission, top navigation, popups.
 *   This is the minimal set needed for Plotly to render its chart.
 *
 * Usage:
 *
 *   <PlotlyEmbed html={htmlFragmentFromApi} />
 *   <PlotlyEmbed html={page.body} className="my-chart" />
 */

interface PlotlyEmbedProps {
  /** The HTML fragment from POST /api/output/render or a wiki outputs/ page body. */
  html: string;
  className?: string;
}

export default function PlotlyEmbed({ html, className }: PlotlyEmbedProps) {
  return (
    <iframe
      srcDoc={html}
      sandbox="allow-scripts"
      title="Plotly chart"
      className={className}
      style={{ width: "100%", height: "450px", border: "none" }}
    />
  );
}
