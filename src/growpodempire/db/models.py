"""
SQLAlchemy ORM models — the persistent game state.

Design notes:
  * Money is stored as Numeric(18, 6) and handled as Decimal in Python — never
    float — so the in-game currency can later map 1:1 to an Algorand ASA
    (decimals=6) without rounding drift.
  * Enum-valued columns are stored as plain strings (portable across SQLite and
    Postgres); the canonical values live in growpodempire.enums.
  * JSON columns use SQLAlchemy's generic JSON type (JSONB on Postgres, text on
    SQLite).
  * Genetics: every Strain carries a `genome` JSON (the canonical trait vector
    used by the breeding engine); the scalar thc/cbd/etc. columns are the
    display-facing expressed values derived from it.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    Numeric,
    String,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..enums import GrowthStage
from .base import Base, TimestampMixin, UUIDPrimaryKeyMixin

MONEY = Numeric(18, 6)


class Player(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "players"

    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), unique=True)
    # Algorand wallet address (Phase 3); nullable until the player links/creates one.
    algorand_address: Mapped[Optional[str]] = mapped_column(String(64), index=True)
    last_active_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    # Per-player API key for authenticating write requests (returned once at creation).
    api_key: Mapped[Optional[str]] = mapped_column(String(64), unique=True, index=True)
    # Progression: cumulative experience and derived level.
    xp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    # Permanent prestige: the most recent Cannabis Cup title a player has won
    # (a lifetime unlock; the full history lives in cannabis_cups.winner_id).
    cannabis_cup_title: Mapped[Optional[str]] = mapped_column(String(96), default=None)
    # Highest GrowPod University degree title earned (permanent).
    university_title: Mapped[Optional[str]] = mapped_column(String(96), default=None)

    wallet: Mapped["Wallet"] = relationship(
        back_populates="player", uselist=False, cascade="all, delete-orphan"
    )


class Wallet(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "wallets"

    player_id: Mapped[str] = mapped_column(
        ForeignKey("players.id"), unique=True, nullable=False
    )
    # Denormalized cache; authoritative balance is the sum of ledger entries.
    cached_balance: Mapped[Decimal] = mapped_column(
        MONEY, default=Decimal("0"), nullable=False
    )
    # Mirror of on-chain ASA balance (Phase 3); null until materialized.
    asa_balance: Mapped[Optional[Decimal]] = mapped_column(MONEY)
    version: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    player: Mapped["Player"] = relationship(back_populates="wallet")


class LedgerEntry(UUIDPrimaryKeyMixin, Base):
    """Append-only record of every currency movement (source of truth)."""

    __tablename__ = "ledger_entries"

    player_id: Mapped[str] = mapped_column(ForeignKey("players.id"), nullable=False)
    entry_type: Mapped[str] = mapped_column(String(32), nullable=False)
    amount: Mapped[Decimal] = mapped_column(MONEY, nullable=False)  # signed
    balance_after: Mapped[Decimal] = mapped_column(MONEY, nullable=False)
    ref_type: Mapped[Optional[str]] = mapped_column(String(32))
    ref_id: Mapped[Optional[str]] = mapped_column(String(64))
    onchain_txid: Mapped[Optional[str]] = mapped_column(String(80))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    __table_args__ = (
        Index("ix_ledger_player_created", "player_id", "created_at"),
    )


class Strain(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Cannabis genetics — catalog landraces/hybrids plus player-bred lines."""

    __tablename__ = "strains"

    name: Mapped[str] = mapped_column(String(128), nullable=False)
    slug: Mapped[str] = mapped_column(String(160), unique=True, nullable=False)
    lineage_type: Mapped[str] = mapped_column(String(16), nullable=False)
    rarity: Mapped[str] = mapped_column(String(16), nullable=False, index=True)

    # Expressed / display traits (derived from genome).
    indica_ratio: Mapped[float] = mapped_column(Float, nullable=False)  # 0..1
    thc_min: Mapped[float] = mapped_column(Float, nullable=False)
    thc_max: Mapped[float] = mapped_column(Float, nullable=False)
    cbd_min: Mapped[float] = mapped_column(Float, nullable=False)
    cbd_max: Mapped[float] = mapped_column(Float, nullable=False)
    flowering_days_min: Mapped[int] = mapped_column(Integer, nullable=False)
    flowering_days_max: Mapped[int] = mapped_column(Integer, nullable=False)
    yield_min: Mapped[float] = mapped_column(Float, nullable=False)
    yield_max: Mapped[float] = mapped_column(Float, nullable=False)
    difficulty: Mapped[int] = mapped_column(Integer, nullable=False)  # 1..5
    terpenes: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    # Availability window: "all" (always), or a season key (spring/summer/fall/
    # winter) / "limited" for event-gated strains. See balance.yaml:events.
    season: Mapped[str] = mapped_column(String(16), default="all", nullable=False)

    # Canonical trait vector consumed by the genetics engine.
    genome: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    stability: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    generation: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Lineage graph (self-referential).
    parent_a_id: Mapped[Optional[str]] = mapped_column(ForeignKey("strains.id"))
    parent_b_id: Mapped[Optional[str]] = mapped_column(ForeignKey("strains.id"))

    is_base_catalog: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    created_by_player_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("players.id")
    )

    # On-chain (Phase 3): set when a stabilized rare strain is minted as an NFT.
    nft_asset_id: Mapped[Optional[int]] = mapped_column(Integer)
    nft_status: Mapped[str] = mapped_column(String(16), default="none", nullable=False)


class StrainFavorite(UUIDPrimaryKeyMixin, Base):
    """A player's bookmark of a strain."""

    __tablename__ = "strain_favorites"

    player_id: Mapped[str] = mapped_column(ForeignKey("players.id"), nullable=False)
    strain_id: Mapped[str] = mapped_column(ForeignKey("strains.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    __table_args__ = (
        Index("ix_fav_player_strain", "player_id", "strain_id", unique=True),
    )


class SeedInventory(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A stack of seeds of a given strain owned by a player."""

    __tablename__ = "seed_inventory"

    player_id: Mapped[str] = mapped_column(ForeignKey("players.id"), nullable=False)
    strain_id: Mapped[str] = mapped_column(ForeignKey("strains.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    source: Mapped[str] = mapped_column(String(16), default="purchased", nullable=False)
    feminized: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    __table_args__ = (
        Index("ix_seed_player_strain", "player_id", "strain_id"),
    )


class ResearchProgress(UUIDPrimaryKeyMixin, Base):
    """A research-tree node a player has unlocked (Phase 2 expansion)."""

    __tablename__ = "research_progress"

    player_id: Mapped[str] = mapped_column(ForeignKey("players.id"), nullable=False)
    node_key: Mapped[str] = mapped_column(String(48), nullable=False)
    unlocked_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    __table_args__ = (
        Index("ix_research_player_node", "player_id", "node_key", unique=True),
    )


class ConsumableInventory(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A stack of a shop consumable owned by a player (Phase 2 expansion)."""

    __tablename__ = "consumable_inventory"

    player_id: Mapped[str] = mapped_column(ForeignKey("players.id"), nullable=False)
    item_key: Mapped[str] = mapped_column(String(48), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    __table_args__ = (
        Index("ix_consumable_player_item", "player_id", "item_key", unique=True),
    )


class GrowPod(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "grow_pods"

    player_id: Mapped[str] = mapped_column(ForeignKey("players.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, default=4, nullable=False)
    tier: Mapped[str] = mapped_column(String(16), default="basic", nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    # Automation perks (granted by higher tiers): keep resources topped up.
    auto_water: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    auto_feed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Latest environment snapshot (the 5 sensor params).
    temperature: Mapped[Optional[float]] = mapped_column(Float)
    humidity: Mapped[Optional[float]] = mapped_column(Float)
    co2_level: Mapped[Optional[float]] = mapped_column(Float)
    light_intensity: Mapped[Optional[float]] = mapped_column(Float)
    ph_level: Mapped[Optional[float]] = mapped_column(Float)


class Plant(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A growing plant — the aggregate the Phase 2 simulation will drive."""

    __tablename__ = "plants"

    player_id: Mapped[str] = mapped_column(ForeignKey("players.id"), nullable=False)
    pod_id: Mapped[str] = mapped_column(ForeignKey("grow_pods.id"), nullable=False)
    strain_id: Mapped[str] = mapped_column(ForeignKey("strains.id"), nullable=False)
    seed_id: Mapped[Optional[str]] = mapped_column(ForeignKey("seed_inventory.id"))

    # Immutable per-plant genetics, copied from the seed/strain at plant time.
    genome: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    growth_stage: Mapped[str] = mapped_column(
        String(16), default=GrowthStage.SEED.value, nullable=False
    )
    planted_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    stage_entered_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    # Drives Phase 2 compute-on-read catch-up simulation.
    last_tick_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    height: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    health: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)

    # Resource / stress levels (defaults are sensible neutral values; the
    # simulation engine in Phase 2 evolves these over real time).
    water_level: Mapped[float] = mapped_column(Float, default=60.0, nullable=False)
    nutrient_level: Mapped[float] = mapped_column(Float, default=60.0, nullable=False)
    pest_level: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    disease_level: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    condition_flags: Mapped[list] = mapped_column(JSON, default=list, nullable=False)

    is_alive: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    harvested: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class EnvironmentReading(UUIDPrimaryKeyMixin, Base):
    """Time-series of pod environmental sensor readings."""

    __tablename__ = "environment_readings"

    pod_id: Mapped[str] = mapped_column(ForeignKey("grow_pods.id"), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    temperature: Mapped[float] = mapped_column(Float, nullable=False)
    humidity: Mapped[float] = mapped_column(Float, nullable=False)
    co2_level: Mapped[float] = mapped_column(Float, nullable=False)
    light_intensity: Mapped[float] = mapped_column(Float, nullable=False)
    ph_level: Mapped[float] = mapped_column(Float, nullable=False)

    __table_args__ = (Index("ix_env_pod_ts", "pod_id", "timestamp"),)


class GrowthMeasurement(UUIDPrimaryKeyMixin, Base):
    """Time-series of plant growth measurements."""

    __tablename__ = "growth_measurements"

    plant_id: Mapped[str] = mapped_column(ForeignKey("plants.id"), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    height: Mapped[float] = mapped_column(Float, nullable=False)
    leaf_count: Mapped[Optional[int]] = mapped_column(Integer)
    health: Mapped[float] = mapped_column(Float, nullable=False)
    growth_rate: Mapped[Optional[float]] = mapped_column(Float)

    __table_args__ = (Index("ix_growth_plant_ts", "plant_id", "timestamp"),)


class PlantEvent(UUIDPrimaryKeyMixin, Base):
    """Simulation event log: stage changes, condition onsets, death, care."""

    __tablename__ = "plant_events"

    plant_id: Mapped[str] = mapped_column(ForeignKey("plants.id"), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    event_type: Mapped[str] = mapped_column(String(32), nullable=False)
    severity: Mapped[Optional[str]] = mapped_column(String(16))
    payload: Mapped[dict] = mapped_column(JSON, default=dict)

    __table_args__ = (Index("ix_event_plant_ts", "plant_id", "timestamp"),)


class BreedingEvent(UUIDPrimaryKeyMixin, Base):
    """An act of crossing two strains into a new offspring strain."""

    __tablename__ = "breeding_events"

    player_id: Mapped[str] = mapped_column(ForeignKey("players.id"), nullable=False)
    parent_a_id: Mapped[str] = mapped_column(ForeignKey("strains.id"), nullable=False)
    parent_b_id: Mapped[str] = mapped_column(ForeignKey("strains.id"), nullable=False)
    offspring_strain_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("strains.id")
    )
    rng_seed: Mapped[int] = mapped_column(Integer, nullable=False)
    inherited_traits: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )


class Harvest(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "harvests"

    player_id: Mapped[str] = mapped_column(ForeignKey("players.id"), nullable=False)
    plant_id: Mapped[str] = mapped_column(ForeignKey("plants.id"), nullable=False)
    strain_id: Mapped[str] = mapped_column(ForeignKey("strains.id"), nullable=False)
    harvested_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    weight_g: Mapped[float] = mapped_column(Float, nullable=False)
    quality: Mapped[float] = mapped_column(Float, nullable=False)  # 0..100
    thc_actual: Mapped[Optional[float]] = mapped_column(Float)
    cbd_actual: Mapped[Optional[float]] = mapped_column(Float)
    rarity_snapshot: Mapped[str] = mapped_column(String(16), nullable=False)
    # Expressed terpene vector at harvest (trait -> 0..1 intensity).
    terpenes: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    sale_value: Mapped[Optional[Decimal]] = mapped_column(MONEY)
    sold: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Post-harvest curing (Phase 1 expansion). "none" -> "curing" -> "cured".
    cure_status: Mapped[str] = mapped_column(String(16), default="none", nullable=False)
    cure_started_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    cure_target_hours: Mapped[Optional[float]] = mapped_column(Float)
    base_quality: Mapped[Optional[float]] = mapped_column(Float)  # quality before curing
    cure_quality_bonus: Mapped[Optional[float]] = mapped_column(Float)  # net delta applied

    # On-chain (Phase 3).
    nft_asset_id: Mapped[Optional[int]] = mapped_column(Integer)
    nft_status: Mapped[str] = mapped_column(String(16), default="none", nullable=False)


class Contract(UUIDPrimaryKeyMixin, Base):
    """A timed NPC order: deliver target grams of a rarity by a deadline."""

    __tablename__ = "contracts"

    player_id: Mapped[str] = mapped_column(ForeignKey("players.id"), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    target_rarity: Mapped[Optional[str]] = mapped_column(String(16))
    target_grams: Mapped[float] = mapped_column(Float, nullable=False)
    reward_grow: Mapped[Decimal] = mapped_column(MONEY, nullable=False)
    reward_xp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(16), default="open", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    deadline_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    fulfilled_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    __table_args__ = (Index("ix_contract_player_status", "player_id", "status"),)


class CannabisCup(UUIDPrimaryKeyMixin, Base):
    """A seasonal Cannabis Cup competition. One open cup per season `edition`
    (e.g. "2026-summer"); players submit harvests, the best score wins, and the
    champion earns lifetime prestige (a one-of-a-kind strain + a permanent title).
    """

    __tablename__ = "cannabis_cups"

    edition: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    season: Mapped[str] = mapped_column(String(16), nullable=False)
    title: Mapped[str] = mapped_column(String(96), nullable=False)
    status: Mapped[str] = mapped_column(String(16), default="open", nullable=False)
    entry_fee: Mapped[Decimal] = mapped_column(MONEY, nullable=False)
    prize_pool: Mapped[Decimal] = mapped_column(MONEY, default=0, nullable=False)
    starts_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    ends_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    judged_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    winner_id: Mapped[Optional[str]] = mapped_column(ForeignKey("players.id"))
    champion_strain_id: Mapped[Optional[str]] = mapped_column(ForeignKey("strains.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    __table_args__ = (Index("ix_cannabis_cups_status_ends_at", "status", "ends_at"),)


class CupEntry(UUIDPrimaryKeyMixin, Base):
    """One harvest submitted to a Cannabis Cup, with its server-computed score
    snapshotted at submission (immutable). Ranked at judging."""

    __tablename__ = "cup_entries"

    cup_id: Mapped[str] = mapped_column(ForeignKey("cannabis_cups.id"), nullable=False)
    player_id: Mapped[str] = mapped_column(ForeignKey("players.id"), nullable=False)
    harvest_id: Mapped[str] = mapped_column(ForeignKey("harvests.id"), nullable=False)
    strain_id: Mapped[str] = mapped_column(ForeignKey("strains.id"), nullable=False)
    strain_name: Mapped[str] = mapped_column(String(128), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    rank: Mapped[Optional[int]] = mapped_column(Integer)
    prize_grow: Mapped[Decimal] = mapped_column(MONEY, default=0, nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    __table_args__ = (
        Index("ix_cup_entries_cup_score", "cup_id", "score"),
        Index("uq_cup_entries_cup_harvest", "cup_id", "harvest_id", unique=True),
    )


class CourseEnrollment(UUIDPrimaryKeyMixin, Base):
    """A player enrolled in a GrowPod University course. `status` goes
    enrolled -> completed once the study time elapses and the practical is met."""

    __tablename__ = "course_enrollments"

    player_id: Mapped[str] = mapped_column(ForeignKey("players.id"), nullable=False)
    course_key: Mapped[str] = mapped_column(String(48), nullable=False)
    status: Mapped[str] = mapped_column(String(16), default="enrolled", nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    __table_args__ = (
        Index("uq_course_enrollments_player_course", "player_id", "course_key", unique=True),
    )


class DegreeProgress(UUIDPrimaryKeyMixin, Base):
    """A degree a player has earned — a permanent unlock granting perks + a title."""

    __tablename__ = "degree_progress"

    player_id: Mapped[str] = mapped_column(ForeignKey("players.id"), nullable=False)
    degree_key: Mapped[str] = mapped_column(String(48), nullable=False)
    earned_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    __table_args__ = (
        Index("uq_degree_progress_player_degree", "player_id", "degree_key", unique=True),
    )


class MarketListing(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "market_listings"

    seller_id: Mapped[str] = mapped_column(ForeignKey("players.id"), nullable=False)
    item_type: Mapped[str] = mapped_column(String(16), nullable=False)
    item_ref_id: Mapped[str] = mapped_column(String(64), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(MONEY, nullable=False)
    status: Mapped[str] = mapped_column(String(16), default="active", nullable=False)
    buyer_id: Mapped[Optional[str]] = mapped_column(ForeignKey("players.id"))

    # Auction fields (is_auction=False -> a fixed-price listing).
    is_auction: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    min_bid: Mapped[Optional[Decimal]] = mapped_column(MONEY)
    highest_bid: Mapped[Optional[Decimal]] = mapped_column(MONEY)
    highest_bidder_id: Mapped[Optional[str]] = mapped_column(ForeignKey("players.id"))
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
