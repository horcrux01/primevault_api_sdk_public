from primevault_python_sdk.api_client import APIClient
from primevault_python_sdk.types import CreateTradeQuoteRequest, GetTradeQuoteResponse, DetailedBalanceResponse, \
    DepositAddressResponse, CreateTradeTransactionRequest, Transaction


def get_quotes(api_client: APIClient) -> GetTradeQuoteResponse:
    vault = api_client.get_vault_by_id("vault_id")
    params = CreateTradeQuoteRequest(
        vaultId=str(vault.id),
        fromAsset="USD",
        toAsset="USDT",
        fromAmount="2",

    )
    response =  api_client.get_trade_quote(params)
    return response

def get_balance(api_client: APIClient) -> DetailedBalanceResponse:
    vault = api_client.get_vault_by_id("vault_id")

    response = api_client.get_detailed_balances(str(vault.id))
    return response

def get_deposit_address(api_client: APIClient) -> DepositAddressResponse:
    vault = api_client.get_vault_by_id("vault_id")

    response = api_client.get_deposit_address(str(vault.id), currency="USDC")
    return response

def execute_quote(api_client: APIClient) -> Transaction:
    vault = api_client.get_vault_by_id("vault_id")
    params = CreateTradeQuoteRequest(
        vaultId=str(vault.id),
        fromAsset="USD",
        toAsset="USDT",
        fromAmount="2",

    )
    quote_data = api_client.get_trade_quote(params)

    quote_request = quote_data.tradeRequestData
    quote_response = quote_data.tradeResponseDataList[0]
    transaction_request = CreateTradeTransactionRequest(vaultId=str(vault.id), tradeRequestData=quote_request,
                                      tradeResponseData=quote_response,
                                      externalId="a9acfd61-2e36-48ab-b709-5c7c4936ea01")
    transaction_response = api_client.create_trade_transaction(transaction_request)
    return transaction_response