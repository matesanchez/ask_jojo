"use client";

/**
 * Graph tab -- Phase 7a knowledge-graph visualization.
 *
 *   [ top bar: rebuild | last-rebuild | graphify-or-fallback badge ]
 *   [ iframe (graph.html) | side panel (stats + report) ]
 *
 * Graph tab embeds /api/graph/html in an iframe. When graphify isn't
 * installed, the fallback HTML still renders a minimal SVG view so the
 * tab is usable today; the fallback gets replaced by graphify's
 * interactive D3 view when the install lands.
 *
 * URL params (Phase 7a step 6 -- Chat-tab provenance hand-off):
 *   ?highlight=cbl-b,cbl-b-target,del-screening
 * The query param is parsed and forwarded to the iframe via
 * postMessage so graphify (or our fallback viewer) can highlight the
 * cited slugs.
 */

import { useCallback, useEffect, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";

interface GraphAvailable {
  available: boolean;
  source: "graphify" | "fallback";
}

interface GraphStats {
  node_count: number;
  edge_count: number;
  source: "graphify" | "fallback";
  avg_degree?: number;
  max_degree?: number;
  connected_components?: number;
  orphan_count?: number;
}

interface RebuildResponse {
  status: "ok";
  node_count: number;
  edge_count: number;
  used_fallback: boolean;
  graph_html: string;
  graph_report: string;
}

async function fetchJSON<T>(url: string, init?: RequestInit): Promise<T> {
  const r = await fetch(url, { cache: "no-store", ...init });
  if (!r.ok) {
    throw new Error(`${r.status} ${r.statusText}`);
  }
  return r.json() as Promise<T>;
}

export default function GraphPage() {
  const search = useSearchParams();
  const highlight = search?.get("highlight") ?? "";

  const [available, setAvailable] = useState<GraphAvailable | null>(null);
  const [stats, setStats] = useState<GraphStats | null>(null);
  const [report, setReport] = useState<string>("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [iframeKey, setIframeKey] = useState(0); // increment to force reload
  const iframeRef = useRef<HTMLIFrameElement | null>(null);

  const refresh = useCallback(async () => {
    try {
      const [a, s] = await Promise.all([
        fetchJSON<GraphAvailable>("/api/graph/available"),
        fetchJSON<GraphStats>("/api/graph/stats"),
      ]);
      setAvailable(a);
      setStats(s);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
    try {
      const r = await fetch("/api/graph/report", { cache: "no-store" });
      if (r.ok) setReport(await r.text());
    } catch (_) {
      /* report is optional */
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const rebuild = useCallback(async () => {
    setBusy(true);
    setError(null);
    try {
      const res = await fetchJSON<RebuildResponse>("/api/graph/rebuild", {
        method: "POST",
      });
      setIframeKey((k) => k + 1);
      await refresh();
      if (res.used_fallback) {
        setError(
          "graphify not installed -- using fallback. See docs/graph/graphify-setup.md.",
        );
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }, [refresh]);

  // Pass highlight slugs to the iframe.
  useEffect(() => {
    if (!highlight || !iframeRef.current) return;
    const slugs = highlight.split(",").map((s) => s.trim()).filter(Boolean);
    const target = iframeRef.current.contentWindow;
    if (!target) return;
    target.postMessage({ type: "highlight", slugs }, "*");
  }, [highlight, iframeKey]);

  return (
    <div className="graph-tab">
      <div className="graph-topbar">
        <button
          type="button"
          className="graph-button"
          onClick={rebuild}
          disabled={busy}
        >
          {busy ? "Rebuilding…" : "Rebuild graph"}
        </button>
        {available && (
          <span
            className={
              "graph-badge " +
              (available.available ? "graph-badge-ok" : "graph-badge-warn")
            }
            title={
              available.available
                ? "graphify CLI is installed"
                : "graphify not installed -- using packages/jojo_graph fallback. See docs/graph/graphify-setup.md."
            }
          >
            {available.source}
          </span>
        )}
        {stats && (
          <span className="graph-stats">
            {stats.node_count} nodes &middot; {stats.edge_count} edges
            {stats.connected_components != null && (
              <> &middot; {stats.connected_components} components</>
            )}
          </span>
        )}
        {error && <span className="graph-error">{error}</span>}
      </div>
      <div className="graph-body">
        <iframe
          ref={iframeRef}
          key={iframeKey}
          src="/api/graph/html"
          className="graph-iframe"
          title="Wiki knowledge graph"
        />
        <aside className="graph-sidebar">
          <h3>Graph report</h3>
          <pre className="graph-report">{report || "(no report yet)"}</pre>
          {highlight && (
            <div className="graph-highlight-banner">
              <strong>Highlighting:</strong>{" "}
              {highlight.split(",").map((s, i) => (
                <code key={i}>{s.trim()}</code>
              ))}
            </div>
          )}
        </aside>
      </div>
    </div>
  );
}
