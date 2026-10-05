from typing import List, Optional

from primevault_python_sdk.api_client import APIClient
from primevault_python_sdk.types import CreateSubOrgRequest, SubOrg


def create_and_list_sub_orgs(api_client: APIClient) -> List[SubOrg]:
    api_client.create_sub_org(CreateSubOrgRequest(name="Acme customer"))

    sub_orgs: List[SubOrg] = []
    cursor: Optional[str] = None
    while True:
        page = api_client.get_sub_orgs({"name": "%Acme%"}, limit=20, cursor=cursor)
        sub_orgs.extend(page.results)
        if not page.hasNext:
            return sub_orgs
        cursor = page.nextCursor
