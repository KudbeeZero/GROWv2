# GROWv2

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A cannabis‑cultivation game with a persistent economy, deterministic genetics &
crossbreeding, a real‑time grow simulation, and an Algorand on‑chain asset layer.
A Flask + SQLAlchemy backend serves a JSON game API; a Next.js web client in
[`web/`](web/) plays the full loop in the browser.

> **Entertainment / simulation only.** No real cannabis is grown, sold, or
> exchanged. The "GROW" currency and any on‑chain assets are in‑game only.

## What you do

Grow → care → harvest → **cure** → sell / breed / stabilize → mint → trade.

- **Grow.** Buy seeds, build pods (growing chambers with environment + automation
  tiers), and plant. A deterministic engine advances each plant in 1‑hour ticks.
- **Care.** Water, feed, and treat pests/disease. Resources decay; neglect lowers
  health and can kill the plant. Weather events shift the pod environment.
- **Breed.** Cross two strains; traits inherit through a deterministic genetics
  engine. Self/backcross to **stabilize** a line and unlock NFT minting.
- **Trade.** Sell harvests/seeds to the NPC market or list them player‑to‑player
  at a fixed price or via auction. Fulfil timed NPC delivery contracts.
- **Progress.** Earn XP, level up, claim a daily stipend and achievements, and
  climb the leaderboards (richest, top breeders, biggest harvest, highest level).
- **On‑chain.** The in‑game GROW currency maps to an Algorand ASA; rare/stabilized
  strains and premium harvests can be minted as ARC‑3 NFTs on TestNet. Gameplay
  stays **DB‑authoritative** — the chain is a settlement/mirror, never the source
  of truth for yield, quality, or balances.

## Architecture

```
GROWv2/
├── server.py                       # Production entry point (Flask app factory)
├── src/growpodempire/
│   ├── api/                        # Flask blueprint (/api/game/*), auth, errors, OpenAPI
│   ├── db/                         # SQLAlchemy models, session, seed data
│   ├── services/                   # Game logic (game, simulation, minting, settlement, …)
│   ├── simulation/                 # Compute-on-read plant engine + reactions
│   ├── genetics/                   # Deterministic crossbreeding + traits
│   ├── economy/                    # Append-only ledger + pure pricing formulas
│   ├── chain/                      # Algorand provider abstraction (mock + real)
│   └── data/balance.yaml           # ALL economy/simulation tuning lives here
├── web/                            # Next.js 15 + React 19 + Tailwind + React Query
├── alembic/                        # Database migrations
├── tests/                          # pytest suite (mock chain, no network needed)
└── docs/                           # ROADMAP + per-phase deep dives
```

**Stack:** Python 3.8+, Flask, SQLAlchemy 2.0, Alembic, SQLite (dev) / PostgreSQL
(prod), `py-algorand-sdk` (TestNet, optional). Frontend: Next.js 15, React 19,
TypeScript, Tailwind, TanStack React Query.

## Quick start

### Backend

```bash
pip install -r requirements.txt
export PYTHONPATH=src
alembic upgrade head            # create the schema
python -m growpodempire.db.seed # seed the strain catalog (idempotent)
python server.py                # serves on http://localhost:10000
```

The chain layer defaults to an **offline mock provider**, so the game runs fully
without any Algorand configuration or secrets. To mint on real TestNet, set the
`ALGOD_*` / `ALGO_TREASURY_MNEMONIC` env vars (see [`.env.example`](.env.example)).

### Web client

```bash
cd web
npm install
npm run dev                     # http://localhost:3000 (polls the API on :10000)
```

### Docker (API + Postgres)

```bash
docker compose up
```

## API docs

The API is self‑describing — it never drifts from the code:

- **`GET /openapi.json`** — generated OpenAPI 3 spec.
- **`/docs`** — Swagger UI.
- **`/health`** and **`/readiness`** — probes.

Write endpoints require a per‑player `X-API-Key` header (issued once at player
creation). Reads are public. See [`SECURITY.md`](SECURITY.md) for the auth, rate
limiting, and anti‑cheat model.

## Tests

```bash
pip install -r requirements-dev.txt
PYTHONPATH=src pytest -q                 # full suite (uses the mock chain)
PYTHONPATH=src pytest --cov=growpodempire # with coverage
```

CI runs lint + migrations + seed + pytest on every push/PR; the web client has a
separate lint/typecheck/build workflow.

## Roadmap & history

- [`docs/ROADMAP.md`](docs/ROADMAP.md) — phased roadmap.
- [`BUILDLOG.md`](BUILDLOG.md) — chronological record of what shipped.
- [`docs/PHASE1_ECONOMY_DB.md`](docs/PHASE1_ECONOMY_DB.md),
  [`PHASE2_SIMULATION.md`](docs/PHASE2_SIMULATION.md),
  [`PHASE3_ONCHAIN.md`](docs/PHASE3_ONCHAIN.md) — per‑phase deep dives.

Recently added: a post‑harvest **curing** stage, richer **terpene/cannabinoid**
genetics, and an AI **"Master Grower" advisor** (`GET /players/<id>/plants/<id>/advisor`)
that reads a plant's live state and recommends care. The advisor runs a Claude
model when `ANTHROPIC_API_KEY` is set and falls back to an offline deterministic
advisor otherwise, so it works (and tests) with no key. There's also a
**research tree** (15 upgrades across 5 branches that boost yield, quality,
curing, and cut costs), a **consumables shop**, and **seasonal strains**.
Planned next: an opt‑in **agentic auto‑care** mode where the advisor calls the
care endpoints itself within a spend cap.

## License

MIT — see [`LICENSE`](LICENSE).
