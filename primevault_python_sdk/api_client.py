from dataclasses import asdict
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlencode

from dacite import Config, from_dict

from primevault_python_sdk.base_api_client import BaseAPIClient
from primevault_python_sdk.types import (
    ActivityEventListResponse,
    ApprovalAction,
    ApprovalActionResponse,
    Asset,
    BalanceResponse,
    BankAccount,
    BankAccountListResponse,
    ChainData,
    Contact,
    ContactListResponse,
    CreateBankAccountRequest,
    CreateContactRequest,
    CreateContractCallTransactionRequest,
    CreateTransferTransactionRequest,
    CreateVaultRequest,
    DelegateResourceRequest,
    DetailedBalance,
    DetailedBalanceResponse,
    EstimatedFeeResponse,
    EstimateFeeRequest,
    GetApprovalMessageResponse,
    GetApprovalRequest,
    GetQuoteRequest,
    QuoteResponse,
    ReplaceTransactionRequest,
    StakeResourceRequest,
    Transaction,
    TransactionCategory,
    TransactionExecuteIntentRequest,
    TransactionIntentRequest,
    TransactionListResponse,
    TransactionStatus,
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

    def get_activity_events(
        self,
        params: Optional[dict] = None,
        limit: Optional[int] = 20,
        cursor: Optional[str] = None,
    ) -> ActivityEventListResponse:
        query: Dict[str, str] = {"limit": str(limit), "cursor": cursor or ""}
        if params:
            query.update(params)

        url = f"/api/external/activity/events/?{urlencode(query)}"

        return from_dict(
            ActivityEventListResponse,
            self.get(url),
        )

    def get_transaction_by_id(self, transaction_id: str) -> Transaction:
        return from_dict(
            Transaction, self.get(f"/api/external/transactions/{transaction_id}/")
        )

    def get_change_approval_message(self, entity_id: str) -> GetApprovalMessageResponse:
        data = {
            "entityId": entity_id,
        }
        return from_dict(
            GetApprovalMessageResponse,
            self.get(
                "/api/external/change_requests/approvals/approval_message/", params=data
            ),
        )

    def submit_change_approval_action(
        self,
        approval_id: str,
        action: str,
        signature_hex: str,
        reason: Optional[str] = "ok",
    ) -> ApprovalActionResponse:
        approval_request = {
            "action": action,
            "signature": signature_hex,
        }
        if reason is not None:
            approval_request["reason"] = reason

        return from_dict(
            ApprovalActionResponse,
            self.post(
                f"/api/external/change_requests/approvals/{approval_id}/action/",
                data=approval_request,
            ),
        )

    def approve_change_request(
        self,
        request: GetApprovalRequest,
    ) -> ApprovalActionResponse:
        """Approve or reject the pending change request for any supported entity."""
        approval_message = self.get_change_approval_message(request.entityId)
        signature_hex = self.signature_service.sign(
            approval_message.message.encode("utf-8")
        ).hex()
        return self.submit_change_approval_action(
            approval_id=approval_message.approvalId,
            action=request.action,
            signature_hex=signature_hex,
            reason=request.reason,
        )

    def _approve_pending_transaction_change_request(
        self, transaction: Transaction
    ) -> Transaction:
        if transaction.status != TransactionStatus.PENDING.value:
            return transaction

        self.approve_change_request(
            GetApprovalRequest(
                entityId=transaction.id,
                action=ApprovalAction.APPROVE.value,
            )
        )
        return self.get_transaction_by_id(transaction.id)

    def estimate_fee(self, request: EstimateFeeRequest) -> EstimatedFeeResponse:
        data = {
            "source": asdict(request.source),
            "destination": asdict(request.destination),
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
            "source": asdict(request.source),
            "destination": asdict(request.destination),
            "amount": request.amount,
            "asset": request.asset,
            "blockChain": request.chain,
            "category": "TRANSFER",
            "gasParams": gas_params,
            "externalId": request.externalId,
            "memo": request.memo,
            "feePayer": request.feePayer and request.feePayer.__dict__,
        }
        response = self.post("/api/external/transactions/", data=data)
        return from_dict(Transaction, response)

    def create_transaction_with_approval(
        self, request: CreateTransferTransactionRequest
    ) -> Transaction:
        """Create a transfer transaction and approve it in one call.

        The transaction is only signed for approval when it lands in PENDING,
        so orgs whose policy approves on create get the created transaction back
        untouched.
        """
        transaction = self.create_transfer_transaction(request)
        return self._approve_pending_transaction_change_request(transaction)

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

    @staticmethod
    def _transaction_intent_data(request: TransactionIntentRequest) -> dict[str, Any]:
        return {
            "source": asdict(request.source) if request.source else None,
            "destination": asdict(request.destination) if request.destination else None,
            "fromAsset": request.fromAsset,
            "toAsset": request.toAsset,
            "fromAmount": request.fromAmount,
            "fromChain": request.fromChain,
            "fromPaymentRail": request.fromPaymentRail,
            "toAmount": request.toAmount,
            "toChain": request.toChain,
            "toPaymentRail": request.toPaymentRail,
        }

    @staticmethod
    def _transaction_execute_intent_request_data(
        request: TransactionExecuteIntentRequest,
    ) -> dict[str, Any]:
        data = {
            "intent": (
                APIClient._transaction_intent_data(request.intent)
                if request.intent
                else None
            ),
            "quoteId": request.quoteId,
            "externalId": request.externalId,
            "memo": request.memo,
        }
        if request.subOrgId is not None:
            data["subOrgId"] = request.subOrgId
        return data

    def get_quote(self, request: GetQuoteRequest) -> QuoteResponse:
        intent_data = self._transaction_intent_data(request.intent)
        if request.intent.routeAccounts is not None:
            intent_data["routeAccounts"] = [
                asdict(route_account) for route_account in request.intent.routeAccounts
            ]

        data: dict[str, Any] = {"intent": intent_data}
        if request.subOrgId is not None:
            data["subOrgId"] = request.subOrgId
        response = self.post(
            "/api/external/transactions/quote/",
            data=data,
        )
        return from_dict(QuoteResponse, response)

    def create_transaction_from_intent(
        self, request: TransactionExecuteIntentRequest
    ) -> Transaction:
        data = self._transaction_execute_intent_request_data(request)
        transaction = from_dict(
            Transaction,
            self.post("/api/external/transactions/intent/create/", data=data),
        )
        return self._approve_pending_transaction_change_request(transaction)

    def mark_deposit_done(self, transactionId: str) -> Transaction:
        return from_dict(
            Transaction,
            self.post(
                "/api/external/transactions/mark_deposit_done/",
                data={"transactionId": transactionId},
            ),
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

    def create_vault_approval(self, vault: Vault) -> Vault:
        self.approve_change_request(
            GetApprovalRequest(
                entityId=vault.id,
                action=ApprovalAction.APPROVE.value,
            )
        )
        return self.get_vault_by_id(vault.id)

    def create_vault_with_approval(self, request: CreateVaultRequest) -> Vault:
        vault = self.create_vault(request)
        return self.create_vault_approval(vault)

    def get_balances(self, vault_id: str) -> BalanceResponse:
        return self.get(f"/api/external/vaults/{vault_id}/balances/")

    def get_detailed_balances(
        self, vault_id: str, params: Optional[dict] = None
    ) -> DetailedBalanceResponse:
        response = self.get(
            f"/api/external/vaults/{vault_id}/detailed_balances/", params=params
        )
        return [from_dict(DetailedBalance, balance) for balance in response]

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
            "subOrgId": request.subOrgId,
            "address": request.address,
            "blockChain": request.chain,
            "tags": request.tags,
            "externalId": request.externalId,
            "assetList": request.assetList if request.assetList else [],
            "contactGroupIds": request.contactGroupIds,
        }
        response = self.post("/api/external/contacts/", data=data)
        return from_dict(Contact, response)

    def create_contact_approval(
        self, contact: Union[Contact, UpdateContactResponse]
    ) -> Contact:
        self.approve_change_request(
            GetApprovalRequest(
                entityId=contact.id,
                action=ApprovalAction.APPROVE.value,
            )
        )
        return self.get_contact_by_id(contact.id)

    def create_contact_with_approval(self, request: CreateContactRequest) -> Contact:
        contact = self.create_contact(request)
        return self.create_contact_approval(contact)

    def update_contact(self, request: UpdateContactRequest) -> UpdateContactResponse:
        data = {
            "assetList": request.assetList if request.assetList else [],
            "contactGroupIds": request.contactGroupIds,
        }
        response = self.put(f"/api/external/contacts/{request.id}/", data=data)
        return from_dict(UpdateContactResponse, response)

    def update_contact_with_approval(self, request: UpdateContactRequest) -> Contact:
        updated = self.update_contact(request)
        return self.create_contact_approval(updated)

    def delegate_resource(self, request: DelegateResourceRequest) -> Transaction:
        data = {
            "source": asdict(request.source),
            "destination": asdict(request.destination),
            "asset": request.asset,
            "blockChain": request.chain,
            "amount": request.amount,
            "resourceType": request.resourceType,
            "externalId": request.externalId,
            "memo": request.memo,
            "category": TransactionCategory.DELEGATE_RESOURCE.value,
        }
        return from_dict(
            Transaction, self.post("/api/external/transactions/", data=data)
        )

    def stake_resource(self, request: StakeResourceRequest) -> Transaction:
        data = {
            "source": asdict(request.source),
            "asset": request.asset,
            "blockChain": request.chain,
            "amount": request.amount,
            "resourceType": request.resourceType,
            "category": TransactionCategory.STAKE.value,
            "externalId": request.externalId,
            "memo": request.memo,
        }
        return from_dict(
            Transaction, self.post("/api/external/transactions/", data=data)
        )

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

    def create_bank_account_approval(self, bank_account: BankAccount) -> BankAccount:
        self.approve_change_request(
            GetApprovalRequest(
                entityId=bank_account.id,
                action=ApprovalAction.APPROVE.value,
            )
        )
        return self.get_bank_account_by_id(bank_account.id)

    def create_bank_account_with_approval(
        self, request: CreateBankAccountRequest
    ) -> BankAccount:
        bank_account = self.create_bank_account(request)
        return self.create_bank_account_approval(bank_account)
