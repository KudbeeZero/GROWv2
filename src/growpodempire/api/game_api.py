"""
Flask blueprint for the DB-backed game: players, wallets, strains, seeds,
breeding, harvest, and the marketplace.

Each request runs inside a `session_scope` transaction; ORM rows are serialized
to JSON-safe dicts before the scope closes.
"""

from flask import Blueprint, request, jsonify

from ..db.session import session_scope
from ..services.game_service import GameService, GameError
from ..economy.ledger import InsufficientFundsError
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


@game_bp.get("/players/<player_id>/ledger")
def get_ledger(player_id):
    with session_scope() as s:
        entries = GameService(s).get_ledger(player_id)
        payload = [S.ledger_dict(e) for e in entries]
    return jsonify(payload)


# ----- Strains -----------------------------------------------------------
@game_bp.get("/strains")
def list_strains():
    catalog_only = request.args.get("catalog_only", "false").lower() == "true"
    with session_scope() as s:
        strains = GameService(s).list_strains(catalog_only=catalog_only)
        payload = [S.strain_dict(st) for st in strains]
    return jsonify(payload)


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


# ----- Marketplace -------------------------------------------------------
@game_bp.get("/market")
def market():
    with session_scope() as s:
        listings = GameService(s).list_market()
        payload = [S.listing_dict(x) for x in listings]
    return jsonify(payload)


@game_bp.post("/players/<player_id>/market/list")
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
def buy_listing(player_id, listing_id):
    try:
        with session_scope() as s:
            listing = GameService(s).buy_listing(player_id, listing_id)
            payload = S.listing_dict(listing)
        return jsonify(payload)
    except (GameError, InsufficientFundsError) as e:
        return _error(str(e))
