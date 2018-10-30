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
from tfe.core.variable import Variable
from tfe.core.tfe import TFEObject, Validator


class Team(TFEObject):
    
    _base_dir = os.path.dirname(__file__)
    json_template = None
    hcl_template = None

    fields = [
        "name"
    ]

    def __init__(self, team_id=None):
        super()
        self.organization = None
        if team_id:
            self.id = team_id
        else:
            self.id = None
        
        logging.basicConfig(
            filename=self.logfile, 
            format='%(asctime)-15s com.happypathway.tfe.%(name)s: %(message)s'
        )
        
        Team.logger = logging.getLogger(self.__class__.__name__)
        Team.validator =  type("{0}Validator".format(self.__class__.__name__), 
                                        (Validator, ), 
                                        dict(_fields=self.__class__.fields))()

        with open("{0}/templates/json/team.json.j2".format(self._base_dir)) as _template:
            Team.json_template = Template(_template.read())

        with open("{0}/templates/hcl/team.j2".format(self._base_dir)) as _template:
            Team.hcl_template = Template(_template.read())

        try:
            if self.id:
                self.get()
        except TypeError as te:
            self.logger.info(str(te))

    @property
    def list_url(self):
        return "{0}/api/v2/organizations/{1}/teams".format(
            self.base_url,
            self.organization
        )

    @property
    def create_url(self):
        return "{0}/api/v2/organizations/{1}/teams".format(
            self.base_url,
            self.organization
        )

    @property
    def read_url(self):
        return "{0}/api/v2/teams/{1}".format(
            self.base_url,
            self.id
        )

    @property
    def delete_url(self):
        return "{0}/api/v2/teams/{1}".format(
            self.base_url,
            self.id
        )

