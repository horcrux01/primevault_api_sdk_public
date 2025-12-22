"""
Solana Transaction Handler Module

This module provides functionality for creating, signing, and relaying Solana blockchain transactions
using PrimeVault for secure transaction signing.

Required packages:
solana==0.34.3
solders==0.21.0
"""

import time
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from solana.rpc.api import Client as SolanaClient
from solana.rpc.commitment import Confirmed, Finalized
from solana.rpc.types import TxOpts
from solders.instruction import AccountMeta, Instruction
from solders.message import Message
from solders.pubkey import Pubkey
from solders.signature import Signature
from solders.system_program import TransferParams, transfer
from solders.transaction import Transaction

from primevault_python_sdk.api_client import APIClient
from primevault_python_sdk.types import (
    CreateContractCallTransactionRequest,
    RawSigningData,
    TransactionStatus,
    Wallet,
)


def parse_transaction_result(
    solana_client: SolanaClient, signature: str
) -> Tuple[str, Decimal]:
    """
    Parse a Solana transaction result and determine its status and fee.

    Args:
        solana_client: Initialized Solana RPC client
        signature: Transaction signature string

    Returns:
        Tuple containing:
          - Transaction status: "COMPLETED", "FAILED", or "SUBMITTED"
          - Transaction fee in SOL as Decimal
    """
    fee = Decimal(0)

    try:
        # Get transaction details
        response = solana_client.get_transaction(
            Signature.from_string(signature),
            commitment=Finalized,
            max_supported_transaction_version=0,
        )

        if response.value is None:
            return "SUBMITTED", fee

        transaction_meta = response.value.transaction.meta
        if transaction_meta is None:
            return "SUBMITTED", fee

        # Calculate fee (in lamports, convert to SOL)
        if transaction_meta.fee:
            fee = Decimal(transaction_meta.fee) / Decimal(1_000_000_000)

        # Check for errors
        if transaction_meta.err is None:
            return "COMPLETED", fee
        else:
            return "FAILED", fee

    except Exception as e:
        print(f"Error parsing transaction result: {e}")
        return "SUBMITTED", fee


def relay_signed_transaction(
    solana_client: SolanaClient, signed_transaction: Transaction
) -> Tuple[Optional[str], Optional[str], Optional[Decimal]]:
    """
    Relay a signed transaction to the Solana blockchain and wait for its confirmation.

    Args:
        solana_client: Initialized Solana RPC client
        signed_transaction: Signed Transaction object

    Returns:
        Tuple containing:
          - Transaction status: "COMPLETED", "FAILED", or None if timeout
          - Transaction signature string
          - Fee in SOL as Decimal, or None if transaction didn't complete
    """
    # Send the transaction to the network
    try:
        send_response = solana_client.send_transaction(
            signed_transaction,
            opts=TxOpts(skip_preflight=False, preflight_commitment=Confirmed),
        )
        signature = str(send_response.value)
        print(f"Transaction sent with signature: {signature}")
    except Exception as e:
        print(f"Error sending transaction: {e}")
        return None, None, None

    # Poll for transaction confirmation
    wait_attempts = 60
    status, fee = None, None

    while wait_attempts > 0:
        try:
            # Check transaction status
            confirm_response = solana_client.confirm_transaction(
                Signature.from_string(signature),
                commitment=Finalized,
            )

            if confirm_response.value and confirm_response.value[0] is not None:
                # Transaction has been processed - check the TransactionStatus
                tx_status = confirm_response.value[0]
                if tx_status.err is None:
                    # No error, transaction succeeded
                    status, fee = parse_transaction_result(solana_client, signature)
                    if status in ["COMPLETED", "FAILED"]:
                        print(f"Transaction {status.lower()} with fee: {fee} SOL")
                        return status, signature, fee
                else:
                    # Transaction failed with an error
                    print(f"Transaction failed with error: {tx_status.err}")
                    return "FAILED", signature, Decimal(0)

        except Exception as e:
            print(f"Error confirming transaction: {e}")

        time.sleep(2)
        wait_attempts -= 1

    return status, signature, fee


def create_solana_transfer_instruction(
    from_pubkey: Pubkey,
    to_pubkey: Pubkey,
    lamports: int,
) -> Instruction:
    """
    Create a SOL transfer instruction.

    Args:
        from_pubkey: Sender's public key
        to_pubkey: Recipient's public key
        lamports: Amount to transfer in lamports (1 SOL = 1,000,000,000 lamports)

    Returns:
        Transfer instruction
    """
    return transfer(
        TransferParams(
            from_pubkey=from_pubkey,
            to_pubkey=to_pubkey,
            lamports=lamports,
        )
    )


def create_solana_transaction(
    solana_client: SolanaClient,
    from_pubkey: Pubkey,
    instructions: List[Instruction],
) -> Tuple[Transaction, bytes]:
    """
    Create a Solana transaction with the given instructions.

    Args:
        solana_client: Initialized Solana RPC client
        from_pubkey: Fee payer's public key
        instructions: List of instructions to include in the transaction

    Returns:
        Tuple containing:
          - Unsigned Transaction object
          - Message bytes to be signed
    """
    # Get recent blockhash
    blockhash_response = solana_client.get_latest_blockhash(commitment=Finalized)
    recent_blockhash = blockhash_response.value.blockhash

    # Create message
    message = Message.new_with_blockhash(
        instructions,
        from_pubkey,
        recent_blockhash,
    )

    # Create unsigned transaction
    transaction = Transaction.new_unsigned(message)

    # Get message bytes for signing
    message_bytes = bytes(message)

    return transaction, message_bytes


def create_custom_instruction(
    program_id: str,
    accounts: List[Dict[str, Any]],
    data: bytes,
) -> Instruction:
    """
    Create a custom Solana instruction for arbitrary program calls.

    Args:
        program_id: Program ID (base58 string)
        accounts: List of account metadata dictionaries with keys:
            - pubkey: Account public key (base58 string)
            - is_signer: Whether this account is a signer
            - is_writable: Whether this account is writable
        data: Instruction data as bytes

    Returns:
        Custom instruction
    """
    account_metas = [
        AccountMeta(
            pubkey=Pubkey.from_string(acc["pubkey"]),
            is_signer=acc.get("is_signer", False),
            is_writable=acc.get("is_writable", False),
        )
        for acc in accounts
    ]

    return Instruction(
        program_id=Pubkey.from_string(program_id),
        accounts=account_metas,
        data=data,
    )


def sign_and_relay_solana_transfer(
    api_client: APIClient,
    vault_id: str,
    to_address: str,
    amount_sol: float,
    rpc_url: str,
) -> Tuple[Optional[str], Optional[str], Optional[Decimal]]:
    """
    Sign and relay a SOL transfer transaction using PrimeVault for secure signing.

    This function:
    1. Gets the wallet from PrimeVault vault
    2. Creates a transfer transaction
    3. Gets the message bytes for signing
    4. Sends to PrimeVault for secure signing
    5. Attaches the signature to the transaction
    6. Relays the transaction to Solana

    Args:
        api_client: PrimeVault API client object
        vault_id: PrimeVault vault ID containing the signing wallet
        to_address: Recipient's Solana address (base58)
        amount_sol: Amount of SOL to transfer
        rpc_url: RPC URL for the Solana cluster

    Returns:
        Tuple containing:
          - Transaction status: "COMPLETED", "FAILED", or None if timeout
          - Transaction signature string
          - Fee in SOL as Decimal, or None if transaction didn't complete
    """
    # Get wallet from PrimeVault vault
    vault = api_client.get_vault_by_id(vault_id)
    wallets: List[Wallet] = vault.wallets or []
    wallet = next(w for w in wallets if w.blockchain == "SOLANA")

    # Initialize Solana client
    solana_client = SolanaClient(rpc_url)

    # Get public keys
    from_pubkey = Pubkey.from_string(wallet.address)
    to_pubkey = Pubkey.from_string(to_address)

    # Convert SOL to lamports
    lamports = int(amount_sol * 1_000_000_000)

    # Create transfer instruction
    transfer_instruction = create_solana_transfer_instruction(
        from_pubkey, to_pubkey, lamports
    )

    # Create transaction
    transaction, message_bytes = create_solana_transaction(
        solana_client, from_pubkey, [transfer_instruction]
    )
    print(f"Transaction message bytes (hex): {message_bytes.hex()}")

    # Request signature from PrimeVault
    pv_raw_transaction = api_client.create_contract_call_transaction(
        CreateContractCallTransactionRequest(
            vaultId=str(vault_id),
            chain="SOLANA",
            data=RawSigningData(
                messageHex=message_bytes.hex(),
            ),
        )
    )

    # Wait for PrimeVault to sign the transaction
    while True:
        pv_raw_transaction = api_client.get_transaction_by_id(pv_raw_transaction.id)
        if pv_raw_transaction.status in ["COMPLETED", "FAILED", "DECLINED"]:
            break
        time.sleep(1)

    if pv_raw_transaction.status != "COMPLETED":
        print(f"PrimeVault signing failed with status: {pv_raw_transaction.status}")
        return "FAILED", None, None

    # Get signature from PrimeVault response
    signature_hex = pv_raw_transaction.txnSignature
    if not signature_hex:
        print("No signature returned from PrimeVault")
        return "FAILED", None, None

    print(f"PrimeVault signature (hex): {signature_hex}")

    # Convert hex signature to Signature object
    signature_bytes = bytes.fromhex(
        signature_hex[2:] if signature_hex.startswith("0x") else signature_hex
    )
    signature = Signature.from_bytes(signature_bytes)

    # Add signature to transaction
    # Solana transactions have a list of signatures matching the signers in the message
    transaction = Transaction.populate(transaction.message, [signature])

    print(f"Signed transaction: {transaction}")

    # Relay the transaction to Solana
    status, tx_signature, fee = relay_signed_transaction(solana_client, transaction)
    print(f"Transaction status: {status}, signature: {tx_signature}, fee: {fee} SOL")
    return status, tx_signature, fee


def sign_and_relay_solana_instruction(
    api_client: APIClient,
    vault_id: str,
    instructions: List[Instruction],
    rpc_url: str,
) -> Tuple[Optional[str], Optional[str], Optional[Decimal]]:
    """
    Sign and relay a Solana transaction with custom instructions using PrimeVault.

    This is a more generic function that allows you to execute arbitrary Solana
    program instructions.

    Args:
        api_client: PrimeVault API client object
        vault_id: PrimeVault vault ID containing the signing wallet
        instructions: List of Solana instructions to execute
        rpc_url: RPC URL for the Solana cluster

    Returns:
        Tuple containing:
          - Transaction status: "COMPLETED", "FAILED", or None if timeout
          - Transaction signature string
          - Fee in SOL as Decimal, or None if transaction didn't complete
    """
    # Get wallet from PrimeVault vault
    vault = api_client.get_vault_by_id(vault_id)
    wallets: List[Wallet] = vault.wallets or []
    wallet = next(w for w in wallets if w.blockchain == "SOLANA")

    # Initialize Solana client
    solana_client = SolanaClient(rpc_url)

    # Get public key
    from_pubkey = Pubkey.from_string(wallet.address)

    # Create transaction with custom instructions
    transaction, message_bytes = create_solana_transaction(
        solana_client, from_pubkey, instructions
    )
    print(f"Transaction message bytes (hex): {message_bytes.hex()}")

    # Request signature from PrimeVault
    pv_raw_transaction = api_client.create_contract_call_transaction(
        CreateContractCallTransactionRequest(
            vaultId=str(vault_id),
            chain="SOLANA",
            data=RawSigningData(
                messageHex=message_bytes.hex(),
            ),
        )
    )

    # Wait for PrimeVault to sign the transaction
    while True:
        pv_raw_transaction = api_client.get_transaction_by_id(pv_raw_transaction.id)
        if pv_raw_transaction.status in [
            TransactionStatus.COMPLETED.value,
            TransactionStatus.FAILED.value,
            TransactionStatus.DECLINED.value,
        ]:
            break
        time.sleep(1)

    if pv_raw_transaction.status != TransactionStatus.COMPLETED.value:
        print(f"PrimeVault signing failed with status: {pv_raw_transaction.status}")
        return TransactionStatus.FAILED.value, None, None

    # Get signature from PrimeVault response
    signature_hex = pv_raw_transaction.txnSignature
    if not signature_hex:
        print("No signature returned from PrimeVault")
        return TransactionStatus.FAILED.value, None, None

    print(f"PrimeVault signature (hex): {signature_hex}")

    # Convert hex signature to Signature object
    signature_bytes = bytes.fromhex(
        signature_hex[2:] if signature_hex.startswith("0x") else signature_hex
    )
    signature = Signature.from_bytes(signature_bytes)

    # Add signature to transaction
    transaction = Transaction.populate(transaction.message, [signature])

    print(f"Signed transaction: {transaction}")

    # Relay the transaction to Solana
    status, tx_signature, fee = relay_signed_transaction(solana_client, transaction)
    print(f"Transaction status: {status}, signature: {tx_signature}, fee: {fee} SOL")
    return status, tx_signature, fee


"""
# Example usage - SOL Transfer

api_client = APIClient(...)

# Simple SOL transfer
status, signature, fee = sign_and_relay_solana_transfer(
    api_client=api_client,
    vault_id="7ad54443-21d2-4075-abef-83758c9dceb7",
    to_address="9WzDXwBbmPdCBkEpxZWqkBdGsDJYYqWfJhFAkNPNJZvP",
    amount_sol=0.001,
    rpc_url="https://api.mainnet-beta.solana.com",
)

# Custom instruction example (e.g., interacting with a program)
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta

program_id = Pubkey.from_string("YourProgramIdHere...")
instruction = Instruction(
    program_id=program_id,
    accounts=[
        AccountMeta(pubkey=Pubkey.from_string("Account1..."), is_signer=True, is_writable=True),
        AccountMeta(pubkey=Pubkey.from_string("Account2..."), is_signer=False, is_writable=True),
    ],
    data=bytes([1, 2, 3, 4]),  # Your instruction data
)

status, signature, fee = sign_and_relay_solana_instruction(
    api_client=api_client,
    vault_id="7ad54443-21d2-4075-abef-83758c9dceb7",
    instructions=[instruction],
    rpc_url="https://api.mainnet-beta.solana.com",
)
"""
