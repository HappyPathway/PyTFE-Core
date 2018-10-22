import requests
import os
from jinja2 import Template
from functools import partial
import urllib
import json
import logging

from tfe.core.session import TFESession
from tfe.core.exception import RaisesTFEException, TFESessionException
from tfe.core.variable import Variable
from tfe.core.tfe import TFEObject, Validator


class TeamAccess(TFEObject):
    
    _base_dir = os.path.dirname(__file__)
    json_template = None
    hcl_template = None

    fields = [
        "access",
        "workspace",
        "team"
    ]

    def __init__(self, team_access_id=None):
        super()
        if team_access_id:
            self.id = team_access_id
        else:
            self.id = None
        logging.basicConfig(format='%(asctime)-15s %(message)s')
        TeamAccess.logger = logging.getLogger(self.__class__.__name__)
        TeamAccess.validator =  type("{0}Validator".format(self.__class__.__name__), 
                                        (Validator, ), 
                                        dict(_fields=self.__class__.fields))()
        
        with open("{0}/templates/json/teamaccess.json.j2".format(self._base_dir)) as _template:
            TeamAccess.json_template = Template(_template.read())

        with open("{0}/templates/hcl/team_access.j2".format(self._base_dir)) as _template:
            TeamAccess.hcl_template = Template(_template.read())

        try:
            if self.id:
                self.get()
        except TypeError as te:
            self.logger.info(str(te))

    @property
    def create_url(self):
        return "{0}/api/v2/team-workspaces".format(
            self.base_url
        )

    @property
    def list_url(self):
        return "{0}/api/v2/team-workspaces?filter%5Bworkspace%5D%5Bid%5D={1}".format(
            self.base_url,
            self.workspace
        )

    @property
    def read_url(self):
        return "{0}/api/v2/team-workspaces/{1}".format(
            self.base_url,
            self.id
        )

    @property
    def update_url(self):
        return "{0}/api/v2/team-workspaces/{1}".format(
            self.base_url,
            self.id
        )

    @property
    def delete_url(self):
        return "{0}/api/v2/team-workspaces/{1}".format(
            self.base_url,
            self.id
        )

