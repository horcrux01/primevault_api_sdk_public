from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Union


# Enums
class TransferPartyType(str, Enum):
    CONTACT = "CONTACT"
    VAULT = "VAULT"
    EXTERNAL_ADDRESS = "EXTERNAL_ADDRESS"


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


class TransactionCategory(str, Enum):
    TRANSFER = "TRANSFER"
    SWAP = "SWAP"


class TransactionSubCategory(str, Enum):
    INCOMING_TRANSFER = "INCOMING_TRANSFER"
    EXTERNAL_TRANSFER = "EXTERNAL_TRANSFER"
    INTERNAL_TRANSFER = "INTERNAL_TRANSFER"
    LIMIT_TRADE = "LIMIT_TRADE"
    MARKET_TRADE = "MARKET_TRADE"  # nosec
    APPROVE_TOKEN_ALLOWANCE = "APPROVE_TOKEN_ALLOWANCE"  # nosec


class TransactionStatus(str, Enum):
    DRAFT = "DRAFT"
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    DECLINED = "DECLINED"
    SUBMITTED = "SUBMITTED"
    WAITING_CONFIRMATION = "WAITING_CONFIRMATION"


class TransactionFeeTier(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass
class Asset:
    name: str
    symbol: str
    blockChain: str
    details: Any
    logoURL: Optional[str] = None
    tokenAddress: Optional[str] = None


@dataclass
class ChainData:
    value: str
    label: str
    logo: str


@dataclass
class TransferPartyData:
    type: str  # TransferPartyType
    id: Optional[str] = None
    value: Optional[str] = None


@dataclass
class Wallet:
    id: str
    blockchain: str
    address: str


@dataclass
class User:
    id: str
    firstName: str
    lastName: str
    email: str


@dataclass
class Vault:
    id: str
    orgId: str
    vaultName: str
    vaultType: str  # VaultType
    wallets: List[Wallet]
    signers: List[User]
    viewers: List[User]
    createdAt: str
    updatedAt: str
    isDeleted: bool
    walletsGenerated: Optional[bool] = None


@dataclass
class Contact:
    id: str
    orgId: str
    name: str
    blockChain: str
    address: str
    status: str  # ContactStatus
    isSmartContractAddress: bool
    createdById: str
    isSanctioned: bool
    createdAt: str
    updatedAt: str
    isDeleted: bool
    tags: Optional[List[str]] = None
    externalId: Optional[str] = None
    operationId: Optional[str] = None


@dataclass
class EVMOutput:
    returnData: Optional[str] = None


@dataclass
class ICPOutput:
    certificate: Optional[str] = None
    contentMap: Optional[str] = None


# A transaction output can be one of these two
TransactionOutput = Union[EVMOutput, ICPOutput]


@dataclass
class Transaction:
    id: str
    orgId: str
    vaultId: str
    amount: str
    blockChain: str
    status: str  # TransactionStatus
    toAddress: str
    transactionType: str  # TransactionType
    category: str  # TransactionCategory
    subCategory: str  # TransactionSubCategory
    createdAt: str
    updatedAt: str
    isDeleted: bool
    # Optional fields
    asset: Optional[str] = None
    toAddressName: Optional[str] = None
    createdById: Optional[str] = None
    txHash: Optional[str] = None
    error: Optional[str] = None
    toVaultId: Optional[str] = None
    externalId: Optional[str] = None
    gasParams: Optional[Dict[str, Any]] = None
    memo: Optional[str] = None
    sourceAddress: Optional[str] = None
    txnSignature: Optional[str] = None
    output: Optional[TransactionOutput] = None


# Requests


@dataclass
class CreateTransferTransactionRequest:
    source: TransferPartyData
    destination: TransferPartyData
    amount: str
    asset: str
    chain: str
    gasParams: Optional[Dict[str, Any]] = None
    externalId: Optional[str] = None
    isAutomation: Optional[bool] = None
    executeAt: Optional[str] = None
    memo: Optional[str] = None


@dataclass
class EVMContractCallData:
    callData: str
    toAddress: Optional[str] = None


@dataclass
class ICPCanisterCallData:
    canisterId: str
    method: str
    arg: str


# ContractCallData can be EVMContractCallData or ICPCanisterCallData
ContractCallData = Union[EVMContractCallData, ICPCanisterCallData]


@dataclass
class TransactionCreationGasParams:
    feeTier: Optional[str] = None  # TransactionFeeTier


@dataclass
class CreateContractCallTransactionRequest:
    vaultId: str
    chain: str
    amount: Optional[str] = None
    messageHex: Optional[str] = None
    toAddress: Optional[str] = None
    data: Optional[ContractCallData] = None
    externalId: Optional[str] = None
    gasParams: Optional[TransactionCreationGasParams] = None


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
    defaultTransferSpendLimit: Dict[str, Any]
    defaultTradeSpendLimit: Dict[str, Any]


@dataclass
class TradeQuoteRequest:
    vaultId: str
    fromAsset: str
    fromAmount: str
    fromChain: str
    toAsset: str
    toChain: str
    slippage: str


@dataclass
class CreateContactRequest:
    name: str
    address: str
    chain: str
    tags: Optional[List[str]] = None
    externalId: Optional[str] = None


# Fee and Quote Responses


@dataclass
class FeeData:
    expectedFeeInAsset: str
    asset: str
    expectedFeeInUSD: str
    baseFee: Optional[str] = None
    priorityFee: Optional[str] = None


@dataclass
class EstimatedFeeResponse:
    high: FeeData
    medium: FeeData
    low: FeeData


@dataclass
class TradeQuoteResponseData:
    finalToAmount: str
    finalToAmountUSD: str
    sourceName: str
    feeInUSD: str
    autoSlippage: str
    unitToAssetAmount: Optional[str] = None
    quotesValidTill: Optional[str] = None
    estCompletionTimeInSec: Optional[str] = None


@dataclass
class CreateTradeTransactionRequest:
    vaultId: str
    tradeRequestData: TradeQuoteRequest
    tradeResponseData: TradeQuoteResponseData
    externalId: Optional[str] = None
    memo: Optional[str] = None


@dataclass
class TradeQuoteRequestData:
    fromAsset: str
    fromAmount: str
    blockChain: str  # fromChain
    toAsset: str
    toBlockchain: str  # toChain
    slippage: str
    fromAmountUSD: Optional[str] = None
    destinationAddress: Optional[str] = None


@dataclass
class GetTradeQuoteResponse:
    tradeRequestData: TradeQuoteRequestData
    tradeResponseDataList: List[TradeQuoteResponseData]


@dataclass
class VaultListResponse:
    results: List[Vault]
    count: int
    previous: Optional[str] = None
    next: Optional[str] = None


@dataclass
class TransactionListResponse:
    results: List[Transaction]
    count: int
    previous: Optional[str] = None
    next: Optional[str] = None


@dataclass
class ContactListResponse:
    results: List[Contact]
    count: int
    previous: Optional[str] = None
    next: Optional[str] = None


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
