import sys
import os
import unittest
import hvac
import requests

from tfe import Organization


class TestOrganization(unittest.TestCase):

    def setUp(self):
        self.vault_client = hvac.Client(
            os.environ.get("VAULT_ADDR"),
            os.environ.get("VAULT_TOKEN")
        )

        vault_data = self.vault_client.read(
            os.path.join(
                os.environ.get("PYTFE_CORE_VAULT_BASE_PATH")
            )
        ).get("data")

        self.org_name = vault_data.get("orgname")
        self.admin_email = vault_data.get("admin_email")
        self.atlas_token = vault_data.get("atlas_token")
        self.api = vault_data.get("api")

    @property
    def org(self):
        return Organization(
            api=self.api,
            atlas_token=self.atlas_token,
            org_name=self.org_name,
            email=self.admin_email
        )

    def test_create(self):
        self.org.create()
        assert(self.org.org_name == self.org_name)

    def test_multi_create(self):
        try:
            self.org.delete()
        except:
            pass
        self.org.create()
        # self.assertRaises(Exception, org.create)
        self.assertRaises(requests.exceptions.HTTPError, self.org.create)

    def test_delete(self):
        try:
            self.org.create()
        except:
            pass
        self.org.delete()

    def test_multi_delete(self):
        try:
            self.org.create()
        except:
            pass
        self.org.delete()
        # self.assertRaises(Exception, org.create)
        self.assertRaises(requests.exceptions.HTTPError, self.org.delete)
    




    def tearDown(self):
        org = Organization(
            api=self.api,
            atlas_token=self.atlas_token,
            org_name=self.org_name,
            email=self.admin_email
        )
        org.delete()

        