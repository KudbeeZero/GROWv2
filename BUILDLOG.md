# Build Log

Chronological record of what shipped on the trunk
(`claude/cannabis-game-lut-economics-utfiK`). Newest at the bottom of each section.

## Phases (foundation)
- **Phase 1** — Persistent DB, ledger economy, strain genetics & crossbreeding.
- **Phase 2** — Real-time grow simulation engine (reactions, health, events).
- **Phase 3** — Algorand on-chain layer (ASA token + ARC-3 NFT minting).

## Overnight build session
Each entry: branch · what shipped · test count after merge.

- `docs/roadmap` · 90-day roadmap (`docs/ROADMAP.md`) + this build log · 79 tests.
- `feature/daily-stipend-quests` (merged) · daily login stipend + achievement rewards · 81 tests.
- `feature/player-leveling` (merged) · XP/levels awarded on harvest/breed/mint · 81 tests.
- `feature/api-key-auth` (merged) · per-player API-key auth on all write endpoints · 84 tests.
- `feature/error-handling-validation` (merged) · uniform JSON error envelope + 1 MiB body cap · 87 tests.
- `feature/health-observability` (merged) · /health + /readiness probes, request-id access logs · 90 tests.
- `feature/ci-github-actions` (merged) · CI: lint + migrations + seed + pytest on push/PR · 90 tests.
- `feature/dockerize` (merged) · Dockerfile + compose (Postgres) + gunicorn server · 90 tests.
- `feature/openapi-docs` (merged) · /openapi.json + Swagger UI at /docs · 92 tests.

### Wave 1 (production hardening) complete: auth, errors, health, CI, docker, OpenAPI.
- `feature/strain-search-favorites` (merged) · strain search/filter + favorites · 95 tests.
