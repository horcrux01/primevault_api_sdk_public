import json
import sys

from primevault_python_sdk.api_client import APIClient
from primevault_python_sdk.config import Config


def fetch_ec_user(email: str):
    api_key = "YOUR_API_KEY"  # replace with the API user's key
    api_url = "https://api.primevault.com"
    private_key = "YOUR_PRIVATE_KEY"  # replace with actual private key hex

    Config.set("SIGNATURE_SERVICE", "PRIVATE_KEY")

    client = APIClient(api_key, api_url, private_key)

    response = client.get("/api/external/ec_users/", params={"email": email})
    print(json.dumps(response, indent=2, default=str))


if __name__ == "__main__":
    email = sys.argv[1] if len(sys.argv) > 1 else "tushal@primevault.com"
    fetch_ec_user(email)
