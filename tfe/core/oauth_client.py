import requests
import os

from jinja2 import Template
from functools import partial
import urllib
import json
import sys
import logging


from tfe.core.session import TFESession
from tfe.core.exception import RaisesTFEException, TFESessionException
from tfe.core.organization import Organization
from tfe.core.tfe import _Create, TFEObject, Validator


class _OauthToken(TFEObject):

    def __init__(self, organization, oauth_client):
        self.oauth_client = oauth_client
        url = "{0}/api/v2/organizations/{1}/oauth-tokens".format(
            self.base_url,
            organization
        )
        resp = self.session.get(url)
        resp.raise_for_status()
        self.raw_data = resp.json()

    @property
    def token(self):
        for x in self.raw_data.get("data"):
            if x.get("relationships").get("oauth-client").get("data").get("id") == self.oauth_client:
                return x.get("id")

    

class OauthClient(TFEObject):    
    
    _base_dir = os.path.dirname(__file__)
    json_template = None
    hcl_template = None

    fields = [
        "service_provider", 
        "http_url",
        "api_url",
        "personal_access_token"
    ]

    def __init__(self, id=None):
        super()
        if id:
            self.id = id
        else:
            self.id = None
        self.organization = None
        
        logging.basicConfig(
            filename=self.logfile, 
            format='%(asctime)-15s com.happypathway.tfe.%(name)s: %(message)s'
        )
        
        OauthClient.logger = logging.getLogger(self.__class__.__name__)
        OauthClient.validator =  type("{0}Validator".format(self.__class__.__name__), 
                                        (Validator, ), 
                                        dict(_fields=self.__class__.fields))()
        with open("{0}/templates/json/oauth_client.json.j2".format(self._base_dir)) as _template:
            OauthClient.json_template = Template(_template.read())

    @property
    def token(self):
        oauth_token = _OauthToken(self.organization, self.id)
        return oauth_token.token

    @property
    def list_url(self):
        return "{0}/api/v2/organizations/{1}/oauth-clients".format(
            self.base_url,
            self.organization
        )

    @property
    def create_url(self):
        return "{0}/api/v2/organizations/{1}/oauth-clients".format(
            self.base_url,
            self.organization
        )

    @property
    def delete_url(self):
        return "{0}/api/v2/organizations/{1}/oauth-clients/{2}".format(
            self.base_url,
            self.organization,
            self.id
        )

    @property
    def read_url(self):
        return "{0}/api/v2/organizations/{1}/oauth-clients/{2}".format(
            self.base_url,
            self.organization,
            self.id
        )