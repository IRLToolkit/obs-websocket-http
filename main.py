import logging
logging.basicConfig(level=logging.INFO)
import os
import argparse
import asyncio
import json
import simpleobsws
import aiohttp
from aiohttp import web
from configparser import ConfigParser

loop = asyncio.get_event_loop()
app = web.Application()
ws = None

# Make aiohttp shut up
aiohttpLogger = logging.getLogger('aiohttp')
aiohttpLogger.setLevel(logging.WARNING)

def fail_response(comment):
    return web.json_response({'result': False, 'comment': comment})

def validate_request(request):
    if not httpAuthKey:
        return True, None
    if 'Authorization' not in request.headers:
        return False, 'You are missing the `Authorization` header.'
    if request.headers['Authorization'] != httpAuthKey:
        return False, 'Invalid authorization key.'
    return True, None

async def get_json(request):
    try:
        return await request.json()
    except json.decoder.JSONDecodeError:
        return None

def response_to_object(response: simpleobsws.RequestResponse):
    ret = {}
    ret['requestType'] = response.requestType
    ret['requestStatus'] = {'result': response.requestStatus.result, 'code': response.requestStatus.code}
    if response.requestStatus.comment:
        ret['requestStatus']['comment'] = response.requestStatus.comment
    if response.responseData:
        ret['responseData'] = response.responseData
    return ret

async def request_callback(request, emit):
    if not ws or not ws.is_identified():
        return fail_response('obs-websocket is not connected.')
    authOk, comment = validate_request(request)
    if not authOk:
        return fail_response(comment)

    requestType = request.match_info.get('requestType')
    if not requestType:
        return fail_response('Your path is missing a request type.')
    requestData = await get_json(request)
    req = simpleobsws.Request(requestType, requestData)

    logging.info('Performing request for request type `{}` | Emit: {} | Client IP: {}'.format(requestType, emit, request.remote))
    logging.debug('Request data:\n{}'.format(requestData))

    if emit:
        await ws.emit(req)
        return web.json_response({'result': True})

    try:
        ret = await ws.call(req)
    except simpleobsws.MessageTimeout:
        return fail_response('The obs-websocket request timed out.')
    responseData = {'result': True, 'requestResult': response_to_object(ret)}
    return web.json_response(responseData)

async def call_request_callback(request):
    return await request_callback(request, False)

async def emit_request_callback(request):
    return await request_callback(request, True)

async def init():
    logging.info('Connecting to obs-websocket...')
    try:
        await ws.connect()
    except ConnectionRefusedError:
        logging.error('Failed to connect to the obs-websocket server. Got connection refused.')
        return False
    if not await ws.wait_until_identified():
        logging.error('Identification with obs-websocket timed out. Could it be using 4.x?')
        return False
    logging.info('Connected to obs-websocket.')
    return True

async def shutdown(app):
    logging.info('Shutting down...')
    if ws.is_identified():
        logging.info('Disconnecting from obs-websocket...')
        await ws.disconnect()
        logging.info('Disconnected from obs-websocket.')
    else:
        logging.info('Not connected to obs-websocket, not disconnecting.')

if __name__ == '__main__':
    config = ConfigParser()
    config.read('config.ini')

    # Command line args take priority, with fallback to config.ini, and further fallback to defaults.
    parser = argparse.ArgumentParser(description='A Python-based program that provides HTTP endpoints for obs-websocket')
    parser.add_argument('--http_bind_addres', dest='http_bind_addres', default=config.get('http', 'bind_to_address', fallback='0.0.0.0'))
    parser.add_argument('--http_bind_port', dest='http_bind_port', type=int, default=config.getint('http', 'bind_to_port', fallback=4445))
    parser.add_argument('--http_auth_key', dest='http_auth_key', default=config.get('http', 'authentication_key', fallback=''))
    parser.add_argument('--ws_url', dest='ws_url', default=config.get('obsws', 'ws_url', fallback='ws://127.0.0.1:4444'))
    parser.add_argument('--ws_password', dest='ws_password', default=config.get('obsws', 'ws_password', fallback=''))
    args = parser.parse_args()

    httpAddress = args.http_bind_addres
    httpPort = args.http_bind_port
    httpAuthKey = args.http_auth_key
    wsUrl = args.ws_url
    wsPassword = args.ws_password

    if httpAuthKey:
        logging.info('HTTP server will start with AuthKey set to `{}`'.format(httpAuthKey))
    else:
        logging.info('HTTP server will start without authentication.')
        httpAuthKey = None

    ws = simpleobsws.WebSocketClient(url=wsUrl, password=wsPassword)

    if not loop.run_until_complete(init()):
        os._exit(1)

    app.add_routes([web.post('/call/{requestType}', call_request_callback), web.post('/emit/{requestType}', emit_request_callback)])
    app.on_cleanup.append(shutdown)

    web.run_app(app, host=httpAddress, port=httpPort)
