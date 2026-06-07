"""
Pure pricing formulas. No DB, no randomness — deterministic and unit-tested.

All money is returned as a quantized Decimal.
"""

from decimal import Decimal

from ..enums import Rarity, rarity_index
from .config import EconomyConfig
from .ledger import to_money


def seed_price(rarity: "Rarity | str", cfg: EconomyConfig) -> Decimal:
    """Price of buying a single seed of the given rarity."""
    rarity = Rarity(rarity).value if not isinstance(rarity, str) else rarity
    base = cfg.seed_base_cost()
    mult = cfg.seed_rarity_multiplier(rarity)
    return to_money(base * mult)


def breeding_fee(
    rarity_a: "Rarity | str", rarity_b: "Rarity | str", cfg: EconomyConfig
) -> Decimal:
    """Fee to cross two strains; scales with the parents' average rarity tier."""
    avg_tier = (rarity_index(rarity_a) + rarity_index(rarity_b)) / 2.0
    fee = cfg.breeding_base_fee + avg_tier * cfg.breeding_rarity_fee_per_tier
    return to_money(fee)


def quality_factor(quality: float, cfg: EconomyConfig) -> float:
    """Map a 0..100 quality score to a non-linear 0.5..1.0 value multiplier."""
    exponent = float(cfg.harvest["quality_curve_exponent"])
    q = max(0.0, min(100.0, quality)) / 100.0
    return 0.5 + 0.5 * (q ** exponent)


def terpene_bonus(terpene_intensity: float, cfg: EconomyConfig) -> float:
    """A multiplier (>= 1.0) rewarding a strong dominant-terpene expression.

    `terpene_intensity` is the strongest expressed terpene (0..1); a fully
    expressed terpene earns up to `harvest_sale.terpene_premium_max`.
    """
    premium_max = float(cfg.harvest.get("terpene_premium_max", 0.0))
    return 1.0 + premium_max * max(0.0, min(1.0, terpene_intensity))


def harvest_value(
    weight_g: float,
    quality: float,
    rarity: "Rarity | str",
    cfg: EconomyConfig,
    *,
    thc_actual: float = 15.0,
    terpene_intensity: float = 0.0,
) -> Decimal:
    """Sale value of a harvest at the NPC market.

    value = effective_weight * base_per_gram * rarity_mult * thc_bonus
            * terpene_bonus * quality
    where weight above the soft cap yields diminishing marginal value.
    """
    rarity = Rarity(rarity).value if not isinstance(rarity, str) else rarity
    h = cfg.harvest

    base_per_gram = float(h["base_price_per_gram"])
    rarity_mult = float(h["rarity_multiplier"][rarity])
    thc_bonus = 1.0 + max(0.0, thc_actual - 15.0) * float(
        h["thc_bonus_per_pct_over_15"]
    )

    soft_cap = float(h["soft_cap_grams"])
    soft_factor = float(h["soft_cap_factor"])
    if weight_g <= soft_cap:
        effective_weight = weight_g
    else:
        effective_weight = soft_cap + (weight_g - soft_cap) * soft_factor

    value = (
        effective_weight
        * base_per_gram
        * rarity_mult
        * thc_bonus
        * terpene_bonus(terpene_intensity, cfg)
        * quality_factor(quality, cfg)
    )
    return to_money(value)
