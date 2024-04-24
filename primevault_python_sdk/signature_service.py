from enum import Enum
from typing import Optional

import boto3
from botocore.exceptions import ClientError
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePrivateKey

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
    def __init__(self, private_key_bytes: bytes):
        self.private_key: EllipticCurvePrivateKey = serialization.load_pem_private_key(
            private_key_bytes,
            password=None,
            backend=default_backend(),
        )

    def sign(self, message: bytes):
        return self.private_key.sign(message, ec.ECDSA(hashes.SHA256()))


class KMSSignatureService(BaseSignatureService):
    def __init__(self, key_id: str):
        self.kms_client = boto3.client("kms", region_name=Config.get_aws_region())
        self.key_id = key_id

    def sign(self, message: bytes):
        try:
            response = self.kms_client.sign(
                KeyId=self.key_id,
                Message=message,
                MessageType="RAW",
                SigningAlgorithm=Config.get_kms_signing_algorithm(),
            )
            return response["Signature"]
        except ClientError as e:
            print(f"An error occurred while signing: {e}")
            return None


def get_signature_service(private_key: Optional[bytes] = None, **kwargs):
    signature_service = Config.get_signature_service()
    if signature_service == SignatureServiceEnum.PRIVATE_KEY.value:
        return PrivateKeySignatureService(private_key)
    elif signature_service == SignatureServiceEnum.AWS_KMS.value:
        return KMSSignatureService(**kwargs)
    else:
        raise ValueError(f"Invalid signature service: {signature_service}")
