/**
 * Playwright configuration for JoJo Bot v2.0 frontend smoke tests.
 *
 * Requires: npm i -D @playwright/test
 * Run:      pnpm playwright test tests/e2e/smoke.spec.ts
 *
 * The baseURL targets localhost:8765 (jojo-server proxy, production mode).
 * Override with env var JOJO_BASE_URL=http://localhost:3000 to run against
 * `next dev` directly without the jojo-server proxy.
 */

import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  // Where tests live (relative to this config file).
  testDir: "./tests/e2e",

  // Global test timeout.
  timeout: 30_000,

  // Re-run flaky tests up to 2 extra times so flake rate is observable.
  retries: 2,

  // Test artifacts (traces, screenshots, videos) land here.
  // Resolves to ask_jojo/docs/playwright-results/ from src/frontend/.
  outputDir: "../../docs/playwright-results/",

  // Run tests in a single file sequentially; files in parallel.
  fullyParallel: false,

  // Reporter: list for CI, html for local review.
  reporter: [["list"], ["html", { outputFolder: "../../docs/playwright-results/html-report", open: "never" }]],

  use: {
    baseURL: process.env.JOJO_BASE_URL ?? "http://localhost:8765",

    // Capture trace on first retry to help diagnose flakes.
    trace: "on-first-retry",

    // Screenshot on failure.
    screenshot: "only-on-failure",
  },

  projects: [
    {
      // Single browser pass — Chromium only, as specified.
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
});
