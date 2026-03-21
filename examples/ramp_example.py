from dataclasses import asdict

from primevault_python_sdk.api_client import APIClient
from primevault_python_sdk.types import (
    CreateOffRampTransactionRequest,
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

    # The transaction response includes bank details for the fiat deposit
    # in the source field:
    #
    #   on_ramp_transaction.source.type      # "EXTERNAL_BANK_ACCOUNT"
    #   on_ramp_transaction.source.name      # e.g. "PrimeVault Treasury"
    #   on_ramp_transaction.source.bank.bankName           # e.g. "PrimeVault National Bank"
    #   on_ramp_transaction.source.bank.beneficiaryName    # e.g. "PrimeVault Treasury"
    #   on_ramp_transaction.source.bank.accountNumberMasked
    #   on_ramp_transaction.source.bank.routingNumber
    #   on_ramp_transaction.source.bank.swiftBic
    #   on_ramp_transaction.source.bank.paymentRail        # e.g. "US_ACH"
    #   on_ramp_transaction.source.bank.currency           # e.g. "USD"
    #   on_ramp_transaction.source.bank.bankAddress
    #   on_ramp_transaction.source.bank.iban

    return on_ramp_transaction


def create_off_ramp_transaction(api_client: APIClient) -> Transaction:
    """
    Example: Create an OFF_RAMP transaction (crypto -> fiat).

    Flow:
    1. Fetch a ramp quote for the OFF_RAMP conversion via get_ramp_quote.
    2. Use the quote request and response data to create the off-ramp transaction.
    """
    vault_id = "393f359c-6e66-4490-bf1f-5a4ec44f49d6"

    source = TransferPartyData(
        type=TransferPartyType.VAULT.value,
        id=vault_id,
    )

    bank_account_id = "your-bank-account-id"
    destination = TransferPartyData(
        type=TransferPartyType.EXTERNAL_BANK_ACCOUNT.value,
        id=bank_account_id,
    )

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

    off_ramp_transaction = api_client.create_off_ramp_transaction(
        CreateOffRampTransactionRequest(
            source=source,
            destination=destination,
            rampRequestData=asdict(ramp_quote_request),
            rampResponseData=asdict(ramp_quote_response),
            externalId="off-ramp-example-1",
            memo="off ramp test",
        )
    )

    # The transaction response includes bank details for the fiat delivery
    # in the destination field:
    #
    #   off_ramp_transaction.destination.type   # "EXTERNAL_BANK_ACCOUNT"
    #   off_ramp_transaction.destination.bank.bankName
    #   off_ramp_transaction.destination.bank.beneficiaryName
    #   off_ramp_transaction.destination.bank.routingNumber
    #   off_ramp_transaction.destination.bank.currency

    return off_ramp_transaction
