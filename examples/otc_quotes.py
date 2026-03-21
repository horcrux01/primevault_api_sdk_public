from primevault_python_sdk.api_client import APIClient
from primevault_python_sdk.types import (
    GetQuoteRequest,
    CreateTradeTransactionRequest,
    DepositAddressResponse,
    DetailedBalanceResponse,
    GetTradeQuoteResponse,
    Transaction,
)


def get_quotes(api_client: APIClient) -> GetTradeQuoteResponse:
    params = GetQuoteRequest(
        vaultId="vault_id",
        fromAsset="USD",
        toAsset="USDT",
        fromAmount="2",
    )
    response = api_client.get_trade_quote(params)
    return response


def get_balance(api_client: APIClient) -> DetailedBalanceResponse:
    response = api_client.get_detailed_balances("vault_id")
    return response


def get_deposit_address(api_client: APIClient) -> DepositAddressResponse:
    response = api_client.get_deposit_address("vault_id", currency="USDC")
    return response


def execute_quote(api_client: APIClient) -> Transaction:
    params = GetQuoteRequest(
        vaultId="vault_id",
        fromAsset="USD",
        toAsset="USDT",
        fromAmount="2",
    )
    quote_data = api_client.get_trade_quote(params)

    quote_request = quote_data.tradeRequestData
    quote_response = quote_data.tradeResponseDataList[0]
    transaction_request = CreateTradeTransactionRequest(
        vaultId="vault_id",
        tradeRequestData=quote_request,
        tradeResponseData=quote_response,
        externalId="a9acfd61-2e36-48ab-b709-5c7c4936ea01",
    )
    transaction_response = api_client.create_trade_transaction(transaction_request)
    return transaction_response
