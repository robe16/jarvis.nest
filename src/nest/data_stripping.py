

def strip_data(json_data):
    json_data.pop('metadata', None)
    json_data['structures'] = strip_structures(json_data['structures'])
    json_data['devices'] = strip_devices(json_data['devices'])
    return json_data


def strip_structures(json_data):
    for k, v in json_data:
        json_data[k] = strip_structure(json_data[k])
    return json_data


def strip_structure(json_data):
    json_data.pop('devices', None)
    return False


def strip_devices(json_data):
    #
    if 'thermostats' in json_data.keys():
        json_data['thermostats'] = strip_thermostats(json_data['thermostats'])
    else:
        json_data['thermostats'] = {}
    #
    if 'smoke_co_alarms' in json_data.keys():
        json_data['smoke_co_alarms'] = strip_smokes(json_data['smoke_co_alarms'])
    else:
        json_data['smoke_co_alarms'] = {}
    #
    if 'cameras' in json_data.keys():
        json_data['cameras'] = strip_cameras(json_data['cameras'])
    else:
        json_data['cameras'] = {}
    #
    json_data.pop('$company', None)
    return json_data


def strip_thermostats(json_data):
    for k in json_data:
        json_data[k] = strip_thermostat(json_data[k])
    return json_data


def strip_thermostat(json_data):
    json_data.pop('software_version', None)
    return json_data


def strip_smokes(json_data):
    for k in json_data:
        json_data[k] = strip_smoke(json_data[k])
    return json_data


def strip_smoke(json_data):
    json_data.pop('software_version', None)
    return json_data


def strip_cameras(json_data):
    for k in json_data:
        json_data[k] = strip_camera(json_data[k])
    return json_data


def strip_camera(json_data):
    json_data.pop('software_version', None)
    json_data['web_url'] = 'https://home.nest.com/cameras/device_id?auth={access_token}'.format(access_token='')
    json_data['app_url'] = 'nestmobile://cameras/device_id?auth={access_token}'.format(access_token='')
    return json_data

