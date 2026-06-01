from dataclasses import asdict
import os
import unittest
from unittest.mock import Mock, call

import pytest
from dacite import from_dict

from primevault_python_sdk.api_client import APIClient
from primevault_python_sdk.base_api_client import BadRequestError
from primevault_python_sdk.types import (
    ApprovalAction,
    BankDetails,
    ContactStatus,
    CreateContractCallTransactionRequest,
    CreateTransferTransactionRequest,
    CreateVaultRequest,
    EVMContractCallData,
    GetApprovalRequest,
    GetQuoteRequest,
    TransactionCreationGasParams,
    TransactionExecuteIntentRequest,
    TransactionFeeTier,
    TransactionIntentRequest,
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


def test_intent_request_serialization_matches_backend_contract():
    source = TransferPartyData(
        type=TransferPartyType.VAULT.value,
        id="source-vault",
        provider=None,
    )
    destination = TransferPartyData(
        type=TransferPartyType.BANK_ACCOUNT.value,
        id="destination-bank-account",
        bankDetails=BankDetails(
            bankAccountId="destination-bank-account",
            bankName="Example Bank",
        ),
    )
    intent = TransactionIntentRequest(
        source=source,
        destination=destination,
        fromAsset="USDC",
        toAsset="USD",
        fromAmount="100",
        fromChain="ETHEREUM",
        fromPaymentRail="BLOCKCHAIN",
        toAmount="99",
        toPaymentRail="ACH",
    )

    quote_payload = APIClient._quote_request_data(GetQuoteRequest(intent=intent))
    execute_payload = APIClient._transaction_execute_intent_request_data(
        TransactionExecuteIntentRequest(
            intent=intent,
            quoteId="quote-id",
            externalId="external-id",
            memo="memo",
        )
    )

    expected_intent = {
        "source": asdict(source),
        "destination": asdict(destination),
        "fromAsset": "USDC",
        "toAsset": "USD",
        "fromAmount": "100",
        "fromChain": "ETHEREUM",
        "fromPaymentRail": "BLOCKCHAIN",
        "toAmount": "99",
        "toChain": None,
        "toPaymentRail": "ACH",
    }
    assert quote_payload == {"intent": expected_intent}
    assert execute_payload == {
        "intent": expected_intent,
        "quoteId": "quote-id",
        "externalId": "external-id",
        "memo": "memo",
    }
    assert "orgId" not in quote_payload["intent"]
    assert "userId" not in quote_payload["intent"]
    assert "orgId" not in execute_payload
    assert "userId" not in execute_payload
    assert quote_payload["intent"]["source"]["provider"] is None
    assert "exchange" not in quote_payload["intent"]["source"]
    assert quote_payload["intent"]["destination"]["bankDetails"] == {
        "bankAccountId": "destination-bank-account",
        "bankName": "Example Bank",
        "beneficiaryName": None,
        "accountName": None,
        "accountNumber": None,
        "routingNumber": None,
        "paymentRail": None,
        "bankAddress": None,
        "swiftCode": None,
        "swiftBic": None,
        "iban": None,
        "currency": None,
        "country": None,
    }
    assert "bank" not in quote_payload["intent"]["destination"]


def test_transaction_execute_intent_request_serializes_quote_only_execution():
    execute_payload = APIClient._transaction_execute_intent_request_data(
        TransactionExecuteIntentRequest(
            quoteId="quote-id",
            externalId="external-id",
            memo="trade from quote",
        )
    )

    assert execute_payload == {
        "intent": None,
        "quoteId": "quote-id",
        "externalId": "external-id",
        "memo": "trade from quote",
    }


def test_get_quote_posts_intent_and_parses_ramp_quote_fields():
    client = object.__new__(APIClient)
    client.post = Mock(
        return_value={
            "quotes": [
                {
                    "quoteId": "quote-id",
                    "finalToAmount": "100",
                    "fees": {"amount": "0", "asset": "NGN"},
                    "sourceName": None,
                }
            ]
        }
    )

    destination = TransferPartyData(type=TransferPartyType.VAULT.value, id="vault-id")
    intent = TransactionIntentRequest(
        destination=destination,
        fromAsset="NGN",
        fromAmount="137500",
        toAsset="USDC",
        toChain="ETHEREUM",
    )

    quote_response = client.get_quote(GetQuoteRequest(intent=intent))

    client.post.assert_called_once_with(
        "/api/external/transactions/quote/",
        data={"intent": APIClient._transaction_intent_data(intent)},
    )
    assert quote_response.quotes[0].quoteId == "quote-id"
    assert quote_response.quotes[0].finalToAmount == "100"
    assert quote_response.quotes[0].fees.amount == "0"
    assert quote_response.quotes[0].sourceName is None


def test_change_approval_helpers_fetch_message_sign_and_submit_action():
    client = object.__new__(APIClient)
    client.get = Mock(
        return_value={
            "message": "message-to-sign",
            "approvalId": "approval-id",
            "changeRequestId": "change-request-id",
            "entityId": "entity-id",
        }
    )
    client.post = Mock(
        return_value={
            "success": True,
        }
    )
    client.signature_service = Mock()
    client.signature_service.sign.return_value = bytes.fromhex("deadbeef")

    approval_message = client.get_change_approval_message("entity-id")
    assert approval_message.message == "message-to-sign"
    assert approval_message.approvalId == "approval-id"
    client.get.assert_called_once_with(
        "/api/external/change_requests/approvals/approval_message/",
        params={"entityId": "entity-id"},
    )

    approval_response = client.approve_change_request(
        GetApprovalRequest(
            entityId="entity-id",
            action=ApprovalAction.APPROVE.value,
        )
    )

    client.signature_service.sign.assert_called_once_with(b"message-to-sign")
    client.post.assert_called_once_with(
        "/api/external/change_requests/approvals/approval-id/action/",
        data={
            "action": ApprovalAction.APPROVE.value,
            "signature": "deadbeef",
            "reason": "ok",
        },
    )
    assert approval_response.success is True


def test_create_transaction_from_intent_approves_pending_transaction():
    client = object.__new__(APIClient)
    transaction_response = {
        "id": "transaction-id",
        "orgId": "org-id",
        "vaultId": "vault-id",
        "amount": "1",
        "status": TransactionStatus.PENDING.value,
        "transactionType": "OUTGOING",
        "category": "TRANSFER",
        "subCategory": "EXTERNAL_TRANSFER",
        "createdAt": "2026-05-25T00:00:00Z",
        "updatedAt": "2026-05-25T00:00:00Z",
        "isDeleted": False,
    }
    client.post = Mock(
        side_effect=[
            transaction_response,
            {"success": True},
        ]
    )
    approved_transaction_response = {
        **transaction_response,
        "status": TransactionStatus.APPROVED.value,
    }
    client.get = Mock(
        side_effect=[
            {
                "message": "approval-message",
                "approvalId": "approval-id",
            },
            approved_transaction_response,
        ]
    )
    client.signature_service = Mock()
    client.signature_service.sign.return_value = bytes.fromhex("0a0b")

    transaction = client.create_transaction_from_intent(
        TransactionExecuteIntentRequest(
            intent=TransactionIntentRequest(),
            quoteId="quote-id",
            externalId="external-id",
            memo="memo",
        )
    )

    assert transaction.id == "transaction-id"
    assert transaction.status == TransactionStatus.APPROVED.value
    assert client.post.call_args_list[0][0][0] == (
        "/api/external/transactions/intent/create/"
    )
    assert client.get.call_args_list == [
        call(
            "/api/external/change_requests/approvals/approval_message/",
            params={"entityId": "transaction-id"},
        ),
        call("/api/external/transactions/transaction-id/"),
    ]
    assert client.post.call_args_list[1] == call(
        "/api/external/change_requests/approvals/approval-id/action/",
        data={
            "action": ApprovalAction.APPROVE.value,
            "signature": "0a0b",
            "reason": "ok",
        },
    )


def test_on_and_off_ramp_transactions_delegate_to_intent_execution():
    client = object.__new__(APIClient)
    client.create_transaction_from_intent = Mock(return_value="transaction")
    intent_request = TransactionExecuteIntentRequest(
        intent=TransactionIntentRequest(),
        quoteId="quote-id",
        externalId="external-id",
        memo="memo",
    )

    assert client.create_on_ramp_transaction(intent_request) == "transaction"
    assert client.create_off_ramp_transaction(intent_request) == "transaction"
    assert client.create_transaction_from_intent.call_args_list == [
        call(intent_request),
        call(intent_request),
    ]


def test_transaction_parses_deposit_instructions():
    client = object.__new__(APIClient)
    deposit_instructions = {
        "type": TransferPartyType.EXTERNAL_BANK_ACCOUNT.value,
        "currency": "NGN",
        "paymentRail": "WIRE",
        "bankDetails": {
            "beneficiaryName": "PrimeVault Treasury",
            "bankName": "Example Bank",
            "accountNumber": "000123456789",
            "routingNumber": "021000021",
            "swiftCode": "PNVBUS33",
        },
    }
    client.post = Mock(
        return_value={
            "id": "transaction-id",
            "orgId": "org-id",
            "vaultId": "vault-id",
            "amount": "137500",
            "status": TransactionStatus.APPROVED.value,
            "transactionType": "OUTGOING",
            "category": "ON_RAMP",
            "subCategory": "PROVIDER_DEPOSIT",
            "createdAt": "2026-05-25T00:00:00Z",
            "updatedAt": "2026-05-25T00:00:00Z",
            "isDeleted": False,
            "source": {
                "type": TransferPartyType.VAULT.value,
                "id": "vault-id",
                "provider": None,
            },
            "destination": {
                "type": TransferPartyType.BANK_ACCOUNT.value,
                "id": "destination-bank-account",
                "bankDetails": {
                    "bankName": "Example Bank",
                    "accountNumber": "000123456789",
                },
            },
            "depositInstructions": deposit_instructions,
            "quoteResponse": {
                "quoteId": "quote-id",
                "finalToAmount": "100",
            },
        }
    )

    transaction = client.create_transaction_from_intent(
        TransactionExecuteIntentRequest(
            intent=TransactionIntentRequest(),
            quoteId="quote-id",
        )
    )

    assert transaction.depositInstructions is not None
    assert transaction.depositInstructions.type == (
        TransferPartyType.EXTERNAL_BANK_ACCOUNT.value
    )
    assert transaction.quoteResponse is not None
    assert transaction.quoteResponse.quoteId == "quote-id"
    assert transaction.quoteResponse.finalToAmount == "100"
    assert transaction.source is not None
    assert transaction.source.provider is None
    assert transaction.destination is not None
    assert transaction.destination.bankDetails is not None
    assert transaction.destination.bankDetails.bankName == "Example Bank"
    assert transaction.depositInstructions.currency == "NGN"
    assert transaction.depositInstructions.paymentRail == "WIRE"
    assert transaction.depositInstructions.bankDetails is not None
    assert transaction.depositInstructions.bankDetails.accountNumber == "000123456789"
    assert transaction.depositInstructions.bankDetails.bankName == (
        "Example Bank"
    )


def test_legacy_transfer_transaction_does_not_auto_approve():
    client = object.__new__(APIClient)
    transaction_response = {
        "id": "transaction-id",
        "orgId": "org-id",
        "vaultId": "vault-id",
        "amount": "1",
        "status": TransactionStatus.PENDING.value,
        "transactionType": "OUTGOING",
        "category": "TRANSFER",
        "subCategory": "EXTERNAL_TRANSFER",
        "createdAt": "2026-05-25T00:00:00Z",
        "updatedAt": "2026-05-25T00:00:00Z",
        "isDeleted": False,
    }
    client.post = Mock(return_value=transaction_response)
    client.get = Mock()
    client.signature_service = Mock()

    transaction = client.create_transfer_transaction(
        CreateTransferTransactionRequest(
            source=TransferPartyData(type=TransferPartyType.VAULT.value, id="vault-id"),
            destination=TransferPartyData(
                type=TransferPartyType.CONTACT.value,
                id="contact-id",
            ),
            amount="1",
            asset="USDC",
            chain="ETHEREUM",
        )
    )

    assert transaction.id == "transaction-id"
    client.post.assert_called_once()
    client.get.assert_not_called()
    client.signature_service.sign.assert_not_called()


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
            "APTOS",
            "ARBITRUM",
            "ETHEREUM",
            "ICP",
            "MOONBEAM",
            "NEAR",
            "OPTIMISM",
            "POLYGON",
            "RADIX",
            "SOLANA",
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
        self.assertEqual(len(vault.signers), 9)
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
        self.assertEqual(len(balances), 2)

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
            {"ETHEREUM": "0.00950008", "OPTIMISM": "0", "ARBITRUM": "0"},
        )

        self.assertIn("MATIC", balances2)
        self.assertIsInstance(balances2["MATIC"], dict)
        self.assertEqual(len(balances2["MATIC"]), 1)
        self.assertEqual(balances2["MATIC"], {"POLYGON": "0.00767327"})

    def test_get_detailed_balances(self):
        # Test with vault having non-zero balances
        vaults = self.api_client.get_vaults({"vaultName": "Ethereum Vault"})
        vault_id = vaults.results[0].id
        detailed_balances = self.api_client.get_detailed_balances(vault_id)

        # Verify the response type and overall structure
        self.assertIsInstance(detailed_balances, list)
        self.assertGreater(len(detailed_balances), 0)

        # Create dictionary for easier lookup by chain and symbol
        balances_by_key = {}
        for balance in detailed_balances:
            key = f"{balance.chain}:{balance.symbol}"
            balances_by_key[key] = balance

        # Check specific expected balances
        # ETH on Ethereum
        eth_key = "ETHEREUM:ETH"
        self.assertIn(eth_key, balances_by_key)
        eth_balance = balances_by_key[eth_key]
        self.assertEqual(eth_balance.chain, "ETHEREUM")
        self.assertEqual(eth_balance.symbol, "ETH")
        self.assertEqual(eth_balance.name, "Ethereum")
        self.assertEqual(eth_balance.balance, "0.00950008")

        # MATIC on Polygon
        matic_key = "POLYGON:MATIC"
        self.assertIn(matic_key, balances_by_key)
        matic_balance = balances_by_key[matic_key]
        self.assertEqual(matic_balance.chain, "POLYGON")
        self.assertEqual(matic_balance.symbol, "MATIC")
        self.assertEqual(matic_balance.name, "Matic")
        self.assertEqual(matic_balance.balance, "0.00767327")

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
            "templateId": "09b02e2c-f33f-49f5-8488-bda8fd9ae0b3",
        }
        # The original test expects a 400 error if the vault exists
        with pytest.raises(BadRequestError) as exc_info:
            self.api_client.create_vault(
                from_dict(data_class=CreateVaultRequest, data=data)
            )

        self.assertIn(
            "A record with the same information already exists",
            str(exc_info.value.response_text),
        )

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
        destination_contacts = self.api_client.get_contacts({"name": "Brandi Taylor"})

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

        self.assertIn(
            "A record with the same information already exists",
            exc_info.value.response_text,
        )

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
        self.assertIn(
            "A record with the same information already exists",
            str(exc_info.value.response_text),
        )
