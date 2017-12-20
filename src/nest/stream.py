import json
import sseclient
import requests
from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST
from config.config import get_cfg_details_oauthToken
from resources.global_resources.broadcast import *
from log.log import log_internal


def nest_stream(url):
    #
    headers = {'Authorization': 'Bearer {authcode}'.format(authcode=get_cfg_details_oauthToken()),
               'Accept': 'text/event-stream'}
    #
    with requests.get(url, headers=headers, stream=True) as r:
        #
        client = sseclient.SSEClient(r)
        for event in client.events():
            event_type = event.event
            if event_type == 'open':  # not always received here
                # The event stream has been opened
                data = False
            elif event_type == 'put':
                # The data has changed (or initial data sent)
                data = json.loads(event.data)
            elif event_type == 'keep-alive':
                # No data updates. Receiving an HTTP header to keep the connection open.
                data = False
            elif event_type == 'auth_revoked':
                # The API authorization has been revoked.
                data = json.loads(event.data)
            elif event_type == 'error':
                # Error occurred, such as connection closed.
                data = json.loads(event.data)
            else:
                # Unknown event, no handler for it.
                data = False
            #
            if bool(data):
                broadcast_update(data)
            #
        log_internal(True, 'Nest server update stream: {event}:{data}'.format(event=event_type, data=data), desc='pass')
        #
        # TODO - response to be added to a list for picking up by a broadcast capability


def broadcast_update(update):
    try:
        s = socket(AF_INET, SOCK_DGRAM)
        s.bind(('0.0.0.0', 0))
        s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        #
        s.sendto(update, ('<broadcast>', jarvis_broadcastPort))
        #
        # TODO
        # log_internal(True, '', desc='pass')
        #
    except Exception as e:
        # TODO
        # log_internal(True, '', desc='fail', exception=e)
        pass
