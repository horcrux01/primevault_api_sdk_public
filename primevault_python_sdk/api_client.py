from dataclasses import asdict
from typing import Any, List, Optional

from dacite import Config, from_dict

from primevault_python_sdk.base_api_client import BaseAPIClient
from primevault_python_sdk.types import (
    Asset,
    BalanceResponse,
    BankAccount,
    BankAccountListResponse,
    ChainData,
    Contact,
    ContactListResponse,
    CreateApprovalResponse,
    CreateAssetTransferRequest,
    CreateBankAccountRequest,
    CreateContactRequest,
    CreateContractCallTransactionRequest,
    CreateOffRampTransactionRequest,
    CreateOnRampTransactionRequest,
    CreateTradeQuoteRequest,
    CreateTradeTransactionRequest,
    CreateTransferTransactionRequest,
    CreateVaultRequest,
    DepositAddressResponse,
    DetailedBalance,
    DetailedBalanceResponse,
    EstimatedFeeResponse,
    EstimateFeeRequest,
    GetApprovalRequest,
    GetApprovalResponse,
    GetTradeQuoteResponse,
    RampQuoteRequest,
    RampQuoteResponse,
    ReplaceTransactionRequest,
    Transaction,
    TransactionCategory,
    TransactionListResponse,
    TransactionSubCategory,
    UpdateContactRequest,
    UpdateContactResponse,
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
        limit: Optional[int] = 20,
        cursor: Optional[str] = None,
    ) -> TransactionListResponse:
        query_params = ""
        if params:
            query_params = "&".join([f"{k}={v}" for k, v in params.items()])

        url = f"/api/external/transactions/?limit={limit}&cursor={cursor or ''}"

        if query_params:
            url += f"&{query_params}"

        return from_dict(
            TransactionListResponse,
            self.get(url),
        )

    def get_transaction_by_id(self, transaction_id: str) -> Transaction:
        return from_dict(
            Transaction, self.get(f"/api/external/transactions/{transaction_id}/")
        )

    def initiate_change_approval_action(
        self, request: GetApprovalRequest
    ) -> CreateApprovalResponse:
        data = {
            "entityId": request.entityId,
        }
        # This will fetch the approval message for the change request entity and user
        response = from_dict(
            GetApprovalResponse,
            self.get(
                "/api/external/change_requests/approvals/approval_message/", params=data
            ),
        )
        # This will sign the  message and take the action given by user on change request
        # reason is optional field if someone wants to set the field
        entity_approval_request = {
            "entityId": request.entityId,
            "message": response.message,
            "signature": self.signature_service.sign(
                response.message.encode("utf-8")
            ).hex(),
            "action": request.action,
            "reason": "ok",
        }
        return from_dict(
            CreateApprovalResponse,
            self.post(
                f"/api/external/change_requests/approvals/{response.approvalId}/action/",
                data=entity_approval_request,
            ),
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

    def get_trade_quote(self, request: CreateTradeQuoteRequest):
        if request.category == TransactionCategory.TRADE:
            trade_data: dict[str, Any] = {
                "source": (
                    {"type": "VAULT", "id": request.vaultId}
                    if request.vaultId
                    else None
                ),
                "fromAsset": request.fromAsset,
                "toAsset": request.toAsset,
                "fromAmount": request.fromAmount,
                "category": request.category,
                "paymentMethod": request.paymentMethod,
            }
            return from_dict(
                RampQuoteResponse,
                self.post("/api/external/transactions/quote/", data=trade_data),
            )
        swap_data: dict[str, Any] = {
            "vaultId": request.vaultId,
            "fromAsset": request.fromAsset,
            "toAsset": request.toAsset,
            "fromAmount": request.fromAmount,
            "blockChain": request.fromChain,
            "toBlockchain": request.toChain,
            "slippage": request.slippage,
            "expectedToAmount": request.expectedToAmount,
            "expiryInMinutes": request.expiryInMinutes,
            "category": request.category,
            "paymentMethod": request.paymentMethod,
        }
        return from_dict(
            GetTradeQuoteResponse,
            self.get("/api/external/transactions/trade_quote/", params=swap_data),
        )

    def create_trade_transaction(
        self, request: CreateTradeTransactionRequest
    ) -> Transaction:
        category = (
            request.category.value
            if isinstance(request.category, TransactionCategory)
            else request.category or "SWAP"
        )
        payload: dict[str, Any]
        if request.quoteId:
            payload = {
                "quoteId": request.quoteId,
                "category": category,
                "externalId": request.externalId,
                "operationMessage": request.operationMessage,
                "memo": request.memo,
            }
            if category == TransactionCategory.TRADE.value:
                return self.create_intent_transaction(payload)
        else:
            if not request.tradeRequestData or not request.tradeResponseData:
                raise ValueError(
                    "tradeRequestData and tradeResponseData are required "
                    "when quoteId is not provided"
                )
            payload = {
                "vaultId": request.vaultId,
                "tradeRequestData": asdict(request.tradeRequestData),
                "tradeResponseData": asdict(request.tradeResponseData),
                "category": category,
                "blockChain": request.tradeRequestData.blockChain,
                "externalId": request.externalId,
                "operationMessage": request.operationMessage,
                "memo": request.memo,
            }
        return from_dict(
            Transaction, self.post("/api/external/transactions/", data=payload)
        )

    def create_intent_transaction(self, payload: dict[str, Any]) -> Transaction:
        return from_dict(
            Transaction,
            self.post("/api/external/transactions/intent/create/", data=payload),
        )

    def mark_transaction_as_deposit_complete(self, transaction_id: str) -> Transaction:
        return from_dict(
            Transaction,
            self.post(
                "/api/external/transactions/mark_transaction_as_deposit_complete/",
                data={"transactionId": transaction_id},
            ),
        )

    def create_asset_transfer(self, request: CreateAssetTransferRequest) -> Transaction:
        vault_party = {"type": "VAULT", "id": request.vaultId}
        source = self._party_to_dict(request.source)
        destination = self._party_to_dict(request.destination)
        counterparty = self._party_to_dict(request.counterparty)
        sub_category = (
            request.subCategory.value
            if isinstance(request.subCategory, TransactionSubCategory)
            else request.subCategory
        )

        if source is None and destination is None:
            if sub_category == TransactionSubCategory.DEPOSIT.value:
                source = counterparty
                destination = vault_party
            elif sub_category == TransactionSubCategory.WITHDRAW.value:
                source = vault_party
                destination = counterparty

        data = {
            "quoteId": None,
            "category": request.category,
            "intent": {
                "source": source,
                "destination": destination,
                "fromAsset": request.asset,
                "fromAmount": request.amount,
                "toAsset": request.toAsset,
                "toAmount": request.toAmount,
                "fromChain": request.fromChain,
                "toChain": request.toChain,
                "fromPaymentRail": request.fromPaymentRail,
                "toPaymentRail": request.toPaymentRail,
            },
            "externalId": request.externalId,
            "memo": request.memo,
        }
        return self.create_intent_transaction(data)

    @classmethod
    def _party_to_dict(cls, party: Any) -> Optional[dict[str, Any]]:
        if party is None:
            return None
        return cls._compact_dict(asdict(party))

    @classmethod
    def _compact_dict(cls, value: Any) -> Any:
        if isinstance(value, dict):
            return {
                key: cls._compact_dict(child_value)
                for key, child_value in value.items()
                if child_value is not None
            }
        return value

    def get_ramp_quote(self, request: RampQuoteRequest) -> RampQuoteResponse:
        data = {
            "destination": asdict(request.destination) if request.destination else None,
            "source": asdict(request.source) if request.source else None,
            "fromAsset": request.fromAsset,
            "fromAmount": request.fromAmount,
            "fromChain": request.fromChain,
            "toAsset": request.toAsset,
            "toChain": request.toChain,
            "category": request.category,
        }
        return from_dict(
            RampQuoteResponse,
            self.post("/api/external/transactions/quote/", data=data),
        )

    def create_on_ramp_transaction(
        self, request: CreateOnRampTransactionRequest
    ) -> Transaction:
        data = {
            "destination": asdict(request.destination),
            "quoteId": request.quoteId,
            "category": TransactionCategory.ON_RAMP.value,
            "externalId": request.externalId,
            "memo": request.memo,
        }
        return from_dict(
            Transaction, self.post("/api/external/transactions/", data=data)
        )

    def create_off_ramp_transaction(
        self, request: CreateOffRampTransactionRequest
    ) -> Transaction:
        data = {
            "source": asdict(request.source),
            "destination": asdict(request.destination),
            "quoteId": request.quoteId,
            "category": TransactionCategory.OFF_RAMP.value,
            "externalId": request.externalId,
            "memo": request.memo,
        }
        return from_dict(
            Transaction, self.post("/api/external/transactions/", data=data)
        )

    def get_vaults(
        self,
        params: Optional[dict] = None,
        limit: Optional[int] = 20,
        cursor: Optional[str] = None,
    ) -> VaultListResponse:
        query_params = ""
        if params:
            query_params = "&".join([f"{k}={v}" for k, v in params.items()])

        url = f"/api/external/vaults/?limit={limit}&cursor={cursor or ''}"

        if query_params:
            url += f"&{query_params}"

        return from_dict(data_class=VaultListResponse, data=self.get(url))

    def get_vault_by_id(self, vault_id: str) -> Vault:
        return from_dict(Vault, self.get(f"/api/external/vaults/{vault_id}/"))

    def create_vault(self, request: CreateVaultRequest) -> Vault:
        return from_dict(
            Vault, self.post("/api/external/vaults/", data=request.__dict__)
        )

    def get_balances(self, vault_id: str) -> BalanceResponse:
        return self.get(f"/api/external/vaults/{vault_id}/balances/")

    def get_detailed_balances(
        self, vault_id: str, params: Optional[dict] = None
    ) -> DetailedBalanceResponse:
        response = self.get(
            f"/api/external/vaults/{vault_id}/detailed_balances/", params=params
        )
        return [from_dict(DetailedBalance, balance) for balance in response]

    def get_deposit_address(
        self, vault_id: str, currency: Optional[str] = None
    ) -> DepositAddressResponse:
        params = {"vaultId": vault_id}
        if currency:
            params["currency"] = currency

        response = self.get(
            "/api/external/transactions/get_deposit_address/", params=params
        )
        return from_dict(DepositAddressResponse, response)

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
        limit: Optional[int] = 20,
        cursor: Optional[str] = None,
    ) -> ContactListResponse:
        query_params = ""
        if params:
            query_params = "&".join([f"{k}={v}" for k, v in params.items()])

        url = f"/api/external/contacts/?limit={limit}&cursor={cursor or ''}"

        if query_params:
            url += f"&{query_params}"

        return from_dict(data_class=ContactListResponse, data=self.get(url))

    def get_contact_by_id(self, contact_id: str) -> Contact:
        return from_dict(Contact, self.get(f"/api/external/contacts/{contact_id}/"))

    def create_contact(self, request: CreateContactRequest) -> Contact:
        data = {
            "name": request.name,
            "address": request.address,
            "blockChain": request.chain,
            "tags": request.tags,
            "externalId": request.externalId,
            "assetList": request.assetList if request.assetList else [],
        }
        response = self.post("/api/external/contacts/", data=data)
        return from_dict(Contact, response)

    def update_contact(self, request: UpdateContactRequest) -> UpdateContactResponse:
        data = {
            "assetList": request.assetList if request.assetList else [],
        }
        response = self.put(f"/api/external/contacts/{request.id}/", data=data)
        return from_dict(UpdateContactResponse, response)

    # Bank Account Methods

    _BANK_DACITE_CFG = Config(cast=[str])

    def get_bank_accounts(
        self,
        params: Optional[dict] = None,
        limit: Optional[int] = 20,
        cursor: Optional[str] = None,
    ) -> BankAccountListResponse:
        query_params = ""
        if params:
            query_params = "&".join([f"{k}={v}" for k, v in params.items()])

        url = f"/api/external/bank_accounts/?limit={limit}&cursor={cursor or ''}"

        if query_params:
            url += f"&{query_params}"

        return from_dict(
            BankAccountListResponse, self.get(url), config=self._BANK_DACITE_CFG
        )

    def get_bank_account_by_id(self, bank_account_id: str) -> BankAccount:
        response = self.get(f"/api/external/bank_accounts/{bank_account_id}/")
        return from_dict(BankAccount, response, config=self._BANK_DACITE_CFG)

    def create_bank_account(self, request: CreateBankAccountRequest) -> BankAccount:
        response = self.post("/api/external/bank_accounts/", data=asdict(request))
        return from_dict(BankAccount, response, config=self._BANK_DACITE_CFG)

    def submit_bank_account_approval_action(
        self, request: GetApprovalRequest
    ) -> CreateApprovalResponse:
        return self.initiate_change_approval_action(request)
