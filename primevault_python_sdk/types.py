from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Union


# Enums
class TransferPartyType(str, Enum):
    CONTACT = "CONTACT"
    VAULT = "VAULT"
    EXTERNAL_ADDRESS = "EXTERNAL_ADDRESS"
    EXTERNAL_BANK_ACCOUNT = "EXTERNAL_BANK_ACCOUNT"
    BANK_ACCOUNT = "BANK_ACCOUNT"


class VaultType(str, Enum):
    EXCHANGE = "EXCHANGE"
    DEFAULT = "DEFAULT"
    GAS = "GAS"


class ContactStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    DECLINED = "DECLINED"


class TransactionType(str, Enum):
    INCOMING = "INCOMING"
    OUTGOING = "OUTGOING"


class ApprovalAction(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"
    # Alias of REJECT, kept so callers can mirror the JS SDK spelling.
    DECLINE = "reject"


class TransactionCategory(str, Enum):
    TRANSFER = "TRANSFER"
    SWAP = "SWAP"
    ON_RAMP = "ON_RAMP"
    OFF_RAMP = "OFF_RAMP"
    TOKEN_TRANSFER = "TOKEN_TRANSFER"  # nosec B105
    TOKEN_APPROVAL = "TOKEN_APPROVAL"  # nosec B105
    CONTRACT_CALL = "CONTRACT_CALL"
    STAKE = "STAKE"
    REVOKE_TOKEN_ALLOWANCE = "REVOKE_TOKEN_ALLOWANCE"  # nosec B105
    DELEGATE_RESOURCE = "DELEGATE_RESOURCE"


class TransactionSubCategory(str, Enum):
    INCOMING_TRANSFER = "INCOMING_TRANSFER"
    EXTERNAL_TRANSFER = "EXTERNAL_TRANSFER"
    INTERNAL_TRANSFER = "INTERNAL_TRANSFER"
    LIMIT_TRADE = "LIMIT_TRADE"
    MARKET_TRADE = "MARKET_TRADE"  # nosec
    APPROVE_TOKEN_ALLOWANCE = "APPROVE_TOKEN_ALLOWANCE"  # nosec
    CUSTOM_MESSAGE = "CUSTOM_MESSAGE"
    CONTRACT_CALL = "CONTRACT_CALL"
    STAKE = "STAKE"
    UNSTAKE = "UNSTAKE"
    CLAIM = "CLAIM"
    ON_RAMP = "ON_RAMP"
    OFF_RAMP = "OFF_RAMP"


class TransactionStatus(str, Enum):
    DRAFT = "DRAFT"
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    DECLINED = "DECLINED"
    SUBMITTED = "SUBMITTED"
    SIGNED = "SIGNED"
    WAITING_CONFIRMATION = "WAITING_CONFIRMATION"


class TransactionFeeTier(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class TransactionOperationType(str, Enum):
    DEPOSIT = "DEPOSIT"
    TRADE = "TRADE"
    TRANSFER = "TRANSFER"
    WITHDRAW = "WITHDRAW"


class TransactionOperationStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    CANCELLED = "CANCELLED"
    REVERSED = "REVERSED"


class PaymentMethod(str, Enum):
    US_ACH = "US_ACH"
    US_WIRE = "US_WIRE"
    SEPA = "SEPA"
    SWIFT = "SWIFT"
    BANK_TRANSFER = "BANK_TRANSFER"


class ResourceType(str, Enum):
    TRON_ENERGY = "TRON_ENERGY"
    TRON_BANDWIDTH = "TRON_BANDWIDTH"


class BankAccountStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    DECLINED = "DECLINED"


class WebhookEventType(str, Enum):
    TRANSACTION_STATUS_CHANGED = "TRANSACTION_STATUS_CHANGED"
    TRANSACTION_OPERATION_STATUS_CHANGED = "TRANSACTION_OPERATION_STATUS_CHANGED"


@dataclass
class TransactionCreationGasParams:
    feeTier: Optional[str] = None  # TransactionFeeTier


@dataclass
class TransactionCreationOptions:
    skipPreprocessSimulation: Optional[bool] = None


@dataclass
class FeePayer:
    id: str


@dataclass
class Asset:
    name: str
    symbol: str
    blockChain: str
    details: Any


@dataclass
class ChainData:
    value: str
    label: str


@dataclass
class BankDetails:
    bankAccountId: Optional[str] = None
    bankName: Optional[str] = None
    beneficiaryName: Optional[str] = None
    accountName: Optional[str] = None
    accountNumber: Optional[str] = None
    accountNumberMasked: Optional[str] = None
    routingNumber: Optional[str] = None
    paymentRail: Optional[str] = None
    bankAddress: Optional[str] = None
    swiftCode: Optional[str] = None
    swiftBic: Optional[str] = None
    iban: Optional[str] = None
    country: Optional[str] = None


@dataclass
class DepositInstructions:
    type: Optional[str] = None  # TransferPartyType
    paymentRail: Optional[str] = None
    bankDetails: Optional[BankDetails] = None
    asset: Optional[str] = None
    address: Optional[str] = None
    chain: Optional[str] = None


@dataclass
class TransferPartyData:
    type: str  # TransferPartyType
    id: Optional[str] = None
    subOrgId: Optional[str] = None
    name: Optional[str] = None
    address: Optional[str] = None
    provider: Optional[str] = None
    bankDetails: Optional[BankDetails] = None
    chain: Optional[str] = None
    paymentRail: Optional[str] = None


@dataclass
class Wallet:
    id: str
    blockchain: str
    address: Optional[str] = None
    publicKey: Optional[str] = None


@dataclass
class User:
    id: str
    firstName: Optional[str] = None
    email: Optional[str] = None
    lastName: Optional[str] = None


@dataclass
class Vault:
    id: str
    orgId: str
    vaultName: str
    vaultType: str  # VaultType
    createdAt: str
    updatedAt: str
    isDeleted: bool
    subOrgId: Optional[str] = None
    signers: Optional[List[User]] = None
    walletsGenerated: Optional[bool] = None
    wallets: Optional[List[Wallet]] = None
    viewers: Optional[List[User]] = None


@dataclass
class Contact:
    id: str
    orgId: str
    name: str
    blockChain: str
    address: str
    status: str  # ContactStatus
    createdAt: str
    updatedAt: str
    isDeleted: bool
    subOrgId: Optional[str] = None
    tags: Optional[List[str]] = None
    externalId: Optional[str] = None
    isSmartContractAddress: Optional[bool] = None
    isSanctioned: Optional[bool] = None
    createdById: Optional[str] = None
    assetList: Optional[List[str]] = None


@dataclass
class EVMOutput:
    returnData: str


@dataclass
class ICPOutput:
    certificate: str
    contentMap: str


# A transaction output can be one of these two
TransactionOutput = Union[EVMOutput, ICPOutput]


@dataclass
class TransactionSourceData:
    type: Optional[str] = None
    id: Optional[str] = None
    subOrgId: Optional[str] = None
    name: Optional[str] = None
    address: Optional[str] = None
    provider: Optional[str] = None
    bankDetails: Optional[BankDetails] = None
    chain: Optional[str] = None
    paymentRail: Optional[str] = None


@dataclass
class TransactionOperationBalanceChange:
    party: Optional[TransferPartyData]
    asset: str
    amount: str
    chain: Optional[str] = None
    paymentRail: Optional[str] = None


@dataclass
class TransactionOperationBalanceChanges:
    changes: List[TransactionOperationBalanceChange]


@dataclass
class TransactionOperation:
    source: Optional[TransferPartyData]
    destination: Optional[TransferPartyData]
    balanceChanges: Optional[TransactionOperationBalanceChanges]
    sequence: int
    type: str  # TransactionOperationType
    status: Optional[str] = None  # TransactionOperationStatus
    provider: Optional[str] = None


@dataclass
class RouteAccountData:
    provider: str
    id: str


@dataclass
class TransactionIntentRequest:
    source: Optional[TransferPartyData] = None
    destination: Optional[TransferPartyData] = None
    routeAccounts: Optional[List[RouteAccountData]] = None
    fromAsset: Optional[str] = None
    fromAmount: Optional[str] = None
    fromChain: Optional[str] = None
    fromPaymentRail: Optional[str] = None
    toAsset: Optional[str] = None
    toAmount: Optional[str] = None
    toChain: Optional[str] = None
    toPaymentRail: Optional[str] = None


@dataclass
class GetQuoteRequest:
    intent: TransactionIntentRequest
    subOrgId: Optional[str] = None


@dataclass
class TransactionExecuteIntentRequest:
    intent: Optional[TransactionIntentRequest] = None
    quoteId: Optional[str] = None
    externalId: Optional[str] = None
    memo: Optional[str] = None
    subOrgId: Optional[str] = None


@dataclass
class Transaction:
    id: str
    orgId: str
    vaultId: str
    amount: str
    status: str  # TransactionStatus
    transactionType: str  # TransactionType
    category: str  # TransactionCategory
    subCategory: str  # TransactionSubCategory
    createdAt: str
    updatedAt: str
    isDeleted: bool
    # Optional fields
    txHash: Optional[str] = None
    error: Optional[str] = None
    externalId: Optional[str] = None
    createdById: Optional[str] = None
    fees: Optional["Fees"] = None
    memo: Optional[str] = None
    txnSignature: Optional[str] = None
    txnSignatureData: Optional[dict] = None
    output: Optional[TransactionOutput] = None
    amountInUSD: Optional[str] = None
    nonce: Optional[int] = None
    dAppId: Optional[str] = None
    source: Optional[TransactionSourceData] = None
    destination: Optional[TransactionSourceData] = None
    intent: Optional[TransactionIntentRequest] = None
    quoteResponse: Optional["QuoteResponseItem"] = None
    depositInstructions: Optional[DepositInstructions] = None
    operations: Optional[List[TransactionOperation]] = None
    balanceChanges: Optional[TransactionOperationBalanceChanges] = None
    blockChain: Optional[str] = None
    toAddress: Optional[str] = None  # deprecated, use destination.address instead
    asset: Optional[str] = None
    toAddressName: Optional[str] = None  # deprecated, use destination.name instead
    toVaultId: Optional[str] = None  # deprecated, use destination.id instead
    sourceAddress: Optional[str] = None  # deprecated, use source.address instead


# Requests


@dataclass
class GetApprovalMessageResponse:
    message: str
    approvalId: str
    changeRequestId: Optional[str] = None
    entityId: Optional[str] = None


@dataclass
class GetApprovalRequest:
    entityId: str
    # approve/reject
    action: str
    reason: Optional[str] = "ok"


@dataclass
class ApprovalActionResponse:
    success: bool
    status: Optional[str] = None
    id: Optional[str] = None
    entityId: Optional[str] = None


@dataclass
class CreateTransferTransactionRequest:
    source: TransferPartyData
    destination: TransferPartyData
    amount: str
    asset: str
    chain: str
    gasParams: Optional[TransactionCreationGasParams] = None
    externalId: Optional[str] = None
    memo: Optional[str] = None
    feePayer: Optional[FeePayer] = None


@dataclass
class ReplaceTransactionRequest:
    transactionId: str


@dataclass
class EVMContractCallData:
    callData: str
    toAddress: Optional[str] = None


@dataclass
class ICPCanisterCallData:
    canisterId: str
    method: str
    arg: str


@dataclass
class RawSigningData:
    messageHex: str


@dataclass
class AlephiumContractCallData:
    method: str
    params: dict


ContractCallData = Union[
    EVMContractCallData, ICPCanisterCallData, RawSigningData, AlephiumContractCallData
]


@dataclass
class CreateContractCallTransactionRequest:
    vaultId: str
    chain: str
    amount: Optional[str] = None
    data: Optional[ContractCallData] = None
    externalId: Optional[str] = None
    gasParams: Optional[TransactionCreationGasParams] = None
    creationOptions: Optional[TransactionCreationOptions] = None


@dataclass
class EstimateFeeRequest:
    source: TransferPartyData
    destination: TransferPartyData
    amount: str
    asset: str
    chain: str


@dataclass
class CreateVaultRequest:
    vaultName: str
    subOrgId: Optional[str] = None
    templateId: Optional[str] = None
    chains: Optional[List[str]] = None
    testNetVault: Optional[bool] = None
    vaultGroupIds: Optional[List[str]] = None


@dataclass
class CreateContactRequest:
    name: str
    address: str
    chain: str
    subOrgId: Optional[str] = None
    tags: Optional[List[str]] = None
    externalId: Optional[str] = None
    assetList: Optional[List[str]] = None
    contactGroupIds: Optional[List[str]] = None


@dataclass
class UpdateContactRequest:
    id: str
    assetList: Optional[List[str]] = None
    contactGroupIds: Optional[List[str]] = None


@dataclass
class UpdateContactResponse:
    id: str
    name: str
    address: str
    blockChain: str
    tags: Optional[List[str]] = None
    externalId: Optional[str] = None
    assetList: Optional[List[str]] = None


# Fee and Quote Responses


@dataclass
class FeeData:
    expectedFeeInAsset: str
    asset: str
    expectedFeeInUSD: str
    baseFee: Optional[str] = None
    priorityFee: Optional[str] = None

    def __eq__(self, other):
        return (
            self.expectedFeeInAsset == other.expectedFeeInAsset
            and self.asset == other.asset
            and self.expectedFeeInUSD == other.expectedFeeInUSD
            and self.baseFee == other.baseFee
            and self.priorityFee == other.priorityFee
        )


@dataclass
class EstimatedFeeResponse:
    high: FeeData
    medium: FeeData
    low: FeeData


@dataclass
class Fees:
    amount: str
    asset: str
    amountInFiat: Optional[str] = None


@dataclass
class QuoteResponseItem:
    quoteId: str
    subOrgId: Optional[str] = None
    rate: Optional[str] = None
    fees: Optional[Fees] = None
    finalFromAmount: Optional[str] = None
    finalToAmount: Optional[str] = None
    sourceName: Optional[str] = None


@dataclass
class QuoteResponse:
    quotes: List[QuoteResponseItem]


@dataclass
class VaultListResponse:
    results: List[Vault]
    nextCursor: Optional[str] = None
    hasNext: Optional[bool] = None


@dataclass
class TransactionListResponse:
    results: List[Transaction]
    nextCursor: Optional[str] = None
    hasNext: Optional[bool] = None


@dataclass
class ActivityEventMetaData:
    platform: Optional[str] = None
    sourceIp: Optional[str] = None
    userAgent: Optional[str] = None


@dataclass
class ActivityEvent:
    id: str
    action: str
    outcome: Optional[str] = None
    activityLabel: Optional[str] = None
    createdAt: Optional[str] = None
    entityType: Optional[str] = None
    entityId: Optional[str] = None
    entityName: Optional[str] = None
    actorId: Optional[str] = None
    metaData: Optional[ActivityEventMetaData] = None
    schemaVersion: Optional[str] = None


@dataclass
class ActivityEventListResponse:
    results: List[ActivityEvent]
    nextCursor: Optional[str] = None
    hasNext: Optional[bool] = None


@dataclass
class ContactListResponse:
    results: List[Contact]
    nextCursor: Optional[str] = None
    hasNext: Optional[bool] = None


@dataclass
class BankAccount:
    id: str
    orgId: str
    orgEntityId: str
    createdAt: str
    updatedAt: str
    isDeleted: bool
    status: str  # BankAccountStatus
    subOrgId: Optional[str] = None
    createdById: Optional[str] = None
    accountNumber: Optional[str] = None
    accountName: Optional[str] = None
    routingNumber: Optional[str] = None
    clientBankAccountId: Optional[str] = None
    paymentMethod: Optional[str] = None  # PaymentMethod
    bankName: Optional[str] = None
    streetLine: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postalCode: Optional[str] = None
    country: Optional[str] = None


@dataclass
class BankAccountListResponse:
    results: List[BankAccount]
    nextCursor: Optional[str] = None
    hasNext: Optional[bool] = None


@dataclass
class CreateBankAccountRequest:
    subOrgId: Optional[str] = None
    accountNumber: Optional[str] = None
    accountName: Optional[str] = None
    routingNumber: Optional[str] = None
    clientBankAccountId: Optional[str] = None
    paymentMethod: Optional[str] = None  # PaymentMethod
    bankName: Optional[str] = None
    streetLine: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postalCode: Optional[str] = None
    country: Optional[str] = None


# Balance Response
BalanceResponse = Dict[str, Dict[str, str]]
"""
 asset: {chain: balance}
 Example:
    {
    "ETH": {
        "ETHEREUM": "1.00000000"
    },
    "USDC": {
        "POLYGON": "1.00000000"
        "ETHEREUM": "1.00000000"
        "ARBITRUM": "1.00000000"
    }
"""


@dataclass
class DetailedBalance:
    symbol: str
    balance: str
    name: Optional[str] = None
    chain: Optional[str] = None
    tokenAddress: Optional[str] = None


DetailedBalanceResponse = List[DetailedBalance]
"""
[
    {
        "chain": "ETHEREUM",
        "tokenAddress": "0x",
        "symbol": "USDC",
        "name": "USD Coin",
        "balance": "1.12"
    }
]
"""


# Resource delegation and staking


@dataclass
class DelegateResourceRequest:
    source: TransferPartyData
    destination: TransferPartyData
    asset: str
    chain: str
    amount: str
    resourceType: str  # ResourceType
    externalId: Optional[str] = None
    memo: Optional[str] = None


@dataclass
class StakeResourceRequest:
    source: TransferPartyData
    asset: str
    chain: str
    amount: str
    resourceType: Optional[str] = None  # ResourceType
    externalId: Optional[str] = None
    memo: Optional[str] = None


# Webhooks


@dataclass
class WebhookEventData:
    transaction: Optional[Transaction] = None
    transactionOperation: Optional[TransactionOperation] = None


@dataclass
class WebhookEvent:
    event: str  # WebhookEventType
    version: str  # "2.0.0"
    eventId: str
    data: WebhookEventData
