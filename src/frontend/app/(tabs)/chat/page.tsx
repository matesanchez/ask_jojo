"use client";

/**
 * Chat tab — Phase 4 Q&A surface.
 *
 *   [ top bar: depth toggle | route override | qmd status | api-key badge ]
 *   [ conversation pane (questions + answers, scrollable)                ]
 *   [ retrieval-bundle preview (collapsible per-turn)                    ]
 *   [ question input + Ask button                                       ]
 *
 * Modelled on ``raw/page.tsx`` and ``wiki/page.tsx`` (Phase 3 scaffolds).
 * State lives in the page; no Zustand. fetchJSON helper is identical.
 *
 * Feature-flag pattern (mirrors Phase 3 ``POST /api/wiki/edit``):
 *   - ``api_key_required`` — show the retrieval bundle and a
 *     "Cowork handoff" panel with paste-ready prompt + bundle JSON.
 *   - ``answered`` — render the answer with markdown + inline
 *     wikilinks; each cited slug navigates to the Wiki tab.
 *   - ``v1_handoff`` — show a routing slip pointing at v1.0.
 *
 * The retrieval bundle preview lets the operator confirm the
 * deterministic plumbing (router decision, candidate slugs, graph
 * neighborhood, raw fallback hits) before any model call. On
 * api_key_required this preview IS the deliverable — it's what a
 * Cowork session pastes into ``docs/qa/qa-prompt.md``.
 */

import { useCallback, useEffect, useState } from "react";

import type {
  ChatTurn,
  FileBackResponse,
  FormatClassifyResponse,
  OutputFileBackRequest,
  OutputFormat,
  QmdStatus,
  QueryResponse,
  RetrievalBundle,
  Route,
  SynthesisDepth,
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

const POLL_INTERVAL_MS = 30_000;

// ------------------------------------------------------------------ helpers

function newTurnId(): string {
  return `turn-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`;
}

function nowIso(): string {
  return new Date().toISOString();
}

function routeBadgeClass(route: Route | undefined): string {
  if (!route) return "chat-badge chat-badge-neutral";
  return route === "v1" ? "chat-badge chat-badge-v1" : "chat-badge chat-badge-wiki";
}

function copyToClipboard(text: string): Promise<void> {
  if (typeof navigator !== "undefined" && navigator.clipboard) {
    return navigator.clipboard.writeText(text);
  }
  return Promise.resolve();
}

/**
 * Build the paste-in payload a Cowork session consumes.
 * Mirrors ``docs/qa/qa-prompt.md``'s SESSION PROMPT section.
 */
function coworkPastePayload(turn: ChatTurn): string {
  const bundle = turn.bundle;
  if (!bundle) return turn.question;

  const lines = [
    "QUESTION:",
    turn.question,
    "",
    "ROUTE:",
    `${bundle.router.route} (${bundle.router.reason})`,
    "",
    "CANDIDATE SLUGS:",
    ...bundle.candidates.map((c) => `- ${c.slug} (${c.type}) — ${c.title}`),
    "",
    "1-HOP NEIGHBORHOOD:",
  ];
  for (const [slug, neighbors] of Object.entries(bundle.graph_neighborhood)) {
    lines.push(`- ${slug}: ${neighbors.join(", ") || "(none)"}`);
  }
  if (bundle.raw_fallback_hits.length > 0) {
    lines.push("");
    lines.push("RAW FALLBACK HITS (use only if wiki coverage is insufficient):");
    for (const h of bundle.raw_fallback_hits) {
      lines.push(`- ${h.entry_id} (${h.source_type}, score=${h.score})`);
    }
  }
  lines.push("");
  lines.push("INSTRUCTIONS:");
  lines.push("Run the SESSION PROMPT in docs/qa/qa-prompt.md against the above.");
  lines.push("Save your answer to docs/qa/answers/<date>-<slug>.md.");
  lines.push("Tick the question off in docs/qa/queue.md.");
  return lines.join("\n");
}

// ================================================================ component

export default function ChatPage() {
  const [turns, setTurns] = useState<ChatTurn[]>([]);
  const [draft, setDraft] = useState<string>("");
  const [depth, setDepth] = useState<SynthesisDepth>("sonnet");
  const [routeOverride, setRouteOverride] = useState<Route | "auto">("auto");
  const [formatOverride, setFormatOverride] = useState<OutputFormat | "auto">("auto");
  const [qmdStatus, setQmdStatus] = useState<QmdStatus | null>(null);
  const [apiKeyConfigured, setApiKeyConfigured] = useState<boolean | null>(null);
  const [busy, setBusy] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [showBundle, setShowBundle] = useState<Record<string, boolean>>({});

  // -- background polling for qmd + api-key status -------------------------

  const refreshStatus = useCallback(async () => {
    try {
      const qmd = await fetchJSON<QmdStatus>("/api/qa/qmd-status");
      setQmdStatus(qmd);
    } catch (e) {
      // Non-fatal: the chat tab still works without qmd status.
      console.warn("qmd status fetch failed", e);
    }
    try {
      // ops_router exposes api_key_configured; check it as a proxy.
      const ops = await fetchJSON<{ api_key_configured: boolean }>("/api/ops/status");
      setApiKeyConfigured(Boolean(ops.api_key_configured));
    } catch (e) {
      console.warn("ops status fetch failed", e);
      setApiKeyConfigured(false);
    }
  }, []);

  useEffect(() => {
    refreshStatus();
    const t = setInterval(refreshStatus, POLL_INTERVAL_MS);
    return () => clearInterval(t);
  }, [refreshStatus]);

  // -- ask handler --------------------------------------------------------

  const ask = useCallback(async () => {
    const question = draft.trim();
    if (!question || busy) return;

    const id = newTurnId();
    const hint: Route | undefined =
      routeOverride === "auto" ? undefined : routeOverride;

    const formatHint: OutputFormat | "auto" = formatOverride;
    const initialTurn: ChatTurn = {
      id,
      question,
      asked_at: nowIso(),
      status: "routing",
      depth,
      routeHint: hint,
      formatHint,
    };
    setTurns((prev) => [...prev, initialTurn]);
    setDraft("");
    setBusy(true);
    setError(null);

    try {
      // 1) Run the regex router + format classifier (synchronous-fast, parallel).
      const [routeRes, formatRes] = await Promise.all([
        fetchJSON<{
          route: Route;
          reason: string;
          matched_keywords: string[];
          override_matched: boolean;
        }>(`/api/qa/route?q=${encodeURIComponent(question)}`),
        fetchJSON<FormatClassifyResponse>(
          `/api/output/classify-format?q=${encodeURIComponent(question)}`,
        ).catch(() => null), // format detection is best-effort; failure is non-fatal
      ]);

      // Update the turn with the format/route badges *before* the
      // synthesis call so the UI reflects classification immediately.
      setTurns((prev) =>
        prev.map((t) =>
          t.id === id
            ? { ...t, routeResponse: routeRes, formatResponse: formatRes ?? undefined }
            : t,
        ),
      );

      // 2) Submit the question to /api/qa/query.
      const body: { question: string; depth: SynthesisDepth; route_hint?: Route } = {
        question,
        depth,
      };
      if (hint) body.route_hint = hint;
      const qres = await fetchJSON<QueryResponse>("/api/qa/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      // 3) Update the turn with the response.
      setTurns((prev) =>
        prev.map((t) => {
          if (t.id !== id) return t;
          if (qres.status === "api_key_required") {
            const isV1 = qres.retrieval_bundle.router.route === "v1";
            return {
              ...t,
              status: isV1 ? "v1_handoff" : "api_key_required",
              routeResponse: routeRes,
              bundle: qres.retrieval_bundle,
            };
          }
          if (qres.status === "answered") {
            return {
              ...t,
              status: "answered",
              routeResponse: routeRes,
              answer: qres.answer,
              citedSlugs: qres.cited_slugs,
              confidence: qres.confidence,
              followUps: qres.follow_ups,
            };
          }
          return {
            ...t,
            status: "error",
            error: qres.message ?? "synthesis path not implemented",
          };
        }),
      );
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e);
      setError(msg);
      setTurns((prev) =>
        prev.map((t) => (t.id === id ? { ...t, status: "error", error: msg } : t)),
      );
    } finally {
      setBusy(false);
    }
  }, [busy, depth, draft, routeOverride]);

  // -- file-back handler --------------------------------------------------

  const fileBack = useCallback(async (turn: ChatTurn) => {
    if (!turn.answer) return;
    const title = window.prompt(
      "Title for the derived page",
      `Cowork answer: ${turn.question.slice(0, 60)}`,
    );
    if (!title) return;
    try {
      const res = await fetchJSON<FileBackResponse>("/api/qa/file-back", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title,
          body: turn.answer,
          corpus: "protein-sciences",
          confidence: "low",
        }),
      });
      window.alert(`Filed to ${res.path}\n${res.next_step}`);
    } catch (e) {
      window.alert(`File-back failed: ${e instanceof Error ? e.message : String(e)}`);
    }
  }, []);

  // -- output file-back handler ------------------------------------------

  const fileOutput = useCallback(async (turn: ChatTurn) => {
    // Only meaningful when the format classifier detected a non-markdown format
    // and the turn has a synthesised answer to file.
    const format = turn.formatResponse?.format;
    if (!format || format === "markdown" || !turn.answer) return;

    setTurns((prev) =>
      prev.map((t) =>
        t.id === turn.id ? { ...t, outputFileBackStatus: "filing" } : t,
      ),
    );

    try {
      const title = turn.question.slice(0, 80);
      const payload: OutputFileBackRequest = {
        title,
        body: turn.answer,
        output_format: format,
        source_question: turn.question,
        confidence: "low",
      };
      await fetchJSON<FileBackResponse>("/api/output/file-back", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      setTurns((prev) =>
        prev.map((t) =>
          t.id === turn.id ? { ...t, outputFileBackStatus: "filed" } : t,
        ),
      );
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e);
      setTurns((prev) =>
        prev.map((t) =>
          t.id === turn.id
            ? { ...t, outputFileBackStatus: "error", outputFileBackError: msg }
            : t,
        ),
      );
    }
  }, []);

  // -- per-turn bundle toggle ---------------------------------------------

  const toggleBundle = useCallback((id: string) => {
    setShowBundle((prev) => ({ ...prev, [id]: !prev[id] }));
  }, []);

  // ================================================================ render

  return (
    <div className="chat-tab">
      {/* ---------------- top bar ---------------- */}
      <div className="chat-topbar">
        <div className="chat-controls">
          <label className="chat-label">
            Depth:
            <select
              value={depth}
              onChange={(e) => setDepth(e.target.value as SynthesisDepth)}
              aria-label="Synthesis depth"
            >
              <option value="sonnet">Sonnet (default)</option>
              <option value="opus">Opus (deep)</option>
            </select>
          </label>
          <label className="chat-label">
            Route:
            <select
              value={routeOverride}
              onChange={(e) => setRouteOverride(e.target.value as Route | "auto")}
              aria-label="Route override"
            >
              <option value="auto">Auto (regex)</option>
              <option value="wiki">Force wiki</option>
              <option value="v1">Force v1 / AKTA</option>
            </select>
          </label>
          <label className="chat-label">
            Format:
            <select
              value={formatOverride}
              onChange={(e) =>
                setFormatOverride(e.target.value as OutputFormat | "auto")
              }
              aria-label="Output format override"
            >
              <option value="auto">Auto (regex)</option>
              <option value="markdown">Markdown</option>
              <option value="marp">Marp slides</option>
              <option value="matplotlib">Chart (matplotlib)</option>
              <option value="plotly">Interactive chart</option>
              <option value="table">Table</option>
              <option value="mermaid">Diagram (mermaid)</option>
              <option value="docx">Word (docx)</option>
              <option value="pptx">PowerPoint (pptx)</option>
              <option value="pdf">PDF</option>
            </select>
          </label>
        </div>
        <div className="chat-status">
          <span
            className={
              "chat-badge " +
              (apiKeyConfigured ? "chat-badge-ok" : "chat-badge-warn")
            }
            title={
              apiKeyConfigured
                ? "Synthesis is live."
                : "API key not configured — synthesis returns api_key_required; use the Cowork handoff."
            }
          >
            {apiKeyConfigured ? "API key: ready" : "API key: pending (FU-10)"}
          </span>
          {qmdStatus && (
            <span
              className={"chat-badge " + (qmdStatus.active ? "chat-badge-ok" : "chat-badge-neutral")}
              title={qmdStatus.reason}
            >
              qmd: {qmdStatus.active ? "active" : "dormant"}
            </span>
          )}
        </div>
      </div>

      {/* ---------------- conversation ---------------- */}
      <div className="chat-conversation" role="log" aria-label="Conversation">
        {turns.length === 0 && (
          <div className="chat-empty">
            <p>Ask a question about Nurix programs, targets, decisions, or methods.</p>
            <p>
              Until the Anthropic API key lands (see <code>FU-10</code>), questions return
              the deterministic retrieval bundle and a Cowork handoff. v1.0 routes
              (AKTA, UNICORN, chromatography, buffer prep) get a routing slip.
            </p>
          </div>
        )}
        {turns.map((turn) => (
          <ChatTurnView
            key={turn.id}
            turn={turn}
            showBundle={showBundle[turn.id] ?? false}
            onToggleBundle={() => toggleBundle(turn.id)}
            onFileBack={() => fileBack(turn)}
            onFileOutput={() => fileOutput(turn)}
          />
        ))}
        {error && <div className="chat-error">{error}</div>}
      </div>

      {/* ---------------- input ---------------- */}
      <form
        className="chat-input"
        onSubmit={(e) => {
          e.preventDefault();
          ask();
        }}
      >
        <textarea
          className="chat-textarea"
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          placeholder="Ask JoJo a question..."
          rows={2}
          disabled={busy}
        />
        <button
          type="submit"
          className="chat-button"
          disabled={busy || !draft.trim()}
        >
          {busy ? "Asking..." : "Ask"}
        </button>
      </form>
    </div>
  );
}

// ================================================================ ChatTurnView

interface ChatTurnViewProps {
  turn: ChatTurn;
  showBundle: boolean;
  onToggleBundle: () => void;
  onFileBack: () => void;
  onFileOutput: () => void;
}

function ChatTurnView(props: ChatTurnViewProps) {
  const { turn, showBundle, onToggleBundle, onFileBack, onFileOutput } = props;
  return (
    <div className={"chat-turn chat-turn-" + turn.status}>
      <div className="chat-question">
        <div className="chat-question-header">
          <span className="chat-asked-at">{turn.asked_at}</span>
          {turn.routeResponse && (
            <span className={routeBadgeClass(turn.routeResponse.route)}>
              {turn.routeResponse.route}
            </span>
          )}
          {turn.formatResponse && (
            <span
              className="chat-format-badge"
              title={turn.formatResponse.reason}
            >
              format: {turn.formatResponse.format}
            </span>
          )}
          <span className="chat-depth-badge">depth: {turn.depth}</span>
          {turn.routeHint && (
            <span className="chat-hint-badge">hint: {turn.routeHint}</span>
          )}
          {turn.formatHint && turn.formatHint !== "auto" && (
            <span className="chat-hint-badge">format-hint: {turn.formatHint}</span>
          )}
        </div>
        <div className="chat-question-text">{turn.question}</div>
        {turn.routeResponse && (
          <div className="chat-route-reason" title="Router reasoning">
            <em>{turn.routeResponse.reason}</em>
          </div>
        )}
      </div>

      <div className="chat-response">
        {turn.status === "routing" && <RoutingState />}
        {turn.status === "v1_handoff" && <V1Handoff turn={turn} />}
        {turn.status === "api_key_required" && (
          <ApiKeyRequired
            turn={turn}
            showBundle={showBundle}
            onToggleBundle={onToggleBundle}
          />
        )}
        {turn.status === "answered" && turn.answer && (
          <AnsweredView
            turn={turn}
            onFileBack={onFileBack}
            onFileOutput={onFileOutput}
          />
        )}
        {turn.status === "error" && (
          <div className="chat-error">{turn.error ?? "Unknown error"}</div>
        )}
      </div>
    </div>
  );
}

// ---------------- routing state ----------------

function RoutingState() {
  return <div className="chat-routing">Routing...</div>;
}

// ---------------- v1 handoff ----------------

function V1Handoff({ turn }: { turn: ChatTurn }) {
  return (
    <div className="chat-v1-handoff">
      <h3>Routing slip — v1.0 / AKTA path</h3>
      <p>
        This question routes to the v1.0 ÄKTA / UNICORN system (legacy chromatography
        path). The wiki has near-zero AKTA content today; v1.0 has the answer.
      </p>
      <p>
        <em>{turn.routeResponse?.reason}</em>
      </p>
      <p>
        Open the v1.0 chat surface and re-ask there, or wait for the migration trigger
        described in <code>docs/qa/qa-prompt.md</code> "Routing edge cases".
      </p>
    </div>
  );
}

// ---------------- api_key_required + retrieval bundle ----------------

function ApiKeyRequired({
  turn,
  showBundle,
  onToggleBundle,
}: {
  turn: ChatTurn;
  showBundle: boolean;
  onToggleBundle: () => void;
}) {
  const bundle: RetrievalBundle | undefined = turn.bundle;
  const payload = coworkPastePayload(turn);
  return (
    <div className="chat-api-key-required">
      <div className="chat-banner chat-banner-info">
        <strong>API key pending (FU-10).</strong> The deterministic retrieval bundle
        below is ready for a Cowork handoff: paste it into a fresh session running
        <code> docs/qa/qa-prompt.md</code> to produce a gold answer.
      </div>

      {bundle && (
        <div className="chat-bundle-summary">
          <div>
            <strong>Candidates ({bundle.candidates.length}):</strong>
            <ul>
              {bundle.candidates.map((c) => (
                <li key={c.slug}>
                  <code>{c.slug}</code> — {c.title}{" "}
                  <span className="chat-type-badge">{c.type}</span>
                </li>
              ))}
            </ul>
          </div>
          {bundle.raw_fallback_hits.length > 0 && (
            <div>
              <strong>Raw fallback hits ({bundle.raw_fallback_hits.length}):</strong>
              <ul>
                {bundle.raw_fallback_hits.slice(0, 3).map((h) => (
                  <li key={h.entry_id}>
                    <code>{h.entry_id}</code> ({h.source_type}, score {h.score})
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      <div className="chat-cowork-handoff">
        <button
          type="button"
          className="chat-button chat-button-secondary"
          onClick={onToggleBundle}
        >
          {showBundle ? "Hide" : "Show"} Cowork paste-in payload
        </button>
        <button
          type="button"
          className="chat-button chat-button-secondary"
          onClick={() => copyToClipboard(payload)}
        >
          Copy payload
        </button>
        {showBundle && (
          <pre className="chat-cowork-payload">{payload}</pre>
        )}
      </div>
    </div>
  );
}

// ---------------- answered ----------------

function AnsweredView({
  turn,
  onFileBack,
  onFileOutput,
}: {
  turn: ChatTurn;
  onFileBack: () => void;
  onFileOutput: () => void;
}) {
  // Show the "File output" button only when the classifier detected a
  // non-markdown rich format for this turn.
  const richFormat = turn.formatResponse?.format;
  const isRichOutput = richFormat !== undefined && richFormat !== "markdown";

  function outputButtonLabel(): string {
    switch (turn.outputFileBackStatus) {
      case "filing":
        return "Filing...";
      case "filed":
        return "Output filed";
      case "error":
        return "File error (retry)";
      default:
        return `File ${richFormat ?? "output"} to wiki/outputs/`;
    }
  }

  return (
    <div className="chat-answered">
      <div className="chat-answer-meta">
        <span className={"chat-confidence chat-confidence-" + turn.confidence}>
          confidence: {turn.confidence}
        </span>
      </div>
      <div className="chat-answer-body">
        {/* Render markdown lazily; for now show as preformatted text. */}
        <pre className="chat-answer-text">{turn.answer}</pre>
      </div>
      {turn.citedSlugs && turn.citedSlugs.length > 0 && (
        <div className="chat-cited">
          <strong>Cited:</strong>{" "}
          {turn.citedSlugs.map((s) => (
            <a key={s} href={`/wiki?slug=${s}`} className="chat-citation">
              <code>{s}</code>
            </a>
          ))}
        </div>
      )}
      {turn.followUps && turn.followUps.length > 0 && (
        <div className="chat-follow-ups">
          <strong>Follow-ups:</strong>
          <ul>
            {turn.followUps.map((q, i) => (
              <li key={i}>{q}</li>
            ))}
          </ul>
        </div>
      )}
      <div className="chat-actions">
        {/* Existing Q&A file-back button — unchanged. */}
        <button
          type="button"
          className="chat-button chat-button-secondary"
          onClick={onFileBack}
        >
          File this to wiki/derived/
        </button>

        {/* Rich-output file-back button. Only shown for non-markdown formats. */}
        {isRichOutput && (
          <button
            type="button"
            className="chat-button chat-button-secondary"
            onClick={onFileOutput}
            disabled={turn.outputFileBackStatus === "filing"}
            title={
              turn.outputFileBackStatus === "error"
                ? (turn.outputFileBackError ?? "File output failed")
                : `File the ${richFormat} output to wiki/outputs/`
            }
          >
            {outputButtonLabel()}
          </button>
        )}

        {/* Inline error toast for the output file-back. */}
        {turn.outputFileBackStatus === "error" && turn.outputFileBackError && (
          <span className="chat-output-file-error">
            {turn.outputFileBackError}
          </span>
        )}
      </div>
    </div>
  );
}
