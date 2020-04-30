import asyncio
import json
import simpleobsws
import liteconfig
import aiohttp
from aiohttp import web

cfg = liteconfig.Config("config.ini")
loop = asyncio.get_event_loop()
ws = simpleobsws.obsws(host=cfg.obsws.ws_address, port=cfg.obsws.ws_port, password=cfg.obsws.ws_password, loop=loop)

async def handle_emit_request(request):
    """Handler function for all emit-based HTTP requests. Assumes that you know what you are doing because it will never return an error."""
    requesttype = request.match_info['type']
    requestdata = await request.json()
    await ws.emit(requesttype, requestdata)
    return web.json_response({'status':'ok'})

async def handle_call_request(request):
    """Handler function for all call-based HTTP requests."""
    pass

app = web.Application()
app.add_routes([web.post('/emit/{type}, handle_emit_request), web.post('/call/{type}, handle_call_request)])
loop.run_until_complete(ws.connect())
try:
    web.run_app(app)
except KeyboardInterrupt:
    print('Shutting down...')
