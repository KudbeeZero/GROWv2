"""
SimulationService — runs the real-time engine on reads and applies player care
actions (water, feed, treat pests/disease, set environment).

Every action first brings the plant up to date via the engine's catch-up, then
applies its effect and logs an event. Costed actions go through the economy
ledger.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from ..economy.config import get_economy_config, EconomyConfig
from ..economy.ledger import post
from ..enums import LedgerEntryType
from ..db.models import Plant, GrowPod, PlantEvent, EnvironmentReading
from ..simulation import engine
from ..simulation.clock import Clock, SystemClock
from .game_service import GameError


class SimulationService:
    def __init__(
        self,
        session: Session,
        config: Optional[EconomyConfig] = None,
        clock: Optional[Clock] = None,
    ):
        self.session = session
        self.cfg = config or get_economy_config()
        self.clock = clock or SystemClock()

    @property
    def _sim(self) -> dict:
        return self.cfg.raw.get("simulation", {})

    def _get_plant(self, player_id: str, plant_id: str) -> Plant:
        plant = self.session.get(Plant, plant_id)
        if plant is None or plant.player_id != player_id:
            raise GameError("Plant not found")
        return plant

    def sync(self, plant: Plant) -> List[PlantEvent]:
        """Advance the plant to the current time."""
        return engine.catch_up(self.session, plant, self.clock.now(), self.cfg)

    def get_state(self, player_id: str, plant_id: str):
        plant = self._get_plant(player_id, plant_id)
        self.sync(plant)
        return plant

    def get_events(self, plant_id: str, limit: int = 50) -> List[PlantEvent]:
        return (
            self.session.query(PlantEvent)
            .filter(PlantEvent.plant_id == plant_id)
            .order_by(PlantEvent.timestamp.desc())
            .limit(limit)
            .all()
        )

    # ----- Care actions ---------------------------------------------------
    def water(self, player_id: str, plant_id: str, amount: Optional[float] = None) -> Plant:
        plant = self._get_plant(player_id, plant_id)
        self._require_living(plant)
        self.sync(plant)
        amount = amount if amount is not None else self._sim.get("actions", {}).get("water_amount", 35)
        plant.water_level = min(100.0, plant.water_level + amount)
        self._log(plant, "watered", payload={"amount": amount})
        return plant

    def feed(self, player_id: str, plant_id: str, amount: Optional[float] = None) -> Plant:
        plant = self._get_plant(player_id, plant_id)
        self._require_living(plant)
        self.sync(plant)
        post(
            self.session, player_id, -self.cfg.nutrients_cost,
            LedgerEntryType.NUTRIENT_PURCHASE, ref_type="plant", ref_id=plant_id,
        )
        amount = amount if amount is not None else self._sim.get("actions", {}).get("feed_amount", 30)
        plant.nutrient_level = min(100.0, plant.nutrient_level + amount)
        self._log(plant, "fed", payload={"amount": amount})
        return plant

    def treat_pests(self, player_id: str, plant_id: str) -> Plant:
        plant = self._get_plant(player_id, plant_id)
        self._require_living(plant)
        self.sync(plant)
        post(
            self.session, player_id, -self.cfg.pest_treatment_cost,
            LedgerEntryType.PEST_TREATMENT, ref_type="plant", ref_id=plant_id,
        )
        cleared = plant.pest_level
        plant.pest_level = 0.0
        plant.condition_flags = engine.reactions.compute_conditions(plant, self._sim)
        self._log(plant, "pest_treated", payload={"cleared": cleared})
        return plant

    def treat_disease(self, player_id: str, plant_id: str) -> Plant:
        plant = self._get_plant(player_id, plant_id)
        self._require_living(plant)
        self.sync(plant)
        post(
            self.session, player_id, -self.cfg.disease_treatment_cost,
            LedgerEntryType.DISEASE_TREATMENT, ref_type="plant", ref_id=plant_id,
        )
        cleared = plant.disease_level
        plant.disease_level = 0.0
        plant.condition_flags = engine.reactions.compute_conditions(plant, self._sim)
        self._log(plant, "disease_treated", payload={"cleared": cleared})
        return plant

    def set_environment(
        self, player_id: str, pod_id: str, temperature, humidity, co2_level,
        light_intensity, ph_level,
    ) -> GrowPod:
        pod = self.session.get(GrowPod, pod_id)
        if pod is None or pod.player_id != player_id:
            raise GameError("Pod not found")

        pod.temperature = temperature
        pod.humidity = humidity
        pod.co2_level = co2_level
        pod.light_intensity = light_intensity
        pod.ph_level = ph_level

        self.session.add(
            EnvironmentReading(
                pod_id=pod_id, temperature=temperature, humidity=humidity,
                co2_level=co2_level, light_intensity=light_intensity, ph_level=ph_level,
            )
        )

        # Bring every living plant in the pod up to date under the old
        # environment before the new readings take effect.
        plants = (
            self.session.query(Plant)
            .filter(Plant.pod_id == pod_id, Plant.harvested.is_(False), Plant.is_alive.is_(True))
            .all()
        )
        for plant in plants:
            self.sync(plant)
        return pod

    # ----- helpers --------------------------------------------------------
    def _require_living(self, plant: Plant) -> None:
        if plant.harvested:
            raise GameError("Plant already harvested")
        if not plant.is_alive:
            raise GameError("Plant is dead")

    def _log(self, plant: Plant, event_type: str, payload: dict) -> None:
        self.session.add(
            PlantEvent(
                plant_id=plant.id,
                timestamp=self.clock.now(),
                event_type=event_type,
                payload=payload,
            )
        )
