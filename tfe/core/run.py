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



class Run(TFEObject):

    _base_dir = os.path.dirname(__file__)
    json_template = ""
    fields = [
        "run_message",
        "workspace_id",
        "configuration_version"
    ]

    def __init__(self, run_id=None, **kwargs):
        super()
        self.run_id = run_id
        self.workspace_id = None
        self.configuration_version = None
        
        Run.validator =  type("{0}Validator".format(self.__class__.__name__), 
                                        (Validator, ), 
                                        dict(_fields=self.__class__.fields))()

        
        logging.basicConfig(
            filename=self.logfile, 
            format='%(asctime)-15s com.happypathway.tfe.%(name)s: %(message)s'
        )
        
        Run.logger = logging.getLogger(self.__class__.__name__)
        for k, v in kwargs.items():
            setattr(self, k, v)

        with open("{0}/templates/json/run.json.j2".format(self._base_dir)) as vars_template:
            Run.json_template = Template(vars_template.read())


    @property
    def create_url(self):
        return "{0}/api/v2/runs".format(
            self.base_url
        )
        
    @property
    def read_url(self):
        return "{0}/api/v2/runs/{1}".format(
            self.base_url,
            self.run_id
        )

    @property
    def list_url(self):
        return "{0}/api/v2/workspaces/{1}/runs".format(
            self.base_url,
            self.workspace_id
        )

    @property
    def status(self):
        url = "{0}/api/v2/runs/{1}".format(
            self.base_url,
            self.run_id
        )
        try:
            resp = self.session.get(url)
            return resp.json().get("data").get("attributes").get("status")
        except Exception as e:
            self.logger.error(str(e))
            return None

    @property
    def details(self):
        url = "{0}/api/v2/runs/{1}?include=configuration_version.ingress_attributes,created_by".format(
            self.base_url,
            self.run_id
        )
        try:
            resp = self.session.get(url)
            return resp.json()
        except Exception as e:
            self.logger.error(str(e))
            return None
            
    def apply(self):
        # POST /runs/:run_id/actions/apply
        resp = self.session.post(
            "{0}/api/v2/runs/{1}/actions/apply".format(
                self.base_url,
                self.run_id
            )
        )
        resp.raise_for_status()
        return resp.json()


    def discard(self):
        # POST /runs/:run_id/actions/discard
        resp = self.session.post(
            "{0}/api/v2/runs/{1}/actions/discard".format(
                self.base_url,
                self.run_id
            )
        )
        return resp.status_code


    def cancel(self):
        # POST /runs/:run_id/actions/cancel
        resp = self.session.post(
            "{0}/api/v2/runs/{1}/actions/cancel".format(
                self.base_url,
                self.run_id
            )
        )
        return resp.status_code


    def force_cancel(self):
        # POST /runs/:run_id/actions/force-cancel
        resp = self.session.post(
            "{0}/api/v2/runs/{1}/actions/force-cancel".format(
                self.base_url,
                self.run_id
            )
        )
        return resp.status_code

    def destroy(self):
        resp = self.session.post(
            "{0}/api/v2/runs".format(
                self.base_url
            ),
            data=json.dumps(self.json_template.render(is_destroy=True))
        )
        return resp.status_code