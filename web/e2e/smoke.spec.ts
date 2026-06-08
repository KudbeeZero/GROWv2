/**
 * Smoke tests — no auth required.
 * Verify the API is reachable and the frontend redirects unauthenticated users.
 */

import { test, expect } from "./fixtures";

test("unauthenticated / redirects to /onboarding", async ({ page }) => {
  await page.goto("/");
  await page.waitForURL("**/onboarding");
  await expect(page).toHaveURL(/\/onboarding/);
});

test("Flask API root returns 200 with expected shape", async ({ request }) => {
  const resp = await request.get("http://localhost:10000/");
  expect(resp.ok()).toBe(true);
  const json = await resp.json();
  expect(json.name).toBe("GROWv2 API");
  expect(json.endpoints.game).toBe("/api/game");
});

test("strain catalog returns a non-empty list of strains", async ({
  request,
}) => {
  const resp = await request.get("http://localhost:10000/api/game/strains");
  expect(resp.ok()).toBe(true);
  const strains = await resp.json();
  expect(Array.isArray(strains)).toBe(true);
  expect(strains.length).toBeGreaterThan(0);
  // Each strain has the expected fields
  const s = strains[0];
  expect(s).toHaveProperty("id");
  expect(s).toHaveProperty("name");
  expect(s).toHaveProperty("rarity");
});

test("leaderboard endpoint is reachable", async ({ request }) => {
  const resp = await request.get(
    "http://localhost:10000/api/game/leaderboards/richest",
  );
  expect(resp.ok()).toBe(true);
  expect(Array.isArray(await resp.json())).toBe(true);
});

test("/onboarding page renders create/import tabs", async ({ page }) => {
  await page.goto("/onboarding");
  await expect(
    page.getByText("Welcome to GrowPod Empire"),
  ).toBeVisible();
  await expect(page.getByRole("button", { name: "New account" })).toBeVisible();
  await expect(page.getByRole("button", { name: "I have a key" })).toBeVisible();
});
