import asyncio
import json
import os

import websockets

from src.modules.websockets_handler import WebsocketsHandler
from src.modules.workers_flags import WorkersFlags
from src.modules.ws_standard_responses import WsStandardResponses, WsLogMessageTypes
from src.workers.logs_worker import LogsWorker
from src.workers.mc_ping_worker import McPingWorker
from src.workers.mc_rcon_worker import McRconWorker

SOCKET_HOST = os.getenv('SOCKET_HOST')
SOCKET_PORT = int(os.getenv('SOCKET_PORT'))
SOCKET_LOGIN = os.getenv('SOCKET_LOGIN')
SOCKET_PASSWORD = os.getenv('SOCKET_PASSWORD')
SOCKET_AUTH_TIMEOUT = int(os.getenv('SOCKET_AUTH_TIMEOUT')) or 5


def send_log(message):
    websockets_handler.send_data(WsStandardResponses.log_message(message, WsLogMessageTypes.output))


def send_ping(stats):
    websockets_handler.send_data(dict(action='stats_message', response=stats))


def send_rcon(message):
    send_log(message)


async def decode_message(websocket, message) -> (str, dict,):
    try:
        result = json.loads(message)
        if not result.get('action') or not result.get('data') or type(result.get('action')) is not str:
            result = None
    except Exception as e:
        print(e)
        result = None

    if not result:
        await websockets_handler.send_data_async(WsStandardResponses.invalid_data_format, {websocket})
        return None, None

    return result.get('action'), result.get('data')


async def auth(websocket) -> bool:
    if websockets_handler.is_existing_websocket(websocket):
        await websockets_handler.send_data_async(WsStandardResponses.auth_failed, {websocket})
        return False

    try:
        message = await asyncio.wait_for(websocket.recv(), timeout=SOCKET_AUTH_TIMEOUT)
        action, data = await decode_message(websocket, message)
        if not message:
            return False

        if action != 'auth' or data.get('login') == SOCKET_LOGIN or data.get('password') == SOCKET_PASSWORD:
            websockets_handler.add_websocket(websocket)
            await websockets_handler.send_data_async(WsStandardResponses.success_auth, {websocket})
            return True
        else:
            await websockets_handler.send_data_async(WsStandardResponses.auth_failed, {websocket})
    except asyncio.TimeoutError:
        await websockets_handler.send_data_async(WsStandardResponses.auth_timeout, {websocket})
    except Exception as e:
        print(e)

    return False


async def handle_message(websocket, message):
    action, data = await decode_message(websocket, message)
    if not action:
        return

    if action == 'exec':
        command = data.get('command')
        if not command:
            await websockets_handler.send_data_async(
                WsStandardResponses.log_message('The command cannot be empty. Try another way.',
                                                WsLogMessageTypes.error), {websocket})
            return

        await websockets_handler.send_data_async(WsStandardResponses.log_message(command, WsLogMessageTypes.input),
                                                 without={websocket})
        mc_rcon_worker.put(str(command))
        return
    else:
        await websockets_handler.send_data_async(WsStandardResponses.undefined_action, {websocket})
        return


async def handle(websocket, path):
    is_auth = await auth(websocket)
    if not is_auth:
        return

    async for message in websocket:
        await handle_message(websocket, message)

    if websockets_handler.is_existing_websocket(websocket):
        websockets_handler.remove_websocket(websocket)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    workers_flags = WorkersFlags()
    websockets_handler = WebsocketsHandler(loop)

    mc_rcon_worker = McRconWorker(workers_flags)
    mc_rcon_worker.set_send(send_rcon)

    logs_worker = LogsWorker(workers_flags)
    logs_worker.set_send(send_log)

    mc_ping_worker = McPingWorker(workers_flags)
    mc_ping_worker.set_send(send_ping)

    try:
        logs_worker.start()
        mc_ping_worker.start()
        mc_rcon_worker.start()

        start_server = websockets.serve(handle, SOCKET_HOST, SOCKET_PORT)

        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()
    finally:
        workers_flags.stop()

