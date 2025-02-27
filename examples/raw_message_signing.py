import time

from primevault_python_sdk.api_client import APIClient
from primevault_python_sdk.types import (
    CreateContractCallTransactionRequest,
    EVMContractCallData,
    Transaction,
    TransactionStatus,
    VaultListResponse,
)


def raw_message_signature_for_evm(api_client: APIClient):
    vaults: VaultListResponse = api_client.get_vaults({"vaultName": "core-vault-1"})
    vault_id = vaults.results[0].id

    # Signing a raw message on ETHEREUM
    txn_response: Transaction = api_client.create_contract_call_transaction(
        CreateContractCallTransactionRequest(
            vaultId=vault_id,
            chain="ETHEREUM",
            externalId="externalId-1",  # Optional externalId to track transactions, should be unique
            data=EVMContractCallData(callData="0x095ea7b3000000000000000000000000c"),
        )
    )

    while True:
        txn_response = api_client.get_transaction_by_id(txn_response.id)
        if txn_response.status in [
            TransactionStatus.COMPLETED,
            TransactionStatus.FAILED,
        ]:
            break
        time.sleep(3)

    print(txn_response.txnSignature)
