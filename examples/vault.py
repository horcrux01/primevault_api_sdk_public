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


def get_vaults(api_client: APIClient):
    """List all vaults with cursor-based pagination."""
    all_vaults = []
    cursor = None

    while True:
        response = api_client.get_vaults(limit=50, cursor=cursor)
        all_vaults.extend(response.results)
        print(f"Fetched {len(response.results)} vaults (total: {len(all_vaults)})")

        if not response.hasNext or not response.nextCursor:
            break
        cursor = response.nextCursor

    print(f"Total vaults: {len(all_vaults)}")
    return all_vaults


def get_vaults_filtered(api_client: APIClient):
    """List vaults with a filter."""
    response = api_client.get_vaults(params={"vaultName": "core-vault-1"}, limit=10)
    for vault in response.results:
        print(f"  {vault.id} — {vault.vaultName} ({vault.vaultType})")
