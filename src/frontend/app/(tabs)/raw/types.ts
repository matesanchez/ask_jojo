/**
 * Shared types for the Raw tab.
 *
 * These mirror the response shapes returned by `src/backend/routers/raw_router.py`
 * and `src/backend/routers/ingest_router.py`. If you change a shape there,
 * update it here — a TypeScript check will catch the next render.
 */

export type AccessLevel = "public" | "all_fte" | "department" | "restricted";

export interface ManifestEntry {
  id: string;
  path: string;
  title: string;
  source_type: string;
  source_url: string;
  access_level: string;
  fetched: string;
  size_bytes: number;
  sha256: string;
  supersedes: string | null;
}

export interface TreeNodeFile {
  name: string;
  kind: "file";
  entry: ManifestEntry;
}

export interface TreeNodeDir {
  name: string;
  kind: "dir";
  children: TreeNode[];
}

export type TreeNode = TreeNodeFile | TreeNodeDir;

export interface TreeResponse {
  raw_root: string;
  total_entries: number;
  tree: TreeNode[];
}

export interface FileResponse {
  entry: ManifestEntry & {
    source_id: string;
    redacted_fields: string[];
    superseded_by: string | null;
  };
  frontmatter: Record<string, unknown>;
  body: string;
}

export interface ManifestSummary {
  raw_root: string;
  schema_version: string;
  total_entries: number;
  by_source: Record<string, number>;
  latest_fetched_by_source: Record<string, string>;
  supersedence_chains: number;
}

export interface ConnectorStatus {
  name: string;
  status: string; // "ready" | "needs-token" | "needs-path" | ...
}

export interface IngestJob {
  job_id: string;
  status: string;
  connector: string;
  result?: unknown;
  error?: string;
}
