from datetime import datetime, timedelta
import json
import requests as requests

from resources.lang.enGB.logs import *
from parameters import temp_unit
from log.log import log_outbound, log_internal
from config.config import get_cfg_details_oauthToken, get_cfg_details_oauthTokenExpiry


from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class Nest():

    nest_session = requests.Session()

    nesturl_api = 'https://developer-api.nest.com/'

    def __init__(self):
        #
        self._redirect_url = ''
        #
        self._tokencheck()
        self.createSession()

    def createSession(self):
        with requests.Session() as s:
            s.headers.update({'Authorization': self._header_token(),
                              'Connection': 'close',
                              'content-type': 'application/json'})
        self.nestSession = s

    def _header_token(self):
        return 'Bearer {authcode}'.format(authcode=get_cfg_details_oauthToken())

    def _tokencheck(self):
        # TODO
        # log_general('Checking Auth Token', dvc_id=self.dvc_id())
        if self._checkToken():
            return True
        else:
            # TODO - capability to get new token when old one expires
            return False

    def _checkToken(self):
        exp = get_cfg_details_oauthTokenExpiry()
        if bool(get_cfg_details_oauthTokenExpiry()):
            return datetime.datetime.now() < exp
        else:
            return False

    def _read_json_all(self):
        return self._read_nest_json()

    def _read_json_metadata(self):
        return self._read_nest_json(model='metadata')

    def _read_json_devices(self, device_type=False, device_id=False):
        if bool(device_type) and bool(device_id):
            device_url = '{device_type}/{device_id}'.format(device_type=device_type, device_id=device_id)
        else:
            device_url = ''
        return self._read_nest_json(model='bindings'+device_url)

    def _read_json_structures(self):
        return self._read_nest_json(model='structures')

    def _read_nest_json(self, model=''):
        #
        r = self.nestSession.get(self._get_url() + model)
        #
        if len(r.history) > 0:
            if r.history[0].is_redirect:
                self._set_redirect_url = r.url
        #
        if str(r.status_code).startswith('4'):
            return False
        #
        return r.json()

    def _send_nest_json (self, json_cmd, model, device, id, retry=0):
        #
        if retry >= 2:
            return False
        #
        url2 = '{model}/{device}/{id}'.format(model=model, device=device, id=id)
        #
        r = self.nestSession.put(self._get_url() + url2,
                                 data=json.dumps(json_cmd))
        #
        if len(r.history) > 0:
            if r.history[0].is_redirect:
                self._redirect_url = r.url
        #
        if str(r.status_code).startswith('4'):
            return False
        #
        return r.json()

    def _get_url(self):
        #
        if self._redirect_url != '':
            return self._redirect_url
        else:
            return self.nesturl_api

    def getAll(self):
        data = self._read_json_all()
        del data['metadata']
        return data