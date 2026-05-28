from primevault_python_sdk.api_client import APIClient
from primevault_python_sdk.config import Config


def create_client_from_private_key():
    api_key = (
        "509bc039-65b5-4200-ac56-4827acc5a1ee"  # replace this with the API user's key
    )
    api_url = "https://api.primevault.com"

    private_key = "..."
    Config.set("SIGNATURE_SERVICE", "PRIVATE_KEY")

    return APIClient(api_key, api_url, private_key)


def create_client_from_aws_kms():
    api_key = (
        "509bc039-65b5-4200-ac56-4827acc5a1ee"  # replace this with the API user's key
    )
    api_url = "https://api.primevault.com"
    key_id = ".."  # AWS KMS key Id from Key's detail page

    Config.set("SIGNATURE_SERVICE", "AWS_KMS")
    Config.set("AWS_REGION", "us-east-1")  # replace this with your region

    return APIClient(api_key, api_url, None, key_id)
