"""
EVM Transaction Handler Module

This module provides functionality for creating, signing, and relaying EVM-compatible blockchain transactions
using PrimeVault for secure transaction signing.

web3==6.1.0
"""

import time
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from eth_account._utils.legacy_transactions import (
    encode_transaction,
    serializable_unsigned_transaction_from_dict,
)
from eth_account.datastructures import SignedTransaction
from eth_utils import keccak
from hexbytes import HexBytes
from web3 import Web3
from web3.exceptions import TimeExhausted

from primevault_python_sdk.api_client import APIClient
from primevault_python_sdk.types import (
    CreateContractCallTransactionRequest,
    RawSigningData,
    Wallet,
)

# from web3.middleware import geth_poa_middleware


def parse_transaction_receipt(txn_receipt: Dict[str, Any]) -> Tuple[str, Decimal]:
    """
    Parse an EVM transaction receipt and determine its status and gas fee.

    Args:
        txn_receipt: Transaction receipt dictionary from web3

    Returns:
        Tuple containing:
          - Transaction status: "COMPLETED", "FAILED", or "SUBMITTED"
          - Gas fee in ETH as Decimal
    """
    gas_fee = Decimal(0)

    # Calculate gas fee if available
    if txn_receipt.get("effectiveGasPrice") and txn_receipt.get("gasUsed"):
        total_fee = int(txn_receipt["effectiveGasPrice"]) * int(txn_receipt["gasUsed"])
        gas_fee = Decimal(Web3.from_wei(total_fee, "ether"))

    # Determine transaction status
    if int(txn_receipt["status"]) == 1:
        return "COMPLETED", gas_fee
    elif int(txn_receipt["status"]) == 0:
        return "FAILED", gas_fee
    else:
        return "SUBMITTED", gas_fee


def relay_signed_transaction(
    web3_client: Web3, eth_signed_transaction: SignedTransaction
) -> Tuple[Optional[str], Optional[Decimal]]:
    """
    Relay a signed transaction to the blockchain and wait for its completion.

    Args:
        web3_client: Initialized Web3 client
        eth_signed_transaction: Signed transaction object

    Returns:
        Tuple containing:
          - Transaction status: "COMPLETED", "FAILED", or None if timeout
          - Gas fee in ETH as Decimal, or None if transaction didn't complete
    """
    # Send the transaction to the network
    transaction_hash = web3_client.eth.send_raw_transaction(
        eth_signed_transaction.rawTransaction
    )

    # Poll for transaction receipt
    wait_attempts = 30
    status, fee = None, None

    while wait_attempts > 0:
        try:
            transaction_receipt = web3_client.eth.wait_for_transaction_receipt(
                transaction_hash, poll_latency=5.0
            )
            print(f"Transaction receipt: {transaction_receipt}")

            status, fee = parse_transaction_receipt(transaction_receipt)
            if status in ["COMPLETED", "FAILED"]:
                print(f"Transaction {status.lower()} with gas fee: {fee}")
                return status, fee

        except TimeExhausted:
            print("Transaction is not yet mined")
        except Exception as e:
            print(f"Error waiting for transaction: {e}")

        time.sleep(10)
        wait_attempts -= 1

    return status, fee


def create_evm_transaction_dict(
    web3_client: Web3, wallet: Wallet, contract_address: str, call_data: str
) -> Dict[str, Any]:
    """
    Create a transaction dictionary for an EVM contract call.

    Args:
        web3_client: Initialized Web3 client
        wallet: Wallet object containing the sender's address
        contract_address: Contract address to interact with
        call_data: ABI-encoded function call data

    Returns:
        Transaction dictionary ready for signing
    """
    # Estimate gas required for the transaction
    gas_estimate = web3_client.eth.estimate_gas(
        {"to": contract_address, "data": call_data}
    )

    # Calculate gas prices (for EIP-1559 transactions)
    max_priority_fee = web3_client.eth.max_priority_fee
    max_fee_per_gas = (
        2 * web3_client.eth.get_block("latest")["baseFeePerGas"] + max_priority_fee
    )

    # Get the next nonce for this wallet
    nonce = web3_client.eth.get_transaction_count(wallet.address)

    # Return the complete transaction dictionary
    return {
        "to": contract_address,
        "data": call_data,
        "gas": gas_estimate,
        "maxPriorityFeePerGas": max_priority_fee,
        "maxFeePerGas": max_fee_per_gas,
        "nonce": nonce,
        "type": 2,  # EIP-1559 transaction type
        "chainId": 1,  # Chain ID (137 for Polygon), 1 for Ethereum
        "value": 0,  # Amount of ETH to send (0 for pure contract calls)
    }


def sign_and_relay_evm_contract_calls(
    api_client: APIClient,
    vault_id: str,
    chain: str,
    contract_address: str,
    call_data: str,
    rpc_url: str,
) -> Tuple[Optional[str], Optional[Decimal]]:
    """
    Sign and relay a contract call transaction using PrimeVault for secure signing.

    This function:
    1. Prepares the transaction parameters
    2. Gets the transaction hash for signing
    3. Sends the hash to PrimeVault for secure signing
    4. Constructs the final signed transaction
    5. Relays the transaction to the blockchain

    Args:
        api_client: PrimeVault API client object
        vault_id: PrimeVault vault ID containing the signing wallet
        chain: Blockchain network identifier (e.g., "ETHEREUM", "POLYGON", etc.)
        contract_address: Contract address to interact with
        call_data: ABI-encoded function call data
        rpc_url: RPC URL for the blockchain node

    Returns:
        Tuple containing:
          - Transaction status: "COMPLETED", "FAILED", or None if timeout
          - Gas fee in ETH as Decimal, or None if transaction didn't complete
    """
    # Get wallet from PrimeVault vault
    vault = api_client.get_vault_by_id(vault_id)
    wallets: List[Wallet] = vault.wallets or []
    wallet = next(w for w in wallets if w.blockchain == chain)

    # Initialize web3 client with PoA middleware for networks like Polygon
    web3_client = Web3(Web3.HTTPProvider(rpc_url))
    # web3_client.middleware_onion.inject(geth_poa_middleware, layer=0)

    # Ensure contract address is in checksum format
    contract_address = Web3.to_checksum_address(contract_address)

    # Create transaction dictionary
    transaction_data = create_evm_transaction_dict(
        web3_client, wallet, contract_address, call_data
    )
    print(f"Transaction data: {transaction_data}")

    # Prepare transaction for signing
    unsigned_transaction = serializable_unsigned_transaction_from_dict(transaction_data)
    unsigned_transaction_message_hex = unsigned_transaction.hash().hex()

    # Request signature from PrimeVault
    pv_raw_transaction = api_client.create_contract_call_transaction(
        CreateContractCallTransactionRequest(
            vaultId=str(vault_id),
            chain=chain,
            data=RawSigningData(
                messageHex=unsigned_transaction_message_hex,
            ),
        )
    )

    # Wait for PrimeVault to sign the transaction
    while True:
        pv_raw_transaction = api_client.get_transaction_by_id(pv_raw_transaction.id)
        if pv_raw_transaction.status in ["COMPLETED", "FAILED"]:
            break
        time.sleep(1)  # Small delay to avoid excessive polling

    # Process signature from PrimeVault
    signature_data: dict[str, Any] = pv_raw_transaction.txnSingatureData or {}
    print(f"PrimeVault signature data: {signature_data}")

    # Adjust signature components
    v = int(signature_data["v"]) - 27  # Raw signatures add 27 to v
    r = int(signature_data["r"])
    s = int(signature_data["s"])

    # Encode the final transaction with signature
    encoded_transaction = encode_transaction(unsigned_transaction, vrs=(v, r, s))

    # Create signed transaction object
    eth_signed_transaction = SignedTransaction(
        rawTransaction=HexBytes(encoded_transaction),
        hash=HexBytes(keccak(encoded_transaction)),
        r=r,
        s=s,
        v=v,
    )

    # Relay the transaction to the blockchain
    status, fee = relay_signed_transaction(web3_client, eth_signed_transaction)
    print(f"Transaction status: {status}, gas fee: {fee}")
    return status, fee


"""
# Example usage
api_client = APIClient(...)

sign_and_relay_evm_contract_calls(
    api_client=api_client,
    vault_id="7ad54443-21d2-4075-abef-83758c9dceb7",
    chain="ETHEREUM",
    contract_address="0x1fedda0d98c5b4fdebde9342d3db6eff284b0d18",
    call_data="0xf2b9fdb8000000000000000000000000c2132d05d31c914a87c6611c10748aeb04b58e8f0000000000000000000000000000000000000000000000000000000000002710",
    rpc_url="",
)

"""
