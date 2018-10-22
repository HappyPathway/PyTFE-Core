import requests
import os
from jinja2 import Template
from functools import partial
import urllib
import json
import sys
import logging


from tfe.core.tfe import sanitize_path
from tfe.core.session import TFESession
from tfe.core.exception import RaisesTFEException, TFESessionException
from tfe.core.tfe import TFEObject, Validator



class Sentinel(TFEObject):

    _base_dir = os.path.dirname(__file__)
    json_template = ""
    hcl_template = ""
    fields = [
        "organization",
        "workspace_id"
    ]

    def __init__(self, organization=None, **kwargs):
        super()
        self.organization = organization
        self.policy_id = None

        Sentinel.validator =  type("{0}Validator".format(self.__class__.__name__), 
                                        (Validator, ), 
                                        dict(_fields=self.__class__.fields))()

        logging.basicConfig(format='%(asctime)-15s com.happypathway.tfe.%(name)s: %(message)s')
        Sentinel.logger = logging.getLogger(self.__class__.__name__)
        for k, v in kwargs.items():
            setattr(self, k, v)

        with open("{0}/templates/json/sentinel.json.j2".format(self._base_dir)) as vars_template:
            Sentinel.json_template = Template(vars_template.read())

        with open("{0}/templates/hcl/sentinel.j2".format(self._base_dir)) as vars_template:
            Sentinel.hcl_template = Template(vars_template.read())



    @property
    def create_url(self):
        return "{0}/api/v2/organizations/{1}/policies".format(
            self.base_url,
            self.organization
        )
        
    @property
    def read_url(self):
        return "{0}/api/v2/policies/{1}".format(
            self.base_url,
            self.policy_id
        )

    @property
    def upload_url(self):
        return "{0}/api/v2/policies/{1}".format(
            self.base_url,
            self.policy_id
        )

    
    def upload(self, policy_path):
        _path = sanitize_path(policy_path)
        cur_dir = os.getcwd()
        self.logger.info("Changing Directory to {0}".format(_path))
        os.chdir(os.path.dirname(_path))
        self.logger.info("Uploading {0}".format(_path))
        exit_code = os.system(
            'curl --request PUT -F "data=@{0}" {1}'.format(policy_path, self.upload_url)
        )
        self.logger.info("Changing Directory back to {0}".format(
                cur_dir
            )
        )
        os.chdir(cur_dir)
        return exit_code