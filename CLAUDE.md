# CLAUDE.md — GROWv2 agent memory (Layer 0)

> This is the **always-loaded** top layer of the project's memory system. Keep it short,
> stable, and true. Deeper, more volatile detail lives in `docs/memory/` (see the layer map
> below). If something here is wrong, fix it here first — every session reads this file.

## What this is
**GROWv2** (package `growpodempire`) is a cannabis-growing game with a persistent economy,
real strain genetics/crossbreeding, a real-time grow simulation, an Algorand on-chain asset
layer, and an AI "Master Grower" advisor. Backend is Python/Flask; the web client is Next.js 15
in `web/`. The database is SQLAlchemy + Alembic (SQLite in dev, Postgres in prod).

## North star
Take a working, tested backend → a launchable, long-lived live game, **without breaking the
core loop**: grow → care → harvest → cure → sell/breed/stabilize → mint → trade.

## How to work here (conventions that must not drift)
- **DB is authoritative; the chain is a mirror/settlement layer.** Never let on-chain state
  drive gameplay truth.
- **The simulation engine is pure and server-authoritative.** `simulation/` computes plant state
  on read (compute-on-read, lazy catch-up). Do **not** put player-scoped economy/research logic
  inside the pure engine — layer it in `services/`.
- **Money is `Decimal`, ledger-based, double-entry-ish, auditable.** Every spend/earn posts to the
  ledger. No floats for money. Faucets must have matching sinks (watch inflation).
- **Writes require API-key auth; reads are public.** Mutations are rate-limited.
- **Providers are swappable behind ABCs** (`chain/`, `ai/`): a deterministic Mock for tests/CI and
  a real provider for prod, chosen by config. CI runs with mocks — **never require a live key in CI.**
- **`balance.yaml` is the tuning surface.** Prefer data-driven balance changes over code changes.
- Keep the test suite green and add a test with every feature. Property/invariant tests guard the
  ledger and genetics.

## Run it
```bash
pip install -r requirements.txt -r requirements-dev.txt && pip install -e .
python -m pytest -q          # full suite (currently 139 tests, all green)
python server.py             # local API
cd web && npm i && npm run dev   # web client
```

## Memory layer map (read deeper as needed)
| Layer | File | Purpose | Volatility |
|------|------|---------|-----------|
| 0 | `CLAUDE.md` (this file) | Identity, invariants, how to work | Low |
| 1 | `docs/memory/ARCHITECTURE.md` | System map + load-bearing invariants ("don't break") | Low |
| 2 | `docs/memory/DECISIONS.md` | Why things are the way they are (ADR log) | Append-only |
| 3 | `docs/memory/BACKLOG.md` | Prioritized work: now / medium / low | High |
| 4 | `docs/memory/standups/` | Dated LUT round-table reports | Daily |

See `docs/memory/README.md` for how the layers fit together and how to maintain them.
