import sys
import os
import unittest
import hvac
import requests
import warnings
from tfe import Organization
from tfe.core.organization import Organization as TFEOrganization
from tfe import Workspace
from tfe.core.workspace import Workspace as TFEWorkspace

def ignore_warnings(test_func):
    def do_test(self, *args, **kwargs):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ResourceWarning)
            test_func(self, *args, **kwargs)
    return do_test

class TestWorkspace(unittest.TestCase):

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
        self.vault_client.close()

        self.org_name = vault_data.get("orgname")
        self.admin_email = vault_data.get("admin_email")
        self.atlas_token = vault_data.get("atlas_token")
        self.api = vault_data.get("api")
        self.workspace_name = vault_data.get("workspace")

    @property
    def organization(self):
        orgs = [org.name for org in TFEOrganization.list()]
        org = Organization(
                api=self.api,
                atlas_token=self.atlas_token,
                org_name=self.org_name,
                email=self.admin_email
            )
        if self.org_name not in orgs:
            org.create()
        return org

    @property
    def workspace(self):
        ws = Workspace(
                api=self.api,
                atlas_token=self.atlas_token,
                organization=self.organization.org_name,
                workspace_name=self.workspace_name
            )

        return ws
        
        
        

    @ignore_warnings
    def test_list(self):
        ws = TFEWorkspace()
        for x in ws.list():
            print(x)

    @ignore_warnings
    def test_create(self):
        self.workspace.create()
        assert(self.workspace.ws.name == self.workspace_name)


    @ignore_warnings
    def test_multi_create(self):
        try:
            self.workspace.delete()
        except:
            pass
        self.workspace.create()
        # self.assertRaises(Exception, org.create)
        self.assertRaises(requests.exceptions.HTTPError, self.workspace.create)


    @ignore_warnings
    def test_delete(self):
        self.workspace.create()
        self.workspace.delete()


    @ignore_warnings
    def test_multi_delete(self):
        self.workspace.create()
        self.workspace.delete()
        # self.assertRaises(Exception, org.create)
        self.assertRaises(requests.exceptions.HTTPError, self.workspace.delete)


    @ignore_warnings
    def tearDown(self):
        try:
            self.organization.delete()
        except requests.exceptions.HTTPError:
            pass
        

        
if __name__ == '__main__':
    unittest.main()