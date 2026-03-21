from primevault_python_sdk.api_client import APIClient
from primevault_python_sdk.types import (
    CreateRampTransactionRequest,
    GetQuoteRequest,
    Transaction,
    TransactionCategory,
)


def create_ramp_transfer(api_client: APIClient) -> Transaction:
    create_trade_quote_request = GetQuoteRequest(
        vaultId="393f359c-6e66-4490-bf1f-5a4ec44f49d6",
        fromAsset="USD",
        toAsset="USDC",
        fromAmount="100",
        category="ON_RAMP",
        paymentMethod="US_ACH",
        toChain="POLYGON",
    )
    trade_response = api_client.get_trade_quote(create_trade_quote_request)
    trade_request_data = trade_response.tradeRequestData
    trade_routes = trade_response.tradeResponseDataList or []
    trade_response_data = trade_routes[0]
    vault_id = str(create_trade_quote_request.vaultId)
    on_ramp_request = CreateRampTransactionRequest(
        vaultId=vault_id,
        category=TransactionCategory.ON_RAMP.value,
        tradeRequestData=trade_request_data,
        tradeResponseData=trade_response_data,
        externalId=f"on-ramp-ext-8",
        operationMessage="ON_RAMP test",
        memo="on ramp test",
        paymentMethod="US_ACH",
        toBlockChain="POLYGON",
    )
    on_ramp_transaction_response = api_client.create_ramp_transaction(on_ramp_request)
    return on_ramp_transaction_response
