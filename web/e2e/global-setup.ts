/**
 * Pre-warm the Next.js dev server before any browser tests run.
 *
 * Problem: in dev mode Next.js compiles each route's JS chunks lazily — only
 * when a browser downloads them. Without a warmup pass, the very first test
 * to visit a route waits for on-demand compilation (10-30 s), blowing through
 * the default expect.timeout.
 *
 * Solution: launch a throw-away Chromium instance, inject a real player
 * session (so RequireAuth pages render instead of redirecting), visit every
 * protected route, and wait for React hydration to complete. By the time
 * actual tests run, all bundles are compiled and cached.
 *
 * Playwright starts webServers before globalSetup, so both the Flask API and
 * the Next.js dev server are already running when this function is called.
 */

import { chromium } from "@playwright/test";

const BACKEND = "http://localhost:10000/api/game";
const FRONTEND = "http://localhost:3000";

export default async function globalSetup() {
  // ------------------------------------------------------------------
  // 1. Create a throw-away player so protected routes can hydrate fully.
  // ------------------------------------------------------------------
  const res = await fetch(`${BACKEND}/players`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username: `warmup_${Date.now()}`, email: null }),
    signal: AbortSignal.timeout(30_000),
  });
  const player = (await res.json()) as { id: string; api_key: string };

  // ------------------------------------------------------------------
  // 2. Navigate every route with auth so JS chunks fully compile.
  // ------------------------------------------------------------------
  const browser = await chromium.launch();
  const context = await browser.newContext();

  // Inject the warmup player's session before any navigation.
  await context.addInitScript(
    ({ playerId, apiKey }) => {
      localStorage.setItem("gpe.player_id", playerId);
      localStorage.setItem("gpe.api_key", apiKey);
    },
    { playerId: player.id, apiKey: player.api_key },
  );

  const page = await context.newPage();

  const routes = [
    "/onboarding",
    "/dashboard",
    "/lab",
    "/market",
    "/leaderboards",
    "/account",
    "/contracts",
  ];

  for (const route of routes) {
    try {
      await page.goto(`${FRONTEND}${route}`, {
        waitUntil: "domcontentloaded",
        timeout: 90_000,
      });
      // Wait for React hydration — SessionProvider.useEffect fires, sets
      // hydrated=true, and RequireAuth shows content (not the loading spinner).
      await page
        .waitForFunction(
          () => !document.body.textContent?.includes("Loading session"),
          { timeout: 60_000 },
        )
        .catch(() => {});
    } catch {
      // Errors during warmup don't block tests — just log them.
    }
  }

  await browser.close();
}
