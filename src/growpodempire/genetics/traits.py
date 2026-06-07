"""
Trait definitions for the genetics engine.

A *genome* is a dict mapping trait name -> {"value": float, "dominance": str}.
Each trait has a valid range and a base segregation sigma (as a fraction of its
range) that controls how much offspring vary from the parental mean.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict


class Dominance(str, Enum):
    DOMINANT = "dominant"
    RECESSIVE = "recessive"
    CODOMINANT = "codominant"


@dataclass(frozen=True)
class TraitSpec:
    low: float
    high: float
    sigma_frac: float  # base variance as a fraction of (high - low)
    is_int: bool = False

    def clamp(self, value: float) -> float:
        v = max(self.low, min(self.high, value))
        return round(v) if self.is_int else v

    @property
    def span(self) -> float:
        return self.high - self.low


# Visible traits drive display stats; hidden traits (resistances/vigor) feed the
# Phase 2 simulation but still inherit through breeding.
TRAIT_SPECS: Dict[str, TraitSpec] = {
    "indica_ratio": TraitSpec(0.0, 1.0, 0.12),
    "thc": TraitSpec(0.0, 35.0, 0.10),
    "cbd": TraitSpec(0.0, 25.0, 0.12),
    "flowering_time": TraitSpec(45.0, 120.0, 0.08, is_int=True),
    "yield": TraitSpec(50.0, 800.0, 0.10),
    "difficulty": TraitSpec(1.0, 5.0, 0.10, is_int=True),
    "disease_resistance": TraitSpec(0.0, 1.0, 0.12),
    "pest_resistance": TraitSpec(0.0, 1.0, 0.12),
    "vigor": TraitSpec(0.0, 1.0, 0.10),
}

# Sensible defaults for hidden traits when a catalog entry omits them.
HIDDEN_TRAIT_DEFAULTS = {
    "disease_resistance": 0.5,
    "pest_resistance": 0.5,
    "vigor": 0.5,
}


def normalize_genome(genome: Dict) -> Dict[str, Dict]:
    """Ensure every known trait is present and clamped, with a dominance flag."""
    out: Dict[str, Dict] = {}
    for trait, spec in TRAIT_SPECS.items():
        gene = genome.get(trait)
        if gene is None:
            value = HIDDEN_TRAIT_DEFAULTS.get(trait, (spec.low + spec.high) / 2.0)
            dominance = Dominance.CODOMINANT.value
        else:
            value = spec.clamp(float(gene["value"]))
            dominance = gene.get("dominance", Dominance.CODOMINANT.value)
        out[trait] = {"value": spec.clamp(value), "dominance": dominance}
    return out


def genome_from_traits(
    traits: Dict[str, float], dominant: Dict[str, str] = None
) -> Dict[str, Dict]:
    """Build a normalized genome from a flat trait->value mapping.

    `dominant` optionally maps trait -> dominance flag; unspecified traits are
    codominant. Used by the strain-catalog seeder.
    """
    dominant = dominant or {}
    genome: Dict[str, Dict] = {}
    for trait in TRAIT_SPECS:
        if trait in traits:
            value = float(traits[trait])
        else:
            value = HIDDEN_TRAIT_DEFAULTS.get(trait)
            if value is None:
                continue
        genome[trait] = {
            "value": value,
            "dominance": dominant.get(trait, Dominance.CODOMINANT.value),
        }
    return normalize_genome(genome)
