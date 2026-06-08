"""Provable fairness: a bred strain's genome must re-derive from its seed."""

import copy
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from growpodempire.db.models import Strain
from growpodempire.services.game_service import GameService


def _breed(session, username="breeder"):
    svc = GameService(session)
    p = svc.create_player(username)
    a = session.query(Strain).filter(Strain.slug == "white-widow").one()
    b = session.query(Strain).filter(Strain.slug == "blue-dream").one()
    child = svc.breed(p.id, a.id, b.id)
    return svc, child


def test_bred_strain_verifies(session):
    svc, child = _breed(session)
    proof = svc.verify_strain(child.id)
    assert proof["verifiable"] is True
    assert proof["verified"] is True
    assert proof["max_value_delta"] == 0.0
    assert proof["mismatched_traits"] == []
    assert proof["rng_seed"] is not None
    assert proof["parent_a_id"] and proof["parent_b_id"]


def test_tampered_genome_fails_verification(session):
    """If a strain's stored genome is altered, replay no longer matches."""
    svc, child = _breed(session, username="tamperer")
    tampered = copy.deepcopy(child.genome)
    tampered["thc"]["value"] = 999.0
    child.genome = tampered
    session.flush()
    proof = svc.verify_strain(child.id)
    assert proof["verifiable"] is True
    assert proof["verified"] is False
    assert "thc" in proof["mismatched_traits"]
    assert proof["max_value_delta"] > 1.0


def test_base_catalog_strain_is_not_verifiable(session):
    svc = GameService(session)
    base = session.query(Strain).filter(Strain.is_base_catalog.is_(True)).first()
    proof = svc.verify_strain(base.id)
    assert proof["verifiable"] is False
    assert "reason" in proof
