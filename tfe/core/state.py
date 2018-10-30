import requests
import os
from jinja2 import Template
from functools import partial
import urllib
import json
import hashlib
import base64
import logging
from collections import defaultdict
import sys



from tfe.core.session import TFESession
from tfe.core.exception import RaisesTFEException, TFESessionException
from tfe.core.tfe import TFEObject, Validator

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


class State(TFEObject):

    _base_dir = os.path.dirname(__file__)
    json_template = ""

    fields = [
        "serial",
        "md5",
        "lineage",
        "state"
    ]

    def __init__(self, state_id=None):
        super()
        self.run_id = None
        self.workspace = None
        self.organization = None
        self.hosted_state_download_url = None
        if state_id:
            self.id = state_id
        else:
            self.id = None

        
        logging.basicConfig(
            filename=self.logfile, 
            format='%(asctime)-15s com.happypathway.tfe.%(name)s: %(message)s'
        )
        
        State.logger = logging.getLogger(self.__class__.__name__)
        State.validator =  type("{0}Validator".format(self.__class__.__name__), 
                                        (Validator, ), 
                                        dict(_fields=self.__class__.fields))()
        
        with open("{0}/templates/json/state.json.j2".format(self._base_dir)) as vars_template:
            State.json_template = Template(vars_template.read())

    @property
    def read_url(self):
        return "{0}/api/v2/state-versions/{1}".format(
            self.base_url,
            self.id
        )

    @property
    def create_url(self):
        return "{0}/api/v2/workspaces/{1}/state-versions".format(
            self.base_url,
            self.workspace.id
        )

    @property
    def list_url(self):
        query_params = "filter%5Bworkspace%5D%5Bname%5D={0}".format(
            self.workspace.name
        )
        query_params += "&filter%5Borganization%5D%5Bname%5D={0}".format(
            self.organization
        )
        return "{0}/api/v2/state-versions?{1}".format(
            self.base_url,
            query_params
        )

    def download(self, path):
        try:
            resp = self.session.get(
                self.hosted_state_download_url
            )
            with open(path, "wb") as download_path:
                download_path.write(resp.content)
        except Exception as e:
            return dict(error=str(e))


    
    @staticmethod
    def list(self):
        url_params = []
        url_params.append("filter%5Bworkspace%5D%5Bname%5D={0}".format(self.workspace))
        url_params.append("filter%5Borganization%5D%5Bname%5D={1}".format(self.organization))
        url = "{0}/api/v2/state-versions?{1}".format(
            TFESession.base_url,
            "&".join(url_params)
        )
        resp = self.session.get(url).json()
        for x in resp.get("data"):
            yield State(x.git("id"))

    @property
    def current(self):
        # GET /workspaces/:workspace_id/current-state-version
        url = "{0}/api/v2//workspaces/{1}/current-state-version".format(
            self.base_url,
            self.workspace
        )
        resp = self.session.get(url).json()
        return resp.json().get("data")


    @property
    def outputs(self):
        resp = self.session.get(
                self.hosted_state_download_url
            )
        state_data = json.loads(resp.content)
        d = defaultdict(list)
        flat_dict = dict()
        for x in state_data.get("modules"):
            for k, v in x.get("outputs").items():
                d[k].append(v.get("value"))
        for k, v in d.items():
            if len(v) > 1:
                flat_dict[k] = v
            else:
                flat_dict[k] = v.pop()
        return flat_dict
