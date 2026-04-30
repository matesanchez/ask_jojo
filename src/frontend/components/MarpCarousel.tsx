"use client";

/**
 * MarpCarousel -- renders Marp markdown as an SVG carousel.
 *
 * Off-loads the render to a Web Worker (src/frontend/lib/marp/worker.ts)
 * so the main thread stays responsive on large decks. Arrow keys + click
 * targets navigate between slides.
 *
 * Usage:
 *
 *   <MarpCarousel markdown={marpSource} />
 *
 * Props:
 *   - markdown: the Marp source (frontmatter + slides separated by ---).
 *   - className: optional extra classes for the wrapper.
 *   - onSlideChange: optional callback fired when the active slide changes.
 */

import { useCallback, useEffect, useMemo, useRef, useState } from "react";

interface MarpCarouselProps {
  markdown: string;
  className?: string;
  onSlideChange?: (index: number, total: number) => void;
}

interface MarpRenderResponse {
  id: string;
  status: "ok" | "error";
  svgs?: string[];
  error?: string;
}

export default function MarpCarousel(props: MarpCarouselProps) {
  const { markdown, className, onSlideChange } = props;
  const [svgs, setSvgs] = useState<string[]>([]);
  const [active, setActive] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const workerRef = useRef<Worker | null>(null);
  const reqIdRef = useRef<number>(0);

  // Spin up the worker once.
  useEffect(() => {
    if (typeof Worker === "undefined") {
      setError("Web Workers not available in this environment.");
      return;
    }
    const w = new Worker(new URL("../lib/marp/worker.ts", import.meta.url), {
      type: "module",
    });
    workerRef.current = w;

    w.onmessage = (event: MessageEvent<MarpRenderResponse>) => {
      const res = event.data;
      if (res.status === "ok" && res.svgs) {
        setSvgs(res.svgs);
        setError(null);
        setActive(0);
      } else if (res.status === "error") {
        setError(res.error ?? "Marp render failed");
      }
      setLoading(false);
    };
    w.onerror = (e) => {
      setError(e.message ?? "worker error");
      setLoading(false);
    };

    return () => {
      w.terminate();
      workerRef.current = null;
    };
  }, []);

  // Render whenever the markdown changes.
  useEffect(() => {
    if (!workerRef.current || !markdown.trim()) {
      setSvgs([]);
      return;
    }
    setLoading(true);
    reqIdRef.current += 1;
    workerRef.current.postMessage({
      id: String(reqIdRef.current),
      markdown,
    });
  }, [markdown]);

  // Keyboard navigation: ArrowLeft / ArrowRight while focus is on the wrapper.
  const onKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === "ArrowRight") {
        setActive((i) => Math.min(i + 1, svgs.length - 1));
        e.preventDefault();
      } else if (e.key === "ArrowLeft") {
        setActive((i) => Math.max(i - 1, 0));
        e.preventDefault();
      }
    },
    [svgs.length],
  );

  // Notify parent on slide change.
  useEffect(() => {
    if (onSlideChange && svgs.length) {
      onSlideChange(active, svgs.length);
    }
  }, [active, svgs.length, onSlideChange]);

  const svgHtml = useMemo(() => svgs[active] ?? "", [svgs, active]);

  if (error) {
    return (
      <div className={`marp-carousel marp-carousel-error ${className ?? ""}`}>
        <strong>Marp render failed:</strong> {error}
      </div>
    );
  }
  if (loading) {
    return <div className={`marp-carousel marp-carousel-loading ${className ?? ""}`}>Rendering deck…</div>;
  }
  if (!svgs.length) {
    return <div className={`marp-carousel marp-carousel-empty ${className ?? ""}`}>(no slides)</div>;
  }

  return (
    <div
      tabIndex={0}
      onKeyDown={onKeyDown}
      className={`marp-carousel ${className ?? ""}`}
      aria-label={`Slide ${active + 1} of ${svgs.length}`}
    >
      <div
        className="marp-carousel-slide"
        // Marp output is a self-contained <svg>; injecting via dangerouslySetInnerHTML
        // is safe because (a) html: false is set in the worker so no raw HTML is
        // rendered, and (b) the worker disabled emoji-shortcode injection of HTML.
        dangerouslySetInnerHTML={{ __html: svgHtml }}
      />
      <div className="marp-carousel-controls">
        <button
          type="button"
          onClick={() => setActive((i) => Math.max(i - 1, 0))}
          disabled={active === 0}
          aria-label="Previous slide"
        >
          ◀
        </button>
        <span className="marp-carousel-position">
          {active + 1} / {svgs.length}
        </span>
        <button
          type="button"
          onClick={() => setActive((i) => Math.min(i + 1, svgs.length - 1))}
          disabled={active === svgs.length - 1}
          aria-label="Next slide"
        >
          ▶
        </button>
      </div>
    </div>
  );
}
