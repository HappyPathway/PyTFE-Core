
import requests
import sys


from tfe.core.exception import RaisesTFEException

class TFESession(object):
    base_url = "https://app.terraform.io"
    atlas_token = None
    session_headers = None
    session = None

    def __init__(self, api, token):
        TFESession.atlas_token = token
        TFESession.base_url = api
        TFESession.session = requests.Session()
        TFESession.session.headers = {
            "Authorization": "Bearer {0}".format(token),
            "Content-Type": "application/vnd.api+json"
        }
        TFESession.session_headers = TFESession.session.headers