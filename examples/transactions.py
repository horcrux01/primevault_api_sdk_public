import datetime
import time

from primevault_python_sdk.api_client import APIClient
from primevault_python_sdk.base_api_client import (
    BadRequestError,
    InternalServerError,
    NotFoundError,
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


def create_transfer_transaction(api_client: APIClient):
    assets = api_client.get_assets_data()
    ethereum_asset = next(
        asset
        for asset in assets
        if asset.blockChain == "ETHEREUM" and asset.symbol == "ETH"
    )

    # Fetch source and destination vaults
    source_vaults = api_client.get_vaults({"vaultName": "core-vault-1"})
    destination_contacts = api_client.get_contacts({"name": "Lynn Bell"})

    # Source Vault, this could be Core or Exchange Vault.
    source = TransferPartyData(
        type=TransferPartyType.VAULT.value, id=source_vaults.results[0].id
    )

    # Destination. This could be Core or Exchange Vault or External address.
    destination = TransferPartyData(
        type=TransferPartyType.CONTACT.value, id=destination_contacts.results[0].id
    )
    """
    To send the transaction to an external whitelisted address, change the type and set the value
    const destination: TransferPartyData = TransferPartyData(type=TransferPartyType.EXTERNAL_ADDRESS.value, value='0x123456789..');

    Optional fee estimate API which returns the expected fee for different tiers, HIGH, MEDIUM, LOW.
    Default is HIGH. The feeTier is passed in gasParams argument while creating the transfer transaction.
    """
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
        # Create transaction
        transaction: Transaction = api_client.create_transfer_transaction(
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
    for date range filters, use createdAtGte and createdAtLte
    """
    limit = 50
    page = 1
    transactions = []
    while True:
        try:
            dt = datetime.datetime.now() - datetime.timedelta(days=10)  # last 10 days
            response = api_client.get_transactions(
                params={
                    "vaultId": "7ad54443-21d2-4075-abef-83758c9dceb7",
                    "createdAtGte": str(dt),
                    "status": TransactionStatus.COMPLETED.value,
                },
                page=page,
                limit=limit,
            )
            transactions.append(response.results)
        except NotFoundError:  # end of results
            break
        page += 1

    print(transactions)
