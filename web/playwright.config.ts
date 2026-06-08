import { defineConfig, devices } from "@playwright/test";

// Both servers must be reachable before tests start.
const backendUrl = "http://localhost:10000";
const webUrl = "http://localhost:3000";

export default defineConfig({
  testDir: "./e2e",
  // Generous per-test budget: first navigation still pays for React hydration.
  timeout: 90_000,
  expect: { timeout: 30_000 },
  retries: process.env.CI ? 2 : 0,
  // Single worker: tests share a SQLite backend — serial avoids row-level races.
  workers: 1,
  reporter: [["list"], ["html", { open: "never" }]],

  use: {
    baseURL: webUrl,
    trace: "on-first-retry",
    screenshot: "only-on-failure",
  },

  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],

  webServer: [
    {
      // Fresh SQLite DB + migrations + catalog seed, then Flask on :10000.
      command: "bash ../scripts/start-e2e-backend.sh",
      url: backendUrl,
      timeout: 90_000,
      reuseExistingServer: !process.env.CI,
    },
    {
      // Production build, not `next dev`: the app's CSP allows 'unsafe-inline'
      // scripts but NOT 'unsafe-eval', and dev-mode webpack/HMR relies on eval()
      // — under the CSP that blocks every script, so the app never hydrates and
      // pages hang on "Loading session…". `next build && next start` emits no
      // eval, hydrates correctly, and is what actually ships. It also serves
      // every route precompiled, so no dev-route warmup is needed.
      command: "npm run build && npm run start",
      url: webUrl,
      timeout: 180_000,
      reuseExistingServer: !process.env.CI,
    },
  ],
});
