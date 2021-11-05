import asyncio
import json
from asyncio import AbstractEventLoop


class WebsocketsHandler:
    def __init__(self, loop: AbstractEventLoop):
        self._websockets = set()
        self._loop = loop

    def is_existing_websocket(self, websocket) -> bool:
        return websocket in self._websockets

    def add_websocket(self, websocket):
        if self.is_existing_websocket(websocket):
            # TODO normal exception type and message
            raise Exception('Wtf?')

        self._websockets.add(websocket)

    def remove_websocket(self, websocket):
        if not self.is_existing_websocket(websocket):
            # TODO normal exception type and message
            raise Exception('Wtf?')

        self._websockets.remove(websocket)

    def get_websockets(self):
        return self._websockets.copy()

    def send_data(self, data: dict or list, websockets: set = None, without: set = None):
        if without is None:
            without = set()
        if websockets is None:
            websockets = self.get_websockets()
        websockets.difference_update(without)

        data = json.dumps(data)
        for websocket in websockets:
            try:
                coro = websocket.send(data)
                future = asyncio.run_coroutine_threadsafe(coro, self._loop)
            except Exception as e:
                print('WebsocketsHandler::send_data', e)
                # raise e  # What happens if you don't catch it?
                if self.is_existing_websocket(websocket):
                    self.remove_websocket(websocket)

    async def send_data_async(self, data: dict or list, websockets: set = None, without: set = None):
        if without is None:
            without = set()
        if websockets is None:
            websockets = self.get_websockets()
        websockets.difference_update(without)

        data = json.dumps(data)
        for websocket in websockets:
            try:
                await websocket.send(data)
            except Exception as e:
                print('WebsocketsHandler::send_data_async', e)
                # raise e  # What happens if you don't catch it?
                if self.is_existing_websocket(websocket):
                    self.remove_websocket(websocket)
