import os
import asyncio
import json
import simpleobsws
import aiohttp
from aiohttp import web
from configparser import ConfigParser

config = ConfigParser()
config.read('config.ini')
httpAddress = config.get('http', 'bind_to_address')
httpPort = config.getint('http', 'bind_to_port')
httpAuthKey = config.get('http', 'authentication_key')
if httpAuthKey:
    print('Starting HTTP server with AuthKey set to "{}"'.format(httpAuthKey))
else:
    print('Starting HTTP server without authentication.')
    httpAuthKey = None
wsAddress = config.get('obsws', 'ws_address')
wsPort = config.getint('obsws', 'ws_port')
wsPassword = config.get('obsws', 'ws_password')
loop = asyncio.get_event_loop()
ws = simpleobsws.WebSocketClient(url='ws://{}:{}'.format(wsAddress, wsPort), password=wsPassword)

def statusmessage(message):
    print(str(message) + '...      ', end='', flush=True)

def response_to_object(response: simpleobsws.RequestResponse):
    ret = {}
    ret['requestType'] = response.requestType
    ret['requestStatus'] = {'result': response.requestStatus.result, 'code': response.requestStatus.code}
    if response.requestStatus.comment:
        ret['requestStatus']['comment'] = response.requestStatus.comment
    if ret.has_data():
        ret['responseData'] = response.responseData
    return ret

async def handle_emit_request(request):
    """Handler function for all emit-based HTTP requests. Assumes that you know what you are doing because it will never return an error."""
    if ('AuthKey' not in request.headers) and httpAuthKey != None:
        return web.json_response({'status': False, 'comment': 'AuthKey header is required.'})
    if httpAuthKey == None or (request.headers['AuthKey'] == httpAuthKey):
        requesttype = request.match_info['type']
        try:
            requestdata = await request.json()
        except json.decoder.JSONDecodeError:
            requestdata = None
        req = simpleobsws.Request(requesttype, requestdata)
        await ws.emit(req)
        return web.json_response({'status': True})
    else:
        return web.json_response({'status': False, 'comment': 'Bad AuthKey'})

async def handle_call_request(request):
    """Handler function for all call-based HTTP requests."""
    if ('AuthKey' not in request.headers) and httpAuthKey != None:
        return web.json_response({'status': False, 'comment': 'AuthKey header is required.'})
    if httpAuthKey == None or (request.headers['AuthKey'] == httpAuthKey):
        requesttype = request.match_info['type']
        try:
            requestdata = await request.json()
        except json.decoder.JSONDecodeError:
            if (await request.text()) == '':
                requestdata = None
        try:
            req = simpleobsws.Request(requesttype, requestdata)
            ret = await ws.call(req)
            responsedata = {'status': True, 'response': response_to_object(ret)}
        except simpleobsws.MessageTimeout:
            responsedata = {'status': False, 'comment': 'The obs-websocket request timed out.'}
        return web.json_response(responsedata)
    else:
        return web.json_response({'status': False, 'comment': 'Bad AuthKey'})

async def init_ws():
    await ws.connect()
    if not await ws.wait_until_identified():
        print('Identification with obs-websocket timed out. Could it be using 4.x?')
        return False
    return True

app = web.Application()
app.add_routes([web.post('/emit/{type}', handle_emit_request), web.post('/call/{type}', handle_call_request)])
statusmessage('Connecting to obs-websocket')
if not loop.run_until_complete(init_ws()):
    os._exit(1)
print('[Connected.]')
try:
    web.run_app(app, host=httpAddress, port=httpPort)
except KeyboardInterrupt:
    print('Shutting down...')
