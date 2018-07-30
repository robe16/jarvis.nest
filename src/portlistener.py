from bottle import get, post
from bottle import request, run

from config.config import get_cfg_port
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

    @get('/config')
    def api_get_config():
        return get_config(request)

    @get('/all')
    def api_get_all():
        return get_all(request, _nest)

    @get('/structures')
    def api_get_structures():
        return get_structures(request, _nest)

    @get('/structure/<structure_id>')
    def api_get_structure_specific(structure_id):
        return get_structure_specific(request, _nest, structure_id)

    @get('/devices')
    def api_get_devices():
        return get_devices(request, _nest)

    @get('/devices/<device_type>')
    def api_get_devices_type(device_type):
        return get_devices_type(request, _nest, device_type)

    @get('/devices/<device_type>/<device_id>')
    def api_get_device_specific(device_type, device_id):
        return get_device_specific(request, _nest, device_type, device_id)

    @post('/devices/<device_type>/<device_id>')
    def api_post_device_specific(device_type, device_id):
        return post_device_specific(request, _nest, device_type, device_id)

    ################################################################################################

    host = 'localhost'
    port = get_cfg_port()
    run(host=host, port=port, server='paste', debug=True)

    log_internal(logPass, logDescPortListener.format(port=port), description='started')

    ################################################################################################
