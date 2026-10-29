import time

from primevault_python_sdk.api_client import APIClient
from primevault_python_sdk.types import (
    CreateContractCallTransactionRequest,
    CreateTransferTransactionRequest,
    FeePayer,
    StellarActivationData,
    Transaction,
    TransactionStatus,
    TransferPartyData,
    TransferPartyType,
)


def poll_for_transaction(api_client: APIClient, transaction_id: str) -> Transaction:
    while True:
        transaction = api_client.get_transaction_by_id(transaction_id)
        if transaction.status in [
            TransactionStatus.COMPLETED.value,
            TransactionStatus.FAILED.value,
        ]:
            return transaction
        time.sleep(3)


def activate_stellar_asset(api_client: APIClient):
    """
    A Stellar vault holds XLM by default. Before it can hold an issued asset such as USDC,
    the asset must be activated (a trustline is added) on the vault. Stellar keeps 0.5 XLM
    in the vault for each activated asset; a fee payer vault can only cover the network fee.
    """
    vault_id = api_client.get_vaults({"vaultName": "stellar-vault-1"}).results[0].id
    # Optional: another Stellar vault in the organization pays the network fee.
    fee_payer_vault_id = (
        api_client.get_vaults({"vaultName": "fee-payer-1"}).results[0].id
    )

    transaction = api_client.create_contract_call_transaction(
        CreateContractCallTransactionRequest(
            vaultId=vault_id,
            chain="STELLAR",  # use "STELLAR_TESTNET" for testnet vaults
            externalId="externalId-stellar-activation-1",  # Optional, should be unique
            data=StellarActivationData(activateAsset="USDC"),
            feePayer=FeePayer(
                id=fee_payer_vault_id
            ),  # Optional, must differ from vaultId
        )
    )
    print(transaction.subCategory)  # ACTIVATION

    transaction = poll_for_transaction(api_client, transaction.id)
    print(transaction)


def create_stellar_transfer(api_client: APIClient):
    source_vault_id = (
        api_client.get_vaults({"vaultName": "stellar-vault-1"}).results[0].id
    )
    fee_payer_vault_id = (
        api_client.get_vaults({"vaultName": "fee-payer-1"}).results[0].id
    )

    # The destination account must exist and, for issued assets like USDC, have the asset activated.
    transaction = api_client.create_transfer_transaction(
        CreateTransferTransactionRequest(
            source=TransferPartyData(type=TransferPartyType.VAULT, id=source_vault_id),
            destination=TransferPartyData(
                type=TransferPartyType.EXTERNAL_ADDRESS,
                value="GCACGH7OUW47CNHU2ARUFWFJU5PEZXDISMMYX6MLIVV5XKX4BGQG4U4N",
            ),
            amount="1",
            asset="USDC",
            chain="STELLAR",
            externalId="externalId-stellar-transfer-1",
            feePayer=FeePayer(id=fee_payer_vault_id),  # Optional
        )
    )

    transaction = poll_for_transaction(api_client, transaction.id)
    print(transaction)
