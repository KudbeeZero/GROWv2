import { defineConfig, devices } from "@playwright/test";

// Both servers must be reachable before tests start.
const backendUrl = "http://localhost:10000";
const webUrl = "http://localhost:3000";

export default defineConfig({
  testDir: "./e2e",
  // Pre-warm all Next.js dev routes before any browser tests run.
  globalSetup: "./e2e/global-setup.ts",
  // Dev-mode page compilation + React hydration can take 20-30s on a cold server.
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
      // Next.js dev server on :3000. API_BASE defaults to :10000 in client.ts.
      command: "npm run dev",
      url: webUrl,
      timeout: 60_000,
      reuseExistingServer: !process.env.CI,
    },
  ],
});
