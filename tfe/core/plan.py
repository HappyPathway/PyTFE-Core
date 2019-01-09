import os
import json
import logging

from tfe.core.tfe import Validator, TFEObject


class Plan(TFEObject):   

    _base_dir = os.path.dirname(__file__)

    fields = [
        "plan_id"
    ]

    def __init__(self, plan_id=None):
        super()
        self.id = None

        if plan_id:
            self.id = plan_id
        else:
            self.id = None
        Plan.validator = type("{0}Validator".format(self.__class__.__name__))
        
        logging.basicConfig(
            filename=self.logfile, 
            format='%(asctime)-15s com.happypathway.tfe.%(name)s: %(message)s'
        )

        Plan.logger = logging.getLogger(self.__class__.__name__)
        Plan.validator =  type("{0}Validator".format(self.__class__.__name__), 
                                        (Validator, ), 
                                        dict(_fields=self.__class__.fields))()
        
    @property
    def read_url(self):
        return "{0}/api/v2/plans/{1}".format(
            self.base_url,
            self.id
        )
    
    def __repr__(self):
        return self.id