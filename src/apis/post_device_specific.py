from bottle import HTTPResponse, HTTPError

from common_functions.request_enable_cors import enable_cors
from common_functions.request_log_args import get_request_log_args
from log.log import log_inbound
from resources.global_resources.log_vars import logPass, logFail, logException
from resources.global_resources.variables import *
from validation.validation import validate_thermostat


def post_device_specific(request, _nest, device_type, device_id):
    #
    args = get_request_log_args(request)
    #
    try:
        #
        command = request.json
        #
        if device_type == 'thermostat':
            if validate_thermostat(command):
                status = httpStatusSuccess if _nest.setThermostat(device_id, command) else httpStatusFailure
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
        response = HTTPResponse()
        response.status = status
        enable_cors(response)
        #
        return response
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
