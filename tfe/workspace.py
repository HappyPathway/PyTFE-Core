import random
import os
import json
import string
import hvac

from tfe.core.session import TFESession
from tfe.core.organization import Organization
from tfe.core.workspace import Workspace as TFEWorkspace
from tfe.core.workspace import VCSRepo
from tfe.core.oauth_client import OauthClient
from tfe.core.variable import Variable
from tfe.core.configuration import Configuration
from tfe.core.run import Run


class Workspace(object):
    workspace = None
    organization = None
    atlas_token = None
    api = None

    def __init__(self, api=None, atlas_token=None, organization=None, workspace_name=None):
        
    
        if workspace_name:
            self.workspace = workspace_name

        if organization:
            self.organization = organization

        if api:
            self.api = api

        if atlas_token:
            self.atlas_token = atlas_token

        TFESession(self.api, self.atlas_token)

        self.org = Organization(self.organization)
        self.org.get()
        self.ws = TFEWorkspace()
        self.ws.organization = self.org
        self.ws.name = self.workspace
        self.variables = []
        try:
            self.ws.get()
        except:
            pass


    def config(self, config_path):
        conf = Configuration()
        conf.workspace = self.ws
        new_conf = conf.create()
        new_conf.get()
        new_conf.upload(config_path)
        self.config_version = new_conf.id


    def queue_plan(self, run_message=None):
        run = Run()
        run.run_message = run_message
        run.workspace_id = self.ws.id
        run.configuration_version = self.config_version
        run.create()

    @property
    def outputs(self):
        self.ws.current_state.get()
        return self.ws.current_state.outputs

    @property
    def status(self):
        self.ws.get()
        self.ws.current_run.get()
        return self.ws.current_run.status

    def cancel(self):
        self.ws.current_run.cancel()

    def apply(self):
        self.ws.current_run.apply()

    def discard(self):
        self.ws.current_run.discard()
        
    def force_cancel(self):
        self.ws.current_run.force_cancel()




    def create(self):
        self.ws.create()
        for var in self.variables:
            var.create()


    def repo(self, repo=None, token=None, branch="master"):
        self.ws.vcs_repo = VCSRepo()
        self.ws.vcs_repo.identifier = repo
        self.ws.vcs_repo.oauth_token_id = token
        self.ws.vcs_repo.branch = branch


    def _var(self, category=False, sensitive=False, hcl=False, **kwargs):
        for k, v in kwargs.items():
            var = Variable()
            var.category = category
            var.sensitive = sensitive
            var.workspace_id = self.ws.id
            var.key = k
            var.value = v
            var.hcl = hcl
            var.create()
            self.variables.append(var)


    @property
    def existing_variables(self):
        var = Variable()
        var.organization = self.organization
        var.workspace = self.workspace
        vars = []
        for _var in var.list():
            _var.get()
            vars.append(
                dict(
                    id=_var.id,
                    key=_var.key
                )
            )
        return vars


    def rmvars(self, *args):
        _var = Variable()
        _var.organization = self.org
        _var.workspace = self.ws
        for x in _var.list():
            for var in args:
                x.get()
                if x.key == var:
                    x.delete()

    def sensitive_env_var(self, **kwargs):
        self._var(category="env", sensitive=True, hcl=False, **kwargs)

    def env_var(self, **kwargs):
        self._var(category="env", sensitive=False, hcl=False, **kwargs)

    def sensitive_hcl_var(self, **kwargs):
        self._var(category="terraform", sensitive=True, hcl=True, **kwargs)
    
    def hcl_var(self, **kwargs):
        self._var(category="terraform", sensitive=False, hcl=True, **kwargs)

    def sensitive_var(self, **kwargs):
        self._var(category="terraform", sensitive=True, hcl=False, **kwargs)

    def var(self, **kwargs):
        self._var(category="terraform", sensitive=False, hcl=False, **kwargs)
    
        


