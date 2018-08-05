from bottle import request, run, route, get, post

from config.config import get_cfg_port
from common_functions.request_enable_cors import response_options, enable_cors
from log.log import log_internal
from service.nest import Nest
from resources.global_resources.log_vars import logPass
from resources.lang.enGB.logs import *

from apis.get_config import get_config
from apis.get_all import get_all
from apis.get_structures import get_structures
from apis.get_structure_specific import get_structure_specific
from apis.get_devices import get_devices
from apis.get_devices_type import get_devices_type
from apis.get_device_specific import get_device_specific
from apis.post_device_specific import post_device_specific


def start_bottle():

    ################################################################################################
    # Create device
    ################################################################################################

    _nest = Nest()

    log_internal(logPass, logDescDeviceObjectCreation, description='success')

    ################################################################################################
    # APIs
    ################################################################################################

    @route('/config', method=['OPTIONS'])
    @route('/all', method=['OPTIONS'])
    @route('/structures', method=['OPTIONS'])
    @route('/structure/<structure_id>', method=['OPTIONS'])
    @route('/devices', method=['OPTIONS'])
    @route('/devices/<device_type>', method=['OPTIONS'])
    @route('/devices/<device_type>/<device_id>', method=['OPTIONS'])
    def api_cors_options(**kwargs):
        return response_options()

    @get('/config')
    def api_get_config():
        response = get_config(request)
        return enable_cors(response)

    @get('/all')
    def api_get_all():
        response = get_all(request, _nest)
        return enable_cors(response)

    @get('/structures')
    def api_get_structures():
        response = get_structures(request, _nest)
        return enable_cors(response)

    @get('/structure/<structure_id>')
    def api_get_structure_specific(structure_id):
        response = get_structure_specific(request, _nest, structure_id)
        return enable_cors(response)

    @get('/devices')
    def api_get_devices():
        response = get_devices(request, _nest)
        return enable_cors(response)

    @get('/devices/<device_type>')
    def api_get_devices_type(device_type):
        response = get_devices_type(request, _nest, device_type)
        return enable_cors(response)

    @get('/devices/<device_type>/<device_id>')
    def api_get_device_specific(device_type, device_id):
        response = get_device_specific(request, _nest, device_type, device_id)
        return enable_cors(response)

    @post('/devices/<device_type>/<device_id>')
    def api_post_device_specific(device_type, device_id):
        response = post_device_specific(request, _nest, device_type, device_id)
        return enable_cors(response)

    ################################################################################################

    host = '0.0.0.0'
    port = get_cfg_port()
    run(host=host, port=port, server='paste', debug=True)

    log_internal(logPass, logDescPortListener.format(port=port), description='started')

    ################################################################################################
