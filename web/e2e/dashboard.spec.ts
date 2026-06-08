/**
 * Dashboard: authenticated view, pod creation form, and pod card rendering.
 */

import { test, expect, waitForHydration } from "./fixtures";

test.describe("dashboard", () => {
  test("renders the Grow Dashboard heading", async ({ authedPage: page }) => {
    await page.goto("/dashboard");
    await waitForHydration(page);
    await expect(
      page.getByRole("heading", { name: "Grow Dashboard" }),
    ).toBeVisible();
  });

  test("unauthenticated visit redirects to /onboarding", async ({ page }) => {
    await page.goto("/dashboard");
    // RequireAuth redirects once React hydrates and isAuthed=false.
    await page.waitForURL("**/onboarding", { timeout: 30_000 });
    await expect(page).toHaveURL(/\/onboarding/);
  });

  test("'+ New Pod' reveals the create-pod form", async ({
    authedPage: page,
  }) => {
    await page.goto("/dashboard");
    await waitForHydration(page);
    // The header and the empty-state both expose a "+ New Pod" button; the
    // header one toggles the create form.
    await page.getByRole("button", { name: "+ New Pod" }).first().click();
    await expect(
      page.getByRole("heading", { name: "Create a grow pod" }),
    ).toBeVisible();
    // Form fields
    await expect(page.getByLabel("Pod name")).toBeVisible();
    await expect(page.getByLabel("Tier")).toBeVisible();
  });

  test("create pod via UI → pod card appears on dashboard", async ({
    authedPage: page,
  }) => {
    await page.goto("/dashboard");
    await waitForHydration(page);
    // The header and the empty-state both expose a "+ New Pod" button; the
    // header one toggles the create form.
    await page.getByRole("button", { name: "+ New Pod" }).first().click();

    const nameInput = page.getByLabel("Pod name");
    await nameInput.clear();
    await nameInput.fill("E2E Tent Alpha");

    await page.getByRole("button", { name: "Create Pod" }).click();

    // Success toast and pod card with the pod's name should appear.
    await expect(page.getByText("E2E Tent Alpha")).toBeVisible({
      timeout: 15_000,
    });
  });

  test("empty pod shows 'plant a seed' prompt", async ({
    authedPage: page,
    session,
    request,
  }) => {
    // Create pod via API to avoid spending balance on UI flows.
    const podResp = await request.post(
      `http://localhost:10000/api/game/players/${session.playerId}/pods`,
      {
        headers: {
          "X-API-Key": session.apiKey,
          "Content-Type": "application/json",
        },
        data: { name: "Empty Pod E2E", tier: "basic", capacity: 4 },
      },
    );
    expect(podResp.ok()).toBe(true);

    await page.goto("/dashboard");
    await waitForHydration(page);
    await expect(page.getByText("Empty Pod E2E")).toBeVisible({
      timeout: 15_000,
    });
    await expect(
      page.getByText(/plant a seed to get growing/i),
    ).toBeVisible();
  });
});
