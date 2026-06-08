/**
 * Shared Playwright fixtures and API helpers for GROWv2 e2e tests.
 *
 * authedPage — a Page with localStorage already seeded with a fresh player's
 *   id + api_key, so RequireAuth pages load without hitting /onboarding.
 *
 * session  — the raw { playerId, apiKey, username } for direct API calls.
 */

import {
  test as base,
  type APIRequestContext,
  type Page,
} from "@playwright/test";

export { expect } from "@playwright/test";

export const API_GAME = "http://localhost:10000/api/game";

/**
 * Wait for React to complete client-side hydration on RequireAuth-gated pages.
 *
 * RequireAuth shows "Loading session…" while `!hydrated`. Once SessionProvider's
 * useEffect fires, hydrated becomes true and the spinner disappears. Calling this
 * after page.goto() avoids assertion races on first page load in dev mode.
 */
export async function waitForHydration(page: Page) {
  await page
    .waitForFunction(() => !document.body.textContent?.includes("Loading session"), {
      timeout: 30_000,
    })
    .catch(() => {}); // not all pages use RequireAuth — ignore if already gone
}

export interface PlayerSession {
  playerId: string;
  apiKey: string;
  username: string;
}

export async function createApiPlayer(
  request: APIRequestContext,
): Promise<PlayerSession> {
  const username = `e2e_${Date.now()}`;
  const resp = await request.post(`${API_GAME}/players`, {
    data: { username, email: null },
  });
  const player = await resp.json();
  return {
    playerId: player.id,
    apiKey: player.api_key,
    username: player.username,
  };
}

/** Seed a pod + seed + planted plant via the API and return them. */
export async function apiPlant(
  request: APIRequestContext,
  session: PlayerSession,
  podName = `Pod_${Date.now()}`,
) {
  const pod = await (
    await request.post(`${API_GAME}/players/${session.playerId}/pods`, {
      headers: authHeaders(session),
      data: { name: podName, tier: "basic", capacity: 4 },
    })
  ).json();

  const strains = await (await request.get(`${API_GAME}/strains`)).json();

  await request.post(`${API_GAME}/players/${session.playerId}/seeds/buy`, {
    headers: authHeaders(session),
    data: { strain_id: strains[0].id, quantity: 1 },
  });

  const seeds = await (
    await request.get(`${API_GAME}/players/${session.playerId}/seeds`, {
      headers: authHeaders(session),
    })
  ).json();

  const plant = await (
    await request.post(`${API_GAME}/players/${session.playerId}/plant`, {
      headers: authHeaders(session),
      data: { seed_id: seeds[0].id, pod_id: pod.id },
    })
  ).json();

  return { pod, plant };
}

function authHeaders(session: PlayerSession) {
  return {
    "X-API-Key": session.apiKey,
    "Content-Type": "application/json",
  };
}

// ---------------------------------------------------------------------------
// Extended test fixture
// ---------------------------------------------------------------------------

export const test = base.extend<{
  session: PlayerSession;
  authedPage: Page;
}>({
  session: async ({ request }, use) => {
    const s = await createApiPlayer(request);
    await use(s);
  },

  authedPage: async ({ page, session }, use) => {
    // addInitScript runs before any page script — localStorage is populated
    // before React hydrates, so RequireAuth sees the session immediately.
    await page.addInitScript(({ playerId, apiKey }) => {
      localStorage.setItem("gpe.player_id", playerId);
      localStorage.setItem("gpe.api_key", apiKey);
    }, session);
    await use(page);
  },
});
