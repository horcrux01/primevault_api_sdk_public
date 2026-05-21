from primevault_python_sdk.api_client import APIClient
from primevault_python_sdk.types import (
    CreateTradeQuoteRequest,
    CreateTradeTransactionRequest,
    DepositAddressResponse,
    DetailedBalanceResponse,
    Transaction,
)

VAULT_ID = "your-vault-id"


def get_quotes(api_client: APIClient):
    """Get TRADE quotes — quotes are cached server-side and return quoteId."""
    params = CreateTradeQuoteRequest(
        vaultId=VAULT_ID,
        fromAsset="USD",
        toAsset="USDT",
        fromAmount="100",
        category="TRADE",
    )
    response = api_client.get_trade_quote(params)
    print(f"Quotes: {response.quotes}")
    return response


def get_balance(api_client: APIClient) -> DetailedBalanceResponse:
    response = api_client.get_detailed_balances(VAULT_ID)
    return response


def get_deposit_address(api_client: APIClient) -> DepositAddressResponse:
    response = api_client.get_deposit_address(VAULT_ID, currency="USDC")
    return response


def execute_quote(api_client: APIClient) -> Transaction:
    """Get a quote, then create a trade transaction using only the quoteId."""
    quote_response = get_quotes(api_client)
    selected_quote = quote_response.quotes[0]

    transaction_request = CreateTradeTransactionRequest(
        quoteId=selected_quote.quoteId,
        category="TRADE",
        operationMessage="USD to USDT OTC trade",
        externalId="a9acfd61-2e36-48ab-b709-5c7c4936ea01",
    )
    transaction_response = api_client.create_trade_transaction(transaction_request)
    print(f"Transaction: {transaction_response.id} {transaction_response.status}")
    return transaction_response
