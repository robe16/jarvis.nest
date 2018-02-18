import threading

from bottle import HTTPError
from bottle import get, post
from bottle import request, run, HTTPResponse

from common_functions.query_to_string import convert_query_to_string
from config.config import get_cfg_port_listener
from config.config import get_cfg_serviceid, get_cfg_name_long, get_cfg_name_short, get_cfg_groups, get_cfg_subservices
from log.log import log_inbound, log_internal
from service.nest import Nest
from resources.global_resources.exposed_apis import *
from resources.global_resources.log_vars import logPass, logFail, logException
from resources.global_resources.variables import *
from resources.lang.enGB.logs import *
from validation.validation import validate_thermostat


def start_bottle(port_threads):

    ################################################################################################
    # Create device
    ################################################################################################

    _device = Nest()

    log_internal(logPass, logDescDeviceObjectCreation, description='success')

    ################################################################################################
    # Enable cross domain scripting
    ################################################################################################

    def enable_cors(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET'
        return response

    ################################################################################################
    # Log arguments
    ################################################################################################

    def _get_log_args(request):
        #
        urlparts = request.urlparts
        #
        try:
            client_ip = request.headers['X-Forwarded-For']
        except:
            client_ip = request['REMOTE_ADDR']
        #
        try:
            server_ip = request.headers['X-Real-IP']
        except:
            server_ip = urlparts.hostname
        #
        try:
            client_user = request.headers[service_header_clientid_label]
        except:
            client_user = request['REMOTE_ADDR']
        #
        server_request_query = convert_query_to_string(request.query) if request.query_string else '-'
        server_request_body = request.body.read() if request.body.read()!='' else '-'
        #
        return {'client_ip': client_ip,
                'client_user': client_user,
                'server_ip': server_ip,
                'server_thread_port': urlparts.port,
                'server_method': request.method,
                'server_request_uri': urlparts.path,
                'server_request_query': server_request_query,
                'server_request_body': server_request_body}

    ################################################################################################
    # Service info & Groups
    ################################################################################################

    @get(uri_config)
    def get_config():
        #
        args = _get_log_args(request)
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
            args['result'] = logPass
            args['http_response_code'] = status
            args['description'] = '-'
            log_inbound(**args)
            #
            return HTTPResponse(body=data, status=status)
            #
        except Exception as e:
            #
            status = httpStatusServererror
            #
            args['result'] = logException
            args['http_response_code'] = status
            args['description'] = '-'
            args['exception'] = e
            log_inbound(**args)
            #
            raise HTTPError(status)

    ################################################################################################
    # All data
    ################################################################################################

    @get(uri_get_all)
    def get_get_all():
        #
        args = _get_log_args(request)
        #
        try:
            #
            r = _device.getAll()
            #
            if not bool(r):
                status = httpStatusFailure
                args['result'] = logFail
            else:
                status = httpStatusSuccess
                args['result'] = logPass
            #
            args['http_response_code'] = status
            args['description'] = '-'
            log_inbound(**args)
            #
            if isinstance(r, bool):
                return HTTPResponse(status=status)
            else:
                return HTTPResponse(body=r, status=status)
            #
        except Exception as e:
            #
            status = httpStatusServererror
            #
            args['result'] = logException
            args['http_response_code'] = status
            args['description'] = '-'
            args['exception'] = e
            log_inbound(**args)
            #
            raise HTTPError(status)

    ################################################################################################
    # Structures
    ################################################################################################

    @get(uri_get_structures)
    def get_structures():
        #
        args = _get_log_args(request)
        #
        try:
            #
            r = _device.getStructures()
            #
            if not bool(r):
                status = httpStatusFailure
                args['result'] = logFail
            else:
                status = httpStatusSuccess
                args['result'] = logPass
            #
            args['http_response_code'] = status
            args['description'] = '-'
            log_inbound(**args)
            #
            if isinstance(r, bool):
                return HTTPResponse(status=status)
            else:
                return HTTPResponse(body=r, status=status)
            #
        except Exception as e:
            #
            status = httpStatusServererror
            #
            args['result'] = logException
            args['http_response_code'] = status
            args['description'] = '-'
            args['exception'] = e
            log_inbound(**args)
            #
            raise HTTPError(status)

    @get(uri_get_structure_specific)
    def get_structure_specific(structure_id):
        #
        args = _get_log_args(request)
        #
        try:
            #
            r = _device.getStructure(structure_id)
            #
            if not bool(r):
                status = httpStatusFailure
                args['result'] = logFail
            else:
                status = httpStatusSuccess
                args['result'] = logPass
            #
            args['http_response_code'] = status
            args['description'] = '-'
            log_inbound(**args)
            #
            if isinstance(r, bool):
                return HTTPResponse(status=status)
            else:
                return HTTPResponse(body=r, status=status)
            #
        except Exception as e:
            #
            status = httpStatusServererror
            #
            args['result'] = logException
            args['http_response_code'] = status
            args['description'] = '-'
            args['exception'] = e
            log_inbound(**args)
            #
            raise HTTPError(status)

    ################################################################################################
    # Devices
    ################################################################################################

    @get(uri_get_devices)
    def get_devices():
        #
        args = _get_log_args(request)
        #
        try:
            #
            r = _device.getDevices()
            #
            if not bool(r):
                status = httpStatusFailure
                args['result'] = logFail
            else:
                status = httpStatusSuccess
                args['result'] = logPass
            #
            args['http_response_code'] = status
            args['description'] = '-'
            log_inbound(**args)
            #
            if isinstance(r, bool):
                return HTTPResponse(status=status)
            else:
                return HTTPResponse(body=r, status=status)
            #
        except Exception as e:
            #
            status = httpStatusServererror
            #
            args['result'] = logException
            args['http_response_code'] = status
            args['description'] = '-'
            args['exception'] = e
            log_inbound(**args)
            #
            raise HTTPError(status)

    @get(uri_get_devices_type)
    def get_devices_type(device_type):
        #
        args = _get_log_args(request)
        #
        try:
            #
            r = _device.getDevicesType(device_type)
            #
            if not bool(r):
                status = httpStatusFailure
                args['result'] = logFail
            else:
                status = httpStatusSuccess
                args['result'] = logPass
            #
            args['http_response_code'] = status
            args['description'] = '-'
            log_inbound(**args)
            #
            if isinstance(r, bool):
                return HTTPResponse(status=status)
            else:
                return HTTPResponse(body=r, status=status)
            #
        except Exception as e:
            #
            status = httpStatusServererror
            #
            args['result'] = logException
            args['http_response_code'] = status
            args['description'] = '-'
            args['exception'] = e
            log_inbound(**args)
            #
            raise HTTPError(status)

    @get(uri_get_device_specific)
    def get_devices_specific(device_type, device_id):
        #
        args = _get_log_args(request)
        #
        try:
            #
            r = _device.getDevice(device_type, device_id)
            #
            if not bool(r):
                status = httpStatusFailure
                args['result'] = logFail
            else:
                status = httpStatusSuccess
                args['result'] = logPass
            #
            args['http_response_code'] = status
            args['description'] = '-'
            log_inbound(**args)
            #
            if isinstance(r, bool):
                return HTTPResponse(status=status)
            else:
                return HTTPResponse(body=r, status=status)
            #
        except Exception as e:
            #
            status = httpStatusServererror
            #
            args['result'] = logException
            args['http_response_code'] = status
            args['description'] = '-'
            args['exception'] = e
            log_inbound(**args)
            #
            raise HTTPError(status)

    ################################################################################################
    # Send updates to device
    ################################################################################################

    @post(uri_get_device_specific)
    def update_devices_specific(device_type, device_id):
        #
        args = _get_log_args(request)
        #
        try:
            #
            command = request.json
            #
            if device_type == 'thermostat':
                if validate_thermostat(command):
                    status = httpStatusSuccess if _device.setThermostat(device_id, command) else httpStatusFailure
                else:
                    status = httpStatusBadrequest
            else:
                status = httpStatusBadrequest
            #
            args['result'] = logPass if status == httpStatusSuccess else logFail
            #
            args['http_response_code'] = status
            args['description'] = '-'
            log_inbound(**args)
            #
            return HTTPResponse(status=status)
            #
        except Exception as e:
            #
            status = httpStatusServererror
            #
            args['result'] = logException
            args['http_response_code'] = status
            args['description'] = '-'
            args['exception'] = e
            log_inbound(**args)
            #
            raise HTTPError(status)

    ################################################################################################

    def bottle_run(x_host, x_port):
        log_internal(logPass, logDescPortListener.format(port=x_port), description='started')
        run(host=x_host, port=x_port, debug=True)

    ################################################################################################

    host = 'localhost'
    ports = get_cfg_port_listener()
    for port in ports:
        t = threading.Thread(target=bottle_run, args=(host, port,))
        port_threads.append(t)

    # Start all threads
    for t in port_threads:
        t.start()
    # Use .join() for all threads to keep main process 'alive'
    for t in port_threads:
        t.join()
