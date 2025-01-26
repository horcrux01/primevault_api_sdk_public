import base64
import time
from hashlib import sha256
from typing import Optional
from uuid import uuid4

from primevault_python_sdk.config import Config
from primevault_python_sdk.signature_service import get_signature_service
from primevault_python_sdk.utils import json_dumps


class AuthTokenService(object):
    def __init__(
        self,
        api_key: str,
        private_key_hex: Optional[str] = None,
        key_id: Optional[str] = None,
    ):
        self.api_key = api_key
        self.signature_service = get_signature_service(private_key_hex, key_id)

    def generate_auth_token(self, url_path: str, body: Optional[dict] = None):
        timestamp = int(time.time())
        body = body or {}
        body = sha256(json_dumps(body).encode("utf-8")).hexdigest()
        payload = {
            "iat": timestamp,
            "exp": timestamp + Config.get_expires_in(),
            "urlPath": url_path,
            "userId": self.api_key,
            "body": body,
            "jti": str(uuid4()),
        }
        headers = {"alg": "ES256", "typ": "JWT"}
        encoded_request = self.encode_request(headers, payload)
        signature = self.sign_request(encoded_request.encode("utf-8"))
        encoded_signature = base64.urlsafe_b64encode(signature).decode("utf-8")
        return f"{encoded_request}.{encoded_signature}"

    def encode_request(self, headers: dict, payload: dict) -> str:
        json_header = json_dumps(headers).encode()
        json_payload = json_dumps(payload).encode()
        encoded_header = base64.urlsafe_b64encode(json_header).decode("utf-8")
        encoded_payload = base64.urlsafe_b64encode(json_payload).decode("utf-8")
        return f"{encoded_header}.{encoded_payload}"

    def sign_request(self, encoded_request: bytes):
        return self.signature_service.sign(encoded_request)
