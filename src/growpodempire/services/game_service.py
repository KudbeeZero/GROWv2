"""
GameService — the DB-backed game logic layer for the new economy, strain,
breeding, and marketplace features.

Operates on an injected SQLAlchemy Session (the caller owns the transaction
boundary via session_scope). All currency movements go through economy.ledger
so balances stay consistent and auditable.
"""

import random
import secrets
from decimal import Decimal
from typing import List, Optional

from sqlalchemy.orm import Session

from ..config import get_settings
from ..economy import pricing
from ..economy.config import get_economy_config, EconomyConfig
from ..economy.ledger import post, to_money
from ..enums import (
    GrowthStage,
    LedgerEntryType,
    LineageType,
    Rarity,
    SeedSource,
    ListingStatus,
    ListingItemType,
)
from ..genetics.breeding import cross, derive_strain_fields, assign_rarity
from ..simulation import engine
from ..simulation.clock import Clock, SystemClock
from . import leveling_service
from ..db.models import (
    Player,
    Wallet,
    Strain,
    SeedInventory,
    GrowPod,
    Plant,
    BreedingEvent,
    Harvest,
    MarketListing,
    LedgerEntry,
)
from ..db.seed import slugify


class GameError(Exception):
    """Domain error surfaced to the API as a 400."""


class GameService:
    def __init__(
        self,
        session: Session,
        config: Optional[EconomyConfig] = None,
        clock: Optional[Clock] = None,
    ):
        self.session = session
        self.cfg = config or get_economy_config()
        self.clock = clock or SystemClock()

    # ----- Players & wallets ---------------------------------------------
    def create_player(self, username: str, email: Optional[str] = None) -> Player:
        if self.session.query(Player).filter(Player.username == username).first():
            raise GameError(f"Username '{username}' already taken")

        player = Player(
            username=username, email=email, api_key=secrets.token_urlsafe(32)
        )
        self.session.add(player)
        self.session.flush()  # assign player.id

        wallet = Wallet(player_id=player.id, cached_balance=Decimal("0"))
        self.session.add(wallet)
        self.session.flush()

        post(
            self.session,
            player.id,
            self.cfg.starting_balance,
            LedgerEntryType.STARTING_GRANT,
        )
        return player

    def get_player(self, player_id: str) -> Player:
        player = self.session.get(Player, player_id)
        if player is None:
            raise GameError(f"Player {player_id} not found")
        return player

    def link_wallet(self, player_id: str, algorand_address: str) -> Player:
        """Associate a player with an Algorand address (Phase 3)."""
        if not algorand_address:
            raise GameError("algorand_address is required")
        player = self.get_player(player_id)
        player.algorand_address = algorand_address
        return player

    def get_wallet(self, player_id: str) -> Wallet:
        wallet = (
            self.session.query(Wallet)
            .filter(Wallet.player_id == player_id)
            .one_or_none()
        )
        if wallet is None:
            raise GameError(f"Wallet for player {player_id} not found")
        return wallet

    def get_ledger(self, player_id: str, limit: int = 100) -> List[LedgerEntry]:
        return (
            self.session.query(LedgerEntry)
            .filter(LedgerEntry.player_id == player_id)
            .order_by(LedgerEntry.created_at.desc())
            .limit(limit)
            .all()
        )

    # ----- Strains & seeds ------------------------------------------------
    def list_strains(self, catalog_only: bool = False) -> List[Strain]:
        q = self.session.query(Strain)
        if catalog_only:
            q = q.filter(Strain.is_base_catalog.is_(True))
        return q.order_by(Strain.rarity, Strain.name).all()

    def get_strain(self, strain_id: str) -> Strain:
        strain = self.session.get(Strain, strain_id)
        if strain is None:
            raise GameError(f"Strain {strain_id} not found")
        return strain

    def get_seed_inventory(self, player_id: str) -> List[SeedInventory]:
        return (
            self.session.query(SeedInventory)
            .filter(SeedInventory.player_id == player_id, SeedInventory.quantity > 0)
            .all()
        )

    def buy_seed(self, player_id: str, strain_id: str, quantity: int = 1) -> SeedInventory:
        if quantity < 1:
            raise GameError("quantity must be >= 1")
        strain = self.get_strain(strain_id)

        unit = pricing.seed_price(strain.rarity, self.cfg)
        total = to_money(unit * quantity)
        post(
            self.session,
            player_id,
            -total,
            LedgerEntryType.SEED_PURCHASE,
            ref_type="strain",
            ref_id=strain_id,
        )

        stack = self._get_or_create_seed_stack(
            player_id, strain_id, SeedSource.PURCHASED
        )
        stack.quantity += quantity
        return stack

    def _get_or_create_seed_stack(
        self, player_id: str, strain_id: str, source: SeedSource
    ) -> SeedInventory:
        stack = (
            self.session.query(SeedInventory)
            .filter(
                SeedInventory.player_id == player_id,
                SeedInventory.strain_id == strain_id,
            )
            .one_or_none()
        )
        if stack is None:
            stack = SeedInventory(
                player_id=player_id,
                strain_id=strain_id,
                quantity=0,
                source=source.value,
            )
            self.session.add(stack)
            self.session.flush()
        return stack

    # ----- Pods & planting ------------------------------------------------
    def create_pod(
        self,
        player_id: str,
        name: str,
        capacity: int = 4,
        tier: str = "basic",
        charge: bool = True,
    ) -> GrowPod:
        self.get_player(player_id)
        if charge:
            price = self.cfg.pod_price(tier)
            post(
                self.session,
                player_id,
                -to_money(price),
                LedgerEntryType.POD_PURCHASE,
                ref_type="pod_tier",
                ref_id=tier,
            )
        pod = GrowPod(
            player_id=player_id, name=name, capacity=capacity, tier=tier
        )
        self.session.add(pod)
        self.session.flush()
        return pod

    def plant_seed(self, player_id: str, seed_id: str, pod_id: str) -> Plant:
        stack = self.session.get(SeedInventory, seed_id)
        if stack is None or stack.player_id != player_id:
            raise GameError("Seed not found in player's inventory")
        if stack.quantity < 1:
            raise GameError("No seeds left in that stack")

        pod = self.session.get(GrowPod, pod_id)
        if pod is None or pod.player_id != player_id:
            raise GameError("Pod not found")

        planted = (
            self.session.query(Plant)
            .filter(Plant.pod_id == pod_id, Plant.harvested.is_(False))
            .count()
        )
        if planted >= pod.capacity:
            raise GameError("Pod is at full capacity")

        strain = self.get_strain(stack.strain_id)
        stack.quantity -= 1

        plant = Plant(
            player_id=player_id,
            pod_id=pod_id,
            strain_id=strain.id,
            seed_id=seed_id,
            genome=strain.genome,  # immutable per-plant copy
            growth_stage=GrowthStage.SEED.value,
        )
        self.session.add(plant)
        self.session.flush()
        return plant

    # ----- Breeding -------------------------------------------------------
    def breed(
        self,
        player_id: str,
        parent_a_id: str,
        parent_b_id: str,
        rng_seed: Optional[int] = None,
        offspring_name: Optional[str] = None,
    ) -> Strain:
        self.get_player(player_id)
        parent_a = self.get_strain(parent_a_id)
        parent_b = self.get_strain(parent_b_id)

        fee = pricing.breeding_fee(parent_a.rarity, parent_b.rarity, self.cfg)
        post(
            self.session,
            player_id,
            -fee,
            LedgerEntryType.BREEDING_FEE,
            ref_type="breeding",
        )

        if rng_seed is None:
            settings = get_settings()
            rng_seed = (
                settings.rng_seed
                if settings.rng_seed is not None
                else random.randrange(2**31)
            )
        rng = random.Random(rng_seed)

        result = cross(
            parent_a.genome,
            parent_b.genome,
            rng,
            stability_a=parent_a.stability,
            stability_b=parent_b.stability,
            generation_a=parent_a.generation,
            generation_b=parent_b.generation,
        )
        rarity = assign_rarity(
            result.genome, result.stability, (parent_a.rarity, parent_b.rarity)
        )
        fields = derive_strain_fields(result.genome, result.stability)

        name = offspring_name or f"{parent_a.name} x {parent_b.name}"
        offspring = Strain(
            name=name,
            slug=self._unique_slug(slugify(name)),
            lineage_type=LineageType.BRED.value,
            rarity=rarity.value,
            terpenes=list({*(parent_a.terpenes or []), *(parent_b.terpenes or [])}),
            genome=result.genome,
            stability=result.stability,
            generation=result.generation,
            parent_a_id=parent_a.id,
            parent_b_id=parent_b.id,
            is_base_catalog=False,
            created_by_player_id=player_id,
            **fields,
        )
        self.session.add(offspring)
        self.session.flush()

        event = BreedingEvent(
            player_id=player_id,
            parent_a_id=parent_a.id,
            parent_b_id=parent_b.id,
            offspring_strain_id=offspring.id,
            rng_seed=rng_seed,
            inherited_traits=result.inherited_traits,
        )
        self.session.add(event)

        # Reward the breeder with a seed of their new strain.
        stack = self._get_or_create_seed_stack(player_id, offspring.id, SeedSource.BRED)
        stack.quantity += 1

        leveling_service.award(self.session, player_id, "breed", self.cfg)
        return offspring

    def _unique_slug(self, base: str) -> str:
        slug = base
        i = 2
        while self.session.query(Strain).filter(Strain.slug == slug).first():
            slug = f"{base}-{i}"
            i += 1
        return slug

    # ----- Harvest & sale -------------------------------------------------
    def harvest_plant(
        self,
        player_id: str,
        plant_id: str,
        weight_g: Optional[float] = None,
        quality: Optional[float] = None,
        sell: bool = True,
    ) -> Harvest:
        plant = self.session.get(Plant, plant_id)
        if plant is None or plant.player_id != player_id:
            raise GameError("Plant not found")
        if plant.harvested:
            raise GameError("Plant already harvested")

        # Bring the plant's simulated state up to "now" so yield/quality reflect
        # how it was actually grown.
        engine.catch_up(self.session, plant, self.clock.now(), self.cfg)

        strain = self.get_strain(plant.strain_id)

        # Yield scales with health; quality is the plant's health at harvest.
        if quality is None:
            quality = max(0.0, min(100.0, plant.health))
        if weight_g is None:
            midpoint = (strain.yield_min + strain.yield_max) / 2.0
            weight_g = round(midpoint * (0.4 + 0.6 * plant.health / 100.0), 1)

        thc_actual = (strain.thc_min + strain.thc_max) / 2.0
        cbd_actual = (strain.cbd_min + strain.cbd_max) / 2.0

        plant.harvested = True
        plant.growth_stage = GrowthStage.HARVEST.value

        harvest = Harvest(
            player_id=player_id,
            plant_id=plant_id,
            strain_id=strain.id,
            weight_g=weight_g,
            quality=quality,
            thc_actual=thc_actual,
            cbd_actual=cbd_actual,
            rarity_snapshot=strain.rarity,
        )
        self.session.add(harvest)
        self.session.flush()

        if sell:
            value = pricing.harvest_value(
                weight_g, quality, strain.rarity, self.cfg, thc_actual=thc_actual
            )
            post(
                self.session,
                player_id,
                value,
                LedgerEntryType.HARVEST_SALE,
                ref_type="harvest",
                ref_id=harvest.id,
            )
            harvest.sale_value = value
            harvest.sold = True

        leveling_service.award(self.session, player_id, "harvest", self.cfg)
        return harvest

    # ----- Marketplace ----------------------------------------------------
    def list_market(self) -> List[MarketListing]:
        return (
            self.session.query(MarketListing)
            .filter(MarketListing.status == ListingStatus.ACTIVE.value)
            .order_by(MarketListing.created_at.desc())
            .all()
        )

    def create_seed_listing(
        self, player_id: str, seed_id: str, quantity: int, unit_price
    ) -> MarketListing:
        stack = self.session.get(SeedInventory, seed_id)
        if stack is None or stack.player_id != player_id:
            raise GameError("Seed not found in player's inventory")
        if quantity < 1 or stack.quantity < quantity:
            raise GameError("Not enough seeds to list")

        unit_price = to_money(unit_price)
        if unit_price <= 0:
            raise GameError("unit_price must be positive")

        # Escrow the seeds out of inventory and charge a listing fee (a sink).
        stack.quantity -= quantity
        fee = to_money(
            unit_price * quantity * Decimal(str(self.cfg.market["listing_fee_pct"]))
        )
        if fee > 0:
            post(
                self.session,
                player_id,
                -fee,
                LedgerEntryType.MARKET_FEE,
                ref_type="listing",
            )

        listing = MarketListing(
            seller_id=player_id,
            item_type=ListingItemType.SEED.value,
            item_ref_id=stack.strain_id,  # buyers receive seeds of this strain
            quantity=quantity,
            unit_price=unit_price,
        )
        self.session.add(listing)
        self.session.flush()
        return listing

    def buy_listing(self, buyer_id: str, listing_id: str) -> MarketListing:
        listing = self.session.get(MarketListing, listing_id)
        if listing is None or listing.status != ListingStatus.ACTIVE.value:
            raise GameError("Listing not available")
        if listing.seller_id == buyer_id:
            raise GameError("Cannot buy your own listing")

        total = to_money(listing.unit_price * listing.quantity)
        tax = to_money(total * Decimal(str(self.cfg.market["sale_tax_pct"])))
        seller_proceeds = to_money(total - tax)  # tax is burned (inflation sink)

        # Buyer pays the full price.
        post(
            self.session,
            buyer_id,
            -total,
            LedgerEntryType.MARKET_BUY,
            ref_type="listing",
            ref_id=listing_id,
        )
        # Seller receives proceeds net of tax.
        post(
            self.session,
            listing.seller_id,
            seller_proceeds,
            LedgerEntryType.MARKET_SALE,
            ref_type="listing",
            ref_id=listing_id,
        )

        # Deliver the goods (seeds) to the buyer.
        if listing.item_type == ListingItemType.SEED.value:
            stack = self._get_or_create_seed_stack(
                buyer_id, listing.item_ref_id, SeedSource.MARKET
            )
            stack.quantity += listing.quantity

        listing.status = ListingStatus.SOLD.value
        listing.buyer_id = buyer_id
        return listing
