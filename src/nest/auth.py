import requests
import json
import datetime
from log.log import log_outbound


def get_accesstoken(client_id, client_secret, pincode):
    url_access = 'https://api.home.nest.com/oauth2/access_token'
    #
    headers = {'Connection': 'close',
               'User-Agent': 'Linux/2.6.18 UDAP/2.0 CentOS/5.8',
               'Content-type': 'application/x-www-form-urlencoded'}
    #
    payload = {'client_id': client_id,
               'client_secret': client_secret,
               'code': pincode,
               'grant_type': 'authorization_code'}
    #
    r = requests.post(url_access,
                      headers=headers,
                      data=payload)
    #
    r_pass = (r.status_code == requests.codes.ok)
    log_outbound(r_pass, url_access, '-', 'POST', r.status_code)
    #
    if not r_pass:
        raise Exception()
    #
    try:
        response = json.loads(r.text)
    except Exception as e:
        log_outbound(r_pass, url_access, '-', 'POST', r.status_code, exception=e)
        raise Exception()
    #
    token = response['access_token']
    tokenexpiry = datetime.datetime.now() + datetime.timedelta(seconds=response['expires_in'])
    #
    return {'token': token,
            'tokenexpiry': tokenexpiry}