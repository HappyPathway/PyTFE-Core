import requests
import os
from jinja2 import Template
from functools import partial
import urllib
import json
import logging
import sys


from tfe.core.session import TFESession
from tfe.core.exception import RaisesTFEException, TFESessionException
from tfe.core.run import Run
from tfe.core.state import State
from tfe.core.tfe import TFEObject, Validator
from tfe.core import organization

class VCSRepo(object):
    _fields = [
        "identifier", 
        "oauth_token_id",
        "branch",
        "default_branch",
        "ingress_submodules"
    ]

    def __init__(self, vcs_repo=None):
        self.ingress_submodules = True
        self.identifier = None
        self.__dict__["_raw"] = vcs_repo
        if not vcs_repo:
            vcs_repo = dict()

        for attr in VCSRepo._fields:
            attr = "_".join(attr.split("-"))
            setattr(self, attr, None)

        for k, v in vcs_repo.items():
            if k in self._fields:
                setattr(self, "_".join(k.split("-")), v)
    
    def __setattr__(self, k, v):
        if k in self._fields:
            self.__dict__[k] = v
        else:
            raise AttributeError(
                "{0}: does not have attribute: {1}".format(
                    self.__class__.__name__,
                    k
                )
            )

    def __repr__(self):
        return self.identifier


class Workspace(TFEObject):    
    
    _base_dir = os.path.dirname(__file__)
    json_template = None
    hcl_template = None
    fields = [
        "name",
        "vcs_repo",
        "terraform_version",
        "working_directory",
        "organization"
    ]

    def __init__(self, workspace_id=None, **kwargs):
        super()
        self.vcs_repo = None 
        self.organization = None
        self.name = None
        self.ingress_submodules = True
        if workspace_id:
            self.id = workspace_id
        else:
            self.id = None

        for k, v in kwargs.items():
            setattr(self, k, v)

        self.terraform_version = "0.11.8"
        self.working_directory = None
        
        logging.basicConfig(
            filename=self.logfile, 
            format='%(asctime)-15s com.happypathway.tfe.%(name)s: %(message)s'
        )

        Workspace.logger = logging.getLogger(self.__class__.__name__)
        Workspace.validator =  type("{0}Validator".format(self.__class__.__name__), 
                                    (Validator, ), 
                                    dict(_fields=self.__class__.fields))()

        with open("{0}/templates/json/workspace.json.j2".format(self._base_dir)) as _template:
            Workspace.json_template = Template(_template.read())

        with open("{0}/templates/hcl/workspace.j2".format(self._base_dir)) as _template:
            Workspace.hcl_template = Template(_template.read())

        if self.organization and self.name:
            self.get()

    @property
    def create_url(self):
        return "{0}/api/v2/organizations/{1}/workspaces".format(
            self.base_url,
            self.organization
        )

    @property
    def update_url(self):
        return  "{0}/api/v2/organizations/{1}/workspaces/{2}".format(
            self.base_url,
            self.organization,
            self.name
        )

    @property
    def list_url(self):
        return "{0}/api/v2/organizations/{1}/workspaces".format(
            self.base_url,
            self.organization
        )

    @property
    def delete_url(self):
        return "{0}/api/v2/organizations/{1}/workspaces/{2}".format(
            self.base_url,
            self.organization,
            self.name
        )

    @property
    def read_url(self):
        return "{0}/api/v2/organizations/{1}/workspaces/{2}".format(
            self.base_url,
            self.organization,
            self.name
        )

    @property
    def runs(self):
        for x in Run(workspace_id=self.id).list():
            yield x

    def get(self):
        if not TFESession.session:
            raise TFESessionException("Session is not iniatialized")
        resp = self.session.get(self.read_url)
        resp.raise_for_status()

        self.id = resp.json().get("data").get("id")
        attrs = resp.json().get("data").get("attributes")
        relationships = resp.json().get("data").get("relationships")
        
        for k, v in attrs.items():
            setattr(self, k, v)

        self.name  = attrs.get("name")
        self.auto_apply = attrs.get("auto-apply")
        self.locked = attrs.get("locked")
        self.working_directory = attrs.get("working-directory")
        self.terraform_version = attrs.get("terraform-version")
        self.vcs_repo = VCSRepo(attrs.get("vcs-repo"))
        self.permissions = attrs.get("permissions")
        
        try:
            self.current_run = Run(relationships.get("current-run").get("data").get("id"))
        except AttributeError:
            self.current_run = None

        try:
            self.current_state = State(relationships.get("current-state-version").get("data").get("id"))
        except AttributeError:
            self.current_state = None

        self.organization = organization.Organization(relationships.get("organization").get("data").get("id"))


    def lock(self):
        self.lock_url = "{0}/api/v2/workspaces/{1}/actions/lock".format(
            self.base_url, 
            self.id
        )
        resp = self.session.post(self.lock_url)
        resp.raise_for_status()
        return resp.status_code

    def unlock(self):
        self.lock_url = "{0}/api/v2/workspaces/{1}/actions/unlock".format(
            self.base_url, 
            self.id
        )
        resp = self.session.post(self.lock_url)
        resp.raise_for_status()
        return resp.status_code

    def __repr__(self):
        return self.name