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

    Flow:
      1. Create a contact on a given chain with a restricted assetList.
      2. Approve the pending contact change request.
      3. Verify the contact status after approval.
    """
    # Step 1: Create a contact with an asset whitelist
    contact = api_client.create_contact(
        CreateContactRequest(
            name="USDT/USDC Contact",
            address="0xCa1Dc85B6a8F4Ee45C5C66D887d512355b7D0609",
            chain="ETHEREUM",
            assetList=["USDT", "USDC"],
        )
    )
    print(f"Contact created: {contact.id} ({contact.status})")
    print(f"  name={contact.name}, chain={contact.blockChain}, assetList={contact.assetList}")

    # Step 2: Approve the contact using its ID as the entityId
    approval = api_client.initiate_change_approval_action(
        GetApprovalRequest(
            entityId=contact.id, action=ApprovalAction.APPROVE.value
        )
    )
    print(f"Approval result: success={approval.success}")

    # Step 3: Fetch the contact again to verify it's approved
    verified = api_client.get_contact_by_id(contact.id)
    print(f"Contact status after approval: {verified.status}")

    return verified


def decline_contact(api_client: APIClient, contact_id: str):
    """Decline a pending contact change request."""
    return api_client.initiate_change_approval_action(
        GetApprovalRequest(
            entityId=contact_id, action=ApprovalAction.REJECT.value
        )
    )


def update_contact_asset_list(
    api_client: APIClient, contact_id: str, asset_list: list[str]
):
    """
    Update a contact's asset whitelist and approve the change.

    Replaces the list of assets the contact is allowed to receive.
    The update creates a pending change request that must be approved.
    """
    # Step 1: Update the asset list
    updated = api_client.update_contact(
        UpdateContactRequest(id=contact_id, assetList=asset_list)
    )
    print(f"Contact {updated.id} asset list update requested: {updated.assetList}")

    # Step 2: Approve the update
    approval = api_client.initiate_change_approval_action(
        GetApprovalRequest(
            entityId=updated.id, action=ApprovalAction.APPROVE.value
        )
    )
    print(f"Update approval result: success={approval.success}")

    return updated
