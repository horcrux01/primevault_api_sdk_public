import datetime
import time

from primevault_python_sdk.api_client import APIClient
from primevault_python_sdk.base_api_client import (
    BadRequestError,
    InternalServerError,
    UnauthorizedError,
)
from primevault_python_sdk.types import (
    CreateTransferTransactionRequest,
    EstimateFeeRequest,
    Transaction,
    TransactionCreationGasParams,
    TransactionFeeTier,
    TransactionStatus,
    TransferPartyData,
    TransferPartyType,
)


def create_transfer(api_client: APIClient):
    assets = api_client.get_assets_data()
    ethereum_asset = next(
        asset
        for asset in assets
        if asset.blockChain == "ETHEREUM" and asset.symbol == "ETH"
    )

    # Source and destination can each be a Core Vault or an Exchange Vault. The
    # destination can also be a whitelisted external address:
    # TransferPartyData(type=TransferPartyType.EXTERNAL_ADDRESS.value, address="0x123456789..")
    source_vaults = api_client.get_vaults({"vaultName": "core-vault-1"})
    destination_contacts = api_client.get_contacts({"name": "Lynn Bell"})

    source = TransferPartyData(
        type=TransferPartyType.VAULT.value, id=source_vaults.results[0].id
    )
    destination = TransferPartyData(
        type=TransferPartyType.CONTACT.value, id=destination_contacts.results[0].id
    )

    # Optional. Returns the expected fee for the HIGH, MEDIUM and LOW tiers. The
    # tier is passed as gasParams below and defaults to HIGH.
    fee_estimates = api_client.estimate_fee(
        EstimateFeeRequest(
            source=source,
            destination=destination,
            amount="0.0001",
            asset=ethereum_asset.symbol,
            chain=ethereum_asset.blockChain,
        )
    )
    print(fee_estimates)

    try:
        # Creates the transfer and approves it as the API user in one call.
        transaction: Transaction = api_client.create_transaction_with_approval(
            CreateTransferTransactionRequest(
                source=source,
                destination=destination,
                amount="0.0001",
                asset=ethereum_asset.symbol,
                chain=ethereum_asset.blockChain,
                externalId="externalId-1",  # Optional external ID
                gasParams=TransactionCreationGasParams(  # Optional gas parameters, defaults to TransactionFeeTier.HIGH
                    feeTier=TransactionFeeTier.HIGH.value
                ),
            )
        )
    except BadRequestError as e:
        print(e.response_text, e.code)  # handle 400 error
        raise e
    except UnauthorizedError as e:
        print(e.response_text, e.code)  # handle 401 error
        raise e
    except InternalServerError as e:
        print(e.response_text, e.code)  # handle 500 error
        raise e
    # similarly there are ForbiddenError, NotFoundError, ServiceUnavailableError, TooManyRequestsError exceptions

    print(transaction)

    # Instead of polling, set up a webhook to get notified when the transaction
    # is completed or failed.
    while True:
        txn_response = api_client.get_transaction_by_id(transaction.id)
        if txn_response.status in [
            TransactionStatus.COMPLETED.value,
            TransactionStatus.FAILED.value,
        ]:
            break
        time.sleep(3)

    print(txn_response)


def get_transactions(api_client: APIClient):
    """
    Cursor-based pagination example.
    For date range filters, use createdAtGte and createdAtLte.
    """
    limit = 50
    cursor = ""
    all_transactions = []

    while True:
        dt = datetime.datetime.now() - datetime.timedelta(days=10)  # last 10 days
        response = api_client.get_transactions(
            params={
                "vaultId": "7ad54443-21d2-4075-abef-83758c9dceb7",
                "createdAtGte": str(dt),
                "status": TransactionStatus.COMPLETED.value,
            },
            limit=limit,
            cursor=cursor,
        )
        all_transactions.extend(response.results)
        print(
            f"Fetched {len(response.results)} transactions (total: {len(all_transactions)})"
        )

        if not response.hasNext or not response.nextCursor:
            break
        cursor = response.nextCursor

    print(f"Total transactions: {len(all_transactions)}")
