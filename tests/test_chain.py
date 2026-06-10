"""Chain provider abstraction + GROW token ASA (offline mock)."""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from growpodempire.chain.mock import MockChainProvider
from growpodempire.chain.provider import ChainError
from growpodempire.chain.token import create_token_asa, reset_token_asa
from growpodempire.chain import metadata as md
from growpodempire.economy.config import load_economy_config

CFG = load_economy_config()


def test_mock_create_and_info():
    p = MockChainProvider()
    aid = p.create_asset(unit_name="GROW", asset_name="GrowCoin", total=1000, decimals=6)
    info = p.asset_info(aid)
    assert info.asset_id == aid
    assert info.unit_name == "GROW"
    assert info.total == 1000


def test_mock_transfer_moves_balance():
    p = MockChainProvider()
    aid = p.create_asset(unit_name="X", asset_name="X", total=100, decimals=0)
    p.transfer_asset(aid, "MOCKRECEIVER", 10)
    assert p.balances[aid]["MOCKRECEIVER"] == 10
    assert p.balances[aid]["TREASURY"] == 90


def test_mock_destroy():
    p = MockChainProvider()
    aid = p.create_asset(unit_name="X", asset_name="X", total=1, decimals=0)
    p.destroy_asset(aid)
    assert aid in p.destroyed
    with pytest.raises(ChainError):
        p.asset_info(aid)


def test_create_token_asa_uses_config():
    p = MockChainProvider()
    aid = create_token_asa(p, CFG)
    info = p.asset_info(aid)
    assert info.unit_name == "GROW"
    assert info.decimals == 6


def test_reset_token_asa_replaces_asset():
    p = MockChainProvider()
    old = create_token_asa(p, CFG)
    new = reset_token_asa(p, CFG, old_asset_id=old)
    assert new != old
    assert old in p.destroyed


def test_metadata_hash_is_deterministic():
    meta = {"name": "Z", "properties": {"a": 1, "b": 2}}
    assert md.metadata_hash(meta) == md.metadata_hash({"properties": {"b": 2, "a": 1}, "name": "Z"})
    assert len(md.metadata_hash(meta)) == 32


# --- Phase 4: AlgoKit-based real provider (no algokit-utils in CI) ---------
def test_algorand_provider_network_guard():
    """MainNet/TestNet config mismatch is refused before any network call."""
    from growpodempire.chain.algorand import AlgorandProvider

    AlgorandProvider._guard_network("mainnet", "https://mainnet-api.algonode.cloud")  # ok
    AlgorandProvider._guard_network("testnet", "https://testnet-api.algonode.cloud")  # ok
    with pytest.raises(ChainError):
        AlgorandProvider._guard_network("mainnet", "https://testnet-api.algonode.cloud")
    with pytest.raises(ChainError):
        AlgorandProvider._guard_network("testnet", "https://mainnet-api.algonode.cloud")


def test_algorand_provider_requires_algokit_or_mnemonic():
    """Constructing the real provider fails gracefully without algokit-utils
    installed (CI) or without a treasury mnemonic — never silently."""
    from growpodempire.chain.algorand import AlgorandProvider

    with pytest.raises(ChainError):
        AlgorandProvider(
            algod_url="https://testnet-api.algonode.cloud",
            algod_token="",
            treasury_mnemonic="",
            network_name="testnet",
        )

