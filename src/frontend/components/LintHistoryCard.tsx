"use client";

/**
 * LintHistoryCard — Phase 6 Ops tab component.
 *
 * Displays a table of recent lint runs for a given scope (nightly or weekly),
 * with a "Run now" button that POSTs to /api/ops/lint/{scope} and refreshes
 * the history on completion. Expandable rows show per-check findings.
 *
 * API shapes:
 *   GET /api/ops/lint/history?scope=nightly&days=30
 *     -> { runs: LintRun[] }
 *   POST /api/ops/lint/{scope}
 *     -> { status, scope, results }
 */

import React, { useCallback, useEffect, useState } from "react";

// ------------------------------------------------------------------ types

export interface LintFinding {
  slug: string;
  message: string;
  severity: "error" | "warn" | "info";
}

export interface LintCheckResult {
  check_name: string;
  status: "pass" | "warn" | "fail" | "api_key_required";
  findings: LintFinding[];
  run_at: string;
  duration_ms: number;
}

export interface LintRun {
  run_id?: string;
  run_at: string;
  scope: string;
  results: LintCheckResult[];
}

interface LintHistoryResponse {
  runs: LintRun[];
}

interface LintHistoryCardProps {
  scope: "nightly" | "weekly";
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

function formatTimestamp(iso: string | null | undefined): string {
  if (!iso) return "—";
  try {
    return new Date(iso).toLocaleString();
  } catch {
    return iso;
  }
}

function countsByStatus(results: LintCheckResult[]): {
  pass: number;
  warn: number;
  fail: number;
  apiKeyRequired: number;
} {
  let pass = 0,
    warn = 0,
    fail = 0,
    apiKeyRequired = 0;
  for (const r of results) {
    if (r.status === "pass") pass++;
    else if (r.status === "warn") warn++;
    else if (r.status === "fail") fail++;
    else if (r.status === "api_key_required") apiKeyRequired++;
  }
  return { pass, warn, fail, apiKeyRequired };
}

function totalFindings(results: LintCheckResult[]): number {
  return results.reduce((n, r) => n + r.findings.length, 0);
}

// ------------------------------------------------------------------ component

export default function LintHistoryCard({ scope }: LintHistoryCardProps) {
  const [runs, setRuns] = useState<LintRun[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [running, setRunning] = useState(false);
  const [expandedRunAt, setExpandedRunAt] = useState<string | null>(null);

  const loadHistory = useCallback(async () => {
    try {
      const data = await fetchJSON<LintHistoryResponse>(
        `/api/ops/lint/history?scope=${scope}&days=30`,
      );
      setRuns(data.runs ?? []);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  }, [scope]);

  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  async function handleRunNow() {
    setRunning(true);
    try {
      await fetchJSON(`/api/ops/lint/${scope}`, { method: "POST" });
      await loadHistory();
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setRunning(false);
    }
  }

  function toggleRow(runAt: string) {
    setExpandedRunAt((prev) => (prev === runAt ? null : runAt));
  }

  return (
    <div className="ops-card ops-lint-history-card">
      <div className="ops-lint-history-header">
        <h3 className="ops-card-title">
          Lint History — <span className="ops-lint-scope-badge">{scope}</span>
        </h3>
        <button
          className="ops-lint-run-btn"
          onClick={handleRunNow}
          disabled={running}
        >
          {running ? "Running…" : "Run now"}
        </button>
      </div>

      {loading && <p className="ops-loading">Loading…</p>}
      {error && <p className="ops-lint-error">{error}</p>}

      {!loading && !error && runs.length === 0 && (
        <p className="ops-empty">No lint runs recorded yet.</p>
      )}

      {!loading && runs.length > 0 && (
        <table className="ops-lint-table">
          <thead>
            <tr>
              <th>Run date</th>
              <th>Pass</th>
              <th>Warn</th>
              <th>Fail</th>
              <th>API key req.</th>
              <th>Total findings</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {runs.map((run) => {
              const counts = countsByStatus(run.results ?? []);
              const findings = totalFindings(run.results ?? []);
              const isExpanded = expandedRunAt === run.run_at;
              return (
                <React.Fragment key={run.run_at}>
                  <tr
                    className={`ops-lint-row${isExpanded ? " ops-lint-row-expanded" : ""}`}
                  >
                    <td>{formatTimestamp(run.run_at)}</td>
                    <td className="ops-lint-count ops-lint-count-pass">
                      {counts.pass}
                    </td>
                    <td className="ops-lint-count ops-lint-count-warn">
                      {counts.warn}
                    </td>
                    <td className="ops-lint-count ops-lint-count-fail">
                      {counts.fail}
                    </td>
                    <td className="ops-lint-count ops-lint-count-apikey">
                      {counts.apiKeyRequired}
                    </td>
                    <td>{findings}</td>
                    <td>
                      {(run.results ?? []).length > 0 && (
                        <button
                          className="ops-lint-expand-btn"
                          onClick={() => toggleRow(run.run_at)}
                        >
                          {isExpanded ? "▲ hide" : "▼ details"}
                        </button>
                      )}
                    </td>
                  </tr>
                  {isExpanded &&
                    (run.results ?? []).map((result) => (
                      <tr
                        key={`${run.run_at}-${result.check_name}`}
                        className="ops-lint-detail-row"
                      >
                        <td colSpan={7}>
                          <div className="ops-lint-check">
                            <span className="ops-lint-check-name">
                              {result.check_name}
                            </span>
                            <span
                              className={`ops-lint-status ops-lint-status-${result.status}`}
                            >
                              {result.status === "api_key_required" ? (
                                <span className="ops-lint-apikey-badge">
                                  API key required
                                </span>
                              ) : (
                                result.status
                              )}
                            </span>
                            <span className="ops-lint-duration">
                              {result.duration_ms}ms
                            </span>
                            {result.findings.length > 0 && (
                              <ul className="ops-lint-findings">
                                {result.findings.map((f, i) => (
                                  <li
                                    key={i}
                                    className={`ops-lint-finding ops-lint-finding-${f.severity}`}
                                  >
                                    <code>{f.slug}</code> — {f.message}
                                  </li>
                                ))}
                              </ul>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                </React.Fragment>
              );
            })}
          </tbody>
        </table>
      )}
    </div>
  );
}
