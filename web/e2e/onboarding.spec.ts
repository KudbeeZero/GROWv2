/**
 * Onboarding flow: player creation, API-key reveal, and import-by-key.
 */

import { test, expect } from "./fixtures";

test.describe("create-account flow", () => {
  test("fill form → API-key reveal screen", async ({ page }) => {
    await page.goto("/onboarding");

    await page.getByLabel("Username").fill(`e2e_new_${Date.now()}`);
    await page.getByRole("button", { name: "Create account" }).click();

    await expect(page.getByText("Save your API key now")).toBeVisible();
    await expect(page.getByText("Player ID")).toBeVisible();
    await expect(page.getByText("API key")).toBeVisible();
  });

  test("API-key reveal → enter game navigates to /dashboard", async ({
    page,
  }) => {
    await page.goto("/onboarding");
    await page.getByLabel("Username").fill(`e2e_enter_${Date.now()}`);
    await page.getByRole("button", { name: "Create account" }).click();

    await expect(page.getByText("Save your API key now")).toBeVisible();

    await page.getByRole("button", { name: /I've saved it/ }).click();
    await page.waitForURL("**/dashboard", { timeout: 30_000 });
    await expect(page).toHaveURL(/\/dashboard/);
  });

  test("duplicate username shows an error toast", async ({ page, session }) => {
    await page.goto("/onboarding");
    await page.getByLabel("Username").fill(session.username);
    await page.getByRole("button", { name: "Create account" }).click();

    await expect(
      page.locator(".fixed").filter({ hasText: /already|taken|exist/i }),
    ).toBeVisible();
  });
});

test.describe("import-player flow", () => {
  test("valid credentials sign in and redirect to /dashboard", async ({
    page,
    session,
  }) => {
    await page.goto("/onboarding");
    await page.getByRole("button", { name: "I have a key" }).click();

    await page.getByLabel("Player ID").fill(session.playerId);
    await page.getByLabel("API key").fill(session.apiKey);
    await page.getByRole("button", { name: "Sign in" }).click();

    await page.waitForURL("**/dashboard", { timeout: 30_000 });
    await expect(page).toHaveURL(/\/dashboard/);
  });

  test("wrong player ID shows an error toast", async ({ page }) => {
    await page.goto("/onboarding");
    await page.getByRole("button", { name: "I have a key" }).click();

    await page.getByLabel("Player ID").fill("00000000-0000-0000-0000-000000000000");
    await page.getByLabel("API key").fill("notakey");
    await page.getByRole("button", { name: "Sign in" }).click();

    await expect(
      page.locator(".fixed").filter({ hasText: /not found|error/i }),
    ).toBeVisible();
  });
});

test("authenticated / redirects to /dashboard", async ({ authedPage: page }) => {
  await page.goto("/");
  await page.waitForURL("**/dashboard", { timeout: 30_000 });
  await expect(page).toHaveURL(/\/dashboard/);
});
