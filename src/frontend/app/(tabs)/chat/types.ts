/**
 * Shared types for the Chat tab.
 *
 * Mirrors the response shapes returned by
 * ``src/backend/routers/qa_router.py``. Update here when the backend
 * shapes change — TypeScript will catch the next render.
 */

export type Route = "v1" | "wiki";

export type SynthesisDepth = "sonnet" | "opus";

export type OutputFormat =
  | "markdown"
  | "marp"
  | "matplotlib"
  | "plotly"
  | "table"
  | "mermaid"
  | "docx"
  | "pptx"
  | "pdf";

export interface FormatClassifyResponse {
  format: OutputFormat;
  reason: string;
  matched_keywords: string[];
  confidence: "high" | "medium" | "low";
  candidate_scores: Record<string, number>;
}

export type AnswerStatus =
  | "idle"
  | "routing"
  | "retrieving"
  | "api_key_required"
  | "answered"
  | "v1_handoff"
  | "error";

// ------------------------------------------------------------------ /api/qa/route

export interface RouteResponse {
  route: Route;
  reason: string;
  matched_keywords: string[];
  override_matched: boolean;
}

// ------------------------------------------------------------------ /api/qa/index

export interface IndexEntry {
  slug: string;
  title: string;
  type: string;
  path: string;
}

// ------------------------------------------------------------------ /api/qa/retrieve

export interface RetrievalCandidate {
  slug: string;
  title: string;
  type: string;
  path: string;
}

export interface RetrievalRouter {
  route: Route;
  reason: string;
  matched_keywords: string[];
  override_matched: boolean;
}

export interface RawFallbackHit {
  entry_id: string;
  title: string;
  source_type: string;
  score: number;
  path: string;
}

export interface RetrievalBundle {
  question: string;
  router: RetrievalRouter;
  candidates: RetrievalCandidate[];
  candidate_bodies: Record<string, string>;
  graph_neighborhood: Record<string, string[]>;
  raw_fallback_hits: RawFallbackHit[];
  wiki_root: string;
}

// ------------------------------------------------------------------ /api/qa/query

export type QueryResponse =
  | {
      status: "api_key_required";
      message: string;
      depth: SynthesisDepth;
      retrieval_bundle: RetrievalBundle;
    }
  | {
      status: "answered";
      answer: string;
      cited_slugs: string[];
      confidence: "high" | "medium" | "low";
      follow_ups: string[];
      depth: SynthesisDepth;
    }
  | {
      status: "not_implemented";
      message: string;
    };

// ------------------------------------------------------------------ /api/qa/path

export interface PathResponse {
  path: string[] | null;
  hops: number | null;
  reason?: string;
}

// ------------------------------------------------------------------ /api/qa/graph

export interface GraphStats {
  node_count: number;
  edge_count: number;
  orphan_count: number;
  avg_degree: number;
  max_degree: number;
  connected_components: number;
}

// ------------------------------------------------------------------ /api/qa/qmd-status

export interface QmdTrigger {
  value: number | null;
  threshold: number;
  fired: boolean;
}

export interface QmdStatus {
  active: boolean;
  qmd_available: boolean;
  manual_override: boolean;
  triggers: {
    index: QmdTrigger;
    latency: QmdTrigger;
    miss_rate: QmdTrigger;
  };
  reason: string;
}

// ------------------------------------------------------------------ /api/qa/file-back

export interface FileBackRequest {
  title: string;
  body: string;
  slug?: string;
  corpus?: string;
  sources?: { path: string; hash: string; ingested?: string }[];
  confidence?: "high" | "medium" | "low";
}

export interface FileBackResponse {
  status: "filed";
  path: string;
  absolute_path: string;
  slug: string;
  next_step: string;
}

// ------------------------------------------------------------------ chat session state

export interface ChatTurn {
  id: string;
  question: string;
  asked_at: string;
  status: AnswerStatus;
  routeResponse?: RouteResponse;
  bundle?: RetrievalBundle;
  answer?: string;
  citedSlugs?: string[];
  confidence?: "high" | "medium" | "low";
  followUps?: string[];
  error?: string;
  depth: SynthesisDepth;
  routeHint?: Route;
  formatHint?: OutputFormat | "auto";
  formatResponse?: FormatClassifyResponse;
}
