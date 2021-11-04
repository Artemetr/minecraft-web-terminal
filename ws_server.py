import asyncio
import dotenv
import json
import os
import threading
import time
import websockets
from mcstatus import MinecraftServer
from queue import Queue

from websockets.exceptions import ConnectionClosedOK

from src.logs_reader import tail
from src.rcon import Rcon

dotenv.load_dotenv()


class ServerStatus:
    online = 'online'
    offline = 'offline'


SOCKET_HOST = os.getenv('SOCKET_HOST')
SOCKET_PORT = int(os.getenv('SOCKET_PORT'))
SOCKET_LOGIN = os.getenv('SOCKET_LOGIN')
SOCKET_PASSWORD = os.getenv('SOCKET_PASSWORD')
STOP = False
connected = set()


class RconWorker(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.__rcon = Rcon(os.getenv('RCON_HOST'), os.getenv('RCON_PORT'), os.getenv('RCON_PASSWORD'))
        self.__commands_queue = Queue(512)

    def run(self):
        while not STOP:
            item = self.__get_item()
            if item:
                result = self.__rcon.exec(item)
                ws_worker.send_data_for_all_like_task({'action': 'log_message', 'result': result})

    def __get_item(self) -> dict or None:
        return self.__commands_queue.get_nowait() if not self.__commands_queue.empty() else None

    def exec(self, command):
        self.__commands_queue.put(command)

    def disconnect(self):
        self.__rcon.disconnect()


class StatusWorker(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.__server = MinecraftServer(os.getenv('QUERY_HOST'), int(os.getenv('QUERY_PORT')))
        self.__status = ServerStatus.offline
        self.__ping = None
        self.__query = None
        self.__messages_queue = Queue(1)

    def __get_info__(self):
        try:
            self.__ping = self.__server.ping()
            self.__query = self.__server.query()
            self.__status = ServerStatus.online
        except:
            self.__status = ServerStatus.offline

        self.__build_message__()

    @property
    def server_enabled(self):
        return self.__status == ServerStatus.online

    def run(self):
        while not STOP:
            self.__get_info__()
            time.sleep(2)

    def __build_message__(self):
        enabled = self.__status == ServerStatus.online
        message = {'enabled': enabled}
        if enabled:
            message['players'] = {
                'max': self.__query.players.max,
                'online': self.__query.players.online,
                'names': self.__query.players.names
            }
            message['ping'] = self.__ping
            message['motd'] = self.__query.motd
            message['version'] = self.__query.software.version
            message['plugins'] = self.__query.software.plugins
            message['brand'] = self.__query.software.brand
        self.__messages_queue.put(message)

    def get_message(self) -> dict or None:
        return self.__messages_queue.get_nowait() if not self.__messages_queue.empty() else None


class LogsWorker(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.__logs_queue = Queue(int(os.getenv('LOGS_QUEUE_MAX_SIZE')))

    def run(self):
        while not STOP:
            for line in tail():
                if STOP or not line and not status_worker.server_enabled:
                    break
                if line:
                    self.__logs_queue.put(line)

    def get_message(self) -> str:
        return self.__logs_queue.get_nowait() if not self.__logs_queue.empty() else None


class WSWorker(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.connected = set()

    def run(self):
        while not STOP:
            if self.connected:
                log_message = logs_worker.get_message()
                if log_message:
                    self.send_data_for_all_like_task(dict(action='log_message', result=log_message))

                status_message = status_worker.get_message()
                if status_message:
                    self.send_data_for_all_like_task(dict(action='status_message', result=status_message))

    async def send_data(self, data, websocket):
        try:
            await websocket.send(json.dumps(data))
        except ConnectionClosedOK:
            self.connected.remove(websocket)

    def send_data_for_all_like_task(self, data, except_: list = None):
        if except_ is None:
            except_ = []
        data = json.dumps(data)
        for websocket in self.connected.copy():
            if websocket not in except_:
                try:
                    coro = websocket.send(data)
                    future = asyncio.run_coroutine_threadsafe(coro, loop)
                except ConnectionClosedOK:
                    self.connected.remove(websocket)

    async def send_data_for_all(self, data, except_: list = None):
        if except_ is None:
            except_ = []
        for websocket in self.connected.copy():
            if websocket not in except_:
                try:
                    await self.send_data(data, websocket)
                except ConnectionClosedOK:
                    self.connected.remove(websocket)

    async def auth(self, websocket):
        try:
            message = await asyncio.wait_for(websocket.recv(), timeout=5)
            data = json.loads(message)
            if data['login'] == SOCKET_LOGIN or data['password'] == SOCKET_PASSWORD:
                self.connected.add(websocket)
                await self.send_data(dict(status=True, action='auth'), websocket)
            else:
                await self.send_data(dict(status=False, action='auth', error='Invalid auth data'), websocket)
        except asyncio.TimeoutError:
            await self.send_data(dict(status=False, action='auth', error='Timeout'), websocket)
        except ConnectionRefusedError:
            pass
        except json.decoder.JSONDecodeError:
            await self.send_data(dict(status=False, action='auth', error='Invalid data format'), websocket)

    async def handler(self, websocket, path):
        if websocket not in self.connected.copy():
            await self.auth(websocket)

        if websocket in self.connected.copy():
            try:
                async for message in websocket:
                    await self.message_process(websocket, message)
            finally:
                if websocket in connected:
                    self.connected.remove(websocket)

    async def message_process(self, websocket, message):
        try:
            data = json.loads(message)
        except json.decoder.JSONDecodeError:
            await self.send_data(dict(status=False, error='Invalid data format'), websocket)
            return

        action = data.get('action')
        if not action:
            await self.send_data(dict(status=False, error='Empty action'), websocket)
            return

        if action == 'exec':
            command = data.get('command')
            if not command:
                await self.send_data(dict(action='log_message', result='Empty command'), websocket)
                return

            await self.send_data_for_all(dict(action='exec', result=command), [websocket])
            rcon_worker.exec(command)
            return
        else:
            await self.send_data(websocket=websocket, data=dict(status=False, action=action, error='Undefined action'))
            return


if __name__ == '__main__':
    ws_worker = WSWorker()
    rcon_worker = RconWorker()
    status_worker = StatusWorker()
    logs_worker = LogsWorker()

    try:
        status_worker.start()
        rcon_worker.start()
        logs_worker.start()
        ws_worker.start()

        wss = websockets.serve(ws_worker.handler, SOCKET_HOST, SOCKET_PORT)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(wss)
        loop.run_forever()
    finally:
        STOP = True
        rcon_worker.disconnect()
