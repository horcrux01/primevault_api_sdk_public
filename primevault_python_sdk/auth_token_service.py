import base64
import json
import time
from hashlib import sha256
from typing import Optional

from primevault_python_sdk.signature_service import PrivateKeySignatureService, KMSSignatureService, SignatureServiceEnum

EXPIRES_IN = 3600

SIGNATURE_SERVICE = SignatureServiceEnum.PRIVATE_KEY.value


class AuthTokenService(object):
    def __init__(self, api_key: str, private_key: Optional[bytes] = None, **kwargs):
        self.api_key = api_key
        if SIGNATURE_SERVICE == SignatureServiceEnum.PRIVATE_KEY.value:
            self.signature_service = PrivateKeySignatureService(private_key)
        elif SIGNATURE_SERVICE == SignatureServiceEnum.AWS_KMS.value:
            self.signature_service = KMSSignatureService(**kwargs)

    def generate_auth_token(self, url_path: str, body: Optional[dict] = None):
        timestamp = int(time.time())
        body = body or {}
        body = sha256(json.dumps(body, sort_keys=True).encode("utf-8")).hexdigest()
        payload = {
            "iat": timestamp,
            "exp": timestamp + EXPIRES_IN,
            "urlPath": url_path,
            "userId": self.api_key,
            "body": body,
        }
        headers = {
            "alg": "ES256",
            "typ": "JWT"
        }
        encoded_request = self.encode_request(headers, payload)
        signature = self.sign_request(encoded_request.encode('utf-8'))
        encoded_signature = base64.urlsafe_b64encode(signature).decode("utf-8")
        return f"{encoded_request}.{encoded_signature}"

    def encode_request(self, headers: dict, payload: dict) -> str:
        json_header = json.dumps(
            headers, separators=(",", ":"), sort_keys=True
        ).encode()
        json_payload = json.dumps(
            payload, separators=(",", ":"), sort_keys=True
        ).encode()
        encoded_header = base64.urlsafe_b64encode(json_header).decode("utf-8")
        encoded_payload = base64.urlsafe_b64encode(json_payload).decode("utf-8")
        return f"{encoded_header}.{encoded_payload}"

    def sign_request(self, encoded_request: bytes):
        return self.signature_service.sign(encoded_request)
