"use client";

/**
 * ReviewQueueCard — Phase 6 Ops tab component.
 *
 * Aggregates all findings with severity "error" or "warn" across the last
 * 30 days of lint runs (all scopes) and shows them grouped by slug.
 * Each item links to /wiki?slug={slug}.
 *
 * API:
 *   GET /api/ops/lint/history?days=30
 *     -> { runs: LintRun[] }
 */

import Link from "next/link";
import { useEffect, useState } from "react";
import type { LintFinding, LintRun } from "./LintHistoryCard";

// ------------------------------------------------------------------ types

interface ReviewItem {
  slug: string;
  messages: { message: string; severity: "error" | "warn" }[];
}

interface LintHistoryAllResponse {
  runs: LintRun[];
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

function aggregateFindings(runs: LintRun[]): ReviewItem[] {
  // Collect all error/warn findings, dedup by slug+message.
  const bySlug = new Map<
    string,
    { message: string; severity: "error" | "warn" }[]
  >();

  for (const run of runs) {
    for (const result of run.results ?? []) {
      for (const f of result.findings ?? []) {
        if (f.severity !== "error" && f.severity !== "warn") continue;
        const existing = bySlug.get(f.slug) ?? [];
        // Avoid exact duplicates.
        if (!existing.some((e) => e.message === f.message)) {
          existing.push({ message: f.message, severity: f.severity });
        }
        bySlug.set(f.slug, existing);
      }
    }
  }

  // Sort: slugs with errors first, then by slug name.
  return Array.from(bySlug.entries())
    .map(([slug, messages]) => ({ slug, messages }))
    .sort((a, b) => {
      const aHasError = a.messages.some((m) => m.severity === "error");
      const bHasError = b.messages.some((m) => m.severity === "error");
      if (aHasError && !bHasError) return -1;
      if (!aHasError && bHasError) return 1;
      return a.slug.localeCompare(b.slug);
    });
}

// ------------------------------------------------------------------ component

export default function ReviewQueueCard() {
  const [items, setItems] = useState<ReviewItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const data = await fetchJSON<LintHistoryAllResponse>(
          "/api/ops/lint/history?days=30",
        );
        setItems(aggregateFindings(data.runs ?? []));
        setError(null);
      } catch (e) {
        setError(e instanceof Error ? e.message : String(e));
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  return (
    <div className="ops-card ops-review-queue-card">
      <h3 className="ops-card-title">Review Queue</h3>

      {loading && <p className="ops-loading">Loading…</p>}
      {error && <p className="ops-lint-error">{error}</p>}

      {!loading && !error && items.length === 0 && (
        <p className="ops-review-healthy">
          No pending review items — wiki is healthy
        </p>
      )}

      {!loading && items.length > 0 && (
        <ul className="ops-review-list">
          {items.map((item) => (
            <li key={item.slug} className="ops-review-item">
              <div className="ops-review-item-header">
                <code className="ops-review-slug">{item.slug}</code>
                <Link
                  href={`/wiki?slug=${item.slug}`}
                  className="ops-review-view-link"
                >
                  View page
                </Link>
              </div>
              <ul className="ops-review-messages">
                {item.messages.map((m, i) => (
                  <li key={i} className="ops-review-message">
                    <span
                      className={`ops-lint-severity-badge ops-lint-severity-badge-${m.severity}`}
                    >
                      {m.severity}
                    </span>
                    {m.message}
                  </li>
                ))}
              </ul>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
