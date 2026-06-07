# GROWv2 — 90-Day Roadmap

A cannabis-growing game with a persistent economy, real genetics/crossbreeding, a real-time grow
simulation, and an Algorand on-chain asset layer. Phases 1–3 (DB + economy, simulation, on-chain
ASA/NFT) are built and tested. This roadmap takes it from "working backend" to "production game."

**Legend:** ✅ done · 🔨 in progress · ⬜ planned. Each sprint is ~2 weeks with explicit exit
criteria. "Roles" are functional hats, not headcount.

---

## Foundation (shipped) ✅
- ✅ Persistent DB (SQLAlchemy + Alembic; SQLite dev, Postgres prod)
- ✅ Ledger-based economy (Decimal money, auditable, anti-inflation sinks)
- ✅ Strain genetics + deterministic crossbreeding
- ✅ Real-time grow simulation (overwatering/pests/disease/health, compute-on-read)
- ✅ Algorand provider abstraction: ASA token + ARC-3 NFT minting (TestNet, mock for tests)
- ✅ Retention: daily stipend + achievements; player XP/leveling

---

## Sprint 1 — Harden the core (Days 1–14) 🔨
**Goal:** the backend is safe to expose publicly.
- 🔨 Per-player **API-key auth** on write endpoints (reads stay public)
- ⬜ Uniform **error envelope** + global 400/404/405/500 handlers + input validation
- ⬜ **Health/readiness** probes, structured logging w/ request IDs, request timing
- ⬜ **CI** (GitHub Actions): lint + pytest + `alembic upgrade head` on every PR
- ⬜ **Docker** + docker-compose (api + Postgres); gunicorn in prod
- ⬜ **OpenAPI 3** spec at `/openapi.json` + Swagger UI at `/docs`
- **Exit:** CI green on PRs; image boots against Postgres; `/docs` lists every route; auth enforced.

## Sprint 2 — Gameplay depth (Days 15–28) ⬜
**Goal:** the game is fun to play through an API/CLI.
- ⬜ Strain **search/filter** + favorites
- ⬜ **Leaderboards** (richest, top breeders, biggest harvest, highest level)
- ⬜ **Market auctions** (bids, expiry, highest-bidder settlement)
- ⬜ **Weather events** feeding the sim (heatwave, humidity spike, cold snap)
- ⬜ **Pod automation** (tiers grant auto-water/feed)
- ⬜ **Strain stabilization** (selfing/backcross → unlock NFT mint)
- ⬜ **NPC contracts/orders** (deliver N grams by deadline for GROW + XP)
- **Exit:** a full play-loop (grow → care → harvest → sell/breed/stabilize → mint → trade) via API.

## Sprint 3 — Web frontend, client v1 (Days 29–42) ⬜
**Goal:** players can *see* their grow react in real time.
- ⬜ React/Next app; wallet connect; auth
- ⬜ Pod & plant dashboards rendering live `condition_flags` (drooping leaves, bugs, mildew, height,
  health bars) from `GET /plants/<id>/state`
- ⬜ Market, breeding lab, strain catalog, leaderboards UIs
- ⬜ Real-time updates (polling first, websockets later)
- **Exit:** a player completes the full loop in-browser; plant visuals change with sim state.

## Sprint 4 — Real TestNet + IPFS (Days 43–56) ⬜
**Goal:** assets are really on-chain.
- ⬜ Fund a TestNet treasury; run `reset_asa`; wire `ASA_ID`
- ⬜ Move NFT metadata to **IPFS** (Pinata/web3.storage); image pipeline for cards
- ⬜ DB ↔ chain **reconciliation** job; `onchain_txid` audit
- ⬜ Non-custodial **Pera/WalletConnect** path (transfer NFT to player's own opted-in account)
- **Exit:** mint a real TestNet NFT end-to-end; balances reconcile; metadata resolves on IPFS.

## Sprint 5 — Multiplayer & social (Days 57–70) ⬜
**Goal:** players interact safely.
- ⬜ Player-to-player **trading**, friends, co-op grow rooms, basic chat
- ⬜ **Server-authoritative** review of sim/economy (no client-trusted state) + anti-cheat
- ⬜ **Rate limiting** + abuse controls; idempotency keys on mutations
- **Exit:** two accounts trade and co-grow; load test shows no economy exploits.

## Sprint 6 — LiveOps & tournaments (Days 71–84) ⬜
**Goal:** repeatable engagement.
- ⬜ Seasonal/limited strains; timed events; breeding **competitions**
- ⬜ Seasonal leaderboards; **analytics/telemetry**; data-driven balance passes
- ⬜ Admin/LiveOps console for content + balance (hot-reload `balance.yaml`)
- **Exit:** run a 1-week event end-to-end with rewards and a season reset.

## Launch readiness (Days 85–90) ⬜
- ⬜ **Load & soak testing**; performance budget for `/state` catch-up at scale
- ⬜ **Security review** (authz, secrets, injection, rate limits) + dependency audit
- ⬜ **Age-gating/compliance** review (cannabis-themed, simulated only) + ToS/privacy
- ⬜ **MainNet migration** plan (treasury custody, asset reissue, cost model)
- ⬜ Staged **public beta**.

---

## Cross-cutting tracks (continuous)
- **Testing:** keep suite green; raise coverage; property tests for ledger/genetics; sim determinism.
- **Docs:** keep `docs/PHASE*.md`, `docs/ROADMAP.md`, OpenAPI, and `BUILDLOG.md` current.
- **Observability:** logs → metrics → traces as traffic grows.
- **Economy stewardship:** monitor faucets/sinks; tune `balance.yaml`; watch for inflation.

## Risks & watch-items
- **Sim cost at scale:** compute-on-read catch-up is O(elapsed hours); cap + consider background
  batching/materialization for dormant plants.
- **Custodial key custody:** encrypt at rest, secrets-manager only, before any real value.
- **Regulatory framing:** simulation/entertainment only; no real cannabis sale; clear age-gating.
- **On-chain cost/latency:** keep gameplay DB-authoritative; chain is settlement/mirror.
