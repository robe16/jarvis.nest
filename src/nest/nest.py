from datetime import datetime
import thread
import json
import requests as requests

from resources.lang.enGB.logs import *
from parameters import temp_unit
from log.log import log_outbound, log_internal
from config.config import get_cfg_details_oauthToken, get_cfg_details_oauthTokenExpiry
from stream import nest_stream


class Nest():

    sessionNest_REST = requests.Session()
    sessionNest_RESTstream = requests.Session()

    nesturl_api = 'https://developer-api.nest.com/'

    def __init__(self):
        #
        self._redirect_url = ''
        #
        self._tokencheck()
        self.createSessions()

    def createSessions(self):
        #
        with requests.Session() as s:
            s.headers.update({'Authorization': 'Bearer {authcode}'.format(authcode=get_cfg_details_oauthToken()),
                              'Connection': 'close',
                              'content-type': 'application/json'})
        self.sessionNest_REST = s

    def threadStream(self):
        thread.start_new_thread(nest_stream, (self._get_url(),))

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

    def _check_redirect(self, r):
        if len(r.history) > 0:
            if r.history[0].is_redirect:
                self._set_redirect_url = r.url

    def _read_nest_json(self, uri=''):
        #
        url = self._get_url()
        #
        r = self.sessionNest_REST.get('{url}{uri}'.format(url=url, uri=uri))
        #
        self._check_redirect(r)
        #
        if str(r.status_code).startswith('4'):
            return False
        #
        return r.json()

    def _send_nest_json(self, json_cmd, model, device, id, retry=0):
        #
        if retry >= 2:
            return False
        #
        url = self._get_url()
        uri = '{model}/{device}/{id}'.format(model=model, device=device, id=id)
        #
        r = self.sessionNest_REST.put('{url}{uri}'.format(url=url, uri=uri),
                                      data=json.dumps(json_cmd))
        #
        self._check_redirect(r)
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
        # TODO - neaten/strip returned data
        data = self._read_nest_json()
        del data['metadata']
        return data

    def getStructures(self):
        #
        data = self._read_nest_json('structures/')
        # TODO - neaten/strip returned data
        #
        return data

    def getStructure(self, structure_id):
        #
        data = self._read_nest_json('devices/{structure_id}'.format(structure_id=structure_id))
        # TODO - neaten/strip returned data
        #
        return data

    def getDevices(self):
        #
        data = self._read_nest_json('devices/')
        # TODO - neaten/strip returned data
        #
        return data

    def getDevicesType(self, device_type):
        #
        data = self._read_nest_json('devices/{device_type}'.format(device_type=device_type))
        # TODO - neaten/strip returned data
        #
        return data

    def getDevice(self, device_type, device_id):
        #
        data = self._read_nest_json('devices/{device_type}/{device_id}'.format(device_type=device_type,
                                                                               device_id=device_id))
        # TODO - neaten/strip returned data
        #
        return data
