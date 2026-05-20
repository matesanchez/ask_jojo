"use client";

/**
 * Ops tab — dashboard for absorb triggers, job queue, connector health,
 * and wiki compile status.
 *
 * Layout (top → bottom):
 *
 *   [ Wiki Health ] [ Connector Health ] [ API Key status ]
 *   [ Job Queue — pending/failed counts + "Trigger Absorb" button ]
 *   [ Recent Jobs scrollable list ]
 *   [ Lint History placeholder (Phase 6) ]
 *   [ Review Queue placeholder (Phase 6) ]
 *
 * Design decisions:
 * - All state is local. No Redux, no Zustand.
 * - Polls GET /api/ops/status every 15 s for wiki + connector + queue info.
 * - Polls GET /api/ops/jobs every 15 s for the recent-jobs list.
 * - Also subscribes to GET /api/ops/events (SSE) for live job_update events.
 *   The SSE stream takes priority over the polled jobs list when it fires.
 * - POST /api/ops/absorb shows the returned message in an inline toast.
 */

import { useCallback, useEffect, useRef, useState } from "react";
import LintHistoryCard from "../../../components/LintHistoryCard";
import LintMetrics from "../../../components/LintMetrics";
import ReviewQueueCard from "../../../components/ReviewQueueCard";

// ------------------------------------------------------------------ types

interface WikiHealth {
  total_pages: number;
  last_commit_sha: string;
  last_commit_message: string;
  last_commit_date: string;
  schema_version: string;
}

interface ConnectorInfo {
  name: string;
  status: string;
  last_synced: string | null;
  file_count: number;
}

interface QueueInfo {
  pending: number;
  failed: number;
  recent_jobs: JobRecord[];
}

interface OpsStatus {
  wiki: WikiHealth;
  connectors: ConnectorInfo[];
  api_key_configured: boolean;
  queue: QueueInfo;
}

interface JobRecord {
  job_id: string;
  status?: string;
  message?: string;
  enqueued_at?: string;
  started_at?: string;
  finished_at?: string;
  error?: string;
  [key: string]: unknown;
}

interface JobsResponse {
  jobs: JobRecord[];
}

interface AbsorbResponse {
  status: string;
  job_id: string;
  message: string;
}

// ------------------------------------------------------------------ API helpers

async function fetchJSON<T>(url: string, init?: RequestInit): Promise<T> {
  const r = await fetch(url, { cache: "no-store", ...init });
  if (!r.ok) {
    const text = await r.text().catch(() => "");
    throw new Error(`${r.status} ${r.statusText}${text ? ` — ${text}` : ""}`);
  }
  return r.json() as Promise<T>;
}

const POLL_INTERVAL_MS = 15_000;

// ------------------------------------------------------------------ helpers

function formatTimestamp(iso: string | null | undefined): string {
  if (!iso) return "—";
  try {
    return new Date(iso).toLocaleString();
  } catch {
    return iso;
  }
}

function shortSha(sha: string | null | undefined, len = 8): string {
  if (!sha) return "—";
  return sha.length > len ? sha.slice(0, len) : sha;
}

/** Mirrors the helper in raw/page.tsx — kept local to avoid cross-page imports. */
function connectorStatusClass(status: string): string {
  if (status === "ready") return "ops-badge ops-badge-ready";
  if (status === "needs-token") return "ops-badge ops-badge-warn";
  if (status === "needs-path") return "ops-badge ops-badge-warn";
  return "ops-badge";
}

function jobStatusClass(status: string | undefined): string {
  switch (status) {
    case "finished":
      return "ops-job-status ops-job-status-ok";
    case "started":
      return "ops-job-status ops-job-status-active";
    case "queued":
      return "ops-job-status ops-job-status-queued";
    case "failed":
      return "ops-job-status ops-job-status-fail";
    default:
      return "ops-job-status";
  }
}

// ------------------------------------------------------------------ sub-components

function WikiHealthCard({ wiki }: { wiki: WikiHealth | null }) {
  const [copiedSha, setCopiedSha] = useState(false);

  function copySha() {
    if (!wiki?.last_commit_sha) return;
    navigator.clipboard.writeText(wiki.last_commit_sha).then(() => {
      setCopiedSha(true);
      setTimeout(() => setCopiedSha(false), 1500);
    });
  }

  return (
    <div className="ops-card ops-card-wiki">
      <h3 className="ops-card-title">Wiki Health</h3>
      {!wiki ? (
        <p className="ops-loading">Loading…</p>
      ) : (
        <dl className="ops-dl">
          <dt>Pages</dt>
          <dd>
            <strong>{wiki.total_pages}</strong>
          </dd>

          <dt>Last checkpoint</dt>
          <dd title={wiki.last_commit_message || ""}>
            {formatTimestamp(wiki.last_commit_date)}
          </dd>

          <dt>Commit SHA</dt>
          <dd className="ops-sha-row">
            <code className="ops-sha">{shortSha(wiki.last_commit_sha)}</code>
            <button
              className="ops-copy-btn"
              onClick={copySha}
              title="Copy full SHA"
            >
              {copiedSha ? "✓" : "⧉"}
            </button>
          </dd>

          <dt>Schema</dt>
          <dd>
            <code>{wiki.schema_version || "—"}</code>
          </dd>
        </dl>
      )}
    </div>
  );
}

function ConnectorHealthCard({
  connectors,
}: {
  connectors: ConnectorInfo[] | null;
}) {
  return (
    <div className="ops-card ops-card-connectors">
      <h3 className="ops-card-title">Connector Health</h3>
      {!connectors ? (
        <p className="ops-loading">Loading…</p>
      ) : (
        <div className="ops-connector-row">
          {connectors.map((c) => (
            <span
              key={c.name}
              className={connectorStatusClass(c.status)}
              title={
                c.last_synced
                  ? `Last synced: ${formatTimestamp(c.last_synced)} · ${c.file_count} files`
                  : `${c.file_count} files · never synced`
              }
            >
              {c.name}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

function ApiKeyCard({ configured }: { configured: boolean | null }) {
  return (
    <div className="ops-card ops-card-apikey">
      <h3 className="ops-card-title">API Key</h3>
      {configured === null ? (
        <p className="ops-loading">Loading…</p>
      ) : configured ? (
        <p className="ops-apikey-ok">
          ✅ API key configured — JoJo edits enabled
        </p>
      ) : (
        <p className="ops-apikey-warn">
          ⚠️ API key not configured — JoJo edits and automated absorb
          disabled. Set <code>anthropic_api_key</code> in{" "}
          <code>config.json</code>.
        </p>
      )}
    </div>
  );
}

function JobQueuePanel({
  queue,
  apiKeyConfigured,
  onAbsorb,
  absorbing,
}: {
  queue: QueueInfo | null;
  apiKeyConfigured: boolean | null;
  onAbsorb: () => void;
  absorbing: boolean;
}) {
  const btnLabel =
    apiKeyConfigured === false
      ? "Queue Absorb (manual)"
      : "Trigger Absorb";

  return (
    <div className="ops-card ops-card-queue">
      <h3 className="ops-card-title">Job Queue</h3>
      {!queue ? (
        <p className="ops-loading">Loading…</p>
      ) : (
        <div className="ops-queue-body">
          <div className="ops-queue-counts">
            <span className="ops-count-badge ops-count-pending">
              {queue.pending} pending
            </span>
            <span
              className={`ops-count-badge ${queue.failed > 0 ? "ops-count-failed" : "ops-count-ok"}`}
            >
              {queue.failed} failed
            </span>
          </div>
          <button
            className="ops-absorb-btn"
            onClick={onAbsorb}
            disabled={absorbing}
          >
            {absorbing ? "Queuing…" : btnLabel}
          </button>
        </div>
      )}
    </div>
  );
}

function RecentJobsList({ jobs }: { jobs: JobRecord[] }) {
  const [expandedId, setExpandedId] = useState<string | null>(null);

  function toggle(id: string) {
    setExpandedId((prev) => (prev === id ? null : id));
  }

  if (!jobs.length) {
    return (
      <div className="ops-card ops-card-jobs">
        <h3 className="ops-card-title">Recent Jobs</h3>
        <p className="ops-empty">No jobs yet.</p>
      </div>
    );
  }

  return (
    <div className="ops-card ops-card-jobs">
      <h3 className="ops-card-title">Recent Jobs</h3>
      <ul className="ops-jobs-list">
        {jobs.map((job) => (
          <li
            key={job.job_id}
            className={`ops-job-row${job.status === "failed" ? " ops-job-row-failed" : ""}`}
          >
            <div className="ops-job-header">
              <span className="ops-job-id" title={job.job_id}>
                {job.job_id.length > 32
                  ? `${job.job_id.slice(0, 32)}…`
                  : job.job_id}
              </span>
              <span className={jobStatusClass(job.status)}>
                {job.status ?? "unknown"}
              </span>
              <span className="ops-job-ts">
                {formatTimestamp(
                  job.finished_at ?? job.started_at ?? job.enqueued_at
                )}
              </span>
              {job.message && (
                <span className="ops-job-msg">{String(job.message)}</span>
              )}
              {job.status === "failed" && job.error && (
                <button
                  className="ops-job-expand-btn"
                  onClick={() => toggle(job.job_id)}
                >
                  {expandedId === job.job_id ? "▲ hide" : "▼ error"}
                </button>
              )}
            </div>
            {expandedId === job.job_id && job.error && (
              <pre className="ops-job-error">{String(job.error)}</pre>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}

// Phase6Placeholder removed — slots replaced by LintHistoryCard, LintMetrics,
// and ReviewQueueCard (Phase 6 implementation).

// ------------------------------------------------------------------ page

export default function OpsPage() {
  const [status, setStatus] = useState<OpsStatus | null>(null);
  const [jobs, setJobs] = useState<JobRecord[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [absorbing, setAbsorbing] = useState(false);
  const [toast, setToast] = useState<string | null>(null);
  const toastTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  // ---------------------------------------------------------------- data loading

  const loadStatus = useCallback(async () => {
    try {
      const s = await fetchJSON<OpsStatus>("/api/ops/status");
      setStatus(s);
      // Merge queue jobs into the jobs list; SSE may have already updated it.
      setJobs((prev) => {
        const fromQueue = s.queue.recent_jobs;
        return fromQueue.length ? fromQueue : prev;
      });
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  }, []);

  const loadJobs = useCallback(async () => {
    try {
      const r = await fetchJSON<JobsResponse>("/api/ops/jobs");
      setJobs(r.jobs);
    } catch {
      // Non-fatal — queue panel still shows counts from /status.
    }
  }, []);

  // ---------------------------------------------------------------- polling

  useEffect(() => {
    loadStatus();
    loadJobs();

    const poll = setInterval(() => {
      loadStatus();
      loadJobs();
    }, POLL_INTERVAL_MS);

    return () => clearInterval(poll);
  }, [loadStatus, loadJobs]);

  // ---------------------------------------------------------------- SSE

  useEffect(() => {
    const es = new EventSource("/api/ops/events");

    es.addEventListener("job_update", (ev: MessageEvent) => {
      try {
        const data = JSON.parse(ev.data) as { jobs: JobRecord[] };
        if (Array.isArray(data.jobs)) {
          setJobs(data.jobs);
          // Also refresh queue counts.
          loadStatus();
        }
      } catch {
        /* ignore malformed SSE payload */
      }
    });

    es.onerror = () => {
      // Connection lost — polled fallback keeps data fresh.
      es.close();
    };

    return () => es.close();
  }, [loadStatus]);

  // ---------------------------------------------------------------- absorb

  function showToast(msg: string) {
    setToast(msg);
    if (toastTimer.current) clearTimeout(toastTimer.current);
    toastTimer.current = setTimeout(() => setToast(null), 5000);
  }

  async function handleAbsorb() {
    setAbsorbing(true);
    try {
      const r = await fetchJSON<AbsorbResponse>("/api/ops/absorb", {
        method: "POST",
      });
      showToast(r.message || `Absorb logged: ${r.job_id}`);
      // Refresh so the new job appears in the queue immediately.
      await loadJobs();
      await loadStatus();
    } catch (e) {
      showToast(
        `Absorb failed: ${e instanceof Error ? e.message : String(e)}`
      );
    } finally {
      setAbsorbing(false);
    }
  }

  // ---------------------------------------------------------------- render

  return (
    <div className="ops-page">
      {/* ── error banner ───────────────────────────────────────────── */}
      {error && (
        <div className="ops-error-banner" role="alert">
          ⚠ Could not load Ops data: {error}
          <button
            className="ops-error-dismiss"
            onClick={() => setError(null)}
            aria-label="Dismiss error"
          >
            ×
          </button>
        </div>
      )}

      {/* ── toast ──────────────────────────────────────────────────── */}
      {toast && (
        <div className="ops-toast" role="status">
          {toast}
        </div>
      )}

      {/* ── top row: wiki health / connector health / api key ──────── */}
      <div className="ops-top-row">
        <WikiHealthCard wiki={status?.wiki ?? null} />
        <ConnectorHealthCard connectors={status?.connectors ?? null} />
        <ApiKeyCard configured={status?.api_key_configured ?? null} />
      </div>

      {/* ── job queue ──────────────────────────────────────────────── */}
      <JobQueuePanel
        queue={status?.queue ?? null}
        apiKeyConfigured={status?.api_key_configured ?? null}
        onAbsorb={handleAbsorb}
        absorbing={absorbing}
      />

      {/* ── recent jobs ────────────────────────────────────────────── */}
      <RecentJobsList jobs={jobs} />

      {/* ── phase 6: lint history (nightly + weekly) ───────────────── */}
      <div className="ops-lint-history-row">
        <LintHistoryCard scope="nightly" />
        <LintHistoryCard scope="weekly" />
      </div>

      {/* ── phase 6: metrics trendlines + review queue ─────────────── */}
      <div className="ops-lint-bottom-row">
        <LintMetrics />
        <ReviewQueueCard />
      </div>
    </div>
  );
}
