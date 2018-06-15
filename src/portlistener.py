import threading

from bottle import get, post
from bottle import request, run

from config.config import get_cfg_port_listener
from log.log import log_internal
from service.nest import Nest
from resources.global_resources.log_vars import logPass
from resources.lang.enGB.logs import *

from apis.uri_config import get_config
from apis.uri_get_all import get_all
from apis.uri_get_structures import get_structures
from apis.uri_get_structure_specific import get_structure_specific
from apis.uri_get_devices import get_devices
from apis.uri_get_devices_type import get_devices_type
from apis.uri_get_device_specific import get_device_specific
from apis.uri_post_device_specific import post_device_specific


def start_bottle(port_threads):

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
        return get_structures(_nest)

    @get('/structure/<structure_id>')
    def api_get_structure_specific(structure_id):
        return get_structure_specific(request, structure_id)

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
