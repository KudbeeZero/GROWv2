# Visual QA — plant rendering + crossbreeding (2026-06-10)

Ran the real game (prod web build + backend on a throwaway DB), forced a plant through every growth
stage, captured screenshots, and smoke-tested crossbreeding. Screenshots in
[`screenshots/`](screenshots/) — each stage has `<name>.png` (tight crop of the plant SVG) and
`<name>-page.png` (full plant-detail page).

## What a plant looks like in the UI
A **hand-drawn inline SVG** (`web/src/components/plant/PlantVisual.tsx`) — not sprite art, canvas, or
the constellation. It's a brown pot + soil ellipse, green stem, 5 leaf ellipses, and (flowering/harvest
only) 3 flower-bud circles. Body scaled by stage via a `STAGE_SCALE` map; CSS-animated/tinted by
condition. The full detail page is genuinely rich: the SVG plant card + "Healthy" badge, scientist
readouts (VPD/DLI/PPFD/photoperiod gauges), Health/Water/Nutrients vitals bars, Care buttons, an "AI
Master Grower" panel, and an event log.

Condition rendering is distinct and works well:
- **Drooping/underwatered** — leaves tinted yellow-tan (`#cdbb6a`).
- **Pests** — dark beetle dots across the leaves.
- **Mildew** — white/grey powdery circles on leaves and buds.

## Bugs found (verified)
1. ✅ **FIXED — `flowering.png` == `harvest.png`.** `PlantVisual.tsx` was rebuilt; harvest now shows
   fattened, frosted (trichome), amber-pistilled colas. Confirmed distinct by md5 — see the "after"
   shots in [`screenshots/after-render/`](screenshots/after-render/) (`flowering.png` ≠ `harvest.png`).
2. ✅ **FIXED — early stages shared one silhouette.** The rebuilt render gives each stage its own
   structure: seed = sprout, germination = cotyledons + first leaves, seedling = small, vegetative =
   bushy. (Original "before" shots remain in [`screenshots/`](screenshots/) as the bug record.)
3. **The breed *API* path is not reproducible for a fixed `rng_seed`** (still open) — the genetics engine
   (`genetics/breeding.cross`) IS deterministic (same seed → byte-identical 13-trait genome, verified
   for seeds 42 and 777), but two `POST /players/{id}/breed` calls with `rng_seed=777` returned
   different THC (19.74 vs 18.99), neither matching the pure-engine value (20.25). Something in the
   service path (likely the breeding-fee ledger `post` or a research lookup) advances/derives RNG
   before `cross()` runs. **The "deterministic with a fixed seed" guarantee currently holds only at the
   engine layer, not the API layer.** *Fix: seed `cross()`'s RNG from the persisted `rng_seed`
   independently of any other RNG use in the request path; add an API-level reproducibility test.*

No console errors in the production build.

## Crossbreeding smoke — PASS (with the caveat above)
`POST /players/{id}/breed` produces a named offspring ("Blue Dream x Pineapple Express"), correct
rarity, generation=1, full genome, and grants a bred seed. The load-bearing engine determinism holds.

## Run note (not a bug — already documented)
`npm run dev` leaves authed pages stuck on "Loading session…": dev-mode HMR uses `eval()` but the CSP
in `next.config.mjs` omits `'unsafe-eval'`, so the dev runtime is CSP-blocked and hydration dies. Use
the **production** build (`npm run build && npm run start`) — which is what ships. (Documented in
`web/playwright.config.ts`.)

## Suggested follow-ups (small, high-value)
- Distinct HARVEST and seed/sprout visuals in `PlantVisual.tsx` (bugs 1 & 2) — pure web, ~half a day.
- API-layer breeding reproducibility fix + test (bug 3) — small backend change; matters because
  determinism is a core invariant (see ENGINEERING_PLAYBOOK.md).
