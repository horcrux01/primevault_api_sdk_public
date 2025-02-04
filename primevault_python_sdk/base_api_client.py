import json
from typing import Any, Optional

import requests  # type: ignore

from primevault_python_sdk.auth_token_service import AuthTokenService
from primevault_python_sdk.signature_service import get_signature_service
from primevault_python_sdk.utils import json_dumps


class BaseAPIClient(object):
    def __init__(
        self,
        api_key: str,
        api_url: str,
        private_key_hex: Optional[str] = None,
        key_id: Optional[str] = None,
    ):
        self.api_key = api_key
        self.api_url = api_url
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Api-Key": self.api_key,
        }
        self.auth_token_service = AuthTokenService(
            self.api_key, private_key_hex, key_id
        )
        self.signature_service = get_signature_service(private_key_hex, key_id)

    def get(self, path: str, params: Optional[dict[str, Any]] = None):
        return self._make_request("GET", url_path=path, params=params)

    def post(self, path: str, data: Optional[dict[str, Any]] = None):
        return self._make_request("POST", url_path=path, data=data)

    def _make_request(
        self,
        method: str,
        url_path: Optional[str] = None,
        params: Optional[dict[str, Any]] = None,
        data: Optional[dict[str, Any]] = None,
        timeout: Optional[int] = 20,
    ) -> Optional[Any]:
        full_url = f"{self.api_url}{url_path}"
        api_token = self.auth_token_service.generate_auth_token(url_path or "", data)
        self.headers["Authorization"] = f"Bearer {api_token}"
        if data:
            data["dataSignatureHex"] = self.signature_service.sign(
                json_dumps(data).encode("utf-8")
            ).hex()

        response = None
        try:
            if method == "GET":
                response = requests.get(
                    full_url, headers=self.headers, params=params, timeout=timeout
                )
            elif method == "POST":
                response = requests.post(
                    full_url,
                    headers=self.headers,
                    params=params,
                    json=data,
                    timeout=timeout,
                )
            else:
                raise Exception(f"Invalid method: {method}")

            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if response is not None:
                if response.status_code == 400:
                    raise BadRequestError(
                        f"400 Bad Request: {e} {response.text}",
                        response_text=response.text,
                    )
                elif response.status_code == 401:
                    raise UnauthorizedError(
                        f"401 Unauthorized: {e} {response.text}",
                        response_text=response.text,
                    )
                elif response.status_code == 403:
                    raise ForbiddenError(
                        f"403 Forbidden: {e} {response.text}",
                        response_text=response.text,
                    )
                elif response.status_code == 404:
                    raise NotFoundError(
                        f"404 Not Found: {e} {response.text}",
                        response_text=response.text,
                    )
                elif response.status_code == 429:
                    raise TooManyRequestsError(
                        f"429 Too Many Requests: {e} {response.text}",
                        response_text=response.text,
                    )
                elif response.status_code == 500:
                    raise InternalServerError(
                        f"500 Internal Server Error: {e} {response.text}",
                        response_text=response.text,
                    )
            else:
                raise Exception(f"HTTP Error: {e} {response and response.text}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request Exception: {e} {response and response.text}")

        try:
            return response.json()
        except json.decoder.JSONDecodeError:
            return response.text


class BaseAPIException(Exception):
    def __init__(self, message, response_text=None):
        super().__init__(message)
        self.response_text = response_text


class BadRequestError(BaseAPIException):
    pass


class UnauthorizedError(BaseAPIException):
    pass


class ForbiddenError(BaseAPIException):
    pass


class NotFoundError(BaseAPIException):
    pass


class InternalServerError(BaseAPIException):
    pass


class ServiceUnavailableError(BaseAPIException):
    pass


class TooManyRequestsError(BaseAPIException):
    pass
