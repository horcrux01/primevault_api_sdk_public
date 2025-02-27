from typing import List

from primevault_python_sdk.api_client import APIClient
from primevault_python_sdk.types import Asset, ChainData


def get_supported_chains(api_client: APIClient):
    chains: List[ChainData] = api_client.get_supported_chains()
    print(chains)


def get_assets_data(api_client: APIClient):
    assets: List[Asset] = api_client.get_assets_data()
    print(assets)
