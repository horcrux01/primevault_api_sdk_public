from primevault_python_sdk.api_client import APIClient
from primevault_python_sdk.types import (
    ApprovalAction,
    CreateContactRequest,
    GetApprovalRequest,
    UpdateContactRequest,
)


def create_and_approve_contact(api_client: APIClient):
    """
    Create a contact with an asset whitelist and approve it.

    `create_contact_with_approval` creates the contact and approves the pending
    contact change request, so the returned contact is already approved. Use
    `create_contact` / `create_contact_approval` to run the steps separately.
    """
    contact = api_client.create_contact_with_approval(
        CreateContactRequest(
            name="USDT/USDC Contact",
            address="0xCa1Dc85B6a8F4Ee45C5C66D887d512355b7D0609",
            chain="ETHEREUM",
            assetList=["USDT", "USDC"],
            contactGroupIds=[],  # Optional: contact group IDs from the UI
        )
    )
    print(f"Contact created and approved: {contact.id} ({contact.status})")
    print(
        f"  name={contact.name}, chain={contact.blockChain}, assetList={contact.assetList}"
    )

    return contact


def decline_contact(api_client: APIClient, contact_id: str):
    """Decline a pending contact change request."""
    return api_client.approve_change_request(
        GetApprovalRequest(
            entityId=contact_id,
            action=ApprovalAction.REJECT.value,
        )
    )


def get_contacts(api_client: APIClient):
    """List all contacts with cursor-based pagination."""
    all_contacts = []
    cursor = None

    while True:
        response = api_client.get_contacts(limit=50, cursor=cursor)
        all_contacts.extend(response.results)
        print(f"Fetched {len(response.results)} contacts (total: {len(all_contacts)})")

        if not response.hasNext or not response.nextCursor:
            break
        cursor = response.nextCursor

    print(f"Total contacts: {len(all_contacts)}")
    return all_contacts


def get_contacts_filtered(api_client: APIClient):
    """List contacts with a filter."""
    response = api_client.get_contacts(params={"blockChain": "ETHEREUM"}, limit=10)
    for contact in response.results:
        print(f"  {contact.id} — {contact.name} ({contact.blockChain})")


def update_contact_asset_list(
    api_client: APIClient, contact_id: str, asset_list: list[str]
):
    """
    Update a contact's asset whitelist and approve the change.

    Replaces the list of assets the contact is allowed to receive.
    `update_contact_with_approval` updates the contact and approves the pending
    change request. Use `update_contact` if you want to approve separately.
    """
    updated = api_client.update_contact_with_approval(
        UpdateContactRequest(id=contact_id, assetList=asset_list)
    )
    print(f"Contact {updated.id} asset list updated and approved: {updated.assetList}")

    return updated
