# Board of Advisors — design & strategy pack

A parallel "board of advisors" pass (2026-06-10): several specialist agents each took one big open
question and produced a grounded, codebase-aware plan. These are **design/strategy docs and backlog —
not yet built.** Nothing here changes runtime behavior.

| Doc | What it answers | Status |
|---|---|---|
| [`EQUIPMENT_ECONOMY.md`](EQUIPMENT_ECONOMY.md) | Lights (wattage→PPFD→yield), tents/power tiers, electricity as a recurring sink, and **equipment depreciation + maintenance** (gear ages, yields less, breaks, needs repair). Data model + formulas + balance keys + a ~5-day phased build plan. | ✅ design complete |
| [`COSMETICS_AND_MONETIZATION.md`](COSMETICS_AND_MONETIZATION.md) | Skins/wraps/particles, in-game billboards & equipment stickers (parody brands), the store, and **which cosmetics are DB items vs NFTs** — plus the sales model and the compliance flags. | ✅ strategy complete |
| [`ENGINEERING_PLAYBOOK.md`](ENGINEERING_PLAYBOOK.md) | How elite teams get code correct the first time, and a prioritized checklist to **cut rework** in this repo (real lint gate, Hypothesis, faucet/sink invariant test, mypy, smarter CI). | ✅ research complete |
| Visual QA / plant-stage screenshots | What a plant actually looks like in the UI at each growth stage + crossbreeding smoke test. | 🔄 running (artifacts land in `artifacts/plant-stages/`) |

## On "how do we keep track of all these checks & balances" (the DNA-strand layout)
That instinct is right, and half of it already exists — the goal is to make the *whole* system legible
in one place, the way that genome diagram laid everything out. Two concrete pieces:

1. **One tuning surface.** `src/growpodempire/data/balance.yaml` already holds *every* economic and
   simulation constant (faucets, sinks, sim thresholds, research, shop, cup, curing). Equipment +
   cosmetics extend it. Rule: **balance changes are data, not code.**
2. **A systems map (proposed, small).** A single `docs/board/SYSTEMS_MAP.md` (or a generated diagram)
   that lists, in one table: every **faucet** (where GROW enters) ↔ every **sink** (where it leaves),
   and every **stat → effect** edge (e.g. health→yield, wattage→PPFD→DLI→yield, condition→output,
   terpene→sale premium, research node→modifier). This is the "DNA strand" view — it makes balance and
   correctness auditable at a glance and pairs with the engineering playbook's **"every faucet has a
   sink" invariant test** so the map can't silently drift from the code.

## How to build from here
Each doc is implementer-ready and DB-authoritative (the pure sim engine is never touched; player
modifiers apply in services). Suggested order: ship the engineering-playbook quick wins first (they
stop rework on everything after), then equipment economy (deepest gameplay), then cosmetics (first
real monetization sink). All of it is additive and behind the same patterns already in the codebase.
