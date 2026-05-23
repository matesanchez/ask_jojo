"use client";

/**
 * Graph tab -- Phase 7a knowledge-graph visualization.
 *
 * Two views, toggled by the ?view= URL param:
 *   ?view=brain   → Three.js 3D force-directed brain view (BrainView)
 *   (default)     → D3 iframe / graphify fallback view
 *
 * URL params:
 *   ?highlight=cbl-b,cbl-b-target,...
 *     Forwarded to the iframe via postMessage (D3 view) or passed as a
 *     prop to BrainView so it can pulse/highlight the cited slugs.
 *
 * The D3 view embeds /api/graph/html in an iframe. When graphify isn't
 * installed, the fallback HTML still renders a minimal SVG view so the
 * tab is usable today.
 */

import { Suspense, useCallback, useEffect, useRef, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import dynamic from "next/dynamic";

// BrainView uses Three.js which is browser-only; load it with ssr:false.
const BrainView = dynamic(() => import("../../../components/BrainView"), {
  ssr: false,
  loading: () => (
    <div className="brain-view-container flex items-center justify-center">
      <span className="text-white/40 text-sm font-mono">Initializing brain view…</span>
    </div>
  ),
});

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

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
    const text = await r.text().catch(() => "");
    throw new Error(`${r.status} ${r.statusText}${text ? ` — ${text}` : ""}`);
  }
  return r.json() as Promise<T>;
}

// ---------------------------------------------------------------------------
// Inner component — uses useSearchParams (requires Suspense boundary)
// ---------------------------------------------------------------------------

function GraphPageInner() {
  const router = useRouter();
  const search = useSearchParams();
  const view = search?.get("view") ?? "";
  const highlight = search?.get("highlight") ?? "";

  const isBrainView = view !== "d3";

  const [available, setAvailable] = useState<GraphAvailable | null>(null);
  const [stats, setStats] = useState<GraphStats | null>(null);
  const [report, setReport] = useState<string>("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [iframeKey, setIframeKey] = useState(0);
  const [iframeReady, setIframeReady] = useState(false);
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
    } catch {
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

  // Reset iframeReady when the iframe is rebuilt so the onLoad handler
  // re-arms before we send postMessage.
  useEffect(() => {
    setIframeReady(false);
  }, [iframeKey]);

  // Pass highlight slugs to the iframe (D3 view only).
  // Gated on iframeReady so the message is not sent before the content loads.
  useEffect(() => {
    if (!highlight || !iframeReady || !iframeRef.current) return;
    const slugs = highlight
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);
    const target = iframeRef.current.contentWindow;
    if (!target) return;
    target.postMessage({ type: "highlight", slugs }, "*");
  }, [highlight, iframeReady]);

  // ---------------------------------------------------------------------------
  // View toggle helpers
  // ---------------------------------------------------------------------------

  const switchToD3 = useCallback(() => {
    const params = new URLSearchParams(search?.toString() ?? "");
    params.set("view", "d3");
    router.replace(`/graph?${params.toString()}`);
  }, [router, search]);

  const switchToBrain = useCallback(() => {
    const params = new URLSearchParams(search?.toString() ?? "");
    params.delete("view");
    router.replace(`/graph?${params.toString()}`);
  }, [router, search]);

  return (
    <div className="graph-tab">
      {/* Top bar */}
      <div className="graph-topbar">
        {/* View toggle */}
        <div className="graph-view-toggle">
          <button
            type="button"
            className={`graph-button${!isBrainView ? " graph-button-active" : ""}`}
            onClick={switchToD3}
            title="D3 / graphify iframe view"
          >
            D3 View
          </button>
          <button
            type="button"
            className={`graph-button${isBrainView ? " graph-button-active" : ""}`}
            onClick={switchToBrain}
            title="Three.js 3D brain view"
          >
            Brain View
          </button>
        </div>

        {/* D3-view-only controls */}
        {!isBrainView && (
          <>
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
          </>
        )}

        {error && <span className="graph-error">{error}</span>}
      </div>

      {/* View body */}
      {isBrainView ? (
        <BrainView highlight={highlight} />
      ) : (
        <div className="graph-body">
          <iframe
            ref={iframeRef}
            key={iframeKey}
            src="/api/graph/html"
            className="graph-iframe"
            title="Wiki knowledge graph"
            onLoad={() => setIframeReady(true)}
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
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Page export — wrapped in Suspense for useSearchParams
// ---------------------------------------------------------------------------

export default function GraphPage() {
  return (
    <Suspense
      fallback={
        <div className="graph-tab">
          <div className="graph-topbar">
            <span className="graph-stats">Loading…</span>
          </div>
        </div>
      }
    >
      <GraphPageInner />
    </Suspense>
  );
}
