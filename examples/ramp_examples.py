from primevault_python_sdk.api_client import APIClient
from primevault_python_sdk.types import (
    GetQuoteRequest,
    Transaction,
    TransactionExecuteIntentRequest,
    TransactionIntentRequest,
    TransferPartyData,
    TransferPartyType,
)


def create_on_ramp_transaction(api_client: APIClient) -> Transaction:
    """
    Example: Create an ON_RAMP transaction (fiat -> crypto) with the intent flow.

    Flow:
    1. Build the transaction intent for the ON_RAMP conversion.
    2. Fetch quotes for that intent via get_quote.
    3. Execute the selected quote with create_transaction_from_intent.
    """
    vault_id = "7ad54443-21d2-4075-abef-83758c9dceb7"
    ramp_vault_id = "1eadbf7c-7158-4f9e-ab5d-130c1370d001"
    source = TransferPartyData(
        type=TransferPartyType.VAULT.value,
        id=ramp_vault_id,
    )
    destination = TransferPartyData(
        type=TransferPartyType.VAULT.value,
        id=vault_id,
    )

    intent = TransactionIntentRequest(
        source=source,
        destination=destination,
        fromAsset="NGN",
        toAmount="5",
        toAsset="USDT",
        toChain="ETHEREUM",
    )

    quote_response = api_client.get_quote(GetQuoteRequest(intent=intent))
    print(f"Quotes: {quote_response.quotes}")
    selected_quote = quote_response.quotes[0]

    on_ramp_transaction = api_client.create_transaction_from_intent(
        TransactionExecuteIntentRequest(
            intent=intent,
            quoteId=selected_quote.quoteId,
            externalId="on-ramp-example-17",
            memo="on ramp example",
        )
    )
    print(f"On ramp transaction: {on_ramp_transaction}")
    deposit_instructions = on_ramp_transaction.depositInstructions
    if deposit_instructions and deposit_instructions.bankDetails:
        print(f"On ramp bank details: {deposit_instructions.bankDetails}")

    return on_ramp_transaction


def create_off_ramp_transaction(api_client: APIClient) -> Transaction:
    """
    Example: Create an OFF_RAMP transaction (crypto -> fiat) with the intent flow.

    Flow:
    1. Build the transaction intent for the OFF_RAMP conversion.
    2. Fetch quotes for that intent via get_quote.
    3. Execute the selected quote with create_transaction_from_intent.
    """
    vault_id = "your-vault-id"
    bank_account_id = "your-approved-bank-account-id"

    source = TransferPartyData(
        type=TransferPartyType.VAULT.value,
        id=vault_id,
    )

    destination = TransferPartyData(
        type=TransferPartyType.BANK_ACCOUNT.value,
        id=bank_account_id,
    )

    intent = TransactionIntentRequest(
        source=source,
        destination=destination,
        fromAsset="USDC",
        fromAmount="100",
        fromChain="ETHEREUM",
        toAsset="USD",
    )

    quote_response = api_client.get_quote(GetQuoteRequest(intent=intent))
    print(f"Quotes: {quote_response.quotes}")
    selected_quote = quote_response.quotes[0]

    off_ramp_transaction = api_client.create_transaction_from_intent(
        TransactionExecuteIntentRequest(
            intent=intent,
            quoteId=selected_quote.quoteId,
            externalId="off-ramp-example-1",
            memo="off ramp example",
        )
    )
    print(f"Off ramp transaction: {off_ramp_transaction}")
    return off_ramp_transaction
