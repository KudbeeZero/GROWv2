"""
Real Algorand provider, built on AlgoKit Utils (signer-based accounts).

This replaces hand-rolled transaction construction + a raw treasury private key
with AlgoKit Utils' unified ``AlgorandClient`` and a *registered signer*. The
treasury key is loaded into the signer abstraction rather than used to sign
bytes inline — for dev/TestNet that's an env mnemonic; for MainNet, point it at
a KMS/HSM-backed ``TransactionSigner`` (see docs/MAINNET_READINESS.md).

Gameplay stays DB-authoritative; this provider only materializes assets
on-chain. ``algokit_utils`` (and its ``py-algorand-sdk`` dependency) are imported
lazily so MockChainProvider users — including CI — need neither installed.
"""

from typing import Optional, Tuple

from .provider import ChainProvider, AssetInfo, ChainError, TREASURY


class AlgorandProvider(ChainProvider):
    def __init__(
        self,
        algod_url: str,
        algod_token: str,
        treasury_mnemonic: str,
        network_name: str = "testnet",
    ):
        # Imported lazily so the package works without algokit-utils installed.
        try:
            from algosdk.v2client import algod
            from algokit_utils import AlgorandClient
        except ImportError as exc:  # pragma: no cover - exercised only on-chain
            raise ChainError(
                "algokit-utils (and py-algorand-sdk) are required for on-chain mode"
            ) from exc

        if not treasury_mnemonic:
            raise ChainError("ALGO_TREASURY_MNEMONIC is required for on-chain mode")

        # MainNet safety: refuse to run if the network says mainnet but the algod
        # endpoint still points at a testnet host (or vice versa) — a classic
        # foot-gun that could spend real ALGO against the wrong config.
        self._guard_network(network_name, algod_url)

        self._network = network_name
        algod_client = algod.AlgodClient(algod_token or "", algod_url)
        self.algorand = AlgorandClient.from_clients(algod=algod_client)

        # Register the treasury signer. from_mnemonic adds it to the account
        # manager so the transaction composer can sign for this sender; we also
        # make it the default signer.
        self.treasury = self.algorand.account.from_mnemonic(mnemonic=treasury_mnemonic)
        self.treasury_addr = self.treasury.address
        self.algorand.account.set_default_signer(self.treasury.signer)

    @staticmethod
    def _guard_network(network_name: str, algod_url: str) -> None:
        net = (network_name or "").lower()
        url = (algod_url or "").lower()
        if net == "mainnet" and "testnet" in url:
            raise ChainError(
                "ALGORAND_NETWORK=mainnet but ALGOD_URL points at testnet — refusing to start"
            )
        if net == "testnet" and "mainnet" in url:
            raise ChainError(
                "ALGORAND_NETWORK=testnet but ALGOD_URL points at mainnet — refusing to start"
            )

    def network(self) -> str:
        return self._network

    def create_account(self) -> Tuple[str, str]:
        from algosdk import account, mnemonic

        sk, addr = account.generate_account()
        return addr, mnemonic.from_private_key(sk)

    def create_asset(
        self, *, unit_name, asset_name, total, decimals, url=None, metadata_hash=None
    ) -> int:
        from algokit_utils import AssetCreateParams

        result = self.algorand.send.asset_create(
            AssetCreateParams(
                sender=self.treasury_addr,
                total=total,
                decimals=decimals,
                unit_name=unit_name,
                asset_name=asset_name,
                url=url,
                manager=self.treasury_addr,
                reserve=self.treasury_addr,
                metadata_hash=metadata_hash,
            )
        )
        return result.asset_id

    def destroy_asset(self, asset_id: int) -> str:
        from algokit_utils import AssetDestroyParams

        result = self.algorand.send.asset_destroy(
            AssetDestroyParams(sender=self.treasury_addr, asset_id=asset_id)
        )
        return result.tx_id

    def transfer_asset(self, asset_id, receiver, amount, sender_mnemonic=None) -> str:
        from algokit_utils import AssetTransferParams

        # Resolve the provider-agnostic TREASURY sentinel to the real address.
        if receiver == TREASURY:
            receiver = self.treasury_addr

        if sender_mnemonic:
            sender = self.algorand.account.from_mnemonic(mnemonic=sender_mnemonic).address
        else:
            sender = self.treasury_addr

        result = self.algorand.send.asset_transfer(
            AssetTransferParams(
                sender=sender,
                receiver=receiver,
                asset_id=asset_id,
                amount=int(amount),
            )
        )
        return result.tx_id

    def asset_info(self, asset_id: int) -> AssetInfo:
        info = self.algorand.asset.get_by_id(asset_id)
        return AssetInfo(
            asset_id=info.asset_id,
            name=info.asset_name or "",
            unit_name=info.unit_name or "",
            total=info.total,
            decimals=info.decimals,
            url=info.url,
        )
