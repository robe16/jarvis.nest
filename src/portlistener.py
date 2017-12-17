from bottle import HTTPError
from bottle import get, post
from bottle import request, run, HTTPResponse

from config.config import get_cfg_serviceid, get_cfg_name_long, get_cfg_name_short, get_cfg_groups, get_cfg_subservices
from log.log import log_inbound, log_internal
from resources.lang.enGB.logs import *
from resources.global_resources.variables import *
from resources.global_resources.exposed_apis import *
from nest.nest import Nest


def start_bottle(self_port):

    ################################################################################################
    # Create device
    ################################################################################################

    _device = Nest()

    log_internal(True, logDescDeviceObjectCreation, desc='success')

    ################################################################################################
    # Enable cross domain scripting
    ################################################################################################

    def enable_cors(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET'
        return response

    ################################################################################################
    # Service info & Groups
    ################################################################################################

    @get(uri_config)
    def get_config():
        #
        try:
            client = request.headers[service_header_clientid_label]
        except:
            client = request['REMOTE_ADDR']
        #
        try:
            #
            data = {'service_id': get_cfg_serviceid(),
                    'name_long': get_cfg_name_long(),
                    'name_short': get_cfg_name_short(),
                    'subservices': get_cfg_subservices(),
                    'groups': get_cfg_groups()}
            #
            status = httpStatusSuccess
            #
            log_inbound(True, client, request.url, 'GET', status)
            #
            return HTTPResponse(body=data, status=status)
            #
        except Exception as e:
            status = httpStatusServererror
            log_inbound(False, client, request.url, 'GET', status, exception=e)
            raise HTTPError(status)

    ################################################################################################
    # All data
    ################################################################################################

    @get(uri_get_all)
    def get_get_all():
        #
        try:
            client = request.headers[service_header_clientid_label]
        except:
            client = request['REMOTE_ADDR']
        #
        try:
            #
            r = _device.getAll()
            #
            if not bool(r):
                status = httpStatusFailure
            else:
                status = httpStatusSuccess
            #
            log_inbound(True, client, request.url, 'GET', status)
            #
            if isinstance(r, bool):
                return HTTPResponse(status=status)
            else:
                return HTTPResponse(body=r, status=status)
            #
        except Exception as e:
            status = httpStatusServererror
            log_inbound(False, client, request.url, 'GET', status, exception=e)
            raise HTTPError(status)

    ################################################################################################
    # Structures
    ################################################################################################

    @get(uri_get_structures)
    def get_structures():
        #
        try:
            client = request.headers[service_header_clientid_label]
        except:
            client = request['REMOTE_ADDR']
        #
        try:
            #
            r = _device.getStructures()
            #
            if not bool(r):
                status = httpStatusFailure
            else:
                status = httpStatusSuccess
            #
            log_inbound(True, client, request.url, 'GET', status)
            #
            if isinstance(r, bool):
                return HTTPResponse(status=status)
            else:
                return HTTPResponse(body=r, status=status)
            #
        except Exception as e:
            status = httpStatusServererror
            log_inbound(False, client, request.url, 'GET', status, exception=e)
            raise HTTPError(status)

    @get(uri_get_structure_specific)
    def get_structure_specific(structure_id):
        #
        try:
            client = request.headers[service_header_clientid_label]
        except:
            client = request['REMOTE_ADDR']
        #
        try:
            #
            r = _device.getStructure(structure_id)
            #
            if not bool(r):
                status = httpStatusFailure
            else:
                status = httpStatusSuccess
            #
            log_inbound(True, client, request.url, 'GET', status)
            #
            if isinstance(r, bool):
                return HTTPResponse(status=status)
            else:
                return HTTPResponse(body=r, status=status)
            #
        except Exception as e:
            status = httpStatusServererror
            log_inbound(False, client, request.url, 'GET', status, exception=e)
            raise HTTPError(status)

    ################################################################################################
    # Devices
    ################################################################################################

    @get(uri_get_devices)
    def get_devices():
        #
        try:
            client = request.headers[service_header_clientid_label]
        except:
            client = request['REMOTE_ADDR']
        #
        try:
            #
            r = _device.getDevices()
            #
            if not bool(r):
                status = httpStatusFailure
            else:
                status = httpStatusSuccess
            #
            log_inbound(True, client, request.url, 'GET', status)
            #
            if isinstance(r, bool):
                return HTTPResponse(status=status)
            else:
                return HTTPResponse(body=r, status=status)
            #
        except Exception as e:
            status = httpStatusServererror
            log_inbound(False, client, request.url, 'GET', status, exception=e)
            raise HTTPError(status)

    @get(uri_get_devices_type)
    def get_devices_type(device_type):
        #
        try:
            client = request.headers[service_header_clientid_label]
        except:
            client = request['REMOTE_ADDR']
        #
        try:
            #
            r = _device.getDevicesType(device_type)
            #
            if not bool(r):
                status = httpStatusFailure
            else:
                status = httpStatusSuccess
            #
            log_inbound(True, client, request.url, 'GET', status)
            #
            if isinstance(r, bool):
                return HTTPResponse(status=status)
            else:
                return HTTPResponse(body=r, status=status)
            #
        except Exception as e:
            status = httpStatusServererror
            log_inbound(False, client, request.url, 'GET', status, exception=e)
            raise HTTPError(status)

    @get(uri_get_device_specific)
    def get_devices_specific(device_type, device_id):
        #
        try:
            client = request.headers[service_header_clientid_label]
        except:
            client = request['REMOTE_ADDR']
        #
        try:
            #
            r = _device.getDevice(device_type, device_id)
            #
            if not bool(r):
                status = httpStatusFailure
            else:
                status = httpStatusSuccess
            #
            log_inbound(True, client, request.url, 'GET', status)
            #
            if isinstance(r, bool):
                return HTTPResponse(status=status)
            else:
                return HTTPResponse(body=r, status=status)
            #
        except Exception as e:
            status = httpStatusServererror
            log_inbound(False, client, request.url, 'GET', status, exception=e)
            raise HTTPError(status)

    ################################################################################################

    host='0.0.0.0'
    log_internal(True, logDescPortListener.format(port=self_port), desc='started')
    run(host=host, port=self_port, debug=True)
