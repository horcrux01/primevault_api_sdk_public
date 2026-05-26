from primevault_python_sdk.api_client import APIClient
from primevault_python_sdk.types import (
    CreateTradeQuoteRequest,
    GetTradeQuoteResponse,
    Transaction,
    TransactionExecuteIntentRequest,
    TransactionIntentRequest,
    TransferPartyData,
    TransferPartyType,
)


VAULT_ID = "vault_id"


# Quote the test trade.
def get_test_trade_quote(api_client: APIClient) -> GetTradeQuoteResponse:
    request = CreateTradeQuoteRequest(
        vaultId=VAULT_ID,
        fromAsset="USDT",
        fromAmount="100",
        toAsset="USD",
        fromChain="ETHEREUM",
    )
    return api_client.get_trade_quote(request)


# Create the test trade using intent/create with the quoteId.
def create_test_trade(api_client: APIClient) -> Transaction:
    quote_response = get_test_trade_quote(api_client).tradeResponseDataList[0]
    request = TransactionExecuteIntentRequest(
        quoteId=quote_response.quoteId,
        externalId="trade-001",
        memo="USDT to USD trade from quote",
    )
    return api_client.create_transaction_from_intent(request)


# Create a deposit using intent/create with a direct intent object.
def create_deposit(api_client: APIClient) -> Transaction:
    intent = TransactionIntentRequest(
        source=TransferPartyData(
            type=TransferPartyType.CONTACT.value,
            id="contact-id",
        ),
        destination=TransferPartyData(
            type=TransferPartyType.VAULT.value,
            id=VAULT_ID,
        ),
        fromAsset="USDT",
        fromAmount="500",
        fromChain="ETHEREUM",
    )
    return api_client.create_transaction_from_intent(
        TransactionExecuteIntentRequest(
            intent=intent,
            quoteId=None,
            externalId="deposit-001",
            memo="USDT deposit from Circle",
        )
    )


# Create a withdraw using intent/create with a direct intent object.
def create_withdraw(api_client: APIClient) -> Transaction:
    intent = TransactionIntentRequest(
        source=TransferPartyData(
            type=TransferPartyType.VAULT.value,
            id=VAULT_ID,
        ),
        destination=TransferPartyData(
            type=TransferPartyType.BANK_ACCOUNT.value,
            id="bank-account-id",
        ),
        fromAsset="USD",
        fromAmount="250",
    )
    return api_client.create_transaction_from_intent(
        TransactionExecuteIntentRequest(
            intent=intent,
            quoteId=None,
            externalId="withdraw-001",
            memo="USD withdrawal to bank",
        )
    )


# Mark a deposit done by transaction id.
def mark_deposit_done(api_client: APIClient, transaction_id: str) -> Transaction:
    return api_client.mark_deposit_done(transaction_id)
