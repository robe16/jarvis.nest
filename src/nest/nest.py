from datetime import datetime
import threading
import json
import sseclient
import requests as requests

from discovery.broadcast import broadcast_msg
from common_functions.redirect_url import check_redirect
from resources.global_resources.nest_uris import *
from resources.global_resources.log_vars import logPass, logFail, logException
from resources.lang.enGB.logs import *
from log.log import log_outbound, log_internal
from config.config import get_cfg_details_oauthToken, get_cfg_details_oauthTokenExpiry
from nest.data_stripping import *


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
        self._thermostat = {}
        self._smoke = {}
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

    def _send_nest_json(self, json_cmd, model, device, id, retry=0):
        #
        if retry >= 2:
            return False
        #
        uri = '{model}/{device}/{id}'.format(model=model, device=device, id=id)
        #
        r = self.sessionNest_REST.put('{url}{uri}'.format(url=self._get_url(), uri=uri),
                                      data=json.dumps(json_cmd))
        #
        redirect = check_redirect(r)
        if bool(redirect):
            self._redirect_url = redirect.replace(uri, '')
            return self._send_nest_json(json_cmd, model, device, id)
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
                    if self._thermostat != json_data['devices']['thermostats']:
                        self._thermostat = json_data['devices']['thermostats']
                        logDesc.append('thermostats')
                    if self._smoke != json_data['devices']['smoke_co_alarms']:
                        self._smoke = json_data['devices']['smoke_co_alarms']
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
        except Exception as e:
            log_internal(logException, logDescNest_streamError, exception=e)

    def _createCache(self):
        json_data = self.getAll()
        self._structures = json_data['structures']
        self._thermostat = json_data['devices']['thermostats']
        self._smoke = json_data['devices']['smoke_co_alarms']
        self._cameras = json_data['devices']['cameras']

    def getAll(self):
        data = self._read_nest_json()
        data = strip_data(data)
        return data

    def getStructures(self):
        data = self._read_nest_json(uri_nest_structures)
        data = strip_structures(data)
        return data

    def getStructure(self, structure_id):
        data = self._read_nest_json(uri_nest_devices_structure.format(structure_id=structure_id))
        data = strip_structure(data)
        return data

    def getDevices(self):
        data = self._read_nest_json(uri_nest_devices)
        data = strip_devices(data)
        return data

    def getDevicesType(self, device_type):
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

    def getDevice(self, device_type, device_id):
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
