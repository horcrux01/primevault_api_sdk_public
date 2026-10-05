from primevault_python_sdk.api_client import APIClient
from primevault_python_sdk.types import (
    GetQuoteRequest,
    IntentAsset,
    QuoteResponseItem,
    Transaction,
    TransactionExecuteIntentRequest,
    TransactionIntentRequest,
    TransferPartyData,
    TransferPartyType,
)

# Vault ID that PrimeVault will provide based on the provider you are
# onboarded for. Replace with the value shared by your PrimeVault contact.
VAULT_ID = "vault_id"


def _trade_intent() -> TransactionIntentRequest:
    return TransactionIntentRequest(
        source=TransferPartyData(
            type=TransferPartyType.VAULT.value,
            id=VAULT_ID,
        ),
        destination=TransferPartyData(
            type=TransferPartyType.VAULT.value,
            id=VAULT_ID,
        ),
        input=IntentAsset(asset="USDT", amount="100"),
        output=IntentAsset(asset="USD"),
    )


# Quote the test trade.
def get_test_trade_quote(api_client: APIClient) -> QuoteResponseItem:
    quote_response = api_client.get_quote(GetQuoteRequest(intent=_trade_intent()))
    return quote_response.quotes[0]


# Create the test trade using intent/create with the quoteId.
def create_test_trade(api_client: APIClient) -> Transaction:
    quote_response = get_test_trade_quote(api_client)
    print(f"Quoted selections: {quote_response.input} {quote_response.output}")
    request = TransactionExecuteIntentRequest(
        quoteId=quote_response.quoteId,
        externalId="trade-001",
        memo="USDT to USD trade from quote",
    )
    return api_client.create_transaction_from_intent(request)


# Create a deposit using intent/create with a direct intent object.
#
# The returned Transaction carries `depositInstructions` -- read these to
# know where to actually send the funds, then call `mark_deposit_done`
# with the transaction id once the transfer is on its way.
#
# Crypto deposit instructions look like:
#   transaction.depositInstructions = DepositInstructions(
#       type="EXTERNAL_ADDRESS",
#       asset="USDT",
#       chain="ETHEREUM",
#       address="0xRecipientAddressFromPrimeVault",
#   )
#
# Fiat (bank) deposit instructions look like:
#   transaction.depositInstructions = DepositInstructions(
#       type="BANK_ACCOUNT",
#       asset="USD",
#       paymentRail="ACH",
#       bankDetails=BankDetails(
#           bankName="Chase",
#           accountName="Treasury Account",
#           accountNumber="123456789",
#           routingNumber="021000021",
#           paymentRail="ACH",
#       ),
#   )
def create_deposit(api_client: APIClient) -> Transaction:
    intent = TransactionIntentRequest(
        input=IntentAsset(asset="USDT", amount="500"),
        output=IntentAsset(asset="USDT"),
        source=TransferPartyData(
            type=TransferPartyType.CONTACT.value,
            id="contact-id",
            chain="ETHEREUM",
        ),
        destination=TransferPartyData(
            type=TransferPartyType.VAULT.value,
            id=VAULT_ID,
        ),
    )
    return api_client.create_transaction_from_intent(
        TransactionExecuteIntentRequest(
            intent=intent,
            externalId="deposit-001",
            memo="USDT deposit from external account",
        )
    )


# Create a withdraw using intent/create with a direct intent object.
def create_withdraw(api_client: APIClient) -> Transaction:
    intent = TransactionIntentRequest(
        input=IntentAsset(asset="USD", amount="250"),
        output=IntentAsset(asset="USD"),
        source=TransferPartyData(
            type=TransferPartyType.VAULT.value,
            id=VAULT_ID,
        ),
        destination=TransferPartyData(
            type=TransferPartyType.BANK_ACCOUNT.value,
            id="bank-account-id",
        ),
    )
    return api_client.create_transaction_from_intent(
        TransactionExecuteIntentRequest(
            intent=intent,
            externalId="withdraw-001",
            memo="USD withdrawal to bank",
        )
    )


# Mark a deposit done by transaction id.
def mark_deposit_done(api_client: APIClient, transaction_id: str) -> Transaction:
    return api_client.mark_deposit_done(transaction_id)
