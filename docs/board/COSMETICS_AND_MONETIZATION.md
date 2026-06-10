# Cosmetics, Storefront & In-Game Brand Monetization — Strategy

> Produced by the "board of advisors" pass (2026-06-10).
> Simulation/entertainment product only. No real cannabis is grown, sold, or facilitated.

## 0. Grounding
- DB is authoritative, chain is settlement/mirror; `MintingService` is DB-first/idempotent
  (`PENDING→MINTED/FAILED`). Cosmetics follow the same pattern.
- Money is `Decimal`, ledger-based; **faucets need matching sinks**. Existing sinks: seeds, nutrients,
  pods, breeding, tuition, cup entry, marketplace `listing_fee_pct 0.03` + `sale_tax_pct 0.05` (burned).
- GROW is a soft currency mirrored to an Algorand ASA; rare harvests / stabilized strains mint ARC-3
  NFTs (`mint_min_rarity: rare`, `strain_min_stability: 0.85`). A polymorphic player marketplace
  (`MarketListing`, fixed-price + auctions) and a consumables shop (`shop.consumables`) already exist.

**Takeaway:** cosmetics are 95% a DB-inventory + rendering problem. Reserve the chain for the **rare,
tradeable, status** tier only — exactly the existing harvest/strain NFT philosophy.

## 1. Cosmetics model
- **`CosmeticCatalog`** (data-driven `cosmetics.yaml` next to `balance.yaml`): `key`, `name`, `slot`
  (tent/light/packaging/pod-wrap/pot/label/nameplate), `theme`, `rarity`, `visual_spec`, `acquisition`
  (grow_sink|event|nft|season_pass), `price_grow`, `tradeable`.
- **`CosmeticInventory`** (per-player, mirrors `ConsumableInventory`): `player_id`, `cosmetic_key`,
  `qty`, `source`, optional `nft_asset_id`+`nft_status` (reuse `NFTStatus`).
- **`CosmeticLoadout`** (what's equipped): `player_id`, `target_type`, `target_ref_id`, `slot`,
  `cosmetic_key`. Equipping is free, reversible, pure DB.

**DB-only vs NFT:** *If it's bought-worn-forgotten → DB row. If it's a flex-owned-resold → NFT.*
Common/themed wraps, seasonal/event cosmetics, most sponsor wraps = **DB**. Prestige/1-of-1/champion
gear = **NFT (ARC-3)**, minted only at `rare`+ via the existing `mint_min_rarity` gate (one policy).

**Mint cosmetics via the existing path:** a `mint_cosmetic(...)` in `MintingService` reusing `_mint()`,
`NFTStatus`, a new `cosmetic` metadata kind, and `/api/game/nft/cosmetic/{id}.json`. No new chain surface.

**"Particles" / visual-identity** — server-authoritative `visual_spec` JSON, rendered by a **closed,
versioned** library of GPU-cheap emitters in `web/` (the DB never ships shader code):
```json
{ "base": {"material":"matte|gloss|holo|carbon","palette":["#0b3d2e","#7CFC00"]},
  "pattern": {"type":"camo|grid|topo|waveform|sticker-sheet","scale":1.4,"seed":42},
  "decals": [{"key":"sponsor.kushco","uv":[0.2,0.6],"rot":15}],
  "particles": {"emitter":"canopy-glow|grow-dust|terp-mist|orbital-sparks","color":"#9be15d","rate":12,"intensity":0.6,"gate":"flowering"},
  "identity": {"motif":"orbital","tier":"prestige"} }
```
Deterministic `seed` → "every wrap a little unique" (fits the generative-genetics moat); stage-gated
particles (a wrap that shimmers only in flowering) tie cosmetics to the live sim.

## 2. Sales model (phased)
1. **NOW — pure GROW sink.** Free to ship, zero compliance risk, and the single most effective
   inflation control we can add (every purchase burns GROW). Prices in `cosmetics.yaml`.
2. **NEXT — earnable premium currency ("Stardust"/"Orbital Credits"), cosmetic-only.** Ships earnable
   (cup wins/achievements) → zero payments risk; real-money top-up is a deliberate later switch behind
   age-gating + store review.
3. **LATER — NFT prestige tier only**, routed through the existing marketplace + minting. Royalties via
   the ledger fee (`listing_fee_pct`/`sale_tax_pct`), not on-chain (Algorand royalty support is uneven;
   keep settlement where we control it).

## 3. In-game marketing surfaces (parody brands)
Fiction = an orbital grow station, so sponsors read as "station partners." All names generic/parody.
- **Surfaces:** billboards/station screens (leaderboard hub, Cup arena), decals/stickers on equipment
  (already a cosmetic `slot`), sponsor label slots on packaging.
- **Parody seed list (verify vs live trademarks first):** KushCo Orbital, HelioGrow, Lumenautics,
  TerpTech Labs, Mylar Dynamics, Bud Lightyear, AstroSoil, GravBloom, VaporVoid, Cosmic Canopy Co.,
  Strato-Strains, Nimbus Nutrients, OrbitOG, Zero-G Genetics. These double as the existing shop vendor
  brands.
- **Monetize ad space:** player-buyable billboard leases (recurring GROW sink), sponsor cosmetic
  unlocks via the existing `Contract` system, Cup title-sponsor banners. Always in-fiction/parody.

## 4. Store roadmap + compliance
The store half-exists (`shop.consumables`). Open a **"Station Commissary"** UI once cosmetics ship:
- **v1 (GROW only):** consumables + cosmetic wraps/skins/decals + ad-slot leases (all sinks).
- **v2:** equipment cosmetics + functional equipment tiers (see EQUIPMENT_ECONOMY.md) + season pass
  (earned premium currency).
- **v3 (gated):** real-money premium top-up; NFT prestige cosmetics on the secondary market.

**Compliance — flag honestly:**
- **Age-gating is mandatory** before any cannabis-themed store; non-negotiable before real money.
- Persistent prominent **"simulation only / no real cannabis."**
- **App-store risk:** Apple/Google restrict cannabis + crypto/NFT-commerce → likely **web-first**.
- **NFT/securities:** frame as collectibles-with-utility, never investments (no floor-price/yield talk).
- **Lootbox/gambling:** no paid randomized mints at launch; earned (GROW) + disclosed odds.
- **MSB/KYC:** keep GROW non-cashable; the ASA is a mirror, not redeemable for real money from us.
- **Get legal review before v3.** v1/v2 (GROW-only, DB) carry essentially no novel legal risk.

## 5. Brand identity sketch
Serious-but-fun orbital cultivation sim (the station fiction also softens compliance optics).
- **Names:** *GROW: Orbital* · *GrowPod Empire* · *Canopy Station* · *Orbit Grown* · *Zero-G Gardens*.
- **Voice:** lab-coat-meets-arcade — precise (PPFD, terpene vector, stability) but winking; never
  glamorizes real-world use.
- **Visual motif:** orbital rings + grow-light spectra; matte carbon hardware + neon canopy glow;
  "terp mist" / "orbital sparks" accents. Palette: deep space green `#0b3d2e`, canopy lime `#7CFC00`,
  violet grow-light accent.

## Prioritized backlog
**NOW:** `cosmetics.yaml` + Catalog/Inventory/Loadout tables + buy(GROW)/equip endpoints (DB, M, net-new
sink); closed particles/visual_spec renderer in `web/` (DB, M); Station Commissary store UI (DB, S–M);
persistent compliance copy + age-gate (S, must precede any store).

**NEXT:** parody-sponsor cosmetic line via `Contract` unlocks (DB, M); player-buyable billboard leases
(DB, M); cosmetic NFT minting via existing `MintingService` at `rare`+ (NFT, M); list cosmetics on
existing `MarketListing` with fee-burn (S); champion/cup 1-of-1 cosmetic (NFT, S–M); earnable premium
currency (DB, M).

**LATER (gated):** real-money premium top-up (L, full legal review, web-first, KYC, non-cashable);
NFT secondary-market polish (L, securities/MSB review); seasonal cosmetic pass (L, avoid paid randomized
rewards); first-class equipment cosmetics (after equipment economy).

## Top 3 likely mistakes
1. **Minting cheap cosmetics as NFTs** — gas + opt-in + FAILED-state UX destroys value. NFTs for
   prestige/tradeable only.
2. **Real-money or paid randomized "mint boxes" before legal + age-gating** — cannabis + crypto +
   gambling-adjacent + real money is the highest-risk combo. Soft-launch premium as *earnable* first.
3. **Letting cosmetics/NFTs become a parallel source of truth or an "investment" pitch** — keep pricing
   in the DB ledger (chain = settlement), never frame NFTs as appreciating assets.
