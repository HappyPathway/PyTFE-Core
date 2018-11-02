import sys
import os
import unittest
import hvac
import requests
import warnings
from tfe import Organization
from tfe.core.organization import Organization as TFEOrganization

def ignore_warnings(test_func):
    def do_test(self, *args, **kwargs):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ResourceWarning)
            test_func(self, *args, **kwargs)
    return do_test

class TestOrganization(unittest.TestCase):

    @ignore_warnings
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

    @ignore_warnings
    def test_list(self):
        org = TFEOrganization()
        for x in org.list():
            print(x)

    @ignore_warnings
    def test_create(self):
        self.org.create()
        assert(self.org.org_name == self.org_name)


    @ignore_warnings
    def test_multi_create(self):
        try:
            self.org.delete()
        except:
            pass
        self.org.create()
        # self.assertRaises(Exception, org.create)
        self.assertRaises(requests.exceptions.HTTPError, self.org.create)


    @ignore_warnings
    def test_delete(self):
        self.org.create()
        self.org.delete()


    @ignore_warnings
    def test_multi_delete(self):
        self.org.create()
        self.org.delete()
        # self.assertRaises(Exception, org.create)
        self.assertRaises(requests.exceptions.HTTPError, self.org.delete)


    @ignore_warnings
    def tearDown(self):
        org = Organization(
            api=self.api,
            atlas_token=self.atlas_token,
            org_name=self.org_name,
            email=self.admin_email
        )
        try:
            org.delete()
        except requests.exceptions.HTTPError as Exception:
            pass

        
if __name__ == '__main__':
    unittest.main()