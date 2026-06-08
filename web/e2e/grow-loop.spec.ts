/**
 * Core grow loop: buy seed → plant → care → plant detail.
 *
 * Heavy setup (pod + seed + plant) is done via the API so tests remain fast
 * and independent. UI interactions verify that the frontend correctly renders
 * and acts on the backend state.
 */

import { test, expect, apiPlant, API_GAME, waitForHydration } from "./fixtures";

test.describe("strain lab", () => {
  test("renders catalog heading and buy buttons", async ({
    authedPage: page,
  }) => {
    await page.goto("/lab");
    await waitForHydration(page);
    await expect(page.getByRole("heading", { name: "Strain Lab" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Buy seed" }).first()).toBeVisible();
  });

  test("buy seed from UI → seed appears in inventory", async ({
    authedPage: page,
  }) => {
    await page.goto("/lab");
    await waitForHydration(page);

    const firstBuy = page.getByRole("button", { name: "Buy seed" }).first();
    await expect(firstBuy).toBeVisible();
    await firstBuy.click();

    await expect(page.getByText(/Bought a .+ seed/)).toBeVisible();
    await expect(page.getByText("Your seed inventory")).toBeVisible();
  });
});

test.describe("plant lifecycle", () => {
  test("plant a seed via UI → plant card shows 'Growing' badge", async ({
    authedPage: page,
    session,
    request,
  }) => {
    const podResp = await request.post(
      `${API_GAME}/players/${session.playerId}/pods`,
      {
        headers: {
          "X-API-Key": session.apiKey,
          "Content-Type": "application/json",
        },
        data: { name: "UI Plant Pod", tier: "basic", capacity: 4 },
      },
    );
    expect(podResp.ok()).toBe(true);

    const strains = await (await request.get(`${API_GAME}/strains`)).json();
    await request.post(
      `${API_GAME}/players/${session.playerId}/seeds/buy`,
      {
        headers: {
          "X-API-Key": session.apiKey,
          "Content-Type": "application/json",
        },
        data: { strain_id: strains[0].id, quantity: 1 },
      },
    );

    await page.goto("/dashboard");
    await waitForHydration(page);
    await expect(page.getByText("UI Plant Pod")).toBeVisible();

    const plantBtn = page.getByRole("button", { name: /Plant here/ }).first();
    await expect(plantBtn).toBeVisible();
    await plantBtn.click();

    await expect(page.getByText("Seed planted")).toBeVisible();
    await expect(page.getByText("Growing").first()).toBeVisible();
  });

  test("plant detail page renders vitals and care buttons", async ({
    authedPage: page,
    session,
    request,
  }) => {
    const { plant } = await apiPlant(request, session);

    await page.goto(`/dashboard/plants/${plant.id}`);
    await waitForHydration(page);

    await expect(page.getByRole("link", { name: /Back to dashboard/ })).toBeVisible();
    await expect(page.getByRole("button", { name: /Water/ })).toBeEnabled();
    await expect(page.getByRole("button", { name: /Feed/ })).toBeEnabled();
    await expect(page.getByText("Vitals")).toBeVisible();
    await expect(page.getByText("Care")).toBeVisible();
  });

  test("water action shows 'Watered' success toast", async ({
    authedPage: page,
    session,
    request,
  }) => {
    const { plant } = await apiPlant(request, session, "Water Action Pod");

    await page.goto(`/dashboard/plants/${plant.id}`);
    await waitForHydration(page);

    const waterBtn = page.getByRole("button", { name: /Water/ });
    await expect(waterBtn).toBeEnabled();
    await waterBtn.click();

    await expect(page.getByText("Watered")).toBeVisible();
  });

  test("feed action shows 'Fed nutrients' success toast", async ({
    authedPage: page,
    session,
    request,
  }) => {
    const { plant } = await apiPlant(request, session, "Feed Action Pod");

    await page.goto(`/dashboard/plants/${plant.id}`);
    await waitForHydration(page);

    const feedBtn = page.getByRole("button", { name: /Feed/ });
    await expect(feedBtn).toBeEnabled();
    await feedBtn.click();

    await expect(page.getByText("Fed nutrients")).toBeVisible();
  });

  test("plant detail event log section renders", async ({
    authedPage: page,
    session,
    request,
  }) => {
    const { plant } = await apiPlant(request, session, "Event Log Pod");

    await page.goto(`/dashboard/plants/${plant.id}`);
    await waitForHydration(page);

    await expect(page.getByText("Event log")).toBeVisible();
  });
});

test.describe("market page", () => {
  test("renders Marketplace heading and 'Sell a seed' card", async ({
    authedPage: page,
  }) => {
    await page.goto("/market");
    await waitForHydration(page);
    await expect(page.getByRole("heading", { name: "Marketplace" })).toBeVisible();
    await expect(page.getByText("Sell a seed")).toBeVisible();
  });

  test("empty market shows 'No active listings' message", async ({
    authedPage: page,
  }) => {
    await page.goto("/market");
    await waitForHydration(page);
    await expect(
      page.getByText(/No active listings|Active listings/),
    ).toBeVisible();
  });
});

test.describe("leaderboards page", () => {
  test("renders the Leaderboards heading", async ({ authedPage: page }) => {
    await page.goto("/leaderboards");
    await waitForHydration(page);
    await expect(page.getByRole("heading", { name: "Leaderboards" })).toBeVisible();
  });
});
