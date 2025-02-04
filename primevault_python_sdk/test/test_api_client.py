import os
import unittest

import pytest
from dacite import from_dict

from primevault_python_sdk.api_client import APIClient
from primevault_python_sdk.base_api_client import BadRequestError
from primevault_python_sdk.types import (
    ContactStatus,
    CreateContractCallTransactionRequest,
    CreateTradeQuoteRequest,
    CreateTradeTransactionRequest,
    CreateTransferTransactionRequest,
    CreateVaultRequest,
    EVMContractCallData,
    TransactionCreationGasParams,
    TransactionFeeTier,
    TransactionStatus,
    TransferPartyData,
    TransferPartyType,
    VaultType,
)


def api_client():
    api_key = os.environ.get("API_KEY", "5213c10c-d2db-4036-a310-548f7190d2cf")
    api_url = os.environ.get("API_URL", "https://test.excheqr.xyz")
    private_key = os.environ.get("ACCESS_PRIVATE_KEY", "")
    return APIClient(api_key, api_url, private_key)


class TestApiClient(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.api_client = api_client()

    def test_get_assets_data(self):
        assets_data = self.api_client.get_assets_data()
        self.assertIsInstance(assets_data, list)
        self.assertEqual(len(assets_data), 86)

    def test_get_supported_chains(self):
        supported_chains = self.api_client.get_supported_chains()
        self.assertIsInstance(supported_chains, list)
        self.assertEqual(len(supported_chains), 10)

        # Ensure the 'value' of each chain matches
        expected = [
            "ETHEREUM",
            "POLYGON",
            "SOLANA",
            "NEAR",
            "APTOS",
            "ARBITRUM",
            "OPTIMISM",
            "MOONBEAM",
            "RADIX",
            "RADIX",
        ]
        actual = [chain.value for chain in supported_chains]
        self.assertEqual(actual, expected)

    def test_get_vaults(self):
        vault_response = self.api_client.get_vaults({"vaultName": "core-vault-1"})
        vaults = vault_response.results
        self.assertIsInstance(vaults, list)
        self.assertEqual(len(vaults), 1)

        vault = vaults[0]
        self.assertEqual(vault.vaultName, "core-vault-1")
        self.assertEqual(vault.vaultType, VaultType.DEFAULT.value)
        self.assertEqual(len(vault.wallets), 8)
        self.assertEqual(len(vault.signers), 8)
        self.assertEqual(len(vault.viewers), 0)

        # Check blockchains
        blockchains = sorted([wallet.blockchain for wallet in vault.wallets])
        expected_chains = sorted(
            [
                "ETHEREUM",
                "POLYGON",
                "SOLANA",
                "NEAR",
                "APTOS",
                "ARBITRUM",
                "OPTIMISM",
                "MOONBEAM",
            ]
        )
        self.assertEqual(blockchains, expected_chains)

        # getVaultById
        vault_by_id = self.api_client.get_vault_by_id(vault.id)
        self.assertEqual(vault_by_id.vaultName, "core-vault-1")
        self.assertEqual(vault_by_id.vaultType, VaultType.DEFAULT.value)

    def test_get_balances(self):
        # All balances = 0
        vaults = self.api_client.get_vaults({"vaultName": "core-vault-1"})
        vault_id = vaults.results[0].id
        balances = self.api_client.get_balances(vault_id)
        self.assertIsInstance(balances, dict)
        self.assertEqual(balances, {})

        # Non-zero balances
        vaults_non_zero = self.api_client.get_vaults({"vaultName": "Ethereum Vault"})
        vault_id2 = vaults_non_zero.results[0].id
        balances2 = self.api_client.get_balances(vault_id2)
        self.assertIsNotNone(balances2)
        self.assertIsInstance(balances2, dict)
        self.assertEqual(len(balances2), 5)
        self.assertIn("ETH", balances2)
        self.assertIsInstance(balances2["ETH"], dict)
        self.assertEqual(len(balances2["ETH"]), 3)
        self.assertEqual(
            balances2["ETH"],
            {"ETHEREUM": 0.00950008, "OPTIMISM": 0, "ARBITRUM": 0},
        )

        self.assertIn("MATIC", balances2)
        self.assertIsInstance(balances2["MATIC"], dict)
        self.assertEqual(len(balances2["MATIC"]), 1)
        self.assertEqual(balances2["MATIC"], {"POLYGON": 0.00767327})

    def test_get_contacts(self):
        contacts = self.api_client.get_contacts({"name": "Lynn Bell"})
        self.assertIsInstance(contacts.results, list)
        self.assertEqual(len(contacts.results), 1)

        contact = contacts.results[0]
        self.assertEqual(contact.name, "Lynn Bell")
        self.assertEqual(contact.blockChain, "SOLANA")
        self.assertEqual(
            contact.address,
            "CEzN7mqP9xoxn2HdyW6fjEJ73t7qaX9Rp2zyS6hb3iEu",
        )
        self.assertEqual(contact.status, ContactStatus.APPROVED.value)

    def test_create_vault(self):
        data = {
            "vaultName": "Ethereum Vault",
            "defaultTransferSpendLimit": {
                "action": {
                    "actionType": "NEEDS_MORE_APPROVALS",
                    "additionalApprovalCount": 1,
                },
                "spendLimit": "100",
                "resetFrequency": "86400",
            },
            "defaultTradeSpendLimit": {
                "action": {"actionType": "BLOCK_OPERATION"},
                "spendLimit": "100",
                "resetFrequency": "86400",
            },
        }
        # The original test expects a 400 error if the vault exists
        with pytest.raises(BadRequestError) as exc_info:
            self.api_client.create_vault(
                from_dict(data_class=CreateVaultRequest, data=data)
            )

        self.assertIn("400 Client Error:", str(exc_info.value))

    def test_create_transfer_transaction(self):
        # find the asset and chain
        assets = self.api_client.get_assets_data()

        ethereum_asset = next(
            asset
            for asset in assets
            if asset.blockChain == "ETHEREUM" and asset.symbol == "ETH"
        )

        # Get source vault
        source_vaults = self.api_client.get_vaults({"vaultName": "core-vault-1"})
        destination_contacts = self.api_client.get_contacts({"name": "Lynn Bell"})

        source = from_dict(
            TransferPartyData,
            {"type": TransferPartyType.VAULT.value, "id": source_vaults.results[0].id},
        )
        destination = from_dict(
            TransferPartyData,
            {
                "type": TransferPartyType.CONTACT.value,
                "id": destination_contacts.results[0].id,
            },
        )

        with pytest.raises(BadRequestError) as exc_info:
            self.api_client.create_transfer_transaction(
                from_dict(
                    CreateTransferTransactionRequest,
                    {
                        "source": source,
                        "destination": destination,
                        "amount": "0.0001",
                        "asset": ethereum_asset.symbol,
                        "chain": ethereum_asset.blockChain,
                        "externalId": "externalId-1",
                        "memo": "memo",
                    },
                )
            )

        self.assertIn("400 Client Error:", str(exc_info.value))

    def test_get_transaction_by_id(self):
        transaction_id = "f1cb568d-215e-426f-998a-4ba5be8288d4"
        transaction = self.api_client.get_transaction_by_id(transaction_id)
        self.assertEqual(transaction.id, transaction_id)
        self.assertEqual(transaction.status, TransactionStatus.PENDING.value)
        self.assertEqual(transaction.blockChain, "ETHEREUM")
        self.assertIsNone(transaction.externalId)
        self.assertEqual(transaction.toAddressName, "Compound")
        self.assertEqual(
            transaction.sourceAddress,
            "0x1feDDa0D98c5B4FDEbde9342d3db6Eff284B0d18",
        )
        self.assertIsNone(transaction.memo)
        self.assertIsInstance(transaction.gasParams, dict)
        self.assertEqual(
            transaction.gasParams.get("expectedGasFeeInToken"), "0.00055509"
        )
        self.assertEqual(transaction.gasParams.get("gasFeeToken"), "ETH")

    def test_create_contract_call_transaction(self):
        vaults = self.api_client.get_vaults({"vaultName": "core-vault-1"})
        vault_id = vaults.results[0].id
        with pytest.raises(BadRequestError) as exc_info:
            self.api_client.create_contract_call_transaction(
                CreateContractCallTransactionRequest(
                    **{
                        "vaultId": vault_id,
                        "chain": "ETHEREUM",
                        "externalId": "externalId-1",
                        "data": EVMContractCallData(
                            callData="0x",
                            toAddress="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
                        ),
                        "gasParams": TransactionCreationGasParams(
                            feeTier=TransactionFeeTier.MEDIUM.value
                        ),
                    }
                )
            )
        self.assertIn("400 Client Error:", str(exc_info.value))

    def test_get_trade_quote(self):
        source_vaults = self.api_client.get_vaults({"vaultName": "core-vault-1"})
        vault_id = source_vaults.results[0].id
        trade_quote_response = self.api_client.get_trade_quote(
            CreateTradeQuoteRequest(
                **{
                    "vaultId": vault_id,
                    "fromAsset": "ETH",
                    "fromAmount": "0.0001",
                    "fromChain": "ETHEREUM",
                    "toAsset": "USDC",
                    "toChain": "ETHEREUM",
                    "slippage": "0.05",
                }
            )
        )

        request_data = trade_quote_response.tradeRequestData
        self.assertIsNotNone(request_data)
        self.assertEqual(request_data.fromAsset, "ETH")
        self.assertEqual(request_data.fromAmount, "0.0001")
        self.assertEqual(request_data.blockChain, "ETHEREUM")
        self.assertEqual(request_data.toAsset, "USDC")
        self.assertEqual(request_data.toBlockchain, "ETHEREUM")

        response_data_list = trade_quote_response.tradeResponseDataList
        self.assertIsInstance(response_data_list, list)
        self.assertEqual(len(response_data_list), 2)
        response_data = response_data_list[0]
        self.assertIsNotNone(response_data)
        self.assertIsNotNone(response_data.finalToAmount)
        self.assertIsNotNone(response_data.finalToAmountUSD)
        self.assertIsNotNone(response_data.sourceName)

    def test_create_trade_transaction(self):
        source_vaults = self.api_client.get_vaults({"vaultName": "core-vault-1"})
        vault_id = source_vaults.results[0].id
        trade_quote_response = self.api_client.get_trade_quote(
            CreateTradeQuoteRequest(
                **{
                    "vaultId": vault_id,
                    "fromAsset": "ETH",
                    "fromAmount": "0.0001",
                    "fromChain": "ETHEREUM",
                    "toAsset": "USDC",
                    "toChain": "ETHEREUM",
                    "slippage": "0.05",
                }
            )
        )

        with pytest.raises(BadRequestError) as exc_info:
            self.api_client.create_trade_transaction(
                CreateTradeTransactionRequest(
                    **{
                        "vaultId": vault_id,
                        "tradeRequestData": trade_quote_response.tradeRequestData,
                        "tradeResponseData": trade_quote_response.tradeResponseDataList[
                            0
                        ],
                        "externalId": "externalId-1",
                    }
                )
            )
            self.assertIn("400 Client Error:", str(exc_info.value))
