from typing import List, Optional

from primevault_python_sdk.api_client import APIClient
from primevault_python_sdk.types import ActivityEvent

PAGE_SIZE = 100

# Filters, all optional, one value each, all composable with the cursor:
#   action        create_requested | create_approved | create_rejected | create_applied,
#                 and the same four for update_ and delete_
#   outcome       success | failure
#   entityType    Vault | Transaction | Contact | Group | ECUser | OrgBankAccount |
#                 PolicyRule | PolicySet | PolicyTemplate | OrgMetaPolicy | CustomDApp
#   entityId      id of the entity the action was performed on
#   actorId       id of the user who performed the action
#   platformType  web | pwa | ios | android | api | unknown, which the response
#                 gathers into metaData.platform rather than onto the row
#   createdAtGte  ISO-8601 timestamp, inclusive lower bound on createdAt
#   createdAtLte  ISO-8601 timestamp, inclusive upper bound on createdAt


def export_activity_events(
    api_client: APIClient, params: Optional[dict] = None
) -> List[ActivityEvent]:
    events: List[ActivityEvent] = []
    cursor: Optional[str] = None

    while True:
        page = api_client.get_activity_events(
            params=params, limit=PAGE_SIZE, cursor=cursor
        )
        events.extend(page.results)
        print(f"Fetched {len(page.results)} events (total: {len(events)})")

        if not page.hasNext or not page.nextCursor:
            break
        cursor = page.nextCursor

    for event in events:
        meta = event.metaData
        print(
            f"  {event.createdAt}  {event.action}  {event.outcome}  "
            f"{event.entityType}/{event.entityId} ({event.entityName})  "
            f"by {event.actorId}  [{event.schemaVersion}]"
        )
        if meta:
            print(
                f"      platform={meta.platform}  sourceIp={meta.sourceIp}  "
                f"userAgent={meta.userAgent}"
            )

    print(f"Total events: {len(events)}")
    return events
