"""
The deterministic, compute-on-read simulation engine.

`catch_up(session, plant, now, cfg)` advances a plant in fixed 1-hour steps from
its `last_tick_at` up to `now`, mutating its resource levels, health, growth, and
stage, and emitting PlantEvent rows for stage changes, condition onsets, and
death. Each hourly step seeds its RNG from (plant id, hour) so the trajectory is
a pure function of state + elapsed time — reading at any wall-clock moment yields
the same result (idempotent).
"""

import hashlib
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from ..enums import GrowthStage
from ..db.models import Plant, GrowPod, PlantEvent
from . import reactions, horticulture
from .conditions import PlantCondition

# Stages that actually grow / take time, in order.
_STAGE_ORDER = [
    GrowthStage.SEED,
    GrowthStage.GERMINATION,
    GrowthStage.SEEDLING,
    GrowthStage.VEGETATIVE,
    GrowthStage.FLOWERING,
    GrowthStage.HARVEST,
]


def _rng_for(plant_id: str, t: datetime) -> random.Random:
    """A stable RNG for a given plant-hour (makes catch-up reproducible)."""
    key = f"{plant_id}:{t.isoformat()}".encode("utf-8")
    seed = int(hashlib.sha256(key).hexdigest()[:12], 16)
    return random.Random(seed)


def _gene(plant: Plant, trait: str, default: float = 0.5) -> float:
    gene = (plant.genome or {}).get(trait)
    return float(gene["value"]) if gene else default


def _stage_duration_hours(plant: Plant, stage: GrowthStage, sim: Dict) -> float:
    stages = sim.get("stages", {})
    if stage == GrowthStage.SEED:
        return stages.get("seed_days", 3) * 24
    if stage == GrowthStage.GERMINATION:
        return stages.get("germination_days", 5) * 24
    if stage == GrowthStage.SEEDLING:
        return stages.get("seedling_days", 10) * 24
    if stage == GrowthStage.VEGETATIVE:
        return stages.get("vegetative_days", 26) * 24
    if stage == GrowthStage.FLOWERING:
        # Flowering length is genetic.
        return _gene(plant, "flowering_time", 60) * 24
    return 0.0


def _growth_cm_per_hour(stage: GrowthStage, sim: Dict, health: float) -> float:
    growth = sim.get("growth", {})
    rate = {
        GrowthStage.SEEDLING: growth.get("seedling_cm_per_day", 0.6),
        GrowthStage.VEGETATIVE: growth.get("vegetative_cm_per_day", 2.2),
        GrowthStage.FLOWERING: growth.get("flowering_cm_per_day", 0.5),
    }.get(stage, 0.0)
    return rate / 24.0 * (health / 100.0)


def _env_for(plant: Plant, pod: Optional[GrowPod], sim: Dict) -> Dict:
    defaults = sim.get("environment", {}).get("defaults", {})
    light_default = defaults.get("light_intensity", 600)
    if pod is not None and pod.temperature is not None:
        return {
            "temperature": pod.temperature,
            "humidity": pod.humidity,
            "ph_level": pod.ph_level if pod.ph_level is not None else defaults.get("ph_level", 6.5),
            "light": pod.light_intensity if pod.light_intensity is not None else light_default,
        }
    return {
        "temperature": defaults.get("temperature", 24),
        "humidity": defaults.get("humidity", 50),
        "ph_level": defaults.get("ph_level", 6.5),
        "light": light_default,
    }


def environment_for(plant: Plant, pod: Optional[GrowPod], sim: Dict) -> Dict:
    """Public view of a plant's current environment (temp/humidity/pH/light)."""
    return _env_for(plant, pod, sim)


def _health_target(plant: Plant, env: Dict, sim: Dict) -> float:
    h = sim.get("health", {})
    water = sim.get("water", {})
    nutrient = sim.get("nutrient", {})
    envcfg = sim.get("environment", {})

    def outside(value, lo, hi):
        return max(0.0, lo - value, value - hi)

    water_stress = outside(
        plant.water_level, water.get("optimal_low", 40), water.get("optimal_high", 78)
    )
    nutrient_stress = outside(
        plant.nutrient_level,
        nutrient.get("optimal_low", 35),
        nutrient.get("optimal_high", 82),
    )

    t_lo, t_hi = envcfg.get("temperature", [20, 28])
    h_lo, h_hi = envcfg.get("humidity", [40, 60])
    p_lo, p_hi = envcfg.get("ph_level", [6.0, 7.0])
    env_stress = (
        outside(env["temperature"], t_lo, t_hi)
        + outside(env["humidity"], h_lo, h_hi)
        + outside(env["ph_level"], p_lo, p_hi) * 10.0  # pH swings are potent
    )

    # Light & VPD (Phase A): the engine now reads the pod's light level and the
    # derived leaf vapour-pressure deficit. Bands are generous and the weights
    # modest — adequate light + in-band VPD contribute no penalty.
    lightcfg = sim.get("light", {})
    vpdcfg = sim.get("vpd", {})
    l_lo, l_hi = lightcfg.get("optimal_ppfd", [300, 900])
    light_stress = outside(env.get("light", (l_lo + l_hi) / 2.0), l_lo, l_hi)
    v_lo, v_hi = vpdcfg.get("optimal", [0.8, 1.6])
    vpd = horticulture.vpd_kpa(
        env["temperature"], env["humidity"], vpdcfg.get("leaf_offset_c", 2.0)
    )
    vpd_stress = outside(vpd, v_lo, v_hi)

    penalty = (
        water_stress * h.get("water_stress_weight", 0.6)
        + nutrient_stress * h.get("nutrient_stress_weight", 0.5)
        + env_stress * h.get("env_stress_weight", 0.5)
        + light_stress * h.get("light_stress_weight", 0.02)
        + vpd_stress * h.get("vpd_stress_weight", 0.5)
        + plant.pest_level * h.get("pest_weight", 0.45)
        + plant.disease_level * h.get("disease_weight", 0.55)
    )
    return max(0.0, min(100.0, 100.0 - penalty))


def _step(
    plant: Plant,
    env: Dict,
    sim: Dict,
    rng: random.Random,
    t: datetime,
    auto: Optional[Dict] = None,
) -> List[dict]:
    """Advance the plant by one simulated hour. Returns stage/death events."""
    events: List[dict] = []
    decay = sim.get("resource_decay", {})

    # 1. Resources dry out / deplete.
    plant.water_level = max(0.0, plant.water_level - decay.get("water_per_hour", 1.5))
    plant.nutrient_level = max(
        0.0, plant.nutrient_level - decay.get("nutrient_per_hour", 1.0)
    )

    # 1b. Pod automation tops resources back up when they run low.
    if auto:
        autocfg = sim.get("automation", {})
        if auto.get("water") and plant.water_level < autocfg.get("water_refill_below", 45):
            plant.water_level = autocfg.get("water_refill_to", 72)
        if auto.get("feed") and plant.nutrient_level < autocfg.get("nutrient_refill_below", 40):
            plant.nutrient_level = autocfg.get("nutrient_refill_to", 72)

    # 2. Pests: spawn when absent, otherwise worsen until treated.
    pests = sim.get("pests", {})
    pest_res = _gene(plant, "pest_resistance", 0.5)
    if plant.pest_level <= 0:
        chance = pests.get("base_spawn_chance_per_hour", 0.012)
        if env["humidity"] >= pests.get("humidity_high", 62):
            chance += pests.get("humidity_spawn_bonus", 0.03)
        chance *= (1.0 - 0.5 * pest_res)
        if rng.random() < chance:
            plant.pest_level = 5.0
    else:
        plant.pest_level = min(
            100.0, plant.pest_level + pests.get("growth_per_hour", 1.6) * (1.0 - 0.5 * pest_res)
        )

    # 3. Disease (mildew): grows in damp air, slowly clears in dry air.
    disease = sim.get("disease", {})
    dis_res = _gene(plant, "disease_resistance", 0.5)
    if env["humidity"] >= disease.get("humidity_threshold", 64):
        plant.disease_level = min(
            100.0,
            plant.disease_level + disease.get("growth_per_hour", 1.3) * (1.0 - 0.5 * dis_res),
        )
    else:
        plant.disease_level = max(0.0, plant.disease_level - 0.5)

    # 4. Health drifts toward the target dictated by current stressors.
    target = _health_target(plant, env, sim)
    hcfg = sim.get("health", {})
    drift = hcfg.get("drift_rate", 0.12)
    plant.health = max(0.0, min(100.0, plant.health + (target - plant.health) * drift))

    if plant.health <= hcfg.get("death_threshold", 1.0):
        plant.health = 0.0
        plant.is_alive = False
        events.append({"type": "death", "severity": "severe", "payload": {}})
        return events

    # 5. Growth & stage advancement.
    stage = GrowthStage(plant.growth_stage)
    if stage != GrowthStage.HARVEST:
        plant.height += _growth_cm_per_hour(stage, sim, plant.health)
        base = _stage_duration_hours(plant, stage, sim)
        # Poor health slows development.
        effective = base * (1.0 + (100.0 - plant.health) / 200.0)
        hours_in_stage = (t - plant.stage_entered_at).total_seconds() / 3600.0
        if base > 0 and hours_in_stage >= effective:
            nxt = _STAGE_ORDER[_STAGE_ORDER.index(stage) + 1]
            plant.growth_stage = nxt.value
            plant.stage_entered_at = t
            events.append(
                {
                    "type": "stage_change",
                    "severity": None,
                    "payload": {"from": stage.value, "to": nxt.value},
                }
            )
    return events


def catch_up(session, plant: Plant, now: datetime, cfg) -> List[PlantEvent]:
    """Advance `plant` to `now`, persisting events. Returns the new events."""
    sim = cfg.raw.get("simulation", {})
    emitted: List[PlantEvent] = []

    if plant.harvested or not plant.is_alive:
        plant.last_tick_at = now
        plant.condition_flags = reactions.compute_conditions(plant, sim)
        return emitted

    pod = session.get(GrowPod, plant.pod_id)
    env = _env_for(plant, pod, sim)
    auto = {
        "water": bool(pod and pod.auto_water),
        "feed": bool(pod and pod.auto_feed),
    }

    elapsed_hours = int((now - plant.last_tick_at).total_seconds() // 3600)
    elapsed_hours = max(0, min(elapsed_hours, sim.get("max_catchup_hours", 8760)))

    prev_conditions = {f["condition"] for f in (plant.condition_flags or [])}

    for _ in range(elapsed_hours):
        t = plant.last_tick_at + timedelta(hours=1)
        rng = _rng_for(plant.id, t)
        step_events = _step(plant, env, sim, rng, t, auto)
        plant.last_tick_at = t

        for ev in step_events:
            emitted.append(_record_event(session, plant, t, ev["type"], ev.get("severity"), ev.get("payload", {})))

        # Detect newly-appeared conditions and log their onset.
        conditions = reactions.compute_conditions(plant, sim)
        names = {f["condition"] for f in conditions}
        for f in conditions:
            cond = f["condition"]
            if cond not in prev_conditions and cond != PlantCondition.HEALTHY.value:
                emitted.append(
                    _record_event(session, plant, t, "condition_onset", f["severity"], {"condition": cond})
                )
        prev_conditions = names

        if not plant.is_alive:
            break

    plant.condition_flags = reactions.compute_conditions(plant, sim)
    return emitted


def advance_to(session, plant: Plant, when, cfg) -> List[PlantEvent]:
    """Convenience wrapper accepting a datetime or a Clock."""
    now = when.now() if hasattr(when, "now") else when
    return catch_up(session, plant, now, cfg)


def _record_event(session, plant, t, event_type, severity, payload) -> PlantEvent:
    ev = PlantEvent(
        plant_id=plant.id,
        timestamp=t,
        event_type=event_type,
        severity=severity,
        payload=payload,
    )
    session.add(ev)
    return ev
