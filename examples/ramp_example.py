from dataclasses import asdict

from primevault_python_sdk.api_client import APIClient
from primevault_python_sdk.types import (
    CreateOnRampTransactionRequest,
    RampExchangeRatesRequest,
    Transaction,
    TransactionCategory,
)


def create_ramp_transfer(api_client: APIClient) -> Transaction:
    ramp_quote_request = RampExchangeRatesRequest(
        vaultId="393f359c-6e66-4490-bf1f-5a4ec44f49d6",
        amount="100",
        currency="USD",
        asset="USDC",
        category=TransactionCategory.ON_RAMP.value,
        paymentMethod="US_ACH",
        blockChain="POLYGON",
    )
    ramp_quotes = api_client.get_ramp_exchange_rates(ramp_quote_request)
    if not ramp_quotes:
        raise ValueError("No on-ramp quotes returned for the requested conversion.")

    selected_quote = ramp_quotes[0]
    vault_id = str(ramp_quote_request.vaultId)
    on_ramp_request = CreateOnRampTransactionRequest(
        vaultId=vault_id,
        quoteId=selected_quote.quoteId,
        onRampRequestData=asdict(ramp_quote_request),
        onRampResponseData=asdict(selected_quote),
        externalId="on-ramp-ext-8",
        memo="on ramp test",
    )
    on_ramp_transaction_response = api_client.create_on_ramp_transaction(
        on_ramp_request
    )
    return on_ramp_transaction_response
