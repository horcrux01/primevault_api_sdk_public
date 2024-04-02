import boto3
from botocore.exceptions import ClientError
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePrivateKey

from constants import AWS_REGION


def generate_private_key():
    private_key: EllipticCurvePrivateKey = ec.generate_private_key(
        ec.SECP256R1(), default_backend()
    )
    public_key = private_key.public_key()
    public_key_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    pem_private_key = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    return pem_private_key, public_key_bytes


def generate_aws_kms_key_pair():
    """
    Setup AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in your environment
    """
    kms_client = boto3.client('kms', AWS_REGION)
    key_alias = 'primevault-access-key'
    try:
        # Create a KMS key for signing
        response = kms_client.create_key(
            Description='Key for Signing PrimeVault requests',
            KeyUsage='SIGN_VERIFY',
            CustomerMasterKeySpec='ECC_NIST_P256',
            Origin='AWS_KMS'
        )
        key_id = response['KeyMetadata']['KeyId']

        kms_client.create_alias(
            AliasName=f'alias/{key_alias}',
            TargetKeyId=key_id
        )
        public_key_response = kms_client.get_public_key(KeyId=key_id)
        public_key_der = public_key_response['PublicKey']

        # Convert DER encoded key to PEM format
        public_key = serialization.load_der_public_key(public_key_der, default_backend())
        public_key_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return key_id, public_key_pem
    except ClientError as e:
        print(f"An error occurred: {e}")
        return None

