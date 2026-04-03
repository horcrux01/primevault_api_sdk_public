from primevault_python_sdk.api_client import APIClient
from primevault_python_sdk.types import (
    ApprovalAction,
    CreateBankAccountRequest,
    GetApprovalRequest,
)


def create_and_approve_bank_account(api_client: APIClient):
    """Create a bank account and approve the change request."""
    request = CreateBankAccountRequest(
        accountNumber="123456789",
        accountName="Treasury Account",
        routingNumber="021000021",
        paymentMethod="ACH",
        bankName="Chase",
        currency="USD",
        streetLine="123 Main St",
        city="New York",
        state="NY",
        postalCode="10001",
        country="US",
    )

    bank_account = api_client.create_bank_account(request)
    print(f"Created: {bank_account.id} status={bank_account.status}")
    print(
        f"  accountName={bank_account.accountName} bankName={bank_account.bankName} city={bank_account.city}"
    )

    approve_response = api_client.submit_bank_account_approval_action(
        GetApprovalRequest(
            entityId=bank_account.id,
            action=ApprovalAction.APPROVE.value,
        )
    )
    print(f"Approval response: {approve_response}")
    return approve_response


def decline_bank_account(api_client: APIClient, bank_account_id: str):
    """Decline a pending bank account change request."""
    response = api_client.submit_bank_account_approval_action(
        GetApprovalRequest(
            entityId=bank_account_id,
            action=ApprovalAction.REJECT.value,
        )
    )
    print(f"Decline response: {response}")
    return response


def list_bank_accounts(api_client: APIClient):
    """List all bank accounts with cursor-based pagination."""
    all_accounts = []
    cursor = None

    while True:
        response = api_client.get_bank_accounts(
            params={"status": "APPROVED"}, limit=20, cursor=cursor
        )
        all_accounts.extend(response.results)
        for account in response.results:
            print(
                f"  - {account.accountName} ({account.paymentMethod}) bankName={account.bankName}"
            )

        if not response.has_next or not response.next_cursor:
            break
        cursor = response.next_cursor

    print(f"Total bank accounts: {len(all_accounts)}")
    return all_accounts


def get_bank_account(api_client: APIClient, bank_account_id: str):
    """Get a single bank account by ID."""
    account = api_client.get_bank_account_by_id(bank_account_id)
    print(f"Bank account: {account.id}, status={account.status}")
    print(f"  accountName={account.accountName}, bankName={account.bankName}")
    return account
