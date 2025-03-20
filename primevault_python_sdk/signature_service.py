from enum import Enum
from typing import Optional

import boto3
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec

from primevault_python_sdk.config import Config


class SignatureServiceEnum(Enum):
    AWS_KMS = "AWS_KMS"
    PRIVATE_KEY = "PRIVATE_KEY"


class BaseSignatureService(object):
    """Base class for signature."""

    def sign(self, string_to_sign):
        raise NotImplementedError

    def verify(self, string_to_sign, signature):
        raise NotImplementedError


class PrivateKeySignatureService(BaseSignatureService):
    def __init__(self, private_key_hex: str):
        trimmed_key = private_key_hex.strip()
        self.private_key: ec.EllipticCurvePrivateKey

        if trimmed_key.startswith("-----BEGIN"):
            # If the key is in PEM format.
            pem_bytes = trimmed_key.encode("utf-8")
            self.private_key = serialization.load_pem_private_key(
                pem_bytes, password=None, backend=default_backend()
            )
        else:
            # Assume the key is hex-encoded DER.
            try:
                private_key_bytes = bytes.fromhex(trimmed_key)
            except ValueError:
                raise ValueError("Input is not valid hex-encoded DER or PEM format.")

            self.private_key = serialization.load_der_private_key(
                private_key_bytes, password=None, backend=default_backend()
            )

    def sign(self, message: bytes):
        return self.private_key.sign(message, ec.ECDSA(hashes.SHA256()))


class KMSSignatureService(BaseSignatureService):
    def __init__(self, key_id: str):
        self.kms_client = boto3.client("kms", region_name=Config.get_aws_region())
        self.key_id = key_id

    def sign(self, message: bytes):
        response = self.kms_client.sign(
            KeyId=self.key_id,
            Message=message,
            MessageType="RAW",
            SigningAlgorithm=Config.get_kms_signing_algorithm(),
        )
        return response["Signature"]


def get_signature_service(
    private_key_hex: Optional[str] = None, key_id: Optional[str] = None
):
    signature_service = Config.get_signature_service()
    if signature_service == SignatureServiceEnum.PRIVATE_KEY.value:
        if not private_key_hex:
            raise ValueError(
                "Private key is required for PRIVATE_KEY signature service"
            )
        return PrivateKeySignatureService(private_key_hex)
    elif signature_service == SignatureServiceEnum.AWS_KMS.value:
        if not key_id:
            raise ValueError("Key ID is required for AWS_KMS signature service")
        return KMSSignatureService(key_id=key_id)
    else:
        raise ValueError(f"Invalid signature service: {signature_service}")
