"""
Flask blueprint for the DB-backed game: players, wallets, strains, seeds,
breeding, harvest, and the marketplace.

Each request runs inside a `session_scope` transaction; ORM rows are serialized
to JSON-safe dicts before the scope closes.
"""

from flask import Blueprint, request, jsonify

from ..db.session import session_scope
from ..services.game_service import GameService, GameError
from ..services.simulation_service import SimulationService
from ..services.minting_service import MintingService
from ..services.progression_service import ProgressionService
from ..services.leaderboard_service import LeaderboardService
from ..services import leveling_service
from ..economy.ledger import InsufficientFundsError
from .auth import require_player
from . import serialize as S

game_bp = Blueprint("game", __name__, url_prefix="/api/game")


def _error(message: str, status: int = 400):
    return jsonify({"error": message}), status


@game_bp.errorhandler(GameError)
def _handle_game_error(exc):  # pragma: no cover - registered per blueprint
    return _error(str(exc), 400)


# ----- Players -----------------------------------------------------------
@game_bp.post("/players")
def create_player():
    data = request.get_json(force=True, silent=True) or {}
    if not data.get("username"):
        return _error("username is required")
    try:
        with session_scope() as s:
            svc = GameService(s)
            player = svc.create_player(data["username"], data.get("email"))
            wallet = svc.get_wallet(player.id)
            payload = player_payload(player, wallet)
            # Returned exactly once — the client must store it to authenticate writes.
            payload["api_key"] = player.api_key
        return jsonify(payload), 201
    except GameError as e:
        return _error(str(e))


@game_bp.get("/players/<player_id>")
def get_player(player_id):
    try:
        with session_scope() as s:
            svc = GameService(s)
            player = svc.get_player(player_id)
            wallet = svc.get_wallet(player.id)
            payload = player_payload(player, wallet)
        return jsonify(payload)
    except GameError as e:
        return _error(str(e), 404)


def player_payload(player, wallet) -> dict:
    out = S.player_dict(player, balance=wallet.cached_balance)
    out["wallet"] = S.wallet_dict(wallet)
    return out


@game_bp.get("/players/<player_id>/wallet")
def get_wallet(player_id):
    try:
        with session_scope() as s:
            payload = S.wallet_dict(GameService(s).get_wallet(player_id))
        return jsonify(payload)
    except GameError as e:
        return _error(str(e), 404)


@game_bp.get("/players/<player_id>/level")
def get_level(player_id):
    try:
        with session_scope() as s:
            player = GameService(s).get_player(player_id)
            payload = leveling_service.progress(player)
        return jsonify(payload)
    except GameError as e:
        return _error(str(e), 404)


@game_bp.get("/players/<player_id>/ledger")
def get_ledger(player_id):
    with session_scope() as s:
        entries = GameService(s).get_ledger(player_id)
        payload = [S.ledger_dict(e) for e in entries]
    return jsonify(payload)


# ----- Leaderboards ------------------------------------------------------
@game_bp.get("/leaderboards/<board>")
def leaderboards(board):
    limit = int(request.args.get("limit", 10))
    boards = {
        "richest": "richest",
        "breeders": "top_breeders",
        "harvests": "biggest_harvesters",
        "level": "top_levels",
    }
    if board not in boards:
        return _error(f"Unknown leaderboard '{board}'", 404)
    with session_scope() as s:
        payload = getattr(LeaderboardService(s), boards[board])(limit)
    return jsonify(payload)


# ----- Strains -----------------------------------------------------------
@game_bp.get("/strains")
def list_strains():
    args = request.args

    def _f(name):
        v = args.get(name)
        return float(v) if v not in (None, "") else None

    with session_scope() as s:
        strains = GameService(s).list_strains(
            catalog_only=args.get("catalog_only", "false").lower() == "true",
            q=args.get("q"),
            rarity=args.get("rarity"),
            lineage_type=args.get("lineage_type"),
            min_thc=_f("min_thc"),
            max_thc=_f("max_thc"),
            min_indica=_f("min_indica"),
            max_indica=_f("max_indica"),
        )
        payload = [S.strain_dict(st) for st in strains]
    return jsonify(payload)


@game_bp.get("/players/<player_id>/favorites")
def list_favorites(player_id):
    with session_scope() as s:
        strains = GameService(s).list_favorites(player_id)
        payload = [S.strain_dict(st) for st in strains]
    return jsonify(payload)


@game_bp.post("/players/<player_id>/strains/<strain_id>/favorite")
@require_player
def add_favorite(player_id, strain_id):
    try:
        with session_scope() as s:
            GameService(s).add_favorite(player_id, strain_id)
        return jsonify({"favorited": True}), 201
    except GameError as e:
        return _error(str(e))


@game_bp.delete("/players/<player_id>/strains/<strain_id>/favorite")
@require_player
def remove_favorite(player_id, strain_id):
    with session_scope() as s:
        GameService(s).remove_favorite(player_id, strain_id)
    return jsonify({"favorited": False})


@game_bp.get("/strains/<strain_id>")
def get_strain(strain_id):
    try:
        with session_scope() as s:
            payload = S.strain_dict(GameService(s).get_strain(strain_id))
        return jsonify(payload)
    except GameError as e:
        return _error(str(e), 404)


# ----- Seeds & planting --------------------------------------------------
@game_bp.get("/players/<player_id>/seeds")
def list_seeds(player_id):
    with session_scope() as s:
        seeds = GameService(s).get_seed_inventory(player_id)
        payload = [S.seed_dict(x) for x in seeds]
    return jsonify(payload)


@game_bp.post("/players/<player_id>/seeds/buy")
@require_player
def buy_seed(player_id):
    data = request.get_json(force=True, silent=True) or {}
    if not data.get("strain_id"):
        return _error("strain_id is required")
    try:
        with session_scope() as s:
            stack = GameService(s).buy_seed(
                player_id, data["strain_id"], int(data.get("quantity", 1))
            )
            payload = S.seed_dict(stack)
        return jsonify(payload), 201
    except (GameError, InsufficientFundsError) as e:
        return _error(str(e))


@game_bp.post("/players/<player_id>/pods")
@require_player
def create_pod(player_id):
    data = request.get_json(force=True, silent=True) or {}
    if not data.get("name"):
        return _error("name is required")
    try:
        with session_scope() as s:
            pod = GameService(s).create_pod(
                player_id,
                data["name"],
                int(data.get("capacity", 4)),
                data.get("tier", "basic"),
                charge=bool(data.get("charge", True)),
            )
            payload = S.pod_dict(pod)
        return jsonify(payload), 201
    except (GameError, InsufficientFundsError) as e:
        return _error(str(e))


@game_bp.post("/players/<player_id>/plant")
@require_player
def plant_seed(player_id):
    data = request.get_json(force=True, silent=True) or {}
    if not data.get("seed_id") or not data.get("pod_id"):
        return _error("seed_id and pod_id are required")
    try:
        with session_scope() as s:
            plant = GameService(s).plant_seed(
                player_id, data["seed_id"], data["pod_id"]
            )
            payload = S.plant_dict(plant)
        return jsonify(payload), 201
    except GameError as e:
        return _error(str(e))


# ----- Breeding ----------------------------------------------------------
@game_bp.post("/players/<player_id>/breed")
@require_player
def breed(player_id):
    data = request.get_json(force=True, silent=True) or {}
    if not data.get("parent_a_id") or not data.get("parent_b_id"):
        return _error("parent_a_id and parent_b_id are required")
    rng_seed = data.get("rng_seed")
    try:
        with session_scope() as s:
            offspring = GameService(s).breed(
                player_id,
                data["parent_a_id"],
                data["parent_b_id"],
                rng_seed=int(rng_seed) if rng_seed is not None else None,
                offspring_name=data.get("name"),
            )
            payload = S.strain_dict(offspring)
        return jsonify(payload), 201
    except (GameError, InsufficientFundsError) as e:
        return _error(str(e))


# ----- Harvest -----------------------------------------------------------
@game_bp.post("/players/<player_id>/plants/<plant_id>/harvest")
@require_player
def harvest(player_id, plant_id):
    data = request.get_json(force=True, silent=True) or {}
    try:
        with session_scope() as s:
            h = GameService(s).harvest_plant(
                player_id,
                plant_id,
                weight_g=data.get("weight_g"),
                quality=data.get("quality"),
                sell=bool(data.get("sell", True)),
            )
            payload = S.harvest_dict(h)
        return jsonify(payload), 201
    except GameError as e:
        return _error(str(e))


# ----- Simulation (real-time grow) ---------------------------------------
@game_bp.get("/players/<player_id>/plants/<plant_id>/state")
def plant_state(player_id, plant_id):
    """Return the plant's live simulated state (runs catch-up first)."""
    try:
        with session_scope() as s:
            sim = SimulationService(s)
            plant = sim.get_state(player_id, plant_id)
            events = sim.get_events(plant_id, limit=20)
            payload = S.plant_dict(plant)
            payload["recent_events"] = [S.event_dict(e) for e in events]
        return jsonify(payload)
    except GameError as e:
        return _error(str(e), 404)


@game_bp.get("/plants/<plant_id>/events")
def plant_events(plant_id):
    limit = int(request.args.get("limit", 50))
    with session_scope() as s:
        events = SimulationService(s).get_events(plant_id, limit=limit)
        payload = [S.event_dict(e) for e in events]
    return jsonify(payload)


def _care_action(player_id, plant_id, method_name, **kwargs):
    try:
        with session_scope() as s:
            sim = SimulationService(s)
            plant = getattr(sim, method_name)(player_id, plant_id, **kwargs)
            payload = S.plant_dict(plant)
        return jsonify(payload)
    except (GameError, InsufficientFundsError) as e:
        return _error(str(e))


@game_bp.post("/players/<player_id>/plants/<plant_id>/water")
@require_player
def water_plant(player_id, plant_id):
    data = request.get_json(force=True, silent=True) or {}
    return _care_action(player_id, plant_id, "water", amount=data.get("amount"))


@game_bp.post("/players/<player_id>/plants/<plant_id>/feed")
@require_player
def feed_plant(player_id, plant_id):
    data = request.get_json(force=True, silent=True) or {}
    return _care_action(player_id, plant_id, "feed", amount=data.get("amount"))


@game_bp.post("/players/<player_id>/plants/<plant_id>/treat-pests")
@require_player
def treat_pests(player_id, plant_id):
    return _care_action(player_id, plant_id, "treat_pests")


@game_bp.post("/players/<player_id>/plants/<plant_id>/treat-disease")
@require_player
def treat_disease(player_id, plant_id):
    return _care_action(player_id, plant_id, "treat_disease")


@game_bp.post("/players/<player_id>/pods/<pod_id>/environment")
@require_player
def set_environment(player_id, pod_id):
    data = request.get_json(force=True, silent=True) or {}
    required = ("temperature", "humidity", "co2_level", "light_intensity", "ph_level")
    if not all(k in data for k in required):
        return _error("temperature, humidity, co2_level, light_intensity, ph_level required")
    try:
        with session_scope() as s:
            pod = SimulationService(s).set_environment(
                player_id, pod_id,
                data["temperature"], data["humidity"], data["co2_level"],
                data["light_intensity"], data["ph_level"],
            )
            payload = S.pod_dict(pod)
        return jsonify(payload)
    except GameError as e:
        return _error(str(e))


# ----- Marketplace -------------------------------------------------------
@game_bp.get("/market")
def market():
    with session_scope() as s:
        listings = GameService(s).list_market()
        payload = [S.listing_dict(x) for x in listings]
    return jsonify(payload)


@game_bp.post("/players/<player_id>/market/list")
@require_player
def create_listing(player_id):
    data = request.get_json(force=True, silent=True) or {}
    required = ("seed_id", "quantity", "unit_price")
    if not all(k in data for k in required):
        return _error("seed_id, quantity, and unit_price are required")
    try:
        with session_scope() as s:
            listing = GameService(s).create_seed_listing(
                player_id,
                data["seed_id"],
                int(data["quantity"]),
                data["unit_price"],
            )
            payload = S.listing_dict(listing)
        return jsonify(payload), 201
    except (GameError, InsufficientFundsError) as e:
        return _error(str(e))


@game_bp.post("/players/<player_id>/market/<listing_id>/buy")
@require_player
def buy_listing(player_id, listing_id):
    try:
        with session_scope() as s:
            listing = GameService(s).buy_listing(player_id, listing_id)
            payload = S.listing_dict(listing)
        return jsonify(payload)
    except (GameError, InsufficientFundsError) as e:
        return _error(str(e))


# ----- Progression: daily stipend & achievements -------------------------
@game_bp.post("/players/<player_id>/daily")
@require_player
def claim_daily(player_id):
    try:
        with session_scope() as s:
            payload = ProgressionService(s).claim_daily(player_id)
        return jsonify(payload), 201
    except GameError as e:
        return _error(str(e))


@game_bp.get("/players/<player_id>/achievements")
def list_achievements(player_id):
    with session_scope() as s:
        payload = ProgressionService(s).list_achievements(player_id)
    return jsonify(payload)


@game_bp.post("/players/<player_id>/achievements/<key>/claim")
@require_player
def claim_achievement(player_id, key):
    try:
        with session_scope() as s:
            payload = ProgressionService(s).claim_achievement(player_id, key)
        return jsonify(payload), 201
    except GameError as e:
        return _error(str(e))


# ----- On-chain: wallet linking, NFT minting, metadata -------------------
@game_bp.post("/players/<player_id>/wallet/link")
@require_player
def link_wallet(player_id):
    data = request.get_json(force=True, silent=True) or {}
    if not data.get("address"):
        return _error("address is required")
    try:
        with session_scope() as s:
            player = GameService(s).link_wallet(player_id, data["address"])
            payload = S.player_dict(player)
        return jsonify(payload)
    except GameError as e:
        return _error(str(e))


@game_bp.post("/players/<player_id>/harvests/<harvest_id>/mint")
@require_player
def mint_harvest(player_id, harvest_id):
    try:
        with session_scope() as s:
            harvest = MintingService(s).mint_harvest(player_id, harvest_id)
            payload = S.harvest_dict(harvest)
        return jsonify(payload), 201
    except GameError as e:
        return _error(str(e))


@game_bp.post("/players/<player_id>/strains/<strain_id>/mint")
@require_player
def mint_strain(player_id, strain_id):
    try:
        with session_scope() as s:
            strain = MintingService(s).mint_strain(player_id, strain_id)
            payload = S.strain_dict(strain)
        return jsonify(payload), 201
    except GameError as e:
        return _error(str(e))


@game_bp.get("/nft/<kind>/<obj_id>.json")
def nft_metadata(kind, obj_id):
    """Serve ARC-3 metadata JSON referenced by a minted asset's URL."""
    try:
        with session_scope() as s:
            payload = MintingService(s).metadata_for(kind, obj_id)
        return jsonify(payload)
    except GameError as e:
        return _error(str(e), 404)
