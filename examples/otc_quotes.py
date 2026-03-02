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






    private_key = '''-----BEGIN EC PRIVATE KEY-----
MHcCAQEEIBCECHt9gc+HMhBHloWXoTNLw6ZMpUQkgWk1EVgCNYjKoAoGCCqGSM49
AwEHoUQDQgAE4xtzKI16vOTg6J9eByQTTGAwcHlzkNEZDZSi/bwhAzITuKpwqZ0B
IxDyYuEvNBG53zrEturrN54lpsVd3Lwc0Q==
-----END EC PRIVATE KEY-----'''
    api_client = APIClient(api_key='284d1372-d0ee-4207-9e41-e49603cc269d',private_key_hex=private_key, api_url='https://api.primevault.com')
    vault = api_client.get_vault_by_id("a9acfd61-2e36-48ab-b709-5c7c4936ea00")
    vault_id = vault.id
    detailed_balances = api_client.get_deposit_address(vault_id, currency="USDC")
    params = CreateTradeQuoteRequest (
                vaultId= str(vault.id),
                fromAsset= "USD",
                toAsset= "USDT",
                fromAmount= "2",
                fromChain = "ETHEREUM",
                toChain= "ETHEREUM",
                slippage = "0.1"
    )
    a = api_client.get_trade_quote(params)
    quote_request = a.tradeRequestData
    quote_response = a.tradeResponseDataList[0]
    print(a)
    b = CreateTradeTransactionRequest(vaultId= vault_id, tradeRequestData=  quote_request, tradeResponseData=quote_response , externalId="a9acfd61-2e36-48ab-b709-5c7c4936ea01")
    print(b)

    c = api_client.create_trade_transaction(b)
    print(c)