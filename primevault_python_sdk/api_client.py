from typing import List, Optional

from dacite import from_dict

from primevault_python_sdk.base_api_client import BaseAPIClient
from primevault_python_sdk.types import (
    Asset,
    BalanceResponse,
    ChainData,
    Contact,
    ContactListResponse,
    CreateContactRequest,
    CreateContractCallTransactionRequest,
    CreateTradeQuoteRequest,
    CreateTradeTransactionRequest,
    CreateTransferTransactionRequest,
    CreateVaultRequest,
    DetailedBalance,
    DetailedBalanceResponse,
    EstimatedFeeResponse,
    EstimateFeeRequest,
    GetTradeQuoteResponse,
    ReplaceTransactionRequest,
    Transaction,
    TransactionListResponse,
    Vault,
    VaultListResponse,
)


class APIClient(BaseAPIClient):
    def get_assets_data(self) -> List[Asset]:
        assets_response = self.get("/api/external/assets/")
        return [from_dict(Asset, asset) for asset in assets_response]

    def get_supported_chains(self) -> List[ChainData]:
        chains_response = self.get("/api/external/assets/supported_chains/")
        return [from_dict(ChainData, chain) for chain in chains_response]

    def get_transactions(
        self,
        params: Optional[dict] = None,
        page: Optional[int] = 1,
        limit: Optional[int] = 20,
    ) -> TransactionListResponse:
        query_params = ""
        if params:
            query_params = "&".join([f"{k}={v}" for k, v in params.items()])

        return from_dict(
            TransactionListResponse,
            self.get(
                f"/api/external/transactions/?page={page}&limit={limit}&{query_params}"
            ),
        )

    def get_transaction_by_id(self, transaction_id: str) -> Transaction:
        return from_dict(
            Transaction, self.get(f"/api/external/transactions/{transaction_id}/")
        )

    def estimate_fee(self, request: EstimateFeeRequest) -> EstimatedFeeResponse:
        data = {
            "source": request.source.__dict__,
            "destination": request.destination.__dict__,
            "amount": request.amount,
            "asset": request.asset,
            "blockChain": request.chain,
            "category": "TRANSFER",
        }
        return from_dict(
            EstimatedFeeResponse,
            self.post("/api/external/transactions/estimate_fee/", data=data),
        )

    def create_transfer_transaction(
        self, request: CreateTransferTransactionRequest
    ) -> Transaction:
        gas_params = {}
        if request.gasParams:
            gas_params = request.gasParams.__dict__

        data = {
            "source": request.source.__dict__,
            "destination": request.destination.__dict__,
            "amount": request.amount,
            "asset": request.asset,
            "blockChain": request.chain,
            "category": "TRANSFER",
            "gasParams": gas_params,
            "externalId": request.externalId,
            "isAutomation": request.isAutomation,
            "executeAt": request.executeAt,
            "memo": request.memo,
            "feePayer": request.feePayer and request.feePayer.__dict__,
        }
        response = self.post("/api/external/transactions/", data=data)
        return from_dict(Transaction, response)

    def replace_transaction(self, request: ReplaceTransactionRequest) -> Transaction:
        return from_dict(
            Transaction,
            self.post(
                "/api/external/transactions/replace_transaction/",
                data=request.__dict__,
            ),
        )

    def create_contract_call_transaction(
        self, request: CreateContractCallTransactionRequest
    ) -> Transaction:
        gas_params = {}
        creation_options = {}
        if request.gasParams:
            gas_params = request.gasParams.__dict__
        if request.creationOptions:
            creation_options = request.creationOptions.__dict__

        data = {
            "vaultId": request.vaultId,
            "blockChain": request.chain,
            "amount": request.amount,
            "category": "CONTRACT_CALL",
            "data": request.data.__dict__,
            "externalId": request.externalId,
            "gasParams": gas_params,
            "creationOptions": creation_options,
        }
        return from_dict(
            Transaction, self.post("/api/external/transactions/", data=data)
        )

    def get_trade_quote(
        self, request: CreateTradeQuoteRequest
    ) -> GetTradeQuoteResponse:
        data = {
            "vaultId": request.vaultId,
            "fromAsset": request.fromAsset,
            "toAsset": request.toAsset,
            "fromAmount": request.fromAmount,
            "blockChain": request.fromChain,
            "toBlockchain": request.toChain,
            "slippage": request.slippage,
        }
        return from_dict(
            GetTradeQuoteResponse,
            self.get("/api/external/transactions/trade_quote/", params=data),
        )

    def create_trade_transaction(
        self, request: CreateTradeTransactionRequest
    ) -> Transaction:
        data = {
            "vaultId": request.vaultId,
            "tradeRequestData": request.tradeRequestData.__dict__,
            "tradeResponseData": request.tradeResponseData.__dict__,
            "category": "SWAP",
            "blockChain": request.tradeRequestData.blockChain,
            "externalId": request.externalId,
            "memo": request.memo,
        }
        return from_dict(
            Transaction, self.post("/api/external/transactions/", data=data)
        )

    def get_vaults(
        self,
        params: Optional[dict] = None,
        page: Optional[int] = 1,
        limit: Optional[int] = 20,
        reverse: Optional[bool] = False,
    ) -> VaultListResponse:
        query_params = ""
        if params:
            query_params = "&".join([f"{k}={v}" for k, v in params.items()])

        response = self.get(
            f"/api/external/vaults/?limit={limit}&page={page}&reverse={reverse}&{query_params}"
        )
        return from_dict(data_class=VaultListResponse, data=response)

    def get_vault_by_id(self, vault_id: str) -> Vault:
        return from_dict(Vault, self.get(f"/api/external/vaults/{vault_id}/"))

    def create_vault(self, request: CreateVaultRequest) -> Vault:
        return from_dict(
            Vault, self.post("/api/external/vaults/", data=request.__dict__)
        )

    def get_balances(self, vault_id: str) -> BalanceResponse:
        return self.get(f"/api/external/vaults/{vault_id}/balances/")

    def get_detailed_balances(self, vault_id: str) -> DetailedBalanceResponse:
        response = self.get(f"/api/external/vaults/{vault_id}/detailed_balances/")
        return [from_dict(DetailedBalance, balance) for balance in response]

    def update_balances(self, vault_id: str) -> BalanceResponse:
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

    def get_contacts(
        self,
        params: Optional[dict] = None,
        page: Optional[int] = 1,
        limit: Optional[int] = 20,
    ) -> ContactListResponse:
        query_params = ""
        if params:
            query_params = "&".join([f"{k}={v}" for k, v in params.items()])

        response = self.get(
            f"/api/external/contacts/?limit={limit}&page={page}&{query_params}"
        )
        return from_dict(data_class=ContactListResponse, data=response)

    def get_contact_by_id(self, contact_id: str) -> Contact:
        return from_dict(Contact, self.get(f"/api/external/contacts/{contact_id}/"))

    def create_contact(self, request: CreateContactRequest) -> Contact:
        data = {
            "name": request.name,
            "address": request.address,
            "blockChain": request.chain,
            "tags": request.tags,
            "externalId": request.externalId,
        }
        response = self.post("/api/external/contacts/", data=data)
        return from_dict(Contact, response)
