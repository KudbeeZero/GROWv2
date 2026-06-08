# Backlog (Layer 3) — single source of priority

Status: `⬜ todo · 🔨 doing · ✅ done · ❄️ parked`. Standups may *propose* items; they're only real
once they appear here. Last reconciled: **2026-06-08**.

## 🔴 Immediate (do now — correctness, truth, or unblocks others)
- ✅ Add `CLAUDE.md` + `docs/memory/` memory-layer system (this change).
- 🔴 ⬜ **Reconcile `docs/ROADMAP.md` with reality** — Sprints 1–3 are shipped but still show
  ⬜/🔨. Planning is reading a map that lies. *(partially fixed 2026-06-08; verify exit criteria)*
- 🔴 ⬜ **Retire/replace `docs/NEXT_SESSION_SPRINT3.md`** — Sprint 3 is done; the handoff is stale.
- 🔴 ⬜ **Fix `BUILDLOG.md` header** referencing the old trunk branch
  `claude/cannabis-game-lut-economics-utfiK`. *(fixed 2026-06-08 — keep an eye on drift)*
- ✅ **Repair the dev env install** (2026-06-08) — added `Makefile` (`make setup` = venv-based
  install, sidesteps the system-PyYAML collision), a `pyproject.toml` build backend so
  `pip install -e .` uses PEP 660 (no more legacy `install_layout` crash), and a
  `.claude/hooks/session-start.sh` SessionStart hook so web sessions install deps automatically
  (sets `PYTHONPATH=src`, mirroring CI). Validated: hook exit 0, `make setup && make test` →
  139 passed.

- 🔴 ✅ **Memory-integrity gate** (2026-06-08) — `scripts/check_memory.py` + `make check-memory` +
  a CI step fail on broken internal links, ✅ claims citing missing paths, or a codex that drifts out
  of the layer map. Plus a master `docs/memory/MAP.md` (layer map + code↔doc index + moat dashboard);
  ARCHITECTURE invariant #9 + two DECISIONS entries (Phase A, provable fairness) reconcile the layers
  with this session's code. *(Partly delivers the "docs-drift check" from the 2026-06-08 standup §4A.)*

## 🟠 Medium (next 1–2 weeks — quality & the next real capability)
- 🟠 ✅ **CI coverage gate** (2026-06-08) — `pytest --cov` with a ratchet floor (`pyproject.toml`
  `fail_under=78`, ops scripts omitted), wired into `make test` + CI. Completes the "make truth
  automatic" trio (lint + memory-integrity + coverage). *Ratchet the floor up as coverage climbs.*
- 🟠 ⬜ **Sprint 4: real TestNet + IPFS** — fund treasury, run `reset_asa`, wire `ASA_ID`; move NFT
  metadata to IPFS; add a DB↔chain reconciliation job + `onchain_txid` audit.
- 🟠 ⬜ **Sim cost cap** — bound compute-on-read catch-up; batch/materialize dormant plants.
- 🟠 ⬜ **Idempotency keys on mutations** — protect ledger/economy from double-submits & retries.
- 🟠 ⬜ **Load/soak test the `/state` catch-up path** to find the cost knee before players do.
- 🟠 ⬜ **Web e2e smoke** (Playwright) over the full loop; today web CI is lint/typecheck/build only.
- 🟠 ✅ **Sim depth — Phase A (derive VPD + DLI; wire the stored light scalar into the tick).** Done
  2026-06-08: `simulation/horticulture.py` (VPD/DLI/SVP), light + VPD health terms in `engine.py`
  (tuned in `balance.yaml`), VPD/DLI/PPFD exposed on `/state`. +8 tests (147 total, green). *Next:*
  Phase B (photosynthesis + transpiration + EC/pH→uptake) — land the sim-cost-cap first.

## 🟡 Low / later (valuable, not urgent)
- 🟡 ⬜ Sprint 5 multiplayer: P2P trading, friends, co-op rooms, anti-cheat hardening.
- 🟡 ⬜ Sprint 6 LiveOps: seasonal strains rotation, timed events, breeding competitions, admin
  console with hot-reload `balance.yaml`, analytics/telemetry.
- 🟡 ⬜ Non-custodial Pera/WalletConnect path for player-owned NFTs.
- 🟡 ⬜ Observability upgrade: logs → metrics → traces as traffic grows.
- 🟡 ⬜ Secrets management hardening before any real value (encrypt keys at rest / secrets manager).
- 🟡 ⬜ Age-gating/compliance + ToS/privacy review (simulated cannabis only).
- 🟡 ⬜ **Generative genetics** — polygenic genome + mutation/epistasis/G×E toward endless,
  *discovered* strains; genome fingerprint → on-chain GenBank + Proof-of-Cultivation (needs Sprint 4
  chain). Per `docs/memory/design/02-genetics.md`.
- 🟡 ⬜ **Grower-skill mastery** — use-based skill trees (effort/time → capability), distinct from the
  spend-based research tree; the equipment bridge. Per `docs/memory/design/03-grower-skills.md`.
- 🟡 🔨 **Trust layer** — provable fairness landed for breeding (`/strains/<id>/provenance`) and the
  whole pedigree (`/strains/<id>/lineage`, the GenBank's verifiable family tree). Remaining: generalize
  replay to sim/weather/discovery, a genome fingerprint, a public faucet-vs-sink economy view, advisor
  confidence/uncertainty surfacing, and a no-dark-patterns charter. Per `docs/memory/design/04-honesty-and-trust.md`.

- 🟡 ✅ **Strain knowledge base** (2026-06-08) — catalog grown 16→22 (iconic landraces/classics) +
  `data/strain_knowledge.yaml`, a scientist-grade encyclopedia (lineage, origin, cannabinoid/terpene
  detail, cultivation params) for every catalog strain, at public `GET /strains/<id>/knowledge`. A
  test enforces 1:1 catalog↔KB sync.
- 🟡 ✅ **Deep-research campaign** (2026-06-08) — `docs/research/2026-06-08-cannabis-strain-genetics-and-cultivation.md`:
  5-agent, peer-reviewed-prioritized reference on lineage, chemotype, cultivation, agronomy, and
  taxonomy/genetics. Reconciled into the KB (disputed-lineage flags + scientific caveats header).
- 🟡 ⬜ **KB enrichment pass (research-grounded)** — add a `terpene_cluster` per strain (myrcene /
  terpinolene / limonene-caryophyllene); model assayed THC as an inflation-biased distribution; wire
  the PPFD/DLI→yield relationship into the sim (Phase B). Per the research doc's §6 action items.
- 🟡 ✅ **Seasonal Cannabis Cup** (2026-06-08) — `services/cup_service.py` + `CannabisCup`/`CupEntry`
  models + migration `d5e6f7a8b9c0`: per-season competition, deterministic `cup_score`, lifetime
  champion rewards (one-of-a-kind legendary trophy strain + permanent title + Hall of Fame). Public
  `/cup/*` + authed enter; +9 tests. *Next (⬜): on-chain trophy NFT (Sprint 4), judged terpene-cluster
  categories, grower-reputation tie-in.* Per `docs/memory/design/05-events-and-competition.md`.
- 🟠 ✅ **CI: enforce a single Alembic head** (2026-06-08) — `scripts/check_single_head.py` (reads the
  migration graph via `ScriptDirectory`, fails with an actionable `alembic merge` hint on a fork),
  wired into `make check-migrations` + a CI step before `alembic upgrade head`. Catches the fork class
  of bug (e.g. the old `fbb8fceedacd` fork) automatically instead of by manual testing.
- 🟡 ✅ **GrowPod University** (2026-06-08) — `services/university_service.py` + `lecturer_service.py`
  + `data/curriculum.yaml` + `CourseEnrollment`/`DegreeProgress` + migration `e7a9c1b3f2d8`: enroll
  (tuition sink) → time + practical study → degrees (permanent perks via the research effect keys +
  a title + XP), taught by an AI Professor (mock for CI, Claude in prod). Public `/university/catalog`
  + authed enroll/complete/claim/lecture; +13 tests. Grounded in a cited curriculum research report.
  *Next (⬜): quizzes, more departments, Doctorate tier, diploma NFTs.* Per `docs/memory/design/06-university.md`.
- 🟡 ✅ **Web client — full UI build** (2026-06-08, branch `claude/growv2-web-ui-build-MZWZE`) — the
  Next 15 client now covers all seven screen groups (onboarding hero · grow dashboard with VPD/DLI/PPFD
  · strain lab + encyclopedia + DNA/lineage constellations + Verify provenance · GenBank galaxy ·
  market fixed/auctions/contracts · Cannabis Cup + Hall of Fame · University catalog/transcript/course
  + AI Professor lecture reader · Profile with lifetime titles). Centerpiece: dependency-free
  `web/src/components/viz/Constellation.tsx` (the genetic-constellation signature language). Green
  typecheck/lint/build + live-API contract smoke. Post-build cleanup: fixed a Constellation
  stale-deps bug (genome graphs reused locus ids across strains → now keyed on content + edges),
  hex-sanitized canvas colors + position clamp, retired `/account`+`/contracts` → redirects, and an
  a11y pass (Modal Escape/`role=dialog`, ARIA tabs, `aria-pressed` chips, input/select labels,
  reduced-motion). Follow-up pass: **constellation perf** (O(n²) repulsion → uniform spatial-hash
  grid, semantics preserved) and a **Vitest unit-test harness** (71 tests over `format.ts` +
  `graphAdapters.ts`, `pool: forks` for sandbox/CI robustness, wired into web CI). See standup
  `2026-06-08-lut-report-web-ui-build.md`.
- 🟠 ✅ **Web e2e smoke (Playwright)** (2026-06-08) — mocked-API Playwright suite (`web/e2e/`,
  `playwright.config.ts`) over onboarding + authed dashboard + university; `test:e2e` script + a CI
  `e2e` job. It immediately caught **two real browser-only bugs**, both fixed: (1) the CSP
  `script-src 'self'` blocked Next's inline hydration scripts so the app blanked in-browser — fixed
  by allowing `'unsafe-inline'` for scripts (sources still locked to self, eval still blocked);
  (2) the dashboard's Zustand selector returned a fresh `[]` each render → React #185 infinite loop
  that crashed the page for players with no locally-stored ids — fixed with a stable reference.
- 🟡 ⬜ **Education-gated Master Grower knowledge** (owner idea, 2026-06-08) — tie advisor depth +
  unlocks (tips/tricks, rare bio-DNA traits, breeding **pollen**, "DNA-in-the-seed") to University
  progress. Composes existing systems: degree perks (research effect keys) raise an advisor knowledge
  tier and unlock breeding consumables that bias the still-seeded, provably-fair cross. Needs a design
  doc + balance pass; no new infra.
- 🟡 ⬜ **Sponsored / branded content (revenue)** (owner idea, 2026-06-08) — real cannabis brands
  sponsoring cultivars, branded equipment/pods, and promotions, using the on-chain asset layer to
  sidestep traditional ad/banking restrictions. A "sponsored cultivar" is a GenBank entry with
  verifiable provenance + brand tag. Needs a partner/content model + a no-dark-patterns guardrail
  (ties into the trust layer charter). Business/LiveOps track.

## ✅ Recently shipped (2026-06-07) — see standup 2026-06-08
Foundation P1–P3; Wave 0 retention; Wave 1 hardening (auth/errors/health/CI/docker/openapi);
Wave 2 depth (search, leaderboards, auctions, weather, automation, stabilization, ASA settlement,
contracts); Wave 3 property tests; Sprint 3 web client; security audit (#4); game expansion (#6:
auction-exploit fix, legacy removal, curing/terpenes, research tree/shop/seasons, AI advisor +
agentic auto-care); manual/docs suite (#5).
