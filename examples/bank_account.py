from primevault_python_sdk.api_client import APIClient
from primevault_python_sdk.types import (
    ApprovalAction,
    BankAccountBeneficiary,
    BankAccountBeneficiaryAddress,
    BankAccountBeneficiaryBusiness,
    BankAccountBeneficiaryIdentification,
    BankAccountInfo,
    CreateBankAccountRequest,
    GetApprovalRequest,
    PaymentRail,
)


def create_and_approve_bank_account(api_client: APIClient):
    """Create a bank account and approve the change request."""
    request = CreateBankAccountRequest(
        accountName="Treasury Account",
        bankAccountInfo=BankAccountInfo(
            accountNumber="123456789",
            routingNumber="021000021",
            bankName="Chase",
            country="US",
            accountType="CHECKING",
        ),
        paymentRails=[PaymentRail.ACH],
        currency="USD",
        externalId="treasury-usd-001",
        beneficiary=BankAccountBeneficiary(
            entityType="BUSINESS",
            business=BankAccountBeneficiaryBusiness(
                legalName="Acme Treasury LLC", registrationCountry="US"
            ),
            address=BankAccountBeneficiaryAddress(
                streetLine1="123 Main St",
                city="New York",
                state="NY",
                zip="10001",
                country="US",
            ),
            identifications=[
                BankAccountBeneficiaryIdentification(type="TAX_ID", value="12-3456789")
            ],
        ),
        tags=["treasury", "payroll"],
    )

    bank_account = api_client.create_bank_account_with_approval(request)
    print(f"Created and approved: {bank_account.id} status={bank_account.status}")
    print(f"  accountName={bank_account.accountName}")
    print(f"  currency={bank_account.currency} externalId={bank_account.externalId}")
    if bank_account.beneficiary:
        print(f"  beneficiary city={bank_account.beneficiary.address.city}")
    return bank_account


def decline_bank_account(api_client: APIClient, bank_account_id: str):
    """Decline a pending bank account change request."""
    response = api_client.approve_change_request(
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
            print(f"  - {account.accountName} ({account.paymentRails})")

        if not response.hasNext or not response.nextCursor:
            break
        cursor = response.nextCursor

    print(f"Total bank accounts: {len(all_accounts)}")
    return all_accounts


def get_bank_account(api_client: APIClient, bank_account_id: str):
    """Get a single bank account by ID."""
    account = api_client.get_bank_account_by_id(bank_account_id)
    print(f"Bank account: {account.id}, status={account.status}")
    print(f"  accountName={account.accountName}")
    if account.bankAccountInfo:
        print(f"  bankName={account.bankAccountInfo.bankName}")
    return account


def find_bank_account_by_external_id(api_client: APIClient, external_id: str):
    """Find a bank account by the externalId it was created with."""
    response = api_client.get_bank_accounts(params={"externalId": external_id})
    return response.results[0] if response.results else None
