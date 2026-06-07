"""Genetics: deterministic, reproducible, in-range crossbreeding."""

import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from growpodempire.genetics.traits import (
    TRAIT_SPECS,
    genome_from_traits,
    normalize_genome,
)
from growpodempire.genetics.breeding import cross, derive_strain_fields, assign_rarity


def _genome(**traits):
    # "yield" is a reserved word, so allow passing it via the alias y=...
    if "y" in traits:
        traits["yield"] = traits.pop("y")
    return genome_from_traits(traits)


def test_cross_is_deterministic_for_a_seed():
    a = _genome(thc=20, cbd=1, indica_ratio=0.5, y=500)
    b = _genome(thc=24, cbd=2, indica_ratio=0.3, y=600)
    r1 = cross(a, b, random.Random(42), stability_a=0.8, stability_b=0.8)
    r2 = cross(a, b, random.Random(42), stability_a=0.8, stability_b=0.8)
    assert r1.genome == r2.genome
    assert r1.stability == r2.stability


def test_cross_offspring_traits_within_valid_ranges():
    a = _genome(thc=30, cbd=0, indica_ratio=1.0, y=800)
    b = _genome(thc=5, cbd=20, indica_ratio=0.0, y=50)
    r = cross(a, b, random.Random(7), stability_a=0.6, stability_b=0.6)
    for trait, spec in TRAIT_SPECS.items():
        v = r.genome[trait]["value"]
        assert spec.low <= v <= spec.high, f"{trait}={v} out of range"


def test_selfing_a_stable_line_breeds_true():
    # Crossing a fully stable strain with itself -> zero segregation variance,
    # so offspring gene values equal the parent's exactly.
    a = _genome(thc=22, cbd=1, indica_ratio=0.5, y=500, flowering_time=63)
    r = cross(a, a, random.Random(1), stability_a=1.0, stability_b=1.0)
    na = normalize_genome(a)
    for trait in TRAIT_SPECS:
        assert r.genome[trait]["value"] == na[trait]["value"]


def test_fresh_cross_is_less_stable_than_parents():
    a = _genome(thc=20)
    b = _genome(thc=24)
    r = cross(a, b, random.Random(3), stability_a=0.9, stability_b=0.9)
    assert r.stability < 0.9
    assert r.generation == 1


def test_derive_strain_fields_widen_with_instability():
    g = _genome(thc=20, cbd=1, indica_ratio=0.5, y=500, flowering_time=63)
    stable = derive_strain_fields(g, stability=1.0)
    wild = derive_strain_fields(g, stability=0.5)
    stable_span = stable["thc_max"] - stable["thc_min"]
    wild_span = wild["thc_max"] - wild["thc_min"]
    assert stable_span == 0
    assert wild_span > stable_span


def test_assign_rarity_returns_valid_tier():
    g = _genome(thc=30, y=700)
    r = assign_rarity(g, stability=0.9, parent_rarities=("rare", "rare"))
    assert r.value in {"common", "uncommon", "rare", "epic", "legendary"}
