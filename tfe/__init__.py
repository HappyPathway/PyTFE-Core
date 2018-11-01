import random
import os
import json
import string
import hvac
import logging

from tfe.core.session import TFESession
from tfe.core.organization import Organization as TFEOrganization
from tfe.core.workspace import Workspace as TFEWorkspace
from tfe.core.workspace import VCSRepo
from tfe.core.oauth_client import OauthClient
from tfe.core.variable import Variable
from tfe.core.configuration import Configuration
from tfe.core.run import Run

from tfe.core.state import State
from tfe.core.team_access import TeamAccess
from tfe.core.team import Team
from tfe.core.variable import Variable
from tfe.core.sentinel import Sentinel

TFE_LOGFILE = "/dev/null"

def log_config(logfile=None):
    if not logfile:
        logfile = TFE_LOGFILE
    found_stdout = False
    logger = logging.getLogger() # this gets the root logger
    try:
        lhStdout = logger.handlers[0]  # stdout is the only handler initially
        found_stdout = True
    except:
        pass
        
    f = open(logfile, "a")          # example handler
    lh = logging.StreamHandler(f)
    logger.addHandler(lh)
    if found_stdout:
        logger.removeHandler(lhStdout)

# setup initial logging
log_config()

class Organization(object):
    atlas_token = None
    api = None
    _email = None
    session_remember = 20160
    session_timeout = 20160
    collaborator_auth_policy = "password"

    def __init__(self, api=None, atlas_token=None, org_name=None, email=None):
        if api:
            self.api = api

        if atlas_token:
            self.atlas_token = atlas_token

        TFESession(self.api, self.atlas_token)
        if org_name:
            self._org_name = org_name
            self.organization = TFEOrganization(org_name)
            self.organization.get()
        
        if email:
            self._email = email
            self.organization.email = email


    @property
    def org_name(self):
        return self._org_name

    @org_name.setter
    def org_name(self, org_name):
        self._org_name = org_name
        self.organization = TFEOrganization(org_name)
        self.organization.get()

    @property
    def email(self):
        return self._email
    

    @email.setter
    def email(self, email):
        self._email = email
        self.organization.email = email


    def oauth_client(self, service_provider=None, http_url=None, api_url=None, access_token=None):
        self.oauth = OauthClient()
        self.oauth.organization = self.organization
        self.oauth.service_provider = service_provider
        self.oauth.personal_access_token = access_token
        self.oauth.http_url = http_url
        self.oauth.api_url = api_url
        self.oauth.create()
        return self.oauth.token

    def create(self):
        for field in TFEOrganization.fields:
            try:
                if not getattr(self.organization, field):
                    setattr(self.organization, field, getattr(self, field))
            except AttributeError:
                setattr(self.organization, field, getattr(self, field))
        self.organization.create()

    def update(self):
        self.organization.update()

    def delete(self):
        self.organization.delete()

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

        self.org = TFEOrganization(self.organization)
        self.org.get()
        self.ws = TFEWorkspace()
        self.ws.organization = self.org
        self.ws.name = self.workspace
        self.variables = {}
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
            self.variables[k](var)


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
                    try:
                        self.variables.pop(var)
                    except Exception as e:
                        pass
                        

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
    
        


