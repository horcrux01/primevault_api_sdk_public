from primevault_python_sdk.api_client import APIClient
from primevault_python_sdk.types import (
    ApprovalAction,
    CreateContactRequest,
    GetApprovalRequest,
    UpdateContactRequest,
)


def create_contact(api_client: APIClient):
    contact_request = CreateContactRequest(
        name="test", address="0xa..", chain="ETHEREUM", assetList=["USDT"]
    )
    contact_response = api_client.create_contact(contact_request)
    # action can be approve/reject for the function created below
    approve_response = api_client.initiate_change_approval_action(
        GetApprovalRequest(
            entityId=contact_response.id, action=ApprovalAction.APPROVE.value
        )
    )
    return approve_response


def update_contact(api_client: APIClient):
    contact_request = UpdateContactRequest(id="contact-id", assetList=["USDC"])
    contact_response = api_client.update_contact(contact_request)
    # action can be approve/reject for the function created below
    approve_response = api_client.initiate_change_approval_action(
        GetApprovalRequest(
            entityId=contact_response.id, action=ApprovalAction.APPROVE.value
        )
    )
    return approve_response
