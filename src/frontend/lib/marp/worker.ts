/**
 * Marp Web Worker -- converts Marp markdown to an array of SVG strings.
 *
 * PLAN.md §6 Phase 5: "Marp slides via @marp-team/marp-core Web Worker
 * -> SVG carousel". The worker keeps the heavy CSS / SVG rendering off
 * the main thread so the Chat tab stays responsive even on a 30-slide
 * deck.
 *
 * Protocol:
 *   main -> worker:  { id: string, markdown: string }
 *   worker -> main:  { id: string, status: "ok", svgs: string[] }
 *                  | { id: string, status: "error", error: string }
 *
 * Each `id` round-trips so the main thread can correlate concurrent
 * render requests (multiple Chat turns rendering at once).
 */

import { Marp } from "@marp-team/marp-core";

interface MarpRenderRequest {
  id: string;
  markdown: string;
}

interface MarpRenderResponseOk {
  id: string;
  status: "ok";
  svgs: string[];
}

interface MarpRenderResponseError {
  id: string;
  status: "error";
  error: string;
}

type MarpRenderResponse = MarpRenderResponseOk | MarpRenderResponseError;

// One Marp instance per worker (~stateless across renders).
const marp = new Marp({
  html: false, // no raw HTML in slides (defense-in-depth; LLM output is markdown only)
  inlineSVG: true,
  emoji: { shortcode: true, unicode: true },
});

/**
 * Render Marp markdown -> array of SVG strings.
 *
 * Marp's `render(markdown)` returns one HTML document containing all
 * slides. We split the slides post-render by parsing the SVG roots
 * out of the HTML (Marp wraps each slide in <svg ...>...</svg>).
 */
function renderToSvgs(markdown: string): string[] {
  const result = marp.render(markdown);
  const html = typeof result === "string" ? result : result.html;
  const svgs: string[] = [];
  const re = /<svg[\s\S]*?<\/svg>/g;
  let m: RegExpExecArray | null;
  while ((m = re.exec(html)) !== null) {
    svgs.push(m[0]);
  }
  return svgs;
}

self.onmessage = (event: MessageEvent<MarpRenderRequest>) => {
  const req = event.data;
  if (!req || typeof req.markdown !== "string") {
    const err: MarpRenderResponseError = {
      id: req?.id ?? "",
      status: "error",
      error: "invalid request: missing markdown",
    };
    (self as unknown as Worker).postMessage(err);
    return;
  }

  try {
    const svgs = renderToSvgs(req.markdown);
    const response: MarpRenderResponseOk = {
      id: req.id,
      status: "ok",
      svgs,
    };
    (self as unknown as Worker).postMessage(response);
  } catch (e) {
    const err: MarpRenderResponseError = {
      id: req.id,
      status: "error",
      error: e instanceof Error ? e.message : String(e),
    };
    (self as unknown as Worker).postMessage(err);
  }
};

export type { MarpRenderRequest, MarpRenderResponse };
