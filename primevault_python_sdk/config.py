from typing import Any


class Config:
    _config: dict[str, Any] = {}

    @staticmethod
    def set(key, value):
        Config._config[key] = value

    @staticmethod
    def get(key):
        return Config._config.get(key, None)

    @staticmethod
    def clear():
        Config._config = {}

    @staticmethod
    def get_signature_service():
        from primevault_python_sdk.signature_service import SignatureServiceEnum

        return Config.get("SIGNATURE_SERVICE") or SignatureServiceEnum.PRIVATE_KEY.value

    @staticmethod
    def get_expires_in():
        return Config.get("EXPIRES_IN") or 300

    @staticmethod
    def get_aws_region():
        return Config.get("AWS_REGION") or "eu-north-1"

    @staticmethod
    def get_kms_signing_algorithm():
        return Config.get("KMS_SIGNING_ALGORITHM") or "ECDSA_SHA_256"
