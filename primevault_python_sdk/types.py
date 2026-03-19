import datetime
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Union


# Enums
class TransferPartyType(str, Enum):
    CONTACT = "CONTACT"
    VAULT = "VAULT"
    EXTERNAL_ADDRESS = "EXTERNAL_ADDRESS"
    EXTERNAL_BANK_ACCOUNT = "EXTERNAL_BANK_ACCOUNT"


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


class TransactionStatus(str, Enum):
    DRAFT = "DRAFT"
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    DECLINED = "DECLINED"
    SUBMITTED = "SUBMITTED"
    WAITING_CONFIRMATION = "WAITING_CONFIRMATION"


class PaymentMethod(str, Enum):
    US_ACH = "US_ACH"
    US_WIRE = "US_WIRE"
    SEPA = "SEPA"
    SWIFT = "SWIFT"
    BANK_TRANSFER = "BANK_TRANSFER"


class TransactionFeeTier(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


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
    signers: List[User]
    createdAt: str
    updatedAt: str
    isDeleted: bool
    walletsGenerated: Optional[bool] = None
    wallets: Optional[List[Wallet]] = None
    viewers: Optional[List[User]] = None
    templateId: Optional[str] = None
    totalBalanceInCurrency: Optional[str] = None


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
class BankDetails:
    bankName: Optional[str] = None
    beneficiaryName: Optional[str] = None
    accountNumberMasked: Optional[str] = None
    iban: Optional[str] = None
    swiftBic: Optional[str] = None
    routingNumber: Optional[str] = None
    paymentRail: Optional[str] = None
    currency: Optional[str] = None
    country: Optional[str] = None
    bankAddress: Optional[str] = None


@dataclass
class TransactionSourceData:
    type: Optional[str] = None
    id: Optional[str] = None
    name: Optional[str] = None
    address: Optional[str] = None
    exchange: Optional[str] = None
    bank: Optional[BankDetails] = None


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
    blockChain: Optional[str] = None
    toAddress: Optional[str] = None
    toBlockChain: Optional[str] = None
    asset: Optional[str] = None
    toAsset: Optional[str] = None
    finalToAmount: Optional[str] = None
    toAddressName: Optional[str] = None
    createdById: Optional[str] = None
    txHash: Optional[str] = None
    error: Optional[str] = None
    toVaultId: Optional[str] = None
    externalId: Optional[str] = None
    gasParams: Optional[Dict[str, Any]] = None
    memo: Optional[str] = None
    source: Optional[TransactionSourceData] = None
    destination: Optional[TransferPartyData] = None
    sourceAddress: Optional[str] = None
    txnSignature: Optional[str] = None
    txnSignatureData: Optional[dict] = None
    output: Optional[TransactionOutput] = None
    dAppId: Optional[str] = None
    operationId: Optional[str] = None
    amountInUSD: Optional[str] = None
    nonce: Optional[int] = None
    rampRequestData: Optional[Dict[str, Any]] = None
    rampResponseData: Optional[Dict[str, Any]] = None


# Requests


@dataclass
class GetApprovalResponse:
    message: str
    approvalId: str


@dataclass
class GetApprovalRequest:
    entityId: str
    # approve/reject
    action: str


@dataclass
class CreateApprovalResponse:
    success: bool


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
    templateId: Optional[str] = None
    chains: Optional[List[str]] = None
    testNetVault: Optional[bool] = None


@dataclass
class CreateTradeQuoteRequest:
    vaultId: str
    fromAsset: str
    fromAmount: str
    toAsset: str
    category: Optional[str] = None
    paymentMethod: Optional[str] = None
    fromChain: Optional[str] = None
    toChain: Optional[str] = None
    slippage: Optional[str] = None
    expectedToAmount: Optional[str] = None
    expiryInMinutes: Optional[int] = None


@dataclass
class CreateContactRequest:
    name: str
    address: str
    chain: str
    tags: Optional[List[str]] = None
    externalId: Optional[str] = None
    assetList: Optional[List[str]] = None


@dataclass
class UpdateContactRequest:
    id: str
    assetList: Optional[List[str]] = None


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
class TradeQuoteFee:
    amount: Optional[str] = None
    asset: Optional[str] = None


@dataclass
class TradeQuoteDictData:
    quoteId: Optional[str] = None
    fromAmount: Optional[str] = None
    toAmount: Optional[str] = None
    fromAsset: Optional[str] = None
    toAsset: Optional[str] = None
    fees: Optional[TradeQuoteFee] = None


@dataclass
class TradeQuoteResponseData:
    finalToAmount: str
    quoteResponseDict: Union[str, Dict[str, Any]]
    handler: str
    sourceName: str
    handlerCategory: Optional[str] = None
    unitToAssetAmount: Optional[str] = None
    approvedFinalToAmount: Optional[str] = None
    quotesValidTill: Optional[Union[datetime.datetime, str]] = None
    feeInUSD: Optional[str] = None
    finalToAmountUSD: Optional[str] = None
    stepsData: Optional[list] = None
    sourceLogoURL: Optional[str] = None
    estCompletionTimeInSec: Optional[int] = None
    autoSlippage: Optional[str] = None
    minimumToAmount: Optional[str] = None
    fees: Optional[TradeQuoteFee] = None
    quoteId: Optional[str] = None
    fromAmount: Optional[str] = None
    paymentMethod: Optional[str] = None


@dataclass
class TradeQuoteRequestData:
    fromAsset: str
    fromAmount: str
    toAsset: str
    slippage: Optional[str] = None
    blockChain: Optional[str] = None
    toBlockchain: Optional[str] = None
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
class RampQuoteRequest:
    fromAsset: str
    fromAmount: str
    toAsset: str
    category: str  # TransactionCategory.ON_RAMP or OFF_RAMP
    source: Optional[TransferPartyData] = None
    destination: Optional[TransferPartyData] = None
    fromChain: Optional[str] = None
    toChain: Optional[str] = None
    paymentMethod: Optional[str] = None  # PaymentMethod value


@dataclass
class RampQuoteResponseFees:
    amount: Optional[str] = None
    asset: Optional[str] = None


@dataclass
class RampQuoteResponse:
    finalToAmount: str
    quoteId: str
    fees: RampQuoteResponseFees
    sourceName: str
    quoteResponseDict: Optional[Dict[str, Any]] = None


@dataclass
class CreateOnRampTransactionRequest:
    destination: TransferPartyData
    rampRequestData: Dict[str, Any]
    rampResponseData: Dict[str, Any]
    externalId: Optional[str] = None
    memo: Optional[str] = None


@dataclass
class CreateOffRampTransactionRequest:
    source: TransferPartyData
    destination: TransferPartyData
    rampRequestData: Dict[str, Any]
    rampResponseData: Dict[str, Any]
    externalId: Optional[str] = None
    memo: Optional[str] = None


@dataclass
class CreateRampTransactionRequest:
    vaultId: str
    tradeRequestData: TradeQuoteRequestData
    tradeResponseData: TradeQuoteResponseData
    category: str = TransactionCategory.ON_RAMP.value
    externalId: Optional[str] = None
    operationMessage: Optional[str] = None
    memo: Optional[str] = None
    paymentMethod: Optional[str] = None
    toBlockChain: Optional[str] = None


@dataclass
class GetTradeQuoteResponse:
    tradeRequestData: TradeQuoteRequestData
    tradeResponseDataList: List[TradeQuoteResponseData]


@dataclass
class DepositAddress:
    address: Optional[str] = None
    id: Optional[Union[int, str]] = None
    label: Optional[str] = None
    chain: Optional[str] = None
    chainName: Optional[str] = None
    asset: Optional[str] = None


@dataclass
class DepositAddressResponse:
    addresses: List[DepositAddress]


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


@dataclass
class DetailedBalance:
    symbol: str
    balance: str
    name: Optional[str] = None
    chain: Optional[str] = None
    tokenAddress: Optional[str] = None
    balanceInUSD: Optional[str] = None
    price: Optional[str] = None


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
