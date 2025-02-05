import time

from primevault_python_sdk.api_client import APIClient
from primevault_python_sdk.base_api_client import (
    BadRequestError,
    InternalServerError,
    UnauthorizedError,
)
from primevault_python_sdk.types import (
    CreateContractCallTransactionRequest,
    EVMContractCallData,
    TransactionCreationGasParams,
    TransactionFeeTier,
    TransactionStatus,
)


def create_contract_call_transaction(api_client: APIClient):
    vaults = api_client.get_vaults({"vaultName": "core-vault-1"})
    vault_id = vaults.results[0].id
    try:
        transaction = api_client.create_contract_call_transaction(
            CreateContractCallTransactionRequest(
                vaultId=vault_id,
                chain="ETHEREUM",
                externalId="externalId-1",
                data=EVMContractCallData(
                    callData="0x",
                    toAddress="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
                ),
                gasParams=TransactionCreationGasParams(
                    feeTier=TransactionFeeTier.MEDIUM.value
                ),
            )
        )
    except BadRequestError as e:  # 400
        raise e
    except UnauthorizedError as e:  # 401
        raise e
    except InternalServerError as e:  # 500
        raise e

    while True:
        transaction = api_client.get_transaction_by_id(transaction.id)
        if (
            transaction.status == TransactionStatus.COMPLETED.value
            or transaction.status == TransactionStatus.FAILED.value
        ):
            break

        time.sleep(5)

    print(transaction.__dict__)
