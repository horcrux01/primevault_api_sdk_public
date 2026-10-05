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
api_url = "https://api.primevault.com"

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

### Code Examples

SubOrg creation and cursor-based listing are available through `create_sub_org`
and `get_sub_orgs`; see [the SubOrg example](examples/sub_org.py). Use
`CreateSubOrgRequest(name=...)`; creation defaults to `MANAGED` control mode
and always creates an end-user SubOrg. Supplying `controlMode` in a create
request is rejected by the API. The API user must be ADMIN or OWNER to create
or list SubOrgs. Creation requires organization-wide access; end-user admins
and owners can list only their own SubOrg. Responses use the
`SubOrg` and `SubOrgListResponse` dataclasses, with typed control modes.
The optional `name` filter uses case-insensitive SQL patterns (`%Acme%` for a
substring match). List responses include `results`, `nextCursor`, and `hasNext`.

[Here](https://github.com/horcrux01/primevault_api_sdk_public/tree/main/examples)
