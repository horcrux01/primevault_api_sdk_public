import os
from typing import Optional

from primevault_python_sdk.api_client import APIClient


def create_dev_client() -> APIClient:
    from examples.dev_client import create_client

    return create_client()


def create_prod_client() -> APIClient:
    from examples.prod_client import create_client

    return create_client()


def create_client(env: Optional[str] = None) -> APIClient:
    selected_env = (env or os.environ.get("PV_ENV") or "dev").lower()
    if selected_env == "dev":
        return create_dev_client()
    if selected_env == "prod":
        return create_prod_client()
    raise ValueError("env must be 'dev' or 'prod'")
