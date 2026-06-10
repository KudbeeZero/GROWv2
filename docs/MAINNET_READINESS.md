# MainNet Readiness — what to get right before going live

> **The one mental model:** GROWv2 is **DB-authoritative**. The database (players,
> ledger, plants, strains) is the source of truth; the chain is a *mirror/trophy
> case*. That means **almost everything is fixable after launch** — you can rewrite
> gameplay, retune `balance.yaml`, add features, even wipe and reseed the DB. The
> **only truly irreversible things involve the chain and real money.** Get those
> right; iterate on the rest freely.

---

## Irreversible vs. fixable

| Truly irreversible (real money / on-chain) | Fixable anytime (DB-authoritative) |
|---|---|
| Real ALGO spent on transaction fees | All gameplay logic & balance (`balance.yaml`) |
| An ASA created with the wrong `total`/`decimals`/name (you'd mint a *new* one and migrate) | Strain catalog, research tree, shop, cup, university |
| Assets transferred to a wrong/real wallet | Web UI, API surface, content |
| **A leaked treasury key → funds drained** | The whole DB (back it up, but it's replaceable) |

If you're "not afraid to recreate the game twice to learn" — good instinct. The
cost of a redo is **only** the real ALGO you spent (fees + asset minimum balance)
and any assets already in real users' hands. The code and DB are disposable.

---

## The short list — must be right BEFORE MainNet

1. **Treasury key custody.** Never in the repo, never in the DB. Phase 4 moved the
   real provider to **signer-based accounts** (`chain/algorand.py` on AlgoKit
   Utils). For MainNet, supply the signer from a **secrets manager** at minimum,
   and ideally a **KMS/HSM-backed `TransactionSigner`** so the raw key never lives
   in process memory you control. Rotate it; give it least privilege.
2. **Finalize ASA params** in `balance.yaml → chain.token`: `unit_name`,
   `asset_name`, `total`, `decimals: 6` (keep 6 — the ledger is `Numeric(18,6)` so
   1 GROW = 10^6 base units maps 1:1). Decide on `manager`/`reserve`/`freeze`/
   `clawback`: leaving them set keeps you in control (you can reconfigure/destroy);
   clearing them makes the asset immutable/trustless. Pick deliberately — it's a
   one-way door per asset.
3. **Network guard is on.** `ALGORAND_NETWORK=mainnet` **and** a MainNet
   `ALGOD_URL`. The provider now **refuses to start** if these disagree (e.g.
   `mainnet` network with a `testnet` URL) — don't bypass it.
4. **Withdrawal cap.** Set `MAX_WITHDRAWAL_PER_DAY` to a sane value; the rolling
   24h cap (`settlement_service`) is your defence-in-depth against a stolen API key
   draining the treasury. Minting/settlement are already DB-first and idempotent.
5. **Fund the treasury** with real ALGO for fees **and asset minimum balance** —
   every ASA created or held raises the account's min balance (~0.1 ALGO each).
6. **Secrets & hardening:** `ANTHROPIC_API_KEY`, the treasury signer, and
   `DATABASE_URL` all live in the host secret store. `FLASK_DEBUG=false`.
   `CORS_ALLOWED_ORIGINS` locked to your real domain. Rate limiting on, backed by
   Redis (`RATELIMIT_STORAGE_URI`) so limits hold across workers.
7. **Backups.** The DB is your source of truth — enable Postgres backups.
8. **Compliance gate (do not skip).** Cannabis-themed, **simulation/entertainment
   only** — no real cannabis. Add age-gating + ToS/privacy before any public
   launch. See `docs/ROADMAP.md` → Launch readiness.

---

## The staged path (local → private domain → MainNet)

You said you want to test on your computer and on a password-protected test
domain first. Here's the exact ladder — each rung is safe and reversible until the
last.

### 1. Local, no money (default)
The app runs with an **offline mock chain** out of the box — no secrets, no funds,
full game loop:
```bash
pip install -r requirements.txt
alembic upgrade head && python -m growpodempire.db.seed
python server.py            # USE_MOCK_CHAIN defaults on when no treasury is set
```
This is where you build and break things freely.

### 2. Local, real-ish chain (optional) — Algorand LocalNet
```bash
algokit localnet start
export ALGORAND_NETWORK=localnet
export ALGOD_URL=http://localhost:4001
export ALGOD_TOKEN=aaaaaaaa...   # LocalNet default token
export ALGO_TREASURY_MNEMONIC="<a localnet-funded account mnemonic>"
export USE_MOCK_CHAIN=false
```
Exercises the real AlgoKit code path with fake money. **Run the opt-in TestNet
integration test here / on TestNet** before trusting the binding versions:
`PYTHONPATH=src pytest tests/test_minting.py -k integration` (and verify your
installed `algokit-utils` version matches the API in `chain/algorand.py`).

### 3. Private test domain, behind a password — TestNet
Deploy with TestNet config and the **site password gate** so it isn't public:
```bash
export SITE_PASSWORD="something-only-you-know"   # HTTP Basic on every route
export ALGORAND_NETWORK=testnet
export ALGOD_URL=https://testnet-api.algonode.cloud
export ALGO_TREASURY_MNEMONIC="<testnet treasury>"   # fund via the TestNet dispenser
# create the GROW ASA once, then wire its id:
#   python -c "from growpodempire.chain... reset_token_asa(...)"  → set ASA_ID
export USE_MOCK_CHAIN=false
```
Anyone hitting the domain gets a browser password prompt; `/health` stays open for
your load balancer. Play the full loop end-to-end against TestNet. **No real money.**

### 4. MainNet
Only after step 3 is clean: walk the **short list** above, flip
`ALGORAND_NETWORK=mainnet` + a MainNet `ALGOD_URL`, fund the treasury with real
ALGO, create the real GROW ASA, set `ASA_ID`, and remove `SITE_PASSWORD` when you
want it public. The DB you tested on TestNet can carry over — only the chain ids
change.

---

## What can wait (ship it, fix it later)
Gameplay balance, new strains/research/shop/cup/university content, the AI advisor
prompts and models, UI polish, and even a full DB reseed. None of these touch the
chain, so none of them are irreversible. Launch lean and iterate.
