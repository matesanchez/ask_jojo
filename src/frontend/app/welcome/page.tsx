"use client";

import Link from "next/link";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type StatusSection = {
  ok: boolean;
  detail: string;
};

type StatusResponse = {
  api_key: StatusSection;
  models: StatusSection;
  graph: StatusSection;
  connectors: StatusSection;
  lint: StatusSection;
};

// Human-readable labels for each section key.
const SECTION_LABELS: Record<keyof StatusResponse, string> = {
  api_key: "API Key",
  models: "Models",
  graph: "Graph Auth",
  connectors: "Connectors",
  lint: "Lint",
};

const STATUS_KEYS: (keyof StatusResponse)[] = [
  "api_key",
  "models",
  "graph",
  "connectors",
  "lint",
];

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function WelcomePage() {
  const router = useRouter();

  // `null` means the first fetch has not completed yet.
  const [status, setStatus] = useState<StatusResponse | null>(null);
  const [fetchError, setFetchError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function fetchStatus() {
      try {
        const res = await fetch("/api/ops/status");
        if (!res.ok) {
          throw new Error(`HTTP ${res.status}`);
        }
        const data: StatusResponse = await res.json();
        if (cancelled) return;
        setFetchError(null);
        setStatus(data);

        // Redirect when every section is green.
        const allGreen = STATUS_KEYS.every((key) => data[key].ok);
        if (allGreen) {
          router.push("/");
        }
      } catch (err) {
        if (cancelled) return;
        setFetchError(err instanceof Error ? err.message : "Unknown error");
      }
    }

    // Immediate first fetch, then poll every 10 s.
    fetchStatus();
    const intervalId = setInterval(fetchStatus, 10_000);

    return () => {
      cancelled = true;
      clearInterval(intervalId);
    };
  }, [router]);

  // Determine whether we are still waiting for the very first response.
  const isLoading = status === null && fetchError === null;

  return (
    <div className="welcome-page">
      <div className="welcome-card">
        <h1 className="welcome-heading">Welcome to JoJo Bot</h1>
        <p className="welcome-description">
          Your department&apos;s AI knowledge assistant. To get started,
          configure your settings.
        </p>

        <ol className="welcome-steps">
          <li className="welcome-step">
            <span className="welcome-step-num">1</span>
            <span className="welcome-step-text">
              Paste your Anthropic API key in{" "}
              <strong>Settings &rarr; API key</strong>
            </span>
          </li>
          <li className="welcome-step">
            <span className="welcome-step-num">2</span>
            <span className="welcome-step-text">
              Confirm connector paths (OneDrive and public drive) in{" "}
              <strong>Settings &rarr; Connectors</strong>
            </span>
          </li>
          <li className="welcome-step">
            <span className="welcome-step-num">3</span>
            <span className="welcome-step-text">
              Ask JoJo your first question in the <strong>Chat</strong> tab
            </span>
          </li>
        </ol>

        {/* ----------------------------------------------------------------
            Status checklist — shown once the first fetch has returned.
            While loading, show a subtle "Checking setup…" indicator.
        ---------------------------------------------------------------- */}
        <div style={{ marginTop: "1.25rem" }}>
          {isLoading && (
            <p
              style={{
                fontSize: "0.85rem",
                color: "#9ca3af", // Tailwind gray-400
                margin: 0,
              }}
            >
              Checking setup&hellip;
            </p>
          )}

          {fetchError !== null && (
            <p
              style={{
                fontSize: "0.85rem",
                color: "#f59e0b", // Tailwind amber-400
                margin: 0,
              }}
            >
              Could not reach status endpoint: {fetchError}
            </p>
          )}

          {status !== null && (
            <ul
              style={{
                listStyle: "none",
                margin: 0,
                padding: 0,
                display: "flex",
                flexDirection: "column",
                gap: "0.4rem",
              }}
            >
              {STATUS_KEYS.map((key) => {
                const section = status[key];
                return (
                  <li
                    key={key}
                    style={{
                      display: "flex",
                      alignItems: "baseline",
                      gap: "0.5rem",
                      fontSize: "0.85rem",
                    }}
                  >
                    {/* Green checkmark or yellow pending dot */}
                    <span
                      style={{
                        fontWeight: 700,
                        color: section.ok ? "#22c55e" : "#eab308", // green-500 / yellow-500
                        minWidth: "1rem",
                        lineHeight: 1,
                      }}
                      aria-label={section.ok ? "ok" : "pending"}
                    >
                      {section.ok ? "✓" : "○"}
                    </span>

                    <span style={{ color: "#6b7280" /* gray-500 */ }}>
                      <strong style={{ color: "#374151" /* gray-700 */ }}>
                        {SECTION_LABELS[key]}
                      </strong>
                      {" — "}
                      {section.detail}
                    </span>
                  </li>
                );
              })}
            </ul>
          )}
        </div>

        <Link href="/settings" className="welcome-cta">
          Open Settings
        </Link>
      </div>
    </div>
  );
}
