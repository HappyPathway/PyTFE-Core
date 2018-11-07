
import requests
import os
from jinja2 import Template
from functools import partial
import urllib
import json
import hcl
import logging
import sys

from tfe.core.session import TFESession
from tfe.core.exception import TFEValidationError, TFEException, RaisesTFEException, TFESessionException, TFEAttributeError

def sanitize_path(path):
    path = os.path.expanduser(path)
    path = os.path.expandvars(path)
    path = os.path.abspath(path)
    return path

class Validator(object):

    _fields = []
    validator = None

    def __init__(self, obj=None):
        if not obj:
            obj = dict() 
        for k, v in obj.items():
            if k in self._fields:
                setattr(self, k, v)
    
    def __setattr__(self, k, v):
        if k in self._fields:
            self.__dict__[k] = v

    def validate(self):
        for field in self._fields:
            if field not in dir(self):
                raise TFEValidationError(
                    "missing: {0}".format(field)
                )
        else: 
            return True




class _Create(Validator): pass

class TFEObject(TFESession):   

    _base_dir = os.path.dirname(__file__)
    json_template = None
    hcl_template = None
    fields = []
    list_url = None
    create_url = None
    read_url = None
    update_url = None
    delete_url = None
    validator = None
    logger = None
    logfile = None 

    def __init__(self, _id=None):
        super()
        
        for field in self.fields:
            setattr(self, field, None)
            
        logging.basicConfig(
            filename=self.logfile, 
            format='%(asctime)-15s com.happypathway.tfe.%(name)s: %(message)s'
        )

        TFEObject.logger = logging.getLogger(__name__)
        self._id = _id
        if not self.__class__.json_template:
            template_path = "{0}/templates/json/{1}.json.j2".format(
                self._base_dir, 
                self.__class__.__name__.lower()
            )
            try:
                with open(template_path) as _template:
                    self.__class__.json_template = Template(_template.read())
            except IOError as e:
                self.logger.error(str(e))
                self.__class__.json_template = None

        if not self.__class__.hcl_template:
            template_path = "{0}/templates/hcl/{1}.hcl.j2".format(
                self._base_dir, 
                self.__class__.__name__.lower()
            )
            try:
                with open(template_path) as _template:
                    self.__class__.hcl_template = Template(_template.read())
            except IOError:
                self.logger.error(str(e))
                self.__class__.hcl_template = None
        if self._id:
            try:
                self.get()
            except TFEAttributeError:
                pass


    def list(self):
        if not TFESession.session:
            raise TFESessionException("Session is not iniatialized")
        if not self.list_url:
            raise TFEAttributeError("Object: {0} does not have list_url".format(
                    self.__class__.__name__
                )
            )
        try:
            self.logger.debug(
                "listing items from {0}".format(self.list_url)
            )
            resp = TFESession.session.get(self.list_url)
        except Exception as e:
            self.logger.error(str(e))
        try:
            for x in resp.json().get("data"):
                yield self.__class__(x.get("id"))
        except TypeError:
            return []


    def get(self):
        if not TFESession.session:
            raise TFESessionException("Session is not iniatialized")
        if not self.read_url:
            raise TFEAttributeError("Object: {0} does not have read_url".format(
                    self.__class__.__name__
                )
            )
        try:
            self.logger.debug(
                "getting item from {0}".format(self.read_url)
            )
            resp = self.session.get(self.read_url)
            resp.raise_for_status()
        except Exception as e:
            self.logger.error(str(e))
        try:
            self.raw = resp.json()
            attrs = resp.json().get("data").get("attributes")
            self.id = resp.json().get("data").get("id")
            relationships = resp.json().get("data").get("relationships")
        except AttributeError as e:
            self.logger.error(str(e))
            return None

        for k, v in attrs.items():
            self.logger.debug("Setting {0}:{1}".format(k, v))
            try:
                setattr(self, "_".join(k.split("-")), v)
                setattr(self.validator, k, v)
            except AttributeError as e:
                self.logger.error(str(e))
                
        setattr(self, "relationships", relationships)
        return self.raw



    def delete(self):
        if not TFESession.session:
            raise TFESessionException("Session is not iniatialized")
        if not self.delete_url:
            raise TFEAttributeError("Object: {0} does not have delete_url".format(
                    self.__class__.__name__
                )
            )
        self.logger.debug(
            "deleting from {0}".format(self.delete_url)
        )
        resp = self.session.delete(self.delete_url)
        resp.raise_for_status()
        return resp.status_code


    def create(self, **kwargs):
        if not TFESession.session:
            raise TFESessionException("Session is not iniatialized")
        if not self.create_url:
            raise TFEAttributeError("Object: {0} does not have create_url".format(
                    self.__class__.__name__
                )
            )
        
        for k, v in kwargs.items():
            setattr(self, k, v)
        
        args = dict()
        for attr in self.fields:
            try:
                setattr(self.validator, attr, getattr(self, attr))
                # self.logger.debug("{0}: {1}".format(attr, getattr(self, attr)))
            except AttributeError as e:
                # self.logger.info(str(e))
                continue

        self.validator.validate()
        args[self.__class__.__name__.lower()] = self.validator
        rendered_json = self.json_template.render(
            **args
        )
        payload_failed = False
        try:
            payload = json.loads(rendered_json)
            self.logger.debug(
                json.dumps(
                    payload, 
                    separators=(',', ':'), 
                    indent=4, 
                    sort_keys=True
                )
            )
        except Exception as e:
            payload_failed = True
            self.logger.error("Payload Failed: {0}".format(payload_failed))
            self.logger.error(str(e))
            self.logger.error(rendered_json)
        if payload_failed:
            raise TFEValidationError("Could not load")
        try:
            resp = self.session.post(
                self.create_url,
                data = json.dumps(payload)
            )
            resp.raise_for_status()
        except Exception as e:
            self.logger.error(rendered_json)
            self.logger.error(str(e))
            resp.raise_for_status()

        resp.raise_for_status()
        self.id = resp.json().get("data").get("id")
        return self.__class__(
            resp.json().get("data").get("id")
        )


    def update(self, **kwargs):

        if not TFESession.session:
            raise TFESessionException("Session is not iniatialized")

        if not self.update_url:
            raise TFEAttributeError("Object: {0} does not have update_url".format(
                    self.__class__.__name__
                )
            )
        for k, v in kwargs.items():
            setattr(self, k, v)
            
        args = dict()
        self.logger.debug(
            json.dumps(
                self.fields,
                indent=4,
                sort_keys=True,
                separators=(',', ':')
            )
        )
        for attr in self.fields:
            try:
                setattr(self.validator, attr, getattr(self, attr))
                self.logger.debug("{0}: {1}".format(attr, getattr(self, attr)))
            except AttributeError as e:
                self.logger.info(str(e))
                continue

        args[self.__class__.__name__.lower()] = self.validator
        rendered_json = self.json_template.render(
            **args
        )

        payload = json.loads(rendered_json)
        self.logger.debug(
            json.dumps(
                payload, 
                separators=(',', ':'), 
                indent=4, 
                sort_keys=True
            )
        )
        try:
            resp = self.session.patch(
                self.update_url,
                data = json.dumps(payload)
            )
            resp.raise_for_status()
        except Exception as e:
            self.logger.error(rendered_json)
            self.logger.error(str(e))
        resp.raise_for_status()
        return self.__class__(
            resp.json().get("data").get("id")
        )
    
    def render_hcl(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
            
        args = dict()
        for attr in dir(self):
            try:
                setattr(self.__class__.validator, attr, getattr(self, attr))
            except AttributeError:
                continue

        args[self.__class__.__name__.lower()] = self.__class__.validator
        rendered_hcl = self.hcl_template.render(
            **args
        )
        return rendered_hcl


    def render_json(self, template=None, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
            
        args = dict()
        for attr in dir(self):
            try:
                setattr(self.__class__.validator, attr, getattr(self, attr))
            except AttributeError:
                continue

        args[self.__class__.__name__.lower()] = self.__class__.validator
        if not template:
            rendered_json = self.json_template.render(
                **args
            )
        else:
            rendered_json = template.render(
                **args
            )
        return rendered_json