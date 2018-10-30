import random
import os
import json
import string
import hvac

from tfe.core.session import TFESession
from tfe.core.organization import Organization as TFEOrganization
from tfe.core.workspace import Workspace as TFEWorkspace
from tfe.core.workspace import VCSRepo
from tfe.core.oauth_client import OauthClient
from tfe.core.variable import Variable


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