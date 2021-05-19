import requests
import os
import tarfile
from jinja2 import Template
from functools import partial
import urllib
import json
import sys
import logging

from tfe.core.tfe import sanitize_path
from tfe.core.session import TFESession
from tfe.core.exception import RaisesTFEException, TFESessionException, TFEAttributeError
from tfe.core.organization import Organization
from tfe.core.tfe import _Create, TFEObject, Validator

class RegistryModule(TFEObject):    
    
    _base_dir = os.path.dirname(__file__)
    json_template = None
    hcl_template = None
    cleanup = False
    fields = [
        "repo", 
        "oauth_token_id",
        "organization",
        "name",
        "provider",
        "version"
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
        
        RegistryModule.logger = logging.getLogger(self.__class__.__name__)
        RegistryModule.validator =  type("{0}Validator".format(self.__class__.__name__), 
                                        (Validator, ), 
                                        dict(_fields=self.__class__.fields))()
        with open("{0}/templates/json/registry_module.json.j2".format(self._base_dir)) as _template:
            RegistryModule.json_template = Template(_template.read())

    def create_vcs(self, repo, oauth_token_id):
        self.repo = repo
        self.oauth_token_id = oauth_token_id
        self.create()


    def create_sparse(self, organization, name, provider, version, module_path):
        self.validator.validate()
        self.organization = organization
        self.name = name
        self.provider = provider
        self.version = version
        self.module_path = module_path
        self._create_module()
        self._create_version()
        self._upload(module_path)

        
    def _create_module(self):
        template_path = "{0}/templates/json/create_module.json.j2".format(
            self._base_dir
        )
        with open(template_path) as _template:
            template = Template(_template.read())
        
        rendered_json = self.render_json(template=template)
        resp = self.session.post(
            "{0}/api/v2/organizations/{1}/registry-modules".format(
                self.base_url,
                self.organization
            ),
            data=json.dumps(
                rendered_json
            )
        )
        resp.raise_for_status()


    def _create_version(self):
        # https://app.terraform.io/api/v2/registry-modules/my-organization/my-module/aws/versions
        template_path = "{0}/templates/json/create_registry_version.json.j2".format(
            self._base_dir
        )
        with open(template_path) as _template:
            template = Template(_template.read())
        
        rendered_json = self.render_json(template=template)
        resp = self.session.post(
            "{0}/api/v1/modules{1}/registry-modules/{2}/{3}/versions".format(
                self.base_url,
                self.organization,
                self.name,
                self.provider
            ),
            data=json.dumps(
                rendered_json
            )
        )
        resp.raise_for_status()
        self.upload_url = resp.json().get("data").get("links").get("upload")


    def _upload(self, config_path):
        _path = sanitize_path(config_path)
        cur_dir = os.getcwd()
        self.logger.info("Changing Directory to {0}".format(_path))
        os.chdir(_path)
        
        def _filter(tar_info):
            self.logger.debug("inspecting {0}".format(tar_info.name))
            if tar_info.name != "{0}.tar.gz".format(self.name) and ".git" not in tar_info.name and ".terraform" not in tar_info.name:
                return tar_info
            else:
                return None

        with tarfile.open("{0}.tar.gz".format(self.name), "w:gz") as _tar:
            _tar.add(".", filter=_filter)

       
        # tf_config = {'data': open("terraform_config.tar.gz", "rb")}
        # headers = self.session_headers
        # headers["Content-Type"] = "application/octet-stream"
        self.logger.info("Uploading {0}/{1}.tar.gz".format(
                os.getcwd(),
                self.name
            )
        )

        cur_content_type = self.session.headers.get("Content-Type")
        exit_code = os.system(
            'curl --request PUT -F "data=@{0}" {1}'.format("{0}.tar.gz".format(self.name), self.upload_url)
        )
        # self.session.headers["Content-Type"] = "application/octet-stream"
        #upload_resp = self.session.put(
        #    self.upload_url,
        #    files=tf_config
        #)
        self.session.headers["Content-Type"] = cur_content_type

        # move back into proper directory
        if self.cleanup:
            self.logger.info(
                "Removing {0}".format(
                    os.path.join(
                        os.getcwd(),
                        "terraform_config.tar.gz"
                    )
                )
            )
            os.unlink("terraform_config.tar.gz")

        self.logger.info("Changing Directory back to {0}".format(
                cur_dir
            )
        )
        os.chdir(cur_dir)
        return exit_code


    def list(self, list_url=None):
        if not TFESession.session:
            raise TFESessionException("Session is not iniatialized")
        if not self.list_url:
            raise TFEAttributeError("Object: {0} does not have list_url".format(
                    self.__class__.__name__
                )
            )
        self.logger.debug(
            "listing items from {0}".format(self.list_url)
        )
        if not list_url:
            resp = TFESession.session.get(self.list_url)
        else:
            resp = TFESession.session.get(list_url)
        resp.raise_for_status()
        return resp.json()
        

    @property
    def list_url(self):
        return "{0}/api/registry/v1/modules".format(
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
        return "{0}/api/registry/v1/modules/{1}/{2}/{3}/{4}".format(
            self.base_url,
            self.organization,
            self.name,
            self.provider,
            self.version
        )

    @property
    def read_url(self):
        return "{0}/api/registry/v1/modules/{1}/{2}/{3}/{4}".format(
            self.base_url,
            self.organization,
            self.name,
            self.provider,
            self.version
        )