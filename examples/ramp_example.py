from dataclasses import asdict

from primevault_python_sdk.api_client import APIClient
from primevault_python_sdk.types import (
    CreateOnRampTransactionRequest,
    PaymentMethod,
    RampQuoteRequest,
    Transaction,
    TransactionCategory,
    TransferPartyData,
    TransferPartyType,
)


def create_on_ramp_transaction(api_client: APIClient) -> Transaction:
    """
    Example: Create an ON_RAMP transaction (fiat -> crypto).

    Flow:
    1. Fetch a ramp quote for the ON_RAMP conversion via get_ramp_quote.
    2. Use the quote request and response data to create the on-ramp transaction.
    """
    vault_id = "393f359c-6e66-4490-bf1f-5a4ec44f49d6"

    destination = TransferPartyData(
        type=TransferPartyType.VAULT.value,
        id=vault_id,
    )

    # Step 1: Request a ramp quote for converting 100 USD -> USDC on Polygon
    ramp_quote_request = RampQuoteRequest(
        destination=destination,
        fromAsset="USD",
        toAsset="USDC",
        fromAmount="100",
        category=TransactionCategory.ON_RAMP.value,
        paymentMethod=PaymentMethod.US_ACH.value,
        toChain="POLYGON",
    )

    ramp_quote_response = api_client.get_ramp_quote(ramp_quote_request)

    # Step 2: Create the on-ramp transaction using the quote data.
    on_ramp_transaction = api_client.create_on_ramp_transaction(
        CreateOnRampTransactionRequest(
            destination=destination,
            rampRequestData=asdict(ramp_quote_request),
            rampResponseData=asdict(ramp_quote_response),
            externalId="on-ramp-1110eee2e",
            memo="on ramp test",
        )
    )

    return on_ramp_transaction
