import json
import threading
from datetime import datetime

import requests as requests
import sseclient

from common_functions.redirect_url import check_redirect
from config.config import get_cfg_details_oauthToken, get_cfg_details_oauthTokenExpiry
from log.log import log_outbound, log_internal
from service.data_stripping import *
from resources.global_resources.log_vars import logPass, logFail, logException
from resources.global_resources.nest_uris import *
from resources.lang.enGB.logs import *


class Nest():

    sessionNest_REST = requests.Session()

    def __init__(self):
        #
        self._redirect_url = ''
        #
        self._tokencheck()
        self.createSessions()
        #
        self._structures = {}
        self._thermostats = {}
        self._smokes = {}
        self._cameras = {}
        #
        self._createCache()
        self.threadStream()

    def createSessions(self):
        #
        self.sessionNest_REST.headers = {'Authorization': 'Bearer {authcode}'.format(authcode=get_cfg_details_oauthToken()),
                                         'Connection': 'close',
                                         'content-type': 'application/json'}

    def threadStream(self):
        t = threading.Thread(target=self.nest_stream)
        t.start()

    def _tokencheck(self):
        log_internal(logPass, logDescNest_checkingAuth)
        if self._checkToken():
            return True
        else:
            # TODO - capability to get new token when old one expires
            return False

    def _checkToken(self):
        exp = get_cfg_details_oauthTokenExpiry()
        if bool(get_cfg_details_oauthTokenExpiry()):
            return datetime.now() < exp
        else:
            return False

    def _read_nest_json(self, uri=''):
        #
        r = self.sessionNest_REST.get('{url}{uri}'.format(url=self._get_url(), uri=uri))
        #
        redirect = check_redirect(r)
        if bool(redirect):
            self._redirect_url = redirect.replace(uri, '')
            return self._read_nest_json(uri)
        #
        r_pass = True if r.status_code == requests.codes.ok else False
        result = logPass if r_pass else logFail
        #
        log_outbound(result,
                     self._get_url(), '', 'GET', uri, '-', '-',
                     r.status_code)
        #
        if r_pass:
            return r.json()
        else:
            return False

    def _send_nest_json(self, json_cmd, uri, retry=0):
        #
        if retry >= 2:
            return False
        #
        r = self.sessionNest_REST.put('{url}{uri}'.format(url=self._get_url(), uri=uri),
                                      data=json.dumps(json_cmd))
        #
        redirect = check_redirect(r)
        if bool(redirect):
            self._redirect_url = redirect.replace(uri, '')
            return self._send_nest_json(json_cmd, uri)
        #
        r_pass = True if r.status_code == requests.codes.ok else False
        result = logPass if r_pass else logFail
        #
        log_outbound(result,
                     self._get_url(), '', 'PUT', uri, '-', json_cmd,
                     r.status_code)
        #
        if r_pass:
            return r.json()
        else:
            return False

    def _send_nest_value(self, value, uri, retry=0):
        #
        if retry >= 2:
            return False
        #
        r = self.sessionNest_REST.put('{url}{uri}'.format(url=self._get_url(), uri=uri),
                                      data=str(value))
        #
        redirect = check_redirect(r)
        if bool(redirect):
            self._redirect_url = redirect.replace(uri, '')
            return self._send_nest_value(value, uri)
        #
        r_pass = True if r.status_code == requests.codes.ok else False
        result = logPass if r_pass else logFail
        #
        log_outbound(result,
                     self._get_url(), '', 'PUT', uri, '-', value,
                     r.status_code)
        #
        if r_pass:
            return r.json()
        else:
            return False

    def _get_url(self):
        #
        if self._redirect_url != '':
            return self._redirect_url
        else:
            return url_nest

    def nest_stream(self):
        #
        headers = {'Authorization': 'Bearer {authcode}'.format(authcode=get_cfg_details_oauthToken()),
                   'Accept': 'text/event-stream'}
        #
        try:
            while True:
                #
                r = requests.get(self._get_url(), headers=headers, stream=True)
                #
                redirect_url = check_redirect(r)
                if bool(redirect_url):
                    self._redirect_url = redirect_url.replace(uri_nest_devices, '')
                    r = requests.get(uri_nest_devices, headers=headers, stream=True)
                #
                log_internal(logPass, logDescNest_streamStart)
                #
                client = sseclient.SSEClient(r)
                for event in client.events():
                    event_type = event.event
                    #
                    # Different event types:
                    # 'open' - The event stream has been opened (not always received here)
                    # 'put' - The data has changed (or initial data sent)
                    # 'keep-alive' - No data updates. Receiving an HTTP header to keep the connection open
                    # 'auth_revoked' - The API authorization has been revoked
                    # 'error' - Error occurred, such as connection closed.
                    #
                    if event_type == 'put':
                        #
                        logDesc = []
                        #
                        json_data = json.loads(event.data)
                        json_data = strip_data(json_data['data'])
                        #
                        if self._structures != json_data['structures']:
                            self._structures = json_data['structures']
                            logDesc.append('structures')
                        if self._thermostats != json_data['devices']['thermostats']:
                            self._thermostats = json_data['devices']['thermostats']
                            logDesc.append('thermostats')
                        if self._smokes != json_data['devices']['smoke_co_alarms']:
                            self._smokes = json_data['devices']['smoke_co_alarms']
                            logDesc.append('smoke_co_alarms')
                        if self._cameras != json_data['devices']['cameras']:
                            self._cameras = json_data['devices']['cameras']
                            logDesc.append('cameras')
                        #
                        log_internal(logPass, logDescNest_streamUpdate, description=logDesc)
                        #
                    elif event_type == 'auth_revoked':
                        raise Exception('API authorization has been revoked')
                    #
                log_internal(logFail, logDescNest_streamEnd)
                #
        except Exception as e:
            log_internal(logException, logDescNest_streamError, exception=e)

    def _createCache(self):
        json_data = self._getAll()
        self._structures = json_data['structures']
        self._thermostats = json_data['devices']['thermostats']
        self._smokes = json_data['devices']['smoke_co_alarms']
        self._cameras = json_data['devices']['cameras']

    def _getAll(self):
        data = self._read_nest_json()
        data = strip_data(data)
        return data

    def _getStructures(self):
        data = self._read_nest_json(uri_nest_structures)
        data = strip_structures(data)
        return data

    def _getStructure(self, structure_id):
        data = self._read_nest_json(uri_nest_devices_structure.format(structure_id=structure_id))
        data = strip_structure(data)
        return data

    def _getDevices(self):
        data = self._read_nest_json(uri_nest_devices)
        data = strip_devices(data)
        return data

    def _getDevicesType(self, device_type):
        data = self._read_nest_json(uri_nest_devices_type.format(device_type=device_type))
        #
        if device_type == 'thermostats':
            data = strip_thermostats(data)
        elif device_type == 'smoke_co_alarms':
            data = strip_smokes(data)
        elif device_type == 'cameras':
            data = strip_cameras(data)
        #
        return data

    def _getDevice(self, device_type, device_id):
        data = self._read_nest_json(uri_nest_device_specific.format(device_type=device_type,
                                                                    device_id=device_id))
        #
        if device_type == 'thermostats':
            data = strip_thermostats(data)
        elif device_type == 'smoke_co_alarms':
            data = strip_smokes(data)
        elif device_type == 'cameras':
            data = strip_cameras(data)
        #
        return data

    def getAll(self):
        return {'structures': self._structures,
                'thermostats': self._thermostats,
                'smoke_co_alarms': self._smokes,
                'cameras': self._cameras}

    def getStructures(self):
        return {'structures': self._structures}

    def getStructure(self, structure_id):
        return {'structures': {structure_id: self._structures[structure_id]}}

    def getDevices(self):
        return {'thermostats': self._thermostats,
                'smoke_co_alarms': self._smokes,
                'cameras': self._cameras}

    def getDevicesType(self, device_type):
        if device_type == 'thermostats':
            return self.getThermostats()
        elif device_type == 'smoke_co_alarms':
            return self.getSmokes()
        elif device_type == 'cameras':
            return self.getCameras()
        else:
            return False

    def getThermostats(self):
        return {'thermostats': self._thermostats}

    def getSmokes(self):
        return {'smoke_co_alarms': self._smokes}

    def getCameras(self):
        return {'cameras': self._cameras}

    def getDevice(self, device_type, device_id):
        if device_type == 'thermostats':
            return self.getThermostat(device_id)
        elif device_type == 'smoke_co_alarms':
            return self.getSmoke(device_id)
        elif device_type == 'cameras':
            return self.getCamera(device_id)
        else:
            return False

    def getThermostat(self, device_id):
        return {'thermostats': {device_id: self._thermostats[device_id]}}

    def getSmoke(self, device_id):
        return {'smoke_co_alarms': {device_id: self._smokes[device_id]}}

    def getCamera(self, device_id):
        return {'cameras': {device_id: self._cameras[device_id]}}

    def setThermostat(self, device_id, command):
        #
        if len(command) == 1:
            # if single field, send to 'dedicated' Nest API
            #
            for k in command:
                key = k
                value = command[k]
            #
            return self._send_nest_value(value,
                                         uri_nest_device_specific_value.format(device_type='thermostats',
                                                                               device_id=device_id,
                                                                               field=key))
            #
        else:
            # if multiple fields, send as a 'batch' request to Nest API
            #
            for k in command:
                if k.endswith('_c'):
                    command[k] = float(command[k])
                elif k.endswith('_f'):
                    command[k] = int(command[k])
            #
            return self._send_nest_json(command,
                                        uri_nest_device_specific.format(device_type='thermostats',
                                                                        device_id=device_id))
