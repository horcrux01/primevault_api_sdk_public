from primevault_python_sdk.api_client import APIClient
from primevault_python_sdk.types import (
    GetQuoteRequest,
    Transaction,
    TransactionExecuteIntentRequest,
    TransactionIntentRequest,
    TransferPartyData,
    TransferPartyType,
)


def create_fiat_to_crypto_transaction(api_client: APIClient) -> Transaction:
    """
    Example: Create a fiat-to-crypto transaction with the intent flow.

    Flow:
    1. Build the transaction intent from source and destination details.
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

    fiat_to_crypto_transaction = api_client.create_transaction_from_intent(
        TransactionExecuteIntentRequest(
            intent=intent,
            quoteId=selected_quote.quoteId,
            externalId="fiat-to-crypto-example-1",
            memo="fiat to crypto example",
        )
    )
    print(f"Fiat to crypto transaction: {fiat_to_crypto_transaction}")
    deposit_instructions = fiat_to_crypto_transaction.depositInstructions
    if deposit_instructions and deposit_instructions.bankDetails:
        print(f"Fiat to crypto bank details: {deposit_instructions.bankDetails}")

    return fiat_to_crypto_transaction


def create_crypto_to_fiat_transaction(api_client: APIClient) -> Transaction:
    """
    Example: Create a crypto-to-fiat transaction with the intent flow.

    Flow:
    1. Build the transaction intent from source and destination details.
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

    crypto_to_fiat_transaction = api_client.create_transaction_from_intent(
        TransactionExecuteIntentRequest(
            intent=intent,
            quoteId=selected_quote.quoteId,
            externalId="crypto-to-fiat-example-1",
            memo="crypto to fiat example",
        )
    )
    print(f"Crypto to fiat transaction: {crypto_to_fiat_transaction}")
    return crypto_to_fiat_transaction


def create_fiat_to_fiat_transaction(api_client: APIClient) -> Transaction:
    """
    Example: Create a EUR-to-USD transaction with the intent flow.

    Flow:
    1. Build the transaction intent from source and destination details.
    2. Fetch quotes for that intent via get_quote.
    3. Execute the selected quote with create_transaction_from_intent.
    """
    destination_bank_account_id = "your-usd-bank-account-id"

    source = TransferPartyData(
        type=TransferPartyType.EXTERNAL_BANK_ACCOUNT.value,
    )
    destination = TransferPartyData(
        type=TransferPartyType.BANK_ACCOUNT.value,
        id=destination_bank_account_id,
    )

    intent = TransactionIntentRequest(
        source=source,
        destination=destination,
        fromAsset="EUR",
        fromAmount="1000",
        toAsset="USD",
    )

    quote_response = api_client.get_quote(GetQuoteRequest(intent=intent))
    print(f"Quotes: {quote_response.quotes}")
    selected_quote = quote_response.quotes[0]

    fiat_to_fiat_transaction = api_client.create_transaction_from_intent(
        TransactionExecuteIntentRequest(
            intent=intent,
            quoteId=selected_quote.quoteId,
            externalId="eur-to-usd-example-1",
            memo="EUR to USD example",
        )
    )
    print(f"EUR to USD transaction: {fiat_to_fiat_transaction}")
    operations = fiat_to_fiat_transaction.operations or []
    for operation in operations:
        print(f"Transfer operation sequence: {operation.sequence}: {operation}")

    return fiat_to_fiat_transaction
