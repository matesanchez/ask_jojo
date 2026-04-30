/**
 * Shared types for the Wiki tab.
 *
 * These mirror the response shapes returned by
 * `src/backend/routers/wiki_router.py`. Update here when the backend shapes
 * change — TypeScript will catch the next render.
 */

export type WikiConfidence = "high" | "medium" | "low" | "";

// ------------------------------------------------------------------ tree

export interface WikiTreeFile {
  kind: "file";
  slug: string;
  title: string;
  type: string;
  path: string;
  confidence: WikiConfidence;
  last_updated: string;
}

export interface WikiTreeDir {
  kind: "dir";
  name: string;
  children: WikiTreeNode[];
}

export type WikiTreeNode = WikiTreeFile | WikiTreeDir;

export interface WikiTreeResponse {
  tree: WikiTreeDir[];
  total_pages: number;
}

// ------------------------------------------------------------------ page

export interface WikiPageSource {
  path: string;
  hash: string;
  ingested: string;
}

export interface WikiPage {
  path: string;
  slug: string;
  title: string;
  type: string;
  confidence: WikiConfidence;
  last_updated: string;
  last_reviewed: string;
  schema_version: string;
  corpus: string;
  tags: string[];
  aliases: string[];
  related: string[];
  sources: WikiPageSource[];
  body: string;
}

// ------------------------------------------------------------------ search

export interface WikiSearchResult {
  slug: string;
  title: string;
  type: string;
  path: string;
}

export interface WikiSearchResponse {
  query: string;
  results: WikiSearchResult[];
}

// ------------------------------------------------------------------ stats

export interface WikiStats {
  total_pages: number;
  last_commit_sha: string;
  last_commit_message: string;
  last_commit_date: string;
  schema_version: string;
  index_page_count: number;
}

// ------------------------------------------------------------------ backlinks

export interface WikiBacklinksResponse {
  slug: string;
  linked_from: string[];
}

// ------------------------------------------------------------------ edit

export interface WikiEditRequest {
  path: string;
  instruction: string;
}

export type WikiEditResponse =
  | {
      status: "proposed";
      path: string;
      diff: string;
      proposed_body: string;
    }
  | {
      status: "api_key_required";
      message: string;
    }
  | {
      status: "error";
      message: string;
    };
