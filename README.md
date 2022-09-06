# obs-websocket-http
A Python-based program that provides HTTP endpoints for obs-websocket

## Please Note
This branch is **only** for versions of obs-websocket that are 5.0.0 or higher. If you are using obs-websocket pre-5.0.0, use the `old-4.x` branch.

Click [here](https://github.com/IRLToolkit/obs-websocket-http/tree/old-4.x) to go to the pre-5.0.0 branch.

## Installing on Ubuntu:
- Clone/download the repository
- Edit `config.ini` and set the address, port, and authentication details for the HTTP server (leave `authentication_key` empty for no auth). Set your obs-websocket connection settings in the `[obsws]` section.
- `sudo apt update && sudo apt install python3.8 python3-pip`
- `python3.8 -m pip install -r requirements.txt`
- CD into the `obs-websocket-http` directory
- Run with `python3.8 main.py`

Use `python3.8 main.py --help` to see command line options, which allow you to run this script without a config.ini.

## Running with Docker
- Clone/download the repository
- Edit `docker-compose.yml` to have the correct IPs and ports for this machine and the one running OBS Studio (it may be the same machine). You do NOT need to edit `config.ini` if using docker because it will be created by the container from the values in `docker-compose.yml`.
- Start obs-websocket-http by running `docker-compose up -d && docker-compose logs -f`. This will give you log output and you can press `Ctrl-C` when you wish to return to terminal and the container will run in the background.

## Protocol:
The web server contains these endpoints:
- `/emit/{requestType}` sends off a websocket event without waiting for a response, and immediately returns a generic `{"result": true}` JSON response without a request result.
- `/call/{requestType}` Makes a full request to obs-websocket, and waits for a response. The recieved response is then returned to the HTTP caller.
  - Example JSON response: `{"result": true, "requestResult": {"requestType": "GetCurrentProgramScene", "requestStatus": {"result": true, "code": 100}, "responseData": {"currentProgramSceneName": "Scene 5"}}}`

If authentication is set, then each request much contain an `Authorization` header with the configured auth key as the value.

A request type is always required, however the request body is optional, and is forwarded as the request data for the obs-websocket request. If your obs-websocket request does not require request data, then no body is needed.

For a list of request types, refer to the [obs-websocket protocol docs](https://github.com/obsproject/obs-websocket/blob/master/docs/generated/protocol.md#requests)

## Example cURL commands:
- `curl -XPOST -H 'Authorization: pp123' -H "Content-type: application/json" -d '{"sceneName": "Scene 5"}' 'http://127.0.0.1:4445/emit/SetCurrentProgramScene'`
- `curl -XPOST -H "Content-type: application/json" 'http://127.0.0.1:4445/call/GetCurrentProgramScene'`

## IRLTookit Links

- Please go to the [obs-websocket Discord](https://discord.gg/WBaSQ3A) for support.
- https://twitter.com/IRLToolkit
- https://irltoolkit.com
