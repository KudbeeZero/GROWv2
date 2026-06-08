# Decision Log (Layer 2)

Append-only, lightweight ADRs. Newest at the bottom. To change a past decision, add a new entry
that **supersedes** the old one (don't delete history).

Format: `### YYYY-MM-DD — Title` · **Decision** · **Why** · **Consequences**.

---

### 2026-06-07 — DB-authoritative, chain-as-mirror
**Decision:** Gameplay truth lives in the relational DB; Algorand (ASA token + ARC-3 NFT) is a
settlement/mirror layer behind a provider ABC.
**Why:** On-chain latency/cost/availability can't gate the core loop; tests and CI must run with no
network. **Consequences:** A mock chain provider exists and is the default in tests; real wiring
(funded TestNet, IPFS metadata, reconciliation) is deferred to its own sprint.

### 2026-06-07 — Pure, compute-on-read simulation engine
**Decision:** `simulation/` derives plant state lazily from elapsed time + stored inputs and stays
free of player-scoped logic. **Why:** Determinism (testable, reproducible) and cheap writes.
**Consequences:** Research/consumable perks are applied in `services/` around the engine, never
inside it. Accepted risk: read cost is O(elapsed hours) — flagged for batching at scale.

### 2026-06-07 — Decimal, ledger-based economy with sinks
**Decision:** All currency is `Decimal`; every economic effect posts to an auditable ledger; faucets
are paired with sinks. **Why:** Avoid float rounding bugs and runaway inflation in a persistent
economy. **Consequences:** Property tests assert ledger invariants and pricing monotonicity.

### 2026-06-07 — Swappable providers for chain & AI (mock + real, config-selected)
**Decision:** `chain/` and `ai/` each expose an ABC, a deterministic Mock, a real impl, and a
factory. Config (env) selects the impl; CI uses mocks. **Why:** Keep CI key-free and offline;
make prod a config flip. **Consequences:** New external integrations should follow this same shape.

### 2026-06-07 — AI "Master Grower": read-only advisor first, then guarded agentic auto-care
**Decision:** Ship the advisor as read-only (`AdvisorService`) before letting it act
(`AutoCareService`), and gate actions behind a per-invocation `SpendGuard` (GROW budget + action
cap) that posts through the normal ledger care path. **Why:** Server stays authoritative; an agent
literally cannot overspend. **Consequences:** `ENABLE_AUTO_CARE` flag + budget live in
`balance.yaml:auto_care`; mock loop covers CI.

### 2026-06-07 — Removed the legacy v1 subsystem
**Decision:** Deleted in-memory `app.py`/`models/`/`blockchain/`/CLI/demo + `ENABLE_LEGACY_API`,
and dropped now-unused numpy/pandas. **Why:** Two parallel implementations is debt; OpenAPI at
`/openapi.json` + `/docs` is the single API source of truth. **Consequences:** Stale `API.md` /
`IMPLEMENTATION.md` removed; README rewritten for the real GROWv2.

### 2026-06-08 — Adopt a Markdown memory-layer system
**Decision:** Introduce `CLAUDE.md` (Layer 0) + `docs/memory/` (Layers 1–4) as the project's
persistent memory, with a daily LUT standup ritual. **Why:** Work was moving fast across many
sessions with no durable, structured context; higher layers were drifting from reality (roadmap,
build log). **Consequences:** Invariant changes must update Layer 0/1 in the same change; one
standup per working day under `standups/`.

### 2026-06-08 — Adopt a Design Codex sub-layer (vision/intent beside Layer 1)
**Decision:** Add `docs/memory/design/` as a low-volatility, vision-forward sub-layer next to
ARCHITECTURE: a global game-vision doc that leads with the **proprietary moat** (a real
plant-physiology sim → generative genetics → Proof-of-Cultivation → on-chain GenBank → discovery
economy → earned mastery → AI data flywheel), plus deep docs for the scientist-grade simulation,
generative genetics, and grower-skill mastery. Every capability is tagged `✅/🔨/⬜`.
**Why:** Work was moving fast with no durable home for *deep design intent* — what makes the game
different and how the sim/genetics get there — separate from ARCHITECTURE's "what must not break."
The user wants the depth (horticulture realism, endless genetics, time-as-investment) to be the
differentiator and to be captured before it's built. **Consequences:** The codex *proposes* shape;
work still becomes real via BACKLOG. Moat claims lean on planned (⬜) systems — especially anything
on-chain (the chain is mocked; GenBank/Proof-of-Cultivation are ⬜) — and must stay tagged so the
docs never oversell. When a 🔨/⬜ ships, flip its tag and update ARCHITECTURE/CLAUDE in the same
change if an invariant moved.
