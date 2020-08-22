# obs-websocket-http
A Python-based program that provides HTTP endpoints for obs-websocket

## Installing on Ubuntu:
- Clone/download the repository
- Edit `config.ini` and set the address, port, and authentication details for the HTTP server (leave `authentication_key` empty for no auth). Set your obs-websocket connection settings in the `[obsws]` section.
- `sudo apt update && sudo apt install python3.7 python3-pip`
- `python3.7 -m pip install -r requirements.txt`
- CD into the `obs-websocket-http` directory
- Run with `python3.7 main.py`

## Running with Docker

- Clone/download the repository
- Edit `docker-compose.yml` to have the correct IPs and ports for this machine and the one running OBS Studio (it may be the same machine). You do NOT need to edit `config.ini` if using docker because it will be created by the container from the values in `docker-compose.yml`.
- Start obs-websocket-http by running `docker-compose up -d && docker-compose logs -f`. This will give you log output and you can press `Ctrl-C` when you wish to return to terminal and the container will run in the background.

## Protocol:
This code contains two request endpoints. `/emit/{requesttype}` and `/call/{requesttype}`.
- `/emit/{requesttype}` sends off a websocket event without waiting for a response, and immediately returns a generic `{"status":"ok"}` json response after sending the event, regardless of whether it errors out on the OBS instance.
- `/call/{requesttype}` Makes a full request to obs-websocket, and waits for a response. The recieved response is then returned to the HTTP caller.

If authentication is set, then each request much contain an `AuthKey` header with the configured password as the value.

A request type is always required, however a json body depends on the underlying request in obs-websocket as to whether any data is necessary.

For a list of request types, refer to the [obs-websocket protocol docs](https://github.com/Palakis/obs-websocket/blob/4.x-current/docs/generated/protocol.md#requests)

## Example cURL commands:
- `curl -XPOST -H "Content-type: application/json" -d '{"sc-name":"Scene 2"}' 'http://127.0.0.1/emit/SetCurrentScene'`
- `curl -XPOST -H 'AuthKey: agoodpassword' -H "Content-type: application/json" -d '{"sc-name":"Scene 2"}' 'http://127.0.0.1/emit/SetCurrentScene'`
- `curl -XPOST -H 'AuthKey: agoodpassword' -H "Content-type: application/json" 'http://127.0.0.1/call/GetSceneList'`
