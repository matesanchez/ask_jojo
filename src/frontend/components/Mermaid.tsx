"use client";

/**
 * Mermaid renderer -- takes mermaid source, renders an SVG.
 *
 * Mermaid 11.x can run on the main thread (no Web Worker needed); the
 * library is small enough and renders fast on diagrams produced by
 * Q&A answers.
 *
 * Usage:
 *
 *   <Mermaid source={mermaidSource} />
 *
 * If the source is invalid, an inline error is rendered instead of
 * throwing.
 */

import { useEffect, useRef, useState } from "react";

interface MermaidProps {
  source: string;
  className?: string;
}

let mermaidLoadPromise: Promise<typeof import("mermaid")["default"]> | null = null;

function loadMermaid() {
  if (!mermaidLoadPromise) {
    mermaidLoadPromise = import("mermaid").then((m) => {
      m.default.initialize({
        startOnLoad: false,
        securityLevel: "strict", // disables HTML in node labels
        theme: "default",
        flowchart: { htmlLabels: false },
      });
      return m.default;
    });
  }
  return mermaidLoadPromise;
}

export default function Mermaid(props: MermaidProps) {
  const { source, className } = props;
  const [svg, setSvg] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const idRef = useRef<string>("mermaid-" + Math.random().toString(36).slice(2, 10));

  useEffect(() => {
    let cancelled = false;
    if (!source.trim()) {
      setSvg("");
      setError(null);
      return;
    }
    loadMermaid()
      .then(async (mermaid) => {
        try {
          const { svg: rendered } = await mermaid.render(idRef.current, source);
          if (!cancelled) {
            setSvg(rendered);
            setError(null);
          }
        } catch (e) {
          if (!cancelled) {
            setError(e instanceof Error ? e.message : String(e));
            setSvg("");
          }
        }
      })
      .catch((e) => {
        if (!cancelled) {
          setError(`failed to load mermaid: ${e instanceof Error ? e.message : String(e)}`);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [source]);

  if (error) {
    return (
      <div className={`mermaid-error ${className ?? ""}`}>
        <strong>Mermaid render failed:</strong> {error}
      </div>
    );
  }
  if (!svg) {
    return <div className={`mermaid-loading ${className ?? ""}`}>Rendering diagram…</div>;
  }
  return (
    <div
      className={`mermaid-container ${className ?? ""}`}
      dangerouslySetInnerHTML={{ __html: svg }}
    />
  );
}
