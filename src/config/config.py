import json
import os
import ast
import datetime
from resources.global_resources.variables import oauthConfigTimeformat

file_name = 'config.json'


def write_config(new_data):
    try:
        #
        try:
            new_data = ast.literal_eval(new_data)
        except:
            new_data = new_data
        #
        with open(os.path.join(os.path.dirname(__file__), file_name), 'w+') as output_file:
            output_file.write(json.dumps(new_data, indent=4, separators=(',', ': ')))
            output_file.close()
        #
        return True
    except Exception as e:
        return False


def get_config_json():
    #
    with open(os.path.join(os.path.dirname(__file__), file_name), 'r') as data_file:
        return json.load(data_file)


def get_cfg_serviceid():
    return get_config_json()['service_id']


def get_cfg_name_long():
    return get_config_json()['name_long']


def get_cfg_name_short():
    return get_config_json()['name_short']


def get_cfg_subservices():
    return get_config_json()['subservices']


def get_cfg_subservice(id):
    for s in get_cfg_subservices():
        if s['id'] == id:
            return s
    return False


def get_cfg_subservice_type(id):
    s = get_cfg_subservice(id)
    if bool(s):
        return s['type']
    else:
        return False


def get_cfg_subservice_groups(id):
    s = get_cfg_subservice(id)
    if bool(s):
        return s['groups']
    else:
        return False


def get_cfg_groups():
    return get_config_json()['groups']


def get_cfg_details():
    return get_config_json()['details']


def get_cfg_details_oauthToken():
    return get_cfg_details()['oauth_token']


def get_cfg_details_oauthTokenExpiry():
    return datetime.datetime.strptime(get_cfg_details()['oauth_tokenexpiry'], oauthConfigTimeformat)


def get_cfg_details_oauthState():
    return get_cfg_details()['oauth_state']


def set_cfg_details_oauth(token, expiry, state):
    cfg = get_config_json()
    cfg['details']['oauth_token'] = token
    cfg['details']['oauth_tokenexpiry'] = expiry.strftime(oauthConfigTimeformat)
    cfg['details']['oauth_state'] = state
