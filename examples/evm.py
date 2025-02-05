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
    contract_address = "0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d"
    call_data = "0x095ea7b3000000000000000000000000f2614a233c7c3e7f08b1f887ba133a13f1eb2c5500000000000000000000000000000000000000000000000000038d7ea4c68000"

    vaults = api_client.get_vaults({"vaultName": "core-vault-1"})
    vault_id = vaults.results[0].id
    try:
        transaction = api_client.create_contract_call_transaction(
            CreateContractCallTransactionRequest(
                vaultId=vault_id,
                chain="BNB",
                externalId="external_id-001",
                data=EVMContractCallData(
                    callData=call_data,
                    toAddress=contract_address,
                ),
                gasParams=TransactionCreationGasParams(
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
