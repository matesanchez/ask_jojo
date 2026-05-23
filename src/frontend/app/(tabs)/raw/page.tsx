"use client";

/**
 * Raw tab — three-pane view over `ask_jojo_raw/`.
 *
 *   [ top bar: connector badges + re-sync + totals                ]
 *   [ tree |           markdown preview           | metadata      ]
 *   [ bottom bar: last fetched per source + pending jobs          ]
 *
 * This is a Phase 1 deliverable — the "human audit surface" from PLAN.md
 * §6 Phase 1. Every wiki answer in later phases cites a raw file; this
 * tab is where a human verifies the citation is real and the source is
 * something they're allowed to see.
 *
 * Design decisions worth knowing before editing:
 *
 * - All state is local to the page component. No Redux, no Zustand. If
 *   that stops being tractable we can lift into context, but two dozen
 *   state vars is fine as a single hook cluster for now.
 * - API calls hit `/api/raw/*` and `/api/ingest/*`. Next.js rewrites
 *   those to `localhost:8000` in dev (see `next.config.js`); in local-
 *   mode packaging they'll be same-origin.
 * - We poll `/api/ingest/status` and `/api/raw/manifest` every 15s so a
 *   background sync (kicked off by the re-sync button) shows up without
 *   a page reload. Cheap: both endpoints are O(|manifest|).
 */

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useCallback, useEffect, useMemo, useState } from "react";

import type {
  ConnectorStatus,
  FileResponse,
  IngestJob,
  ManifestSummary,
  TreeNode,
  TreeNodeDir,
  TreeNodeFile,
  TreeResponse,
} from "./types";

// ------------------------------------------------------------------ useDebounce
function useDebounce<T>(value: T, delayMs: number): T {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const t = setTimeout(() => setDebounced(value), delayMs);
    return () => clearTimeout(t);
  }, [value, delayMs]);
  return debounced;
}

// ------------------------------------------------------------------ API helpers
// Thin wrappers so retries, error shaping, and the base URL live in one spot.

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
function formatBytes(bytes: number): string {
  if (!bytes) return "—";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

function formatTimestamp(iso: string | null | undefined): string {
  if (!iso) return "—";
  try {
    return new Date(iso).toLocaleString();
  } catch {
    return iso;
  }
}

function shortSha(sha: string | null | undefined): string {
  if (!sha) return "—";
  return sha.length > 12 ? `${sha.slice(0, 12)}…` : sha;
}

function accessBadgeClass(level: string): string {
  switch (level) {
    case "public":
      return "raw-badge raw-badge-public";
    case "all_fte":
      return "raw-badge raw-badge-allfte";
    case "department":
      return "raw-badge raw-badge-dept";
    case "restricted":
      return "raw-badge raw-badge-restricted";
    default:
      return "raw-badge";
  }
}

function connectorStatusClass(status: string): string {
  if (status === "ready") return "raw-badge raw-badge-ready";
  if (status === "needs-token") return "raw-badge raw-badge-warn";
  if (status === "needs-path") return "raw-badge raw-badge-warn";
  return "raw-badge";
}

// ------------------------------------------------------------------ filterTree
// Recursively prunes tree nodes that don't match the query.
// Uses the `kind` discriminator from TreeNode (not `type`).
function filterTree(nodes: TreeNode[], query: string): TreeNode[] {
  if (!query) return nodes;
  const q = query.toLowerCase();
  return nodes.flatMap<TreeNode>((node) => {
    if (node.kind === "file") {
      return node.name.toLowerCase().includes(q) ? [node] : [];
    }
    const children = filterTree(node.children, q);
    if (children.length === 0 && !node.name.toLowerCase().includes(q)) return [];
    return [{ ...node, children }];
  });
}

// ------------------------------------------------------------------ tree view
function TreeView({
  nodes,
  selectedId,
  onSelect,
}: {
  nodes: TreeNode[];
  selectedId: string | null;
  onSelect: (id: string) => void;
}) {
  if (!nodes.length) {
    return (
      <p className="raw-empty">
        Manifest is empty. Run a connector from the re-sync menu above, or
        from the CLI (<code>jojo-ingest sync-all</code>).
      </p>
    );
  }
  return (
    <ul className="raw-tree">
      {nodes.map((n) =>
        n.kind === "dir" ? (
          <TreeDir
            key={`dir:${n.name}`}
            node={n}
            selectedId={selectedId}
            onSelect={onSelect}
          />
        ) : (
          <TreeFile
            key={`file:${n.entry.id}`}
            node={n}
            selectedId={selectedId}
            onSelect={onSelect}
          />
        )
      )}
    </ul>
  );
}

function TreeDir({
  node,
  selectedId,
  onSelect,
}: {
  node: TreeNodeDir;
  selectedId: string | null;
  onSelect: (id: string) => void;
}) {
  const [open, setOpen] = useState(true);
  return (
    <li className="raw-tree-dir">
      <button
        type="button"
        className="raw-tree-dir-toggle"
        onClick={() => setOpen((x) => !x)}
        aria-expanded={open}
      >
        <span className="raw-tree-caret">{open ? "▾" : "▸"}</span>
        <span className="raw-tree-icon">📁</span>
        <span className="raw-tree-name">{node.name}</span>
      </button>
      {open && node.children.length > 0 && (
        <TreeView
          nodes={node.children}
          selectedId={selectedId}
          onSelect={onSelect}
        />
      )}
    </li>
  );
}

function TreeFile({
  node,
  selectedId,
  onSelect,
}: {
  node: TreeNodeFile;
  selectedId: string | null;
  onSelect: (id: string) => void;
}) {
  const active = selectedId === node.entry.id;
  return (
    <li className="raw-tree-file">
      <button
        type="button"
        className={`raw-tree-file-btn ${active ? "is-active" : ""}`}
        onClick={() => onSelect(node.entry.id)}
        title={node.entry.title || node.name}
      >
        <span className="raw-tree-icon">📄</span>
        <span className="raw-tree-name">{node.entry.title || node.name}</span>
        <span className={accessBadgeClass(node.entry.access_level)}>
          {node.entry.access_level}
        </span>
      </button>
    </li>
  );
}

// ------------------------------------------------------------------ preview
function Preview({
  loading,
  error,
  file,
}: {
  loading: boolean;
  error: string | null;
  file: FileResponse | null;
}) {
  if (loading) return <p className="raw-preview-hint">Loading…</p>;
  if (error) return <p className="raw-preview-error">{error}</p>;
  if (!file) {
    return (
      <p className="raw-preview-hint">
        Select a file from the tree to preview it.
      </p>
    );
  }
  return (
    <article className="raw-preview-body markdown-body">
      <h1>{file.entry.title || file.entry.path}</h1>
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{file.body}</ReactMarkdown>
    </article>
  );
}

// ------------------------------------------------------------------ metadata panel
function Metadata({ file }: { file: FileResponse | null }) {
  if (!file) {
    return (
      <p className="raw-meta-hint">
        Metadata for the selected file will appear here.
      </p>
    );
  }
  const e = file.entry;
  return (
    <dl className="raw-meta">
      <dt>Title</dt>
      <dd>{e.title || e.path}</dd>

      <dt>Source</dt>
      <dd>
        <span className={connectorStatusClass("ready")}>{e.source_type}</span>
      </dd>

      <dt>Access</dt>
      <dd>
        <span className={accessBadgeClass(e.access_level)}>
          {e.access_level}
        </span>
      </dd>

      <dt>Source URL</dt>
      <dd>
        {e.source_url ? (
          <a href={e.source_url} target="_blank" rel="noopener noreferrer">
            Open original ↗
          </a>
        ) : (
          <span className="raw-muted">—</span>
        )}
      </dd>

      <dt>Source ID</dt>
      <dd>
        <code>{e.source_id || "—"}</code>
      </dd>

      <dt>Fetched</dt>
      <dd>{formatTimestamp(e.fetched)}</dd>

      <dt>Size</dt>
      <dd>{formatBytes(e.size_bytes)}</dd>

      <dt>SHA256</dt>
      <dd title={e.sha256}>
        <code>{shortSha(e.sha256)}</code>
      </dd>

      <dt>Path</dt>
      <dd>
        <code>{e.path}</code>
      </dd>

      {e.redacted_fields.length > 0 && (
        <>
          <dt>Redacted fields</dt>
          <dd>{e.redacted_fields.join(", ")}</dd>
        </>
      )}

      {e.supersedes && (
        <>
          <dt>Supersedes</dt>
          <dd>
            <code>{e.supersedes}</code>
          </dd>
        </>
      )}

      {e.superseded_by && (
        <>
          <dt>Superseded by</dt>
          <dd className="raw-warn">
            <code>{e.superseded_by}</code> (newer version exists)
          </dd>
        </>
      )}
    </dl>
  );
}

// ------------------------------------------------------------------ top + bottom bars
function ConnectorBar({
  connectors,
  resyncing,
  onResync,
  summary,
}: {
  connectors: ConnectorStatus[];
  resyncing: string | null;
  onResync: (name: string) => void;
  summary: ManifestSummary | null;
}) {
  return (
    <div className="raw-top-bar">
      <div className="raw-top-totals">
        {summary ? (
          <>
            <strong>{summary.total_entries}</strong> files across{" "}
            <strong>{Object.keys(summary.by_source).length}</strong> sources
          </>
        ) : (
          <span className="raw-muted">Loading manifest summary…</span>
        )}
      </div>
      <div className="raw-top-connectors">
        {connectors.map((c) => (
          <button
            key={c.name}
            type="button"
            className="raw-resync-btn"
            onClick={() => onResync(c.name)}
            disabled={resyncing === c.name || c.status !== "ready"}
            title={
              c.status === "ready"
                ? `Re-sync ${c.name}`
                : `${c.name} is ${c.status} — configure env and reload`
            }
          >
            <span className={connectorStatusClass(c.status)}>{c.name}</span>
            <span className="raw-resync-label">
              {resyncing === c.name ? "syncing…" : "↻"}
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}

function StatusBar({
  summary,
  jobs,
}: {
  summary: ManifestSummary | null;
  jobs: IngestJob[];
}) {
  const pending = jobs.filter((j) => j.status === "queued" || j.status === "started");
  const failed = jobs.filter((j) => j.status === "failed");
  return (
    <div className="raw-bottom-bar">
      <div className="raw-bottom-sources">
        {summary && Object.keys(summary.by_source).length > 0 ? (
          Object.entries(summary.by_source).map(([name, count]) => (
            <span key={name} className="raw-bottom-source">
              <strong>{name}</strong>: {count} file{count === 1 ? "" : "s"}
              {summary.latest_fetched_by_source[name] && (
                <>
                  {" "}· last fetched{" "}
                  {formatTimestamp(summary.latest_fetched_by_source[name])}
                </>
              )}
            </span>
          ))
        ) : (
          <span className="raw-muted">No files ingested yet.</span>
        )}
      </div>
      <div className="raw-bottom-jobs">
        {pending.length > 0 && (
          <span className="raw-muted">{pending.length} pending</span>
        )}
        {failed.length > 0 && (
          <span className="raw-warn">{failed.length} failed</span>
        )}
        {pending.length === 0 && failed.length === 0 && (
          <span className="raw-muted">No active jobs</span>
        )}
      </div>
    </div>
  );
}

// ------------------------------------------------------------------ page
export default function RawPage() {
  const [tree, setTree] = useState<TreeNode[]>([]);
  const [summary, setSummary] = useState<ManifestSummary | null>(null);
  const [connectors, setConnectors] = useState<ConnectorStatus[]>([]);
  const [jobs, setJobs] = useState<IngestJob[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [file, setFile] = useState<FileResponse | null>(null);
  const [fileLoading, setFileLoading] = useState(false);
  const [fileError, setFileError] = useState<string | null>(null);
  const [resyncing, setResyncing] = useState<string | null>(null);
  const [treeError, setTreeError] = useState<string | null>(null);
  const [treeSearch, setTreeSearch] = useState("");
  const debouncedSearch = useDebounce(treeSearch, 200);

  // ------------------------------------------------------------- loaders
  const refreshTreeAndSummary = useCallback(async () => {
    try {
      const [treeRes, sumRes] = await Promise.all([
        fetchJSON<TreeResponse>("/api/raw/tree"),
        fetchJSON<ManifestSummary>("/api/raw/manifest"),
      ]);
      setTree(treeRes.tree);
      setSummary(sumRes);
      setTreeError(null);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      setTreeError(msg);
    }
  }, []);

  const refreshConnectors = useCallback(async () => {
    try {
      const r = await fetchJSON<{ connectors: ConnectorStatus[] }>(
        "/api/ingest/connectors"
      );
      setConnectors(r.connectors);
    } catch {
      // Non-fatal — the tree still renders, the bar just can't flip buttons.
    }
  }, []);

  const refreshJobs = useCallback(async () => {
    try {
      const r = await fetchJSON<{ jobs: IngestJob[] }>("/api/ingest/jobs");
      setJobs(r.jobs);
    } catch {
      // Same rationale — jobs-bar is best-effort.
    }
  }, []);

  // ------------------------------------------------------------- effects
  useEffect(() => {
    refreshTreeAndSummary();
    refreshConnectors();
    refreshJobs();
    const id = setInterval(() => {
      refreshTreeAndSummary();
      refreshJobs();
    }, POLL_INTERVAL_MS);
    return () => clearInterval(id);
  }, [refreshTreeAndSummary, refreshConnectors, refreshJobs]);

  useEffect(() => {
    if (!selectedId) {
      setFile(null);
      return;
    }
    let cancelled = false;
    setFileLoading(true);
    setFileError(null);
    fetchJSON<FileResponse>(`/api/raw/file/${encodeURIComponent(selectedId)}`)
      .then((f) => {
        if (!cancelled) setFile(f);
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setFileError(err instanceof Error ? err.message : String(err));
          setFile(null);
        }
      })
      .finally(() => {
        if (!cancelled) setFileLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [selectedId]);

  // ------------------------------------------------------------- actions
  const onResync = useCallback(
    async (name: string) => {
      setResyncing(name);
      try {
        await fetchJSON(`/api/ingest/resync/${encodeURIComponent(name)}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          // Empty body is fine for onedrive/publicdrive/sharepoint — they
          // read paths from env. Drive needs a `source`, but there's no
          // sensible default we could guess from the UI; disable the
          // button for drive by only enabling when status=="ready"
          // which it currently always is, and surface the 400 below.
          body: JSON.stringify({}),
        });
        // Give the job a moment to finish inproc before refreshing.
        await new Promise((r) => setTimeout(r, 300));
        await refreshTreeAndSummary();
        await refreshJobs();
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : String(err);
        setTreeError(`Re-sync ${name} failed: ${msg}`);
      } finally {
        setResyncing(null);
      }
    },
    [refreshTreeAndSummary, refreshJobs]
  );

  // ------------------------------------------------------------- render
  const hasTree = useMemo(() => tree.length > 0, [tree]);
  const filteredTree = useMemo(
    () => filterTree(tree, debouncedSearch),
    [tree, debouncedSearch]
  );

  return (
    <section className="raw-page">
      <ConnectorBar
        connectors={connectors}
        resyncing={resyncing}
        onResync={onResync}
        summary={summary}
      />
      {treeError && <div className="raw-error-banner">{treeError}</div>}
      <div className="raw-three-pane">
        <aside className="raw-pane raw-pane-tree">
          <header className="raw-pane-header">Tree</header>
          <div className="raw-pane-body">
            <input
              type="search"
              className="raw-search"
              placeholder="Filter files…"
              value={treeSearch}
              onChange={(e) => setTreeSearch(e.target.value)}
            />
            {hasTree ? (
              <TreeView
                nodes={filteredTree}
                selectedId={selectedId}
                onSelect={setSelectedId}
              />
            ) : (
              <p className="raw-empty">
                Manifest is empty. Run a connector from the top bar, or:
                <br />
                <code>jojo-ingest sync-all</code>
              </p>
            )}
          </div>
        </aside>
        <main className="raw-pane raw-pane-preview">
          <header className="raw-pane-header">Preview</header>
          <div className="raw-pane-body">
            <Preview loading={fileLoading} error={fileError} file={file} />
          </div>
        </main>
        <aside className="raw-pane raw-pane-meta">
          <header className="raw-pane-header">Metadata</header>
          <div className="raw-pane-body">
            <Metadata file={file} />
          </div>
        </aside>
      </div>
      <StatusBar summary={summary} jobs={jobs} />
    </section>
  );
}
