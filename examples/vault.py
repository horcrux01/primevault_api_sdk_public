import time

from primevault_python_sdk.api_client import APIClient
from primevault_python_sdk.types import BalanceResponse, CreateVaultRequest


def create_vault(api_client: APIClient):
    template_id = ""  # Template ID from UI
    data = CreateVaultRequest(
        vaultName="vault_from_template", templateId=str(template_id)
    )
    vault = api_client.create_vault(data)
    while True:
        vault = api_client.get_vault_by_id(vault.id)
        if vault.walletsGenerated:
            break
        time.sleep(3)


def get_vault_balance(api_client: APIClient):
    vault_id = ""  # Vault ID
    balances: BalanceResponse = api_client.get_balances(vault_id)
    print(balances)
