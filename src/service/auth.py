import requests
import json
import datetime
from log.log import log_outbound
from config.config import get_cfg_details_clientId, get_cfg_details_clientSecret, set_cfg_details_oauth
from resources.global_resources.log_vars import logPass, logFail, logException


def get_accesstoken_pincode(state, pincode):
    url_access = 'https://api.home.nest.com/oauth2/access_token'
    #
    headers = {'Connection': 'close',
               'User-Agent': 'Linux/2.6.18 UDAP/2.0 CentOS/5.8',
               'Content-type': 'application/x-www-form-urlencoded'}
    #
    payload = {'client_id': get_cfg_details_clientId(),
               'client_secret': get_cfg_details_clientSecret(),
               'code': pincode,
               'grant_type': 'authorization_code'}
    #
    r = requests.post(url_access,
                      headers=headers,
                      data=payload)
    #
    r_pass = (r.status_code == requests.codes.ok)
    #
    result = logPass if r_pass else logFail
    log_outbound(result,
                 url_access, '', 'POST', '',
                 '-', '-',
                 r.status_code)
    #
    if not r_pass:
        raise Exception()
    #
    try:
        response = json.loads(r.text)
    except Exception as e:
        log_outbound(logException,
                     url_access, '', 'POST', '',
                     '-', '-',
                     r.status_code,
                     exception=e)
        raise Exception()
    #
    token = response['access_token']
    tokenexpiry = datetime.datetime.now() + datetime.timedelta(seconds=response['expires_in'])
    #
    set_cfg_details_oauth(token, tokenexpiry, state)
    #
    return {'token': token,
            'tokenexpiry': tokenexpiry}

state = input('Enter State: ')
pincode = input('Enter Pin Code: ')
get_accesstoken_pincode(state, pincode)
