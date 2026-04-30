"use client";

/**
 * Wiki tab -- three-pane IDE over `ask_jojo_wiki/`.
 *
 *   [ top bar: search | "Request edit from JoJo" | page count badge ]
 *   [ tree pane | markdown preview pane | metadata + backlinks pane ]
 *
 * Phase 3 deliverable. Modelled closely on `raw/page.tsx`:
 * - All state is local to the page component (no Zustand yet).
 * - `fetchJSON` helper is identical.
 * - Polling pattern (15s) mirrors the Raw tab for `/api/wiki/stats`.
 * - CSS class prefix is `wiki-` instead of `raw-`.
 *
 * Wikilink resolution: `[[slug|label]]` and `[[slug]]` are pre-processed
 * by regex into `[label](#wiki:slug)` / `[slug](#wiki:slug)` before being
 * passed to ReactMarkdown. An `onClick` on the preview `<article>` intercepts
 * `href` values starting with `#wiki:` and calls `setSelectedPath`.
 */

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useCallback, useEffect, useRef, useState } from "react";

import type {
  WikiBacklinksResponse,
  WikiConfidence,
  WikiEditResponse,
  WikiPage,
  WikiSearchResult,
  WikiStats,
  WikiTreeDir,
  WikiTreeFile,
  WikiTreeNode,
  WikiTreeResponse,
} from "./types";

// ------------------------------------------------------------------ API helpers

async function fetchJSON<T>(url: string, init?: RequestInit): Promise<T> {
  const r = await fetch(url, { cache: "no-store", ...init });
  if (!r.ok) {
    const text = await r.text().catch(() => "");
    throw new Error(`${r.status} ${r.statusText}${text ? ` -- ${text}` : ""}`);
  }
  return r.json() as Promise<T>;
}

const POLL_INTERVAL_MS = 15_000;

// ------------------------------------------------------------------ helpers

function confidenceBadgeClass(confidence: WikiConfidence): string {
  switch (confidence) {
    case "high":
      return "wiki-badge wiki-badge-high";
    case "medium":
      return "wiki-badge wiki-badge-medium";
    case "low":
      return "wiki-badge wiki-badge-low";
    default:
      return "";
  }
}

/** Resolve `[[slug|label]]` and `[[slug]]` wikilinks before passing to ReactMarkdown. */
function resolveWikilinks(body: string): string {
  return body
    .replace(/\[\[([^\]|]+)\|([^\]]+)\]\]/g, (_m, slug, label) => {
      return `[${label}](#wiki:${slug})`;
    })
    .replace(/\[\[([^\]]+)\]\]/g, (_m, slug) => {
      return `[${slug}](#wiki:${slug})`;
    });
}

function formatDate(val: string | null | undefined): string {
  if (!val) return "--";
  return val;
}

// ------------------------------------------------------------------ tree view

function WikiTreeView({
  nodes,
  selectedPath,
  onSelect,
}: {
  nodes: WikiTreeNode[];
  selectedPath: string | null;
  onSelect: (path: string) => void;
}) {
  if (!nodes.length) {
    return (
      <p className="wiki-empty">
        Wiki is empty. Run an absorb pass to populate it.
      </p>
    );
  }
  return (
    <ul className="wiki-tree">
      {nodes.map((n) =>
        n.kind === "dir" ? (
          <WikiTreeDirNode
            key={`dir:${n.name}`}
            node={n}
            selectedPath={selectedPath}
            onSelect={onSelect}
          />
        ) : (
          <WikiTreeFileNode
            key={`file:${n.path}`}
            node={n}
            selectedPath={selectedPath}
            onSelect={onSelect}
          />
        )
      )}
    </ul>
  );
}

function WikiTreeDirNode({
  node,
  selectedPath,
  onSelect,
}: {
  node: WikiTreeDir;
  selectedPath: string | null;
  onSelect: (path: string) => void;
}) {
  const [open, setOpen] = useState(true);
  return (
    <li className="wiki-tree-dir">
      <button
        type="button"
        className="wiki-tree-dir-toggle"
        onClick={() => setOpen((x) => !x)}
        aria-expanded={open}
      >
        <span className="wiki-tree-caret">{open ? "▾" : "▸"}</span>
        <span className="wiki-tree-icon">&#128193;</span>
        <span className="wiki-tree-name">{node.name}</span>
      </button>
      {open && node.children.length > 0 && (
        <WikiTreeView
          nodes={node.children}
          selectedPath={selectedPath}
          onSelect={onSelect}
        />
      )}
    </li>
  );
}

function WikiTreeFileNode({
  node,
  selectedPath,
  onSelect,
}: {
  node: WikiTreeFile;
  selectedPath: string | null;
  onSelect: (path: string) => void;
}) {
  const active = selectedPath === node.path;
  const badgeClass = confidenceBadgeClass(node.confidence);
  return (
    <li className="wiki-tree-file">
      <button
        type="button"
        className={`wiki-tree-file-btn ${active ? "is-active" : ""}`}
        onClick={() => onSelect(node.path)}
        title={node.title || node.slug}
      >
        <span className="wiki-tree-icon">&#128196;</span>
        <span className="wiki-tree-name">{node.title || node.slug}</span>
        {badgeClass && (
          <span className={badgeClass}>{node.confidence}</span>
        )}
      </button>
    </li>
  );
}

// ------------------------------------------------------------------ preview

function WikiPreview({
  loading,
  error,
  page,
  onWikilinkClick,
}: {
  loading: boolean;
  error: string | null;
  page: WikiPage | null;
  onWikilinkClick: (slug: string) => void;
}) {
  if (loading) return <p className="wiki-preview-hint">Loading...</p>;
  if (error) return <p className="wiki-preview-error">{error}</p>;
  if (!page) {
    return (
      <p className="wiki-preview-hint">
        Select a page from the tree to preview it.
      </p>
    );
  }

  const resolvedBody = resolveWikilinks(page.body);

  function handleArticleClick(e: React.MouseEvent<HTMLElement>) {
    const target = e.target as HTMLElement;
    const anchor = target.closest("a");
    if (!anchor) return;
    const href = anchor.getAttribute("href") || "";
    if (href.startsWith("#wiki:")) {
      e.preventDefault();
      const slug = href.slice("#wiki:".length);
      onWikilinkClick(slug);
    }
  }

  return (
    /* eslint-disable jsx-a11y/click-events-have-key-events */
    /* eslint-disable jsx-a11y/no-noninteractive-element-interactions */
    <article
      className="wiki-preview-body markdown-body"
      onClick={handleArticleClick}
    >
      <h1>{page.title}</h1>
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{resolvedBody}</ReactMarkdown>
    </article>
  );
}

// ------------------------------------------------------------------ metadata + backlinks panel

function WikiMetadata({
  page,
  backlinks,
  backlinksLoading,
  onSourceClick,
  onBacklinkClick,
}: {
  page: WikiPage | null;
  backlinks: string[];
  backlinksLoading: boolean;
  onSourceClick: (hash: string) => void;
  onBacklinkClick: (slug: string) => void;
}) {
  if (!page) {
    return (
      <p className="wiki-meta-hint">
        Metadata for the selected page will appear here.
      </p>
    );
  }

  return (
    <div className="wiki-meta">
      <section className="wiki-meta-section">
        <h3 className="wiki-meta-heading">Metadata</h3>
        <dl className="wiki-meta-dl">
          <dt>Title</dt>
          <dd>{page.title}</dd>

          <dt>Type</dt>
          <dd>{page.type || "--"}</dd>

          <dt>Confidence</dt>
          <dd>
            {page.confidence ? (
              <span className={confidenceBadgeClass(page.confidence)}>
                {page.confidence}
              </span>
            ) : (
              "--"
            )}
          </dd>

          <dt>Corpus</dt>
          <dd>{page.corpus || "--"}</dd>

          <dt>Last updated</dt>
          <dd>{formatDate(page.last_updated)}</dd>

          <dt>Last reviewed</dt>
          <dd>{formatDate(page.last_reviewed)}</dd>

          <dt>Schema</dt>
          <dd>{page.schema_version || "--"}</dd>

          {page.tags.length > 0 && (
            <>
              <dt>Tags</dt>
              <dd>{page.tags.join(", ")}</dd>
            </>
          )}

          {page.aliases.length > 0 && (
            <>
              <dt>Aliases</dt>
              <dd>{page.aliases.join(", ")}</dd>
            </>
          )}
        </dl>

        {page.sources.length > 0 && (
          <div className="wiki-meta-sources">
            <p className="wiki-meta-subheading">
              Sources ({page.sources.length})
            </p>
            <ul className="wiki-meta-source-list">
              {page.sources.map((s) => (
                <li key={s.hash}>
                  <button
                    type="button"
                    className="wiki-source-btn"
                    onClick={() => onSourceClick(s.hash)}
                    title={`Open ${s.path} in Raw tab`}
                  >
                    <code>{s.hash.slice(0, 12)}</code>
                    <span className="wiki-source-path">{s.path}</span>
                  </button>
                </li>
              ))}
            </ul>
          </div>
        )}
      </section>

      <section className="wiki-meta-section">
        <h3 className="wiki-meta-heading">
          Backlinks
          {!backlinksLoading && ` (${backlinks.length})`}
        </h3>
        {backlinksLoading ? (
          <p className="wiki-muted">Loading...</p>
        ) : backlinks.length === 0 ? (
          <p className="wiki-muted">No inbound links.</p>
        ) : (
          <ul className="wiki-backlinks-list">
            {backlinks.map((slug) => (
              <li key={slug}>
                <button
                  type="button"
                  className="wiki-backlink-btn"
                  onClick={() => onBacklinkClick(slug)}
                >
                  {slug}
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}

// ------------------------------------------------------------------ search dropdown

function SearchDropdown({
  results,
  onSelect,
  onClose,
}: {
  results: WikiSearchResult[];
  onSelect: (result: WikiSearchResult) => void;
  onClose: () => void;
}) {
  if (!results.length) return null;
  return (
    <ul className="wiki-search-dropdown" role="listbox">
      {results.map((r) => (
        <li key={r.slug} role="option">
          <button
            type="button"
            className="wiki-search-result"
            onClick={() => {
              onSelect(r);
              onClose();
            }}
          >
            <span className="wiki-search-result-title">{r.title}</span>
            <span className="wiki-search-result-type">{r.type}</span>
          </button>
        </li>
      ))}
    </ul>
  );
}

// ------------------------------------------------------------------ edit modal

type EditModalState =
  | { kind: "idle" }
  | { kind: "loading" }
  | { kind: "api_key_required"; message: string }
  | { kind: "proposed"; diff: string; proposed_body: string }
  | { kind: "error"; message: string };

function EditModal({
  page,
  onClose,
}: {
  page: WikiPage;
  onClose: () => void;
}) {
  const [instruction, setInstruction] = useState("");
  const [state, setState] = useState<EditModalState>({ kind: "idle" });

  async function handleAskJoJo() {
    if (!instruction.trim()) return;
    setState({ kind: "loading" });
    try {
      const resp = await fetchJSON<WikiEditResponse>("/api/wiki/edit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ path: page.path, instruction }),
      });
      if (resp.status === "api_key_required") {
        setState({ kind: "api_key_required", message: resp.message });
      } else if (resp.status === "proposed") {
        setState({
          kind: "proposed",
          diff: resp.diff,
          proposed_body: resp.proposed_body,
        });
      } else {
        setState({ kind: "error", message: "Unexpected response from API." });
      }
    } catch (err: unknown) {
      setState({
        kind: "error",
        message: err instanceof Error ? err.message : String(err),
      });
    }
  }

  return (
    <div className="wiki-modal-overlay" role="dialog" aria-modal="true">
      <div className="wiki-modal">
        <div className="wiki-modal-header">
          <h2 className="wiki-modal-title">
            Request an edit to: {page.title}
          </h2>
          <button
            type="button"
            className="wiki-modal-close"
            onClick={onClose}
            aria-label="Close modal"
          >
            &times;
          </button>
        </div>

        <div className="wiki-modal-body">
          <label className="wiki-modal-label" htmlFor="edit-instruction">
            Describe the change you&#39;d like JoJo to make:
          </label>
          <textarea
            id="edit-instruction"
            className="wiki-modal-textarea"
            value={instruction}
            onChange={(e) => setInstruction(e.target.value)}
            disabled={state.kind === "loading"}
            rows={4}
            placeholder="e.g. Add a note that NX-1607 reduces PSA in mCRPC patients."
          />

          <div className="wiki-modal-actions">
            <button
              type="button"
              className="wiki-btn wiki-btn-primary"
              onClick={() => void handleAskJoJo()}
              disabled={state.kind === "loading" || !instruction.trim()}
            >
              {state.kind === "loading" ? "Asking JoJo..." : "Ask JoJo"}
            </button>
          </div>

          {/* State-dependent content */}
          {state.kind === "api_key_required" && (
            <div className="wiki-modal-nudge">
              <p>{state.message}</p>
              <p>
                <a href="/ops" className="wiki-link">
                  Configure in Ops tab
                </a>
              </p>
            </div>
          )}

          {state.kind === "error" && (
            <div className="wiki-modal-error">
              <p>{state.message}</p>
              <button
                type="button"
                className="wiki-btn wiki-btn-secondary"
                onClick={() => setState({ kind: "idle" })}
              >
                Try again
              </button>
            </div>
          )}

          {state.kind === "proposed" && (
            <div className="wiki-modal-diff">
              <p className="wiki-modal-diff-heading">Proposed changes:</p>
              <div className="wiki-diff-view">
                {state.diff.split("\n").map((line, i) => {
                  let cls = "wiki-diff-line";
                  if (line.startsWith("+") && !line.startsWith("+++")) {
                    cls += " wiki-diff-added";
                  } else if (
                    line.startsWith("-") &&
                    !line.startsWith("---")
                  ) {
                    cls += " wiki-diff-removed";
                  } else if (line.startsWith("@@")) {
                    cls += " wiki-diff-hunk";
                  }
                  return (
                    <pre key={i} className={cls}>
                      {line}
                    </pre>
                  );
                })}
              </div>

              <div className="wiki-modal-diff-actions">
                <button
                  type="button"
                  className="wiki-btn wiki-btn-danger"
                  onClick={onClose}
                >
                  Reject
                </button>
                <button
                  type="button"
                  className="wiki-btn wiki-btn-primary"
                  disabled
                  title="Write-back coming in Phase 3 final pass"
                >
                  Accept (coming soon)
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ------------------------------------------------------------------ page component

export default function WikiPage() {
  const [tree, setTree] = useState<WikiTreeDir[]>([]);
  const [stats, setStats] = useState<WikiStats | null>(null);
  const [treeError, setTreeError] = useState<string | null>(null);

  // Selected page
  const [selectedPath, setSelectedPath] = useState<string | null>(null);
  const [page, setPage] = useState<WikiPage | null>(null);
  const [pageLoading, setPageLoading] = useState(false);
  const [pageError, setPageError] = useState<string | null>(null);

  // Backlinks
  const [backlinks, setBacklinks] = useState<string[]>([]);
  const [backlinksLoading, setBacklinksLoading] = useState(false);

  // Search
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<WikiSearchResult[]>([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const searchDebounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Edit modal
  const [showEditModal, setShowEditModal] = useState(false);

  // --------------------------------------------------------- loaders

  const refreshTree = useCallback(async () => {
    try {
      const res = await fetchJSON<{ tree: WikiTreeDir[]; total_pages: number }>(
        "/api/wiki/tree"
      );
      setTree(res.tree);
      setTreeError(null);
    } catch (err: unknown) {
      setTreeError(err instanceof Error ? err.message : String(err));
    }
  }, []);

  const refreshStats = useCallback(async () => {
    try {
      const s = await fetchJSON<WikiStats>("/api/wiki/stats");
      setStats(s);
    } catch {
      // Non-fatal: badge just won't update.
    }
  }, []);

  // --------------------------------------------------------- effects

  useEffect(() => {
    refreshTree();
    refreshStats();
    const id = setInterval(refreshStats, POLL_INTERVAL_MS);
    return () => clearInterval(id);
  }, [refreshTree, refreshStats]);

  // Load page when selection changes.
  useEffect(() => {
    if (!selectedPath) {
      setPage(null);
      setBacklinks([]);
      return;
    }
    let cancelled = false;
    setPageLoading(true);
    setPageError(null);
    setBacklinks([]);
    fetchJSON<WikiPage>(`/api/wiki/page?path=${encodeURIComponent(selectedPath)}`)
      .then((p) => {
        if (!cancelled) {
          setPage(p);
          // Load backlinks.
          setBacklinksLoading(true);
          fetchJSON<WikiBacklinksResponse>(
            `/api/wiki/backlinks?slug=${encodeURIComponent(p.slug)}`
          )
            .then((bl) => {
              if (!cancelled) setBacklinks(bl.linked_from);
            })
            .catch(() => {
              if (!cancelled) setBacklinks([]);
            })
            .finally(() => {
              if (!cancelled) setBacklinksLoading(false);
            });
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setPageError(err instanceof Error ? err.message : String(err));
          setPage(null);
        }
      })
      .finally(() => {
        if (!cancelled) setPageLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [selectedPath]);

  // Debounced search.
  useEffect(() => {
    if (searchDebounceRef.current) {
      clearTimeout(searchDebounceRef.current);
    }
    if (searchQuery.length < 2) {
      setSearchResults([]);
      setShowDropdown(false);
      return;
    }
    searchDebounceRef.current = setTimeout(async () => {
      try {
        const res = await fetchJSON<{ results: WikiSearchResult[] }>(
          `/api/wiki/search?q=${encodeURIComponent(searchQuery)}`
        );
        setSearchResults(res.results);
        setShowDropdown(res.results.length > 0);
      } catch {
        setSearchResults([]);
        setShowDropdown(false);
      }
    }, 300);
    return () => {
      if (searchDebounceRef.current) clearTimeout(searchDebounceRef.current);
    };
  }, [searchQuery]);

  // --------------------------------------------------------- handlers

  function selectByPath(path: string) {
    setSelectedPath(path);
  }

  function selectBySlug(slug: string) {
    // Find matching file node in tree.
    const found = findBySlug(tree, slug);
    if (found) setSelectedPath(found);
  }

  function handleSourceClick(hash: string) {
    if (typeof window !== "undefined") {
      localStorage.setItem("rawSelectedId", hash);
    }
    window.location.href = "/raw";
  }

  // --------------------------------------------------------- render

  return (
    <section className="wiki-page">
      {/* Top bar */}
      <div className="wiki-top-bar">
        <div className="wiki-search-wrap">
          <input
            type="search"
            className="wiki-search-input"
            placeholder="Search wiki..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onFocus={() => {
              if (searchResults.length > 0) setShowDropdown(true);
            }}
            onBlur={() => {
              // Delay hide so clicks on results register.
              setTimeout(() => setShowDropdown(false), 150);
            }}
            aria-label="Search wiki pages"
          />
          {showDropdown && (
            <SearchDropdown
              results={searchResults}
              onSelect={(r) => {
                selectByPath(r.path);
                setSearchQuery("");
              }}
              onClose={() => setShowDropdown(false)}
            />
          )}
        </div>

        <button
          type="button"
          className="wiki-edit-btn"
          disabled={!selectedPath || !page}
          onClick={() => setShowEditModal(true)}
        >
          Request edit from JoJo
        </button>

        {stats && (
          <span className="wiki-page-count-badge">
            {stats.total_pages} pages
          </span>
        )}
      </div>

      {treeError && (
        <div className="wiki-error-banner">{treeError}</div>
      )}

      {/* Three-pane layout */}
      <div className="wiki-three-pane">
        {/* Left: tree */}
        <aside className="wiki-pane wiki-pane-tree">
          <header className="wiki-pane-header">Tree</header>
          <div className="wiki-pane-body">
            {tree.length > 0 ? (
              <WikiTreeView
                nodes={tree as WikiTreeNode[]}
                selectedPath={selectedPath}
                onSelect={selectByPath}
              />
            ) : (
              <p className="wiki-empty">
                Wiki tree is empty. Run an absorb pass first.
              </p>
            )}
          </div>
        </aside>

        {/* Center: markdown preview */}
        <main className="wiki-pane wiki-pane-preview">
          <header className="wiki-pane-header">Preview</header>
          <div className="wiki-pane-body">
            <WikiPreview
              loading={pageLoading}
              error={pageError}
              page={page}
              onWikilinkClick={selectBySlug}
            />
          </div>
        </main>

        {/* Right: metadata + backlinks */}
        <aside className="wiki-pane wiki-pane-meta">
          <header className="wiki-pane-header">Metadata</header>
          <div className="wiki-pane-body">
            <WikiMetadata
              page={page}
              backlinks={backlinks}
              backlinksLoading={backlinksLoading}
              onSourceClick={handleSourceClick}
              onBacklinkClick={selectBySlug}
            />
          </div>
        </aside>
      </div>

      {/* Edit modal (Steps 2 + 3) */}
      {showEditModal && page && (
        <EditModal page={page} onClose={() => setShowEditModal(false)} />
      )}
    </section>
  );
}

// ------------------------------------------------------------------ helpers

/** Depth-first search of the tree for a node matching `slug`. Returns path. */
function findBySlug(nodes: WikiTreeNode[], slug: string): string | null {
  for (const n of nodes) {
    if (n.kind === "file") {
      if (n.slug === slug) return n.path;
    } else {
      const found = findBySlug(n.children, slug);
      if (found) return found;
    }
  }
  return null;
}
