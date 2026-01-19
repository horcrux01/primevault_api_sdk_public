import json
from typing import Optional

import boto3
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

from primevault_python_sdk.config import Config


def generate_public_private_key_pair() -> dict[str, str]:
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()

    public_key_der = public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    public_key_hex = public_key_der.hex()

    private_key_der = private_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    private_key_hex = private_key_der.hex()
    return {"public_key_hex": public_key_hex, "private_key_hex": private_key_hex}


def generate_aws_kms_key_pair(key_alias: Optional[str] = None) -> dict[str, str]:
    """
    Setup AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in your environment
    """
    kms_client = boto3.client("kms", Config.get_aws_region())
    key_alias = key_alias or "primevault-access-key"
    response = kms_client.create_key(
        Description="Key for Signing PrimeVault requests",
        KeyUsage="SIGN_VERIFY",
        CustomerMasterKeySpec="ECC_NIST_P256",
        Origin="AWS_KMS",
    )
    key_id = response["KeyMetadata"]["KeyId"]

    kms_client.create_alias(AliasName=f"alias/{key_alias}", TargetKeyId=key_id)
    public_key_response = kms_client.get_public_key(KeyId=key_id)
    public_key_der = public_key_response["PublicKey"]
    return {"public_key_hex": public_key_der.hex(), "key_id": key_id}


def json_dumps(data: dict) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
