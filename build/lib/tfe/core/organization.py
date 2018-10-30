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
from tfe.core.tfe import TFEObject, Validator


def log_config():
    logger = logging.getLogger() # this gets the root logger
    lhStdout = logger.handlers[0]  # stdout is the only handler initially
    # ... here I add my own handlers 
    f = open("/tmp/debug","w")          # example handler
    lh = logging.StreamHandler(f)
    logger.addHandler(lh)
    logger.removeHandler(lhStdout)

class Organization(TFEObject):
    
    _base_dir = os.path.dirname(__file__)
    json_template = None
    hcl_template = None

    fields = [
        "organization", 
        "email",
        "session_timeout",
        "session_remember",
        "collaborator_auth_policy"
    ]

    def __init__(self, organization=None):
        super()
        
        logging.basicConfig(
            filename=self.logfile, 
            format='%(asctime)-15s com.happypathway.tfe.%(name)s: %(message)s'
        )
        
        Organization.logger = logging.getLogger(self.__class__.__name__)

        Organization.validator =  type("{0}Validator".format(self.__class__.__name__), 
                                        (Validator, ), 
                                        dict(_fields=self.__class__.fields))()
        self.create_url = "{0}/api/v2/organizations".format(
            self.base_url
        )

        if organization:
            self.organization = organization
            self.list_url = "{0}/api/v2/organizations/{1}".format(
                self.base_url,
                self.organization
            )

            self.read_url = "{0}/api/v2/organizations/{1}".format(
                self.base_url,
                self.organization
            )

            self.update_url = "{0}/api/v2/organizations/{1}".format(
                self.base_url,
                self.organization
            )

            self.delete_url = "{0}/api/v2/organizations/{1}".format(
                self.base_url,
                self.organization
            )

            self.token_url = "{0}/api/v2/organizations/{1}/authentication-token".format(
                self.base_url,
                self.organization
            )

            with open("{0}/templates/json/organization.json.j2".format(self._base_dir)) as _template:
                Organization.json_template = Template(_template.read())

            with open("{0}/templates/hcl/organization.j2".format(self._base_dir)) as _template:
                Organization.hcl_template = Template(_template.read())

        try:
            self.get()
        except TypeError as te:
            self.logger.info(str(te))


    def mktoken(self):
        # POST /organizations/:organization_name/authentication-token 
        try:
            resp = self.session.post(self.token_url)
            resp.raise_for_status()
        except:
            self.logger.info(
                dict(
                    response_code=resp.status_code,
                    error=resp.text
                )
            )
        resp.raise_for_status()
        return resp.json().get("data").get("attributes").get("token")


    def rmtoken(self):
        try:
            resp = self.session.delete(self.token_url)
            resp.raise_for_status()
        except:
            self.logger.info(
                dict(
                    response_code=resp.status_code,
                    error=resp.text
                )
            )
        resp.raise_for_status()   
        return resp.status_code


    def __repr__(self):
        return self.organization


