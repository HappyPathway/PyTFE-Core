import requests
import os
from jinja2 import Template
from functools import partial
import sys
import urllib


from tfe.core.session import TFESession



class SentinelPolicy(TFESession):

    hcl_template = None
    json_template = None
    _base_dir = os.path.dirname(__file__)

    def __init__(self, policy_id):
        super()
        self.api_url = None
        self.download = None

        with open("{0}/templates/hcl/sentinel.hcl.j2".format(self._base_dir)) as sentinel_template:
            self.sentinel_template = Template(sentinel_template.read())

    @property
    def policy_doc(self):
        resp = self.session.get(
            self.download
        )
        return resp.content

    @staticmethod
    def list(organization):
        list_url = "{0}/api/v2/organizations/{1}/policies".format(
            TFESession.base_url,
            organization
        )
        resp = TFESession.session.get(list_url)
        sentinel_data = resp.json().get("data")
        for policy in sentinel_data:
            yield SentinelPolicy(policy.get("id"))


    def rendered(self, dir_prefix=None):
        resp = self.session.get(self.api_url)
        sentinel_data = resp.json().get("data")
        enforce = sentinel_data.get("attributes").get("enforce")
        enforce_mode = enforce.get("mode")
        policy_path = enforce.get("path")
        if dir_prefix:
            policy_path = os.path.join(dir_prefix, policy_path)
        return self.sentinel_template.render(
                enforce_mode=enforce_mode,
                policy="${file("+policy_path+")}"
            )

    