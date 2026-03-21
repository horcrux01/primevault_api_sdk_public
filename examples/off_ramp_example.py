from dataclasses import asdict

from primevault_python_sdk.api_client import APIClient
from primevault_python_sdk.types import (
    CreateOffRampTransactionRequest,
    PaymentMethod,
    RampQuoteRequest,
    Transaction,
    TransactionCategory,
    TransferPartyData,
    TransferPartyType,
)


def create_off_ramp_transaction(api_client: APIClient) -> Transaction:
    """
    Example: Create an OFF_RAMP transaction (crypto -> fiat).

    Flow:
    1. Fetch a ramp quote for the OFF_RAMP conversion via get_ramp_quote.
       - source is the vault holding the crypto.
       - category is OFF_RAMP.
       - fromAsset is the crypto (e.g. USDT), toAsset is fiat (e.g. USD).
    2. Use the quote to create the off-ramp transaction.
       - source is the vault (crypto leaves here).
       - destination is the bank account (fiat arrives here).
    """
    vault_id = "393f359c-6e66-4490-bf1f-5a4ec44f49d6"
    bank_account_id = "your-approved-bank-account-id"

    source = TransferPartyData(
        type=TransferPartyType.VAULT.value,
        id=vault_id,
    )

    destination = TransferPartyData(
        type=TransferPartyType.EXTERNAL_BANK_ACCOUNT.value,
        id=bank_account_id,
    )

    # Step 1: Get off-ramp quote
    ramp_quote_request = RampQuoteRequest(
        source=source,
        fromAsset="USDT",
        toAsset="USD",
        fromAmount="100",
        category=TransactionCategory.OFF_RAMP.value,
        paymentMethod=PaymentMethod.US_ACH.value,
        fromChain="ETHEREUM",
    )

    ramp_quote_response = api_client.get_ramp_quote(ramp_quote_request)

    # Step 2: Create the off-ramp transaction
    off_ramp_transaction = api_client.create_off_ramp_transaction(
        CreateOffRampTransactionRequest(
            source=source,
            destination=destination,
            rampRequestData=asdict(ramp_quote_request),
            rampResponseData=asdict(ramp_quote_response),
            externalId="off-ramp-example-1",
            memo="off ramp example",
        )
    )

    # The transaction response includes bank details for the fiat delivery
    # in the destination field:
    #
    #   off_ramp_transaction.destination.type   # "EXTERNAL_BANK_ACCOUNT"
    #   off_ramp_transaction.destination.bank.bankName
    #   off_ramp_transaction.destination.bank.beneficiaryName
    #   off_ramp_transaction.destination.bank.routingNumber
    #   off_ramp_transaction.destination.bank.paymentRail
    #   off_ramp_transaction.destination.bank.currency

    return off_ramp_transaction
