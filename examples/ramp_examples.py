from primevault_python_sdk.api_client import APIClient
from primevault_python_sdk.types import (
    GetQuoteRequest,
    IntentAsset,
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
    1. Build the transaction intent from input/output assets and parties.
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
        chain="ETHEREUM",
    )

    intent = TransactionIntentRequest(
        source=source,
        destination=destination,
        input=IntentAsset(asset="NGN", vaultId=ramp_vault_id),
        output=IntentAsset(asset="USDT", amount="5"),
    )

    quote_response = api_client.get_quote(GetQuoteRequest(intent=intent))
    print(f"Quotes: {quote_response.quotes}")
    selected_quote = quote_response.quotes[0]
    print(f"Quoted selections: {selected_quote.input} {selected_quote.output}")

    fiat_to_crypto_transaction = api_client.create_transaction_from_intent(
        TransactionExecuteIntentRequest(
            quoteId=selected_quote.quoteId,
            externalId="fiat-to-crypto-example-2",
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
    1. Build the transaction intent from input/output assets and parties.
    2. Fetch quotes for that intent via get_quote.
    3. Execute the selected quote with create_transaction_from_intent.
    """
    vault_id = "your-vault-id"
    bank_account_id = "your-approved-bank-account-id"

    source = TransferPartyData(
        type=TransferPartyType.VAULT.value,
        id=vault_id,
        chain="ETHEREUM",
    )

    destination = TransferPartyData(
        type=TransferPartyType.BANK_ACCOUNT.value,
        id=bank_account_id,
    )

    intent = TransactionIntentRequest(
        source=source,
        destination=destination,
        input=IntentAsset(asset="USDC", amount="100"),
        output=IntentAsset(asset="USD"),
    )

    quote_response = api_client.get_quote(GetQuoteRequest(intent=intent))
    print(f"Quotes: {quote_response.quotes}")
    selected_quote = quote_response.quotes[0]
    print(f"Quoted selections: {selected_quote.input} {selected_quote.output}")

    crypto_to_fiat_transaction = api_client.create_transaction_from_intent(
        TransactionExecuteIntentRequest(
            quoteId=selected_quote.quoteId,
            externalId="crypto-to-fiat-example-1",
            memo="crypto to fiat example",
        )
    )
    print(f"Crypto to fiat transaction: {crypto_to_fiat_transaction}")
    return crypto_to_fiat_transaction


def create_fiat_to_fiat_transaction(api_client: APIClient) -> Transaction:
    """
    Example: Create a NGN-to-USD transaction with the intent flow.

    Flow:
    1. Build the transaction intent; both fiat sides name their fiat vault.
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
        input=IntentAsset(asset="NGN", vaultId="your-ngn-fiat-vault-id"),
        output=IntentAsset(asset="USD", amount="100", vaultId="your-usd-fiat-vault-id"),
    )

    quote_response = api_client.get_quote(GetQuoteRequest(intent=intent))
    print(f"Quotes: {quote_response.quotes}")
    selected_quote = quote_response.quotes[0]
    print(f"Quoted selections: {selected_quote.input} {selected_quote.output}")

    fiat_to_fiat_transaction = api_client.create_transaction_from_intent(
        TransactionExecuteIntentRequest(
            quoteId=selected_quote.quoteId,
            externalId="ngn-to-usd-example-1",
            memo="NGN to USD example",
        )
    )
    print(f"NGN to USD transaction: {fiat_to_fiat_transaction}")
    balance_changes = fiat_to_fiat_transaction.balanceChanges
    for change in balance_changes.changes if balance_changes else []:
        print(f"{change.asset} {change.amount}: {change.party}")

    return fiat_to_fiat_transaction
