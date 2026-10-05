import unittest
from unittest.mock import Mock, patch

from primevault_python_sdk.api_client import APIClient
from primevault_python_sdk.types import CreateSubOrgRequest, SubOrg, SubOrgControlMode


class TestSubOrgAPIs(unittest.TestCase):
    def setUp(self) -> None:
        self.client = object.__new__(APIClient)
        self.post = Mock()
        self.get = Mock()
        transport_patch = patch.multiple(self.client, post=self.post, get=self.get)
        transport_patch.start()
        self.addCleanup(transport_patch.stop)
        self.sub_org = {
            "id": "sub-org-id",
            "orgId": "org-id",
            "name": "Acme & Sons",
            "controlMode": "MANAGED",
            "createdAt": "2026-09-14T10:00:00Z",
            "updatedAt": "2026-09-14T10:00:00Z",
            "isDeleted": False,
            "version": 1,
        }

    def test_create_serializes_name_and_parses_managed_sub_org(self) -> None:
        """Creation sends only a name and parses the returned managed SubOrg."""
        self.post.return_value = self.sub_org
        created = self.client.create_sub_org(CreateSubOrgRequest(name="Acme & Sons"))
        self.post.assert_called_once_with(
            "/api/external/sub_orgs/", data={"name": "Acme & Sons"}
        )
        self.assertIsInstance(created, SubOrg)
        self.assertIs(created.controlMode, SubOrgControlMode.MANAGED)
        self.assertEqual(created.orgId, "org-id")

    def test_list_defaults(self) -> None:
        """An omitted filter and cursor request the first page with the default limit."""
        self.get.return_value = {
            "results": [],
            "nextCursor": None,
            "hasNext": False,
        }
        page = self.client.get_sub_orgs()
        self.get.assert_called_once_with("/api/external/sub_orgs/?limit=20&cursor=")
        self.assertEqual(page.results, [])
        self.assertIsNone(page.nextCursor)
        self.assertFalse(page.hasNext)

    def test_list_encodes_filters_and_parses_cursor_pages(self) -> None:
        """Encoded filters and cursors survive pagination, including nullable legacy control modes."""
        self.get.side_effect = [
            {"results": [self.sub_org], "nextCursor": "cursor+/=", "hasNext": True},
            {
                "results": [
                    {
                        **self.sub_org,
                        "id": "legacy-id",
                        "controlMode": None,
                        "version": None,
                    }
                ],
                "nextCursor": None,
                "hasNext": False,
            },
        ]
        first = self.client.get_sub_orgs({"name": "Acme & Sons"}, limit=1)
        self.get.assert_called_with(
            "/api/external/sub_orgs/?limit=1&cursor=&name=Acme+%26+Sons"
        )
        self.assertIs(first.results[0].controlMode, SubOrgControlMode.MANAGED)
        self.assertTrue(first.hasNext)
        second = self.client.get_sub_orgs(
            {"name": "Acme & Sons"}, limit=1, cursor=first.nextCursor
        )
        self.get.assert_called_with(
            "/api/external/sub_orgs/?limit=1&cursor=cursor%2B%2F%3D&name=Acme+%26+Sons"
        )
        self.assertIsNone(second.results[0].controlMode)
        self.assertIsNone(second.results[0].version)
        self.assertIsNone(second.nextCursor)
        self.assertFalse(second.hasNext)
