"use client";

/**
 * LintMetrics — Phase 6 Ops tab component.
 *
 * Fetches GET /api/ops/lint/metrics?days=30 and renders 4 compact sparkline
 * charts (Chart.js / react-chartjs-2):
 *   1. Orphan count
 *   2. Avg confidence score (y-axis 0–1)
 *   3. Stale page count
 *   4. Wikilink error count
 *
 * Chart.js registration: only the elements and scales actually used.
 * If the chart register call is omitted, react-chartjs-2 throws a
 * "missing scale" runtime error in Next.js. Import and register here,
 * before the first render.
 */

import {
  CategoryScale,
  Chart,
  type ChartData,
  Filler,
  LineElement,
  LinearScale,
  PointElement,
  Tooltip,
} from "chart.js";
import { useEffect, useState } from "react";
import { Line } from "react-chartjs-2";

// Register only what this file uses — avoids the "missing scale" error.
Chart.register(
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
  Tooltip,
  Filler,
);

// ------------------------------------------------------------------ types

interface MetricPoint {
  date: string; // ISO date string, e.g. "2026-05-01"
  value: number;
}

// Backend returns a flat list of per-run dicts (history.metrics_series shape).
interface RunMetrics {
  run_at: string;
  orphan_count: number;
  avg_confidence_score: number;
  stale_count: number;
  wikilink_error_count: number;
}

interface LintMetricsResponse {
  series: RunMetrics[];
}

// ------------------------------------------------------------------ helpers

async function fetchJSON<T>(url: string, init?: RequestInit): Promise<T> {
  const r = await fetch(url, { cache: "no-store", ...init });
  if (!r.ok) {
    const text = await r.text().catch(() => "");
    throw new Error(`${r.status} ${r.statusText}${text ? ` — ${text}` : ""}`);
  }
  return r.json() as Promise<T>;
}

// Shared compact sparkline options. Minimalist, no legend, no axes labels.
function sparklineOptions(yMin?: number, yMax?: number) {
  return {
    responsive: true,
    maintainAspectRatio: false,
    animation: { duration: 300 } as const,
    plugins: {
      legend: { display: false },
      tooltip: { enabled: true },
    },
    scales: {
      x: {
        ticks: { font: { size: 9 }, maxTicksLimit: 6, maxRotation: 0 },
        grid: { display: false },
      },
      y: {
        min: yMin,
        max: yMax,
        ticks: { font: { size: 9 }, maxTicksLimit: 4 },
        grid: { color: "#f0f0f0" },
      },
    },
  } as const;
}

function buildDataset(
  label: string,
  points: MetricPoint[],
  color: string,
): ChartData<"line"> {
  return {
    labels: points.map((p) => p.date),
    datasets: [
      {
        label,
        data: points.map((p) => p.value),
        borderColor: color,
        backgroundColor: `${color}22`,
        borderWidth: 1.5,
        pointRadius: 2,
        tension: 0.3,
        fill: true,
      },
    ],
  };
}

interface SparklineProps {
  label: string;
  points: MetricPoint[];
  color: string;
  yMin?: number;
  yMax?: number;
}

function Sparkline({ label, points, color, yMin, yMax }: SparklineProps) {
  if (points.length === 0) {
    return (
      <div className="ops-sparkline-empty">
        <span className="ops-sparkline-label">{label}</span>
        <span className="ops-sparkline-no-data">no data</span>
      </div>
    );
  }
  return (
    <div className="ops-sparkline">
      <span className="ops-sparkline-label">{label}</span>
      <div className="ops-sparkline-chart">
        <Line
          data={buildDataset(label, points, color)}
          options={sparklineOptions(yMin, yMax)}
        />
      </div>
    </div>
  );
}

// ------------------------------------------------------------------ component

export default function LintMetrics() {
  const [data, setData] = useState<LintMetricsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const result = await fetchJSON<LintMetricsResponse>(
          "/api/ops/lint/metrics?days=30",
        );
        setData(result);
        setError(null);
      } catch (e) {
        setError(e instanceof Error ? e.message : String(e));
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  // Transform flat run list into per-metric MetricPoint arrays.
  const runs = data?.series ?? [];
  const toDate = (iso: string) => iso.slice(0, 10);
  const orphanPoints: MetricPoint[] = runs.map((r) => ({ date: toDate(r.run_at), value: r.orphan_count }));
  const confidencePoints: MetricPoint[] = runs.map((r) => ({ date: toDate(r.run_at), value: r.avg_confidence_score }));
  const stalePoints: MetricPoint[] = runs.map((r) => ({ date: toDate(r.run_at), value: r.stale_count }));
  const wikilinkPoints: MetricPoint[] = runs.map((r) => ({ date: toDate(r.run_at), value: r.wikilink_error_count }));

  const noData = !loading && !error && runs.length === 0;

  return (
    <div className="ops-card ops-lint-metrics-card">
      <h3 className="ops-card-title">Lint Metrics (last 30 days)</h3>

      {loading && <p className="ops-loading">Loading…</p>}
      {error && <p className="ops-lint-error">{error}</p>}
      {noData && (
        <p className="ops-empty">No lint runs recorded yet.</p>
      )}

      {!loading && !error && !noData && (
        <div className="ops-sparklines-grid">
          <Sparkline
            label="Orphan count"
            points={orphanPoints}
            color="#888"
            yMin={0}
          />
          <Sparkline
            label="Avg confidence score"
            points={confidencePoints}
            color="#4a90d9"
            yMin={0}
            yMax={1}
          />
          <Sparkline
            label="Stale page count"
            points={stalePoints}
            color="#d97a4a"
            yMin={0}
          />
          <Sparkline
            label="Wikilink error count"
            points={wikilinkPoints}
            color="#c23b22"
            yMin={0}
          />
        </div>
      )}
    </div>
  );
}
