import datetime
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
class TransactionCreationGasParams:
    feeTier: Optional[str] = None  # TransactionFeeTier


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
    address: Optional[str] = None


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
    signers: List[User]
    createdAt: str
    updatedAt: str
    isDeleted: bool
    walletsGenerated: Optional[bool] = None
    wallets: Optional[List[Wallet]] = None
    viewers: Optional[List[User]] = None
    templateId: Optional[str] = None


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
    tags: Optional[List[str]] = None
    externalId: Optional[str] = None
    operationId: Optional[str] = None
    isSmartContractAddress: Optional[bool] = None
    isSanctioned: Optional[bool] = None
    createdById: Optional[str] = None


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
class Transaction:
    id: str
    orgId: str
    vaultId: str
    amount: str
    blockChain: str
    status: str  # TransactionStatus
    transactionType: str  # TransactionType
    category: str  # TransactionCategory
    subCategory: str  # TransactionSubCategory
    createdAt: str
    updatedAt: str
    isDeleted: bool
    # Optional fields
    toAddress: Optional[str] = None
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
    dAppId: Optional[str] = None
    operationId: Optional[str] = None


# Requests


@dataclass
class CreateTransferTransactionRequest:
    source: TransferPartyData
    destination: TransferPartyData
    amount: str
    asset: str
    chain: str
    gasParams: Optional[TransactionCreationGasParams] = None
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


@dataclass
class RawSigningData:
    messageHex: str


ContractCallData = Union[EVMContractCallData, ICPCanisterCallData, RawSigningData]


@dataclass
class CreateContractCallTransactionRequest:
    vaultId: str
    chain: str
    amount: Optional[str] = None
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
    templateId: Optional[str] = None
    defaultTransferSpendLimit: Optional[Dict[str, Any]] = None
    customTransferSpendLimits: Optional[List[Dict[str, Any]]] = None
    defaultTradeSpendLimit: Optional[Dict[str, Any]] = None
    customTradeSpendLimits: Optional[List[Dict[str, Any]]] = None
    vaultSigners: Optional[List[str]] = None
    vaultViewers: Optional[List[str]] = None


@dataclass
class CreateTradeQuoteRequest:
    vaultId: str
    fromAsset: str
    fromAmount: str
    fromChain: str
    toAsset: str
    toChain: str
    slippage: Optional[str] = None


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
class TradeQuoteResponseData:
    finalToAmount: str
    quoteResponseDict: str
    handler: str
    sourceName: str
    handlerCategory: Optional[str] = None
    unitToAssetAmount: Optional[str] = None
    approvedFinalToAmount: Optional[str] = None
    quotesValidTill: Optional[datetime.datetime] = None
    feeInUSD: Optional[str] = None
    finalToAmountUSD: Optional[str] = None
    stepsData: Optional[list] = None
    sourceLogoURL: Optional[str] = None
    estCompletionTimeInSec: Optional[int] = None
    autoSlippage: Optional[str] = None
    minimumToAmount: Optional[str] = None


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
    chainId: Optional[str] = None
    fromAssetLogoURL: Optional[str] = None
    toAssetLogoURL: Optional[str] = None
    expectedToAmountUSD: Optional[str] = None
    expiryInMinutes: Optional[int] = None


@dataclass
class CreateTradeTransactionRequest:
    vaultId: str
    tradeRequestData: TradeQuoteRequestData
    tradeResponseData: TradeQuoteResponseData
    externalId: Optional[str] = None
    memo: Optional[str] = None


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
