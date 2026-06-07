"""Pod automation: tiers grant auto-water/feed honored by the sim."""

import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from growpodempire.db.session import session_scope
from growpodempire.db.models import Strain
from growpodempire.economy.config import load_economy_config
from growpodempire.economy.ledger import balance
from growpodempire.services.game_service import GameService
from growpodempire.simulation import engine

CFG = load_economy_config()
BASE = datetime(2025, 1, 1)


def _plant_in_tier(s, tier):
    svc = GameService(s)
    p = svc.create_player(f"auto_{tier}")
    strain = s.query(Strain).filter(Strain.slug == "white-widow").one()
    stack = svc.buy_seed(p.id, strain.id)
    pod = svc.create_pod(p.id, "Tent", tier=tier, charge=False)
    plant = svc.plant_seed(p.id, stack.id, pod.id)
    for attr in ("last_tick_at", "stage_entered_at", "planted_at"):
        setattr(plant, attr, BASE)
    s.flush()
    return plant


def test_tier_sets_automation_flags(db):
    with session_scope() as s:
        svc = GameService(s)
        p = svc.create_player("tiers")
        basic = svc.create_pod(p.id, "b", tier="basic", charge=False)
        pro = svc.create_pod(p.id, "p", tier="pro", charge=False)
        assert (basic.auto_water, basic.auto_feed) == (False, False)
        assert (pro.auto_water, pro.auto_feed) == (True, True)


def test_pro_pod_keeps_resources_up(db):
    # After a week unattended, a pro (auto) pod holds water far better than basic.
    with session_scope() as s:
        basic_plant = _plant_in_tier(s, "basic")
        pro_plant = _plant_in_tier(s, "pro")
        engine.catch_up(s, basic_plant, BASE + timedelta(days=7), CFG)
        engine.catch_up(s, pro_plant, BASE + timedelta(days=7), CFG)
        assert pro_plant.water_level > basic_plant.water_level
        assert pro_plant.nutrient_level > basic_plant.nutrient_level
        assert pro_plant.health > basic_plant.health


def test_upgrade_charges_difference_and_enables_automation(db):
    with session_scope() as s:
        svc = GameService(s)
        p = svc.create_player("upgrader")
        pod = svc.create_pod(p.id, "Tent", tier="basic")  # costs 100
        before = balance(s, p.id)
        svc.upgrade_pod(p.id, pod.id, "standard")           # diff 400-100 = 300
        assert balance(s, p.id) == before - 300
        assert pod.tier == "standard" and pod.auto_water is True
