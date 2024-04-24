from typing import Optional, List

from primevault_python_sdk.base_api_client import BaseAPIClient


class APIClient(BaseAPIClient):
    def get_assets_data(self):
        return self.get("/api/external/assets/")

    def get_transactions(self, page: Optional[int] = 1, limit: Optional[int] = 20):
        return self.get(f"/api/external/transactions/?page={page}&limit={limit}")

    def get_transaction_by_id(self, transaction_id: str):
        return self.get(f"/api/external/transactions/{transaction_id}/")

    def estimate_fee(
        self, source_id: str, destination_id: str, amount: str, asset: str, chain: str
    ):
        data = {
            "sourceId": source_id,
            "destinationId": destination_id,
            "amount": amount,
            "asset": asset,
            "blockChain": chain,
            "category": "TRANSFER",
        }
        return self.post("/api/external/transactions/estimate_fee/", data=data)

    def create_transfer_transaction(
        self,
        source_id: str,
        destination_id: str,
        amount: str,
        asset: str,
        chain: str,
        gas_params: Optional[dict] = None,
        external_id: Optional[str] = None,
        is_automation: Optional[bool] = False,
        execute_at: Optional[str] = None,
    ):
        data = {
            "sourceId": source_id,
            "destinationId": destination_id,
            "amount": str(amount),
            "asset": asset,
            "blockChain": chain,
            "category": "TRANSFER",
            "gasParams": gas_params or {},
            "externalId": external_id,
            "isAutomation": is_automation,
            "executeAt": execute_at,
        }
        return self.post("/api/external/transactions/", data=data)

    def get_trade_quote(
        self,
        vault_id: str,
        from_asset: str,
        to_asset: str,
        from_amount: str,
        from_chain: str,
        to_chain: str,
        slippage: str,
    ):
        data = {
            "vaultId": vault_id,
            "fromAsset": from_asset,
            "toAsset": to_asset,
            "fromAmount": from_amount,
            "blockChain": from_chain,
            "toBlockchain": to_chain,
            "slippage": slippage,
        }
        return self.get("/api/external/transactions/trade_quote/", params=data)

    def create_trade_transaction(
        self,
        vault_id: str,
        trade_request_data: dict,
        trade_response_data: dict,
        external_id: Optional[str] = None,
    ):
        data = {
            "vaultId": vault_id,
            "tradeRequestData": trade_request_data,
            "tradeResponseData": trade_response_data,
            "category": "SWAP",
            "blockChain": trade_request_data["blockChain"],
            "externalId": external_id,
        }
        return self.post("/api/external/transactions/", data=data)

    def get_vaults(
        self,
        page: Optional[int] = 1,
        limit: Optional[int] = 20,
        reverse: Optional[bool] = False,
    ):
        return self.get(
            f"/api/external/vaults/?limit={limit}&page={page}&reverse={reverse}"
        )

    def get_vault_by_id(self, vault_id: str):
        return self.get(f"/api/external/vaults/{vault_id}/")

    def create_vault(self, data: dict):
        return self.post("/api/external/vaults/", data=data)

    def get_balances(self, vault_id: str):
        return self.get(f"/api/external/vaults/{vault_id}/balances/")

    def update_balances(self, vault_id: str):
        return self.post(f"/api/external/vaults/{vault_id}/update_balances/")

    def get_operation_message_to_sign(self, operation_id: str):
        return self.get(
            f"/api/external/operations/{operation_id}/operation_message_to_sign/"
        )

    def update_user_action(
        self, operation_id: str, is_approved: bool, signature_hex: str
    ):
        data = {
            "isApproved": is_approved,
            "signatureHex": signature_hex,
            "operationId": operation_id,
        }
        return self.post(
            f"/api/external/operations/{operation_id}/update_user_action/", data=data
        )

    def get_contacts(self, page: Optional[int] = 1, limit: Optional[int] = 20):
        return self.get(f"/api/external/contacts/?limit={limit}&page={page}")

    def get_contact_by_id(self, contact_id: str):
        return self.get(f"/api/external/contacts/{contact_id}/")

    def create_contact(
        self,
        name: str,
        address: str,
        chain: str,
        tags: Optional[List[str]] = None,
        external_id: Optional[str] = None,
    ):
        data = {
            "name": name,
            "address": address,
            "blockChain": chain,
            "tags": tags,
            "externalId": external_id,
        }
        return self.post("/api/external/contacts/", data=data)
