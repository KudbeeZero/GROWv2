# Equipment Economy — Design Doc (lights / tents / power / depreciation)

> Produced by the "board of advisors" design pass (2026-06-10). Implementer handoff.
> Grounded in `simulation/engine.py`, `db/models.py`, `services/game_service.py`,
> `services/simulation_service.py`, `services/research_service.py`, `economy/`, `data/balance.yaml`.

## 0. Grounding (extend, don't rewrite)
- **Pods** (`GrowPod`) have `tier` (basic/standard/pro), `capacity`, `auto_water/auto_feed`, and an
  env snapshot incl. `light_intensity` (0..1000, treated as **PPFD**). Tiers priced in
  `balance.yaml:pods` (100/400/1200). `create_pod`/`upgrade_pod` charge via the ledger.
- **Engine is pure & server-authoritative.** `_env_for` reads `pod.light_intensity` → `env["light"]`;
  `_health_target` already penalizes light outside `simulation.light.optimal_ppfd [300,900]` and VPD
  outside band. `horticulture.dli()/vpd_kpa()/derived_metrics()` already compute DLI/PPFD/VPD. **The
  engine never reads player-economy state — preserve that invariant.**
- **Yield/quality** computed in `GameService.harvest_plant`: `weight_g = midpoint*(0.4+0.6*health/100)`
  then `*(1+fx["yield_pct"])` (research/degree effects). **This is the single chokepoint where an
  equipment yield multiplier hooks in.**
- **Care actions** (`SimulationService`): `sync()` → mutate → ledger `post()` sink → `_log()`. New
  maintenance mirrors this exactly.
- **Research effects** aggregate additively into `fx` consulted in services — equipment modifiers
  follow the same "compute modifier in service, apply at the chokepoint" pattern.
- No electricity/equipment/depreciation exists today — greenfield, additive.

**Biggest behavioral change:** effective light becomes an *output* of the installed light + its
condition, not a free dial the player sets via `set_environment`. See Decision 1.

## 1. Grow lights
A light is owned equipment (`PlayerEquipment`, type `light`) installed into a pod. The catalog gives
each light `wattage` (cost/electricity driver) and `rated_ppfd` (sim driver), kept consistent.

```
effective_ppfd = rated_ppfd * output_factor(condition) * canopy_match_factor
```
The engine's existing light_stress already rewards/penalizes correct PPFD via health→yield; we add a
small **direct DLI yield multiplier** at harvest so dialing in a strong light is rewarded beyond just
stress-avoidance.

```yaml
equipment:
  electricity_cost_per_kwh: 0.12      # GROW per kWh (recurring sink rate)
  depreciation:
    knee: 0.80          # condition >= knee -> full output
    floor_output: 0.45  # output_factor at condition 0 (pre-breakdown)
    breakdown_at: 0.0   # condition <= this -> broken, 0 output, needs repair
  lights:
    led_180w:  { name: "LED 180W (Veg Starter)", cost: 250, wattage: 180, rated_ppfd: 450, suits_tier: [basic],    lifetime_hours: 17520, maintenance_cost: 40,  repair_cost: 120 }
    led_320w:  { name: "LED 320W (Bloom)",        cost: 600, wattage: 320, rated_ppfd: 720, suits_tier: [standard], lifetime_hours: 17520, maintenance_cost: 75,  repair_cost: 260 }
    hps_600w:  { name: "HPS 600W (High-Yield)",   cost: 950, wattage: 600, rated_ppfd: 950, suits_tier: [pro],      lifetime_hours: 8760,  maintenance_cost: 110, repair_cost: 400 }
    led_720w_pro: { name: "LED 720W (Pro Canopy)",cost: 1800,wattage: 720, rated_ppfd: 900, suits_tier: [pro],      lifetime_hours: 26280, maintenance_cost: 130, repair_cost: 500 }
```

## 2. Tents / pods (reuse the tier ladder — tent IS the tier)
```yaml
pods: { basic: 100, standard: 400, pro: 1200 }   # unchanged purchase price
equipment:
  tents:
    basic:    { capacity: 4,  power_capacity_w: 250, canopy_rated_ppfd: 450, base_draw_w: 30 }
    standard: { capacity: 8,  power_capacity_w: 450, canopy_rated_ppfd: 720, base_draw_w: 50 }
    pro:      { capacity: 16, power_capacity_w: 900, canopy_rated_ppfd: 950, base_draw_w: 80 }
```
```
ratio = light.rated_ppfd / tent.canopy_rated_ppfd
canopy_match_factor = clamp(ratio, 0, 1)   # underlit -> linear loss; overlighting not bonused
# overlighting is already penalized by the engine's light_stress (burn band) + wasted electricity
```

## 3. Power / electrical capacity
Power budget = **per-pod** (`tents[tier].power_capacity_w`); upgrade the tent tier to run a stronger
light (cleanest). A separately-buyable "breaker" is Decision 2.
- **Install-time guard:** reject install if `light.wattage + base_draw_w > power_capacity_w` ("needs a
  bigger tent / power upgrade"). Primary friendly gate.
- **Runtime penalty (defensive):** over-draw caps deliverable PPFD and decays condition faster
  (`overdraw_wear_mult: 1.5`).

**Electricity sink (compute-on-read, no background job):**
```
kwh_per_hour      = (light.wattage + tent.base_draw_w) / 1000
photoperiod_hours = simulation.light.photoperiod_hours (18)   # lights run during photoperiod only
kwh_over_period   = kwh_per_hour * (photoperiod_hours/24) * elapsed_hours
electricity_cost  = kwh_over_period * electricity_cost_per_kwh
```
Example: HPS 600W + 80W = 0.68 kWh/h × 18/24 × 24h = 12.24 kWh × 0.12 ≈ **1.47 GROW/day**; a ~14-week
pro cycle ≈ **~144 GROW** — meaningful, tunable. Billed in `EquipmentService.accrue_electricity(pod)`
at the same points `sync()`/`catch_up` runs; track `metered_until` and bill `now - metered_until` then
set `metered_until = now` (**idempotent on read — never double-charge**, same discipline as
`last_tick_at`). Posts `LedgerEntryType.ELECTRICITY`.

## 4. Depreciation + maintenance (the strategic core)
Condition `0..1` decays with **runtime hours** (a light off in inventory doesn't age), accrued in the
same pass as electricity:
```
runtime_hours_consumed = (photoperiod_hours/24) * elapsed_hours * overdraw_wear_mult
condition -= runtime_hours_consumed / light.lifetime_hours        # clamp >= 0
```
Output curve — flat to a knee, linear to a floor, then breakdown:
```
if condition <= breakdown_at:  output_factor = 0.0     # BROKEN -> needs repair
elif condition >= knee(0.80):  output_factor = 1.0
else: output_factor = floor_output + (1-floor_output)*(condition/knee)
```
At ~90% of life consumed (condition ≈ 0.10) → output_factor ≈ 0.52 → effective PPFD ~halved →
"noticeably less yield." At 0 → broken → 0 PPFD → grow crashes. (The user's exact ask.)

- `maintain(player, equipment)`: accrue first, restore `condition=1.0`, post
  `EQUIPMENT_MAINTENANCE` (subject to `care_discount_pct` research).
- `repair(player, equipment)`: only when broken; restore to `repair_restores: 0.85`, post
  `EQUIPMENT_REPAIR`.
- Neglect path is emergent — no extra rules.

## 5. Data model (one generic, type-discriminated table)
```python
class PlayerEquipment(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "player_equipment"
    player_id        # FK players.id, indexed
    equipment_type   # "light" | "power"(future) | ...
    catalog_key      # e.g. "hps_600w" -> balance.yaml lookup
    condition        # Float default 1.0 (0..1)
    status           # "ok" | "broken" | "retired"
    installed_pod_id # FK grow_pods.id, nullable (NULL = inventory)
    purchased_at; runtime_hours (Float); metered_until (DateTime nullable)
    # Index("ix_equip_player_pod", "player_id", "installed_pod_id")
```
One `light` installed per pod (enforce in install endpoint). No new `GrowPod` columns strictly needed
(effective light is derived; optionally cache `pod.installed_light_id`). New `LedgerEntryType`:
`EQUIPMENT_PURCHASE`, `ELECTRICITY`, `EQUIPMENT_MAINTENANCE`, `EQUIPMENT_REPAIR`. One Alembic revision.

## 6. Hook points
| Concern | Hook | Change |
|---|---|---|
| Effective light → engine | `engine._env_for` | **Don't teach the engine about equipment.** `SimulationService.sync()` (and harvest's catch-up) computes effective PPFD in the *service* and writes `pod.light_intensity` before `engine.catch_up`. Engine stays pure. |
| DLI yield reward | `harvest_plant` `weight_g *= (1+fx[...])` line | also `* dli_yield_mult` |
| Electricity + decay | every `sync()`/`catch_up` site | call `EquipmentService.accrue(pod, now)` (idempotent via `metered_until`) |
| Buy/install/uninstall | new endpoints | mirror `create_pod`; install-time power guard |
| Maintain/repair | new endpoints | mirror `_care_action` |
| `set_environment` light | `SimulationService.set_environment` | Decision 1: deprecate manual light or cap as a dimmer |
| Catalog accessors | `EconomyConfig` | `light_catalog`, `tent(tier)`, `electricity_rate`, `depreciation` |

```
optimal_dli band e.g. [25,45] mol/m²/day
dli = horticulture.dli(effective_ppfd, photoperiod_hours)
dli_yield_mult = clamp(0.85 + 0.15*(dli/optimal_dli_low), 0.85, 1.15)
```

## 7. Phased plan (~4.5–5 days)
1. **Data model & catalog (S, ~0.5d):** `PlayerEquipment` + migration; new ledger types; `equipment`
   block in `balance.yaml`; `EconomyConfig` accessors. Pure additive.
2. **EquipmentService core + sim hook (M, ~1.5d):** `effective_ppfd/output_factor/accrue` (idempotent),
   service-side write of effective PPFD before `engine.catch_up`; wire into `sync`/`harvest_plant`;
   `dli_yield_mult` at harvest. Verify engine-purity test still passes.
3. **Store + install + maintenance endpoints (M, ~1d):** buy/install/uninstall/maintain/repair; power
   guard; one-light-per-pod; serializer.
4. **Balance tuning (S, ~0.5d, data-only):** power+maintenance ≈ 10–20% of a grow's revenue.
5. **Tests & invariants (M, ~1d):** idempotent accrual, monotonic condition decay, broken→crash,
   engine purity (no equipment import in `simulation/`), faucet/sink balance, coverage ratchet.

## 8. The 3 decisions that need the product owner
1. **Does buying a light remove the free `light_intensity` dial?** Recommend: equipment-derived light;
   `set_environment.light_intensity` becomes a capped dimmer or is dropped. Grandfather existing pods
   with a free starter light. High blast radius.
2. **Power budget: per-pod (bundled in tier) vs per-player (buyable breaker).** Recommend per-pod for
   v1; design `equipment_type` to allow `power` later.
3. **Electricity aggressiveness + AFK fairness.** First *continuous* sink. Recommend: photoperiod-only,
   bill only pods with a living unharvested plant (don't bill empty tents), rate so a grow's power ≈
   10–20% of revenue. Touches retention/AFK fairness — needs sign-off.

**Files touched:** `db/models.py`, new `services/equipment_service.py`, `services/simulation_service.py`
(accrual hook), `services/game_service.py` (harvest chokepoint), `economy/config.py`, `enums.py`,
`data/balance.yaml`, `api/game_api.py` + serializer, new Alembic revision. `simulation/` is NOT modified.
