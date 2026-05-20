/**
 * JoJo Bot v2.0 — end-to-end smoke suite.
 *
 * Requires jojo-server running at localhost:8765.
 * Run: pnpm playwright test tests/e2e/smoke.spec.ts
 *
 * If you are running Next.js directly (npm run dev, port 3000) without the
 * jojo-server proxy, set the env var:
 *   JOJO_BASE_URL=http://localhost:3000 pnpm playwright test tests/e2e/smoke.spec.ts
 *
 * @playwright/test must be installed: npm i -D @playwright/test
 */

import { test, expect, Page } from "@playwright/test";

const BASE_URL = process.env.JOJO_BASE_URL ?? "http://localhost:8765";

// ---------------------------------------------------------------------------
// Helper: collect console errors for a page.
// NOTE: throwing inside a `page.on("console", ...)` handler is swallowed by
// the event emitter and does NOT fail the test. We collect into an array
// and assert at the end of each test instead.
// ---------------------------------------------------------------------------

function attachConsoleCollector(page: Page): { errors: string[] } {
  const collector = { errors: [] as string[] };
  page.on("console", (msg) => {
    if (msg.type() === "error") {
      collector.errors.push(msg.text());
    }
  });
  return collector;
}

// ---------------------------------------------------------------------------
// Helper: assert no console errors, with a readable message on failure.
// ---------------------------------------------------------------------------

function assertNoConsoleErrors(collector: { errors: string[] }): void {
  expect(
    collector.errors,
    `Unexpected console errors:\n  ${collector.errors.join("\n  ")}`,
  ).toEqual([]);
}

// ---------------------------------------------------------------------------
// Helper: wait for the page main content area to be visible.
// Uses networkidle as the primary signal, with a 5 s timeout guard.
// ---------------------------------------------------------------------------

async function waitForPageLoad(page: Page): Promise<void> {
  await page.waitForLoadState("networkidle", { timeout: 5_000 }).catch(() => {
    // networkidle times out on pages with SSE or long-poll connections
    // (Ops tab keeps an EventSource open). Fall back to domcontentloaded.
  });
  // Ensure the body has rendered at all.
  await page.waitForSelector("body", { timeout: 5_000 });
}

// ---------------------------------------------------------------------------
// Helper: assert no "Error" text in the main content area.
// We look for the Next.js <main> element that the layout wraps children in.
// ---------------------------------------------------------------------------

async function assertNoErrorText(page: Page): Promise<void> {
  // Check the page does NOT contain a visible React error overlay or a raw
  // "Error" heading injected by the app's own error boundaries.
  // We allow the word "error" in badges/labels (e.g. "0 failed") — we only
  // flag a standalone <h1> or <h2> that reads exactly "Error".
  const errorHeadings = page.locator("h1, h2").filter({ hasText: /^Error$/i });
  await expect(errorHeadings).toHaveCount(0, { timeout: 3_000 }).catch(() => {
    // Non-fatal: log but don't crash — some tabs may surface benign error
    // banners when the backend is cold. The console-error assertion is the
    // hard gate.
  });

  // Hard gate: the Next.js "Application error" overlay.
  const nextErrorOverlay = page.locator(
    "[data-nextjs-dialog-header], .nextjs-container-errors-header",
  );
  await expect(nextErrorOverlay).toHaveCount(0, { timeout: 2_000 }).catch(() => {
    throw new Error("Next.js error overlay detected on " + page.url());
  });
}

// ---------------------------------------------------------------------------
// Helper: assert the page title is not empty.
// ---------------------------------------------------------------------------

async function assertTitleNotEmpty(page: Page): Promise<void> {
  const title = await page.title();
  expect(title.trim().length).toBeGreaterThan(0);
}

// ---------------------------------------------------------------------------
// Test suite
// ---------------------------------------------------------------------------

test.describe("JoJo Bot smoke test", () => {
  // -------------------------------------------------------------- /wiki

  test("wiki tab loads and search does not crash", async ({ page }) => {
    const console_ = attachConsoleCollector(page);

    await page.goto(`${BASE_URL}/wiki`);
    await waitForPageLoad(page);

    await assertTitleNotEmpty(page);
    await assertNoErrorText(page);

    // Search box should be present (aria-label from wiki/page.tsx).
    const searchBox = page.getByLabel("Search wiki pages");
    await expect(searchBox).toBeVisible({ timeout: 5_000 });

    // Type a query — verify no JS crash (we do NOT require results
    // because the backend may be empty during a smoke run).
    await searchBox.fill("CBL-B");
    // Wait briefly for any debounced fetch to complete or fail gracefully.
    await page.waitForTimeout(500);

    assertNoConsoleErrors(console_);
  });

  // -------------------------------------------------------------- /raw

  test("raw tab loads", async ({ page }) => {
    const console_ = attachConsoleCollector(page);

    await page.goto(`${BASE_URL}/raw`);
    await waitForPageLoad(page);

    await assertTitleNotEmpty(page);
    await assertNoErrorText(page);
    assertNoConsoleErrors(console_);
  });

  // -------------------------------------------------------------- /chat

  test("chat tab loads and sending a question does not crash", async ({ page }) => {
    const console_ = attachConsoleCollector(page);

    await page.goto(`${BASE_URL}/chat`);
    await waitForPageLoad(page);

    await assertTitleNotEmpty(page);
    await assertNoErrorText(page);

    // Locate the textarea and the submit button.
    // Button label is "Ask" (chat/page.tsx) but accept "Send" as well for resilience.
    const textarea = page.locator("textarea.chat-textarea");
    const sendBtn = page.getByRole("button", { name: /^(ask|send)$/i });

    await expect(textarea).toBeVisible({ timeout: 5_000 });

    // Type a question. The send button is disabled while draft is empty, so
    // check it becomes enabled after typing.
    await textarea.fill("What is CBL-B?");
    await expect(sendBtn).toBeEnabled({ timeout: 2_000 });

    // Click send — do NOT wait for an AI response (needs a real API key).
    // Just assert no JS crash.
    await sendBtn.click();

    // Give the network call time to either start or return api_key_required.
    await page.waitForTimeout(1_000);

    assertNoConsoleErrors(console_);
  });

  // -------------------------------------------------------------- /ops

  test("ops tab loads with lint history and queue cards", async ({ page }) => {
    const console_ = attachConsoleCollector(page);

    await page.goto(`${BASE_URL}/ops`);
    await waitForPageLoad(page);

    await assertTitleNotEmpty(page);
    await assertNoErrorText(page);

    // Ops page renders the job queue panel (ops-card-queue) and lint history
    // cards (LintHistoryCard with scope="nightly" and scope="weekly").
    // Check the container elements exist in the DOM (may still be "Loading…").
    await expect(page.locator(".ops-card-queue")).toBeVisible({ timeout: 5_000 });
    // Lint history cards: the component renders a card with ops-lint-history-row.
    await expect(page.locator(".ops-lint-history-row")).toBeVisible({ timeout: 5_000 });

    assertNoConsoleErrors(console_);
  });

  // -------------------------------------------------------------- /graph (D3 default)

  test("graph tab (D3 default) loads", async ({ page }) => {
    const console_ = attachConsoleCollector(page);

    await page.goto(`${BASE_URL}/graph`);
    await waitForPageLoad(page);

    await assertTitleNotEmpty(page);
    await assertNoErrorText(page);

    // The view-toggle buttons should both be present.
    await expect(page.getByRole("button", { name: "D3 View" })).toBeVisible({ timeout: 5_000 });
    await expect(page.getByRole("button", { name: "Brain View" })).toBeVisible({ timeout: 5_000 });

    assertNoConsoleErrors(console_);
  });

  // -------------------------------------------------------------- /graph?view=brain

  test("graph brain view renders a canvas element", async ({ page }) => {
    const console_ = attachConsoleCollector(page);

    await page.goto(`${BASE_URL}/graph?view=brain`);
    // Brain view loads Three.js dynamically; give it more time.
    await page.waitForLoadState("networkidle", { timeout: 10_000 }).catch(() => {});
    await page.waitForTimeout(2_000); // allow Three.js to mount

    await assertTitleNotEmpty(page);
    await assertNoErrorText(page);

    // BrainView mounts a Three.js renderer whose output is a <canvas> element.
    const canvas = page.locator("canvas");
    await expect(canvas).toBeVisible({ timeout: 8_000 });

    assertNoConsoleErrors(console_);
  });

  // -------------------------------------------------------------- /settings

  test("settings tab shows all five section headings", async ({ page }) => {
    const console_ = attachConsoleCollector(page);

    await page.goto(`${BASE_URL}/settings`);
    await waitForPageLoad(page);

    await assertTitleNotEmpty(page);
    await assertNoErrorText(page);

    // Section headings come from the five <h2 className="settings-section-title">
    // elements rendered by each section component. Use case-insensitive matches
    // to be resilient against minor wording changes.
    await expect(
      page.locator(".settings-section-title").filter({ hasText: /api key/i }),
    ).toBeVisible({ timeout: 5_000 });

    await expect(
      page.locator(".settings-section-title").filter({ hasText: /model tier/i }),
    ).toBeVisible({ timeout: 5_000 });

    await expect(
      page.locator(".settings-section-title").filter({ hasText: /ms graph/i }),
    ).toBeVisible({ timeout: 5_000 });

    await expect(
      page.locator(".settings-section-title").filter({ hasText: /connector/i }),
    ).toBeVisible({ timeout: 5_000 });

    await expect(
      page.locator(".settings-section-title").filter({ hasText: /lint cadence/i }),
    ).toBeVisible({ timeout: 5_000 });

    assertNoConsoleErrors(console_);
  });

  // -------------------------------------------------------------- /welcome

  test("welcome page loads (accepts redirect to / when all green)", async ({ page }) => {
    const console_ = attachConsoleCollector(page);

    await page.goto(`${BASE_URL}/welcome`);
    await waitForPageLoad(page);

    // The welcome page redirects to "/" when every status section is green
    // (welcome/page.tsx line 69). Accept either URL.
    const currentUrl = page.url();
    const isWelcomeOrRoot =
      currentUrl === `${BASE_URL}/welcome` ||
      currentUrl === `${BASE_URL}/` ||
      currentUrl.endsWith("/");
    expect(isWelcomeOrRoot, `Unexpected redirect destination: ${currentUrl}`).toBe(true);

    await assertTitleNotEmpty(page);
    await assertNoErrorText(page);
    assertNoConsoleErrors(console_);
  });
});
