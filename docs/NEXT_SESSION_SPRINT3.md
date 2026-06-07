# Next Session — Sprint 3: GROWv2 Web Client

Paste the prompt below into a fresh coding session to start the frontend.

---

**Build the GROWv2 web client (Sprint 3).**

The backend is complete and in `main`: a Flask game API under `/api/game/*` with
players, strain genetics & crossbreeding, a real-time grow simulation (plants
react to overwatering / pests / mildew via `condition_flags`), an economy ledger,
marketplace + auctions, NPC contracts, leaderboards, XP/levels, and an Algorand
ASA/NFT layer. Auth is a per-player API key (`X-API-Key`, returned once at player
creation). The full route list is self-served at `/openapi.json` with Swagger UI
at `/docs`.

**Goal:** a React + TypeScript (Next.js) client in `web/` where a player runs the
full loop and **sees plants react in real time**.

**Build:**
1. Scaffold `web/` (Next.js + TS; an API client generated or hand-written from
   `/openapi.json`). Store the API key in localStorage with an `X-API-Key`
   request interceptor.
2. **Onboarding:** create player (capture `api_key` once), wallet (GROW balance +
   ASA), daily stipend, achievements, level/XP.
3. **Grow dashboard:** pods + plants; poll `GET /players/<id>/plants/<id>/state`
   and render health/water/nutrient bars + animated reactions from
   `condition_flags` (drooping = underwater/wilting, bug overlay =
   pest_infestation, white powder = mildew, etc.) plus the event log. Care
   buttons (water / feed / treat-pests / treat-disease), set environment, roll
   weather.
4. **Strain lab:** catalog search/filter + favorites; breeding (two parents →
   offspring) and stabilization; mint eligible strains/harvests.
5. **Market:** fixed-price listings + auctions (bid/settle); NPC contracts;
   leaderboards.

**Constraints:** the backend is the source of truth — don't reimplement game
logic client-side; treat the API as the contract. Use the latest Claude models
for any AI features. Keep it deployable (the API already ships Docker/compose +
Render config).

**Run the backend locally:**
```bash
# Option A
docker compose up
# Option B
pip install -r requirements.txt
export PYTHONPATH=src
alembic upgrade head && python -m growpodempire.db.seed
python server.py        # serves on :10000
```

**Acceptance:** a new player can, in-browser, create an account, buy + plant a
seed, watch its state/health/conditions change over time, care for it, harvest +
sell, breed + stabilize, and view leaderboards — all against the live API.

---

## Backend reference (already built)

- **Docs:** `docs/PHASE1_ECONOMY_DB.md`, `docs/PHASE2_SIMULATION.md`,
  `docs/PHASE3_ONCHAIN.md`, `docs/ROADMAP.md`, `BUILDLOG.md`.
- **API base:** `/api/game` (blueprint `src/growpodempire/api/game_api.py`).
- **Auth:** `POST /api/game/players` returns `api_key` once; send it as
  `X-API-Key` on all write endpoints. Reads are public.
- **Live spec:** `GET /openapi.json`, human docs at `GET /docs`.
- **Key endpoints:** players/wallet/level/ledger; strains (search/filter) +
  favorites; seeds/buy, pods (+upgrade), plant, plant `/state`, `/events`, care
  actions, weather; breed, stabilize; market list/buy + auction/bid/settle;
  contracts offer/fulfill; leaderboards; wallet link/withdraw/deposit; mint
  harvest/strain; nft metadata.
