# PrimeVault's Python SDK

### Generate API user's access public-private key
```
from primevault_python_sdk.utils import generate_public_private_key_pair, generate_aws_kms_key_pair

# Option 1: PRIVATE_KEY
res = generate_public_private_key_pair()

# Option 2: AWS_KMS
"""
Here the private key is managed by AWS KMS.
Set up AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in your environment before executing this.
"""
res = generate_aws_kms_key_pair()

```

### Setup APIClient
```
from primevault_python_sdk.api_client import APIClient
from primevault_python_sdk.config import Config


api_key = (
    "509bc039-65b5-4200-ac56-4827acc5a1ee"  # available on PrimeVault's users' page after the API user is created.
)
api_url = "https://app.primevault.com"

"""
Set the signature service to PRIVATE_KEY.

Another option is AWS_KMS where AWS KMS manages the private key.
In this case, private_key is not required for initializing the client.
"""
Config.set("SIGNATURE_SERVICE", "PRIVATE_KEY")

"""
Private key for the signature service. Required if the signature service is set to PRIVATE_KEY.
It should be the same that is generated from generate_public_private_key_pair above.
"""
private_key = b"-----BEGIN PRIVATE KEY-----\n....-----END PRIVATE KEY-----\n"

api_client = APIClient(api_key, api_url, private_key=private_key)
```

### Create transfer transaction
```
source_vault_response = api_client.get(f"/api/external/vaults/?vaultName=all-wallets-1")  # source
destination_contact_response = api_client.get(
    f"/api/external/contacts/?name=Karen Christian"
)  # destination

source_id = source_vault_response["results"][0]["id"]
destination_id = destination_contact_response["results"][0]["id"]

transaction = api_client.create_transfer_transaction(
    source_id=source_id,
    destination_id=destination_id,
    amount="0.0001",
    asset="ETH",
    chain="ETHEREUM", # Enum Blockchain
    external_id="external_id_1",
)

while True:
    transaction = api_client.get_transaction_by_id(transaction["id"])
    if transaction["status"] == "COMPLETED":
        break
    time.sleep(5)
```

### Create a new vault
```
data = {
    "vaultName": "test-vault-1",
    "defaultTransferSpendLimit": {
        "action": {"actionType": "NEEDS_MORE_APPROVALS", "additionalApprovalCount": 1},
        "spendLimit": "100",
        "resetFrequency": "86400",
    },
    "defaultTradeSpendLimit": {
        "action": {"actionType": "BLOCK_OPERATION"},
        "spendLimit": "100",
        "resetFrequency": "86400",
    },
}

vault = api_client.create_vault(data)

while True:
    vault = api_client.get_vault_by_id(vault["id"])
    if vault["walletsGenerated"]:
        # wallets are generated
        break
    time.sleep(5)

print(vault)
```
