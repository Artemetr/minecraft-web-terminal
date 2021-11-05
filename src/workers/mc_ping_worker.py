import os
import threading
from time import sleep

from mctools.mclient import BaseClient, PINGClient

from src.modules.workers_flag import WorkersFlag


class McPingWorker(threading.Thread):
    _server_timeout = int(os.getenv('SERVER_TIMEOUT')) or 2

    def __init__(self, flag: WorkersFlag, ping_only: bool = False):
        threading.Thread.__init__(self)
        self._flag = flag
        self._ping_only = ping_only
        self._iteration = 0

    @classmethod
    def _get_ping_client(cls) -> PINGClient:
        return PINGClient(host=os.getenv('PING_HOST'), port=int(os.getenv('PING_PORT')),
                          format_method=BaseClient.REMOVE, timeout=cls._server_timeout)

    @classmethod
    def get_ping(cls) -> float or None:
        try:
            result = cls._get_ping_client().ping()
        except Exception as e:
            print(e)
            result = None

        return result

    @classmethod
    def get_stats(cls) -> dict or None:
        try:
            result = cls._get_ping_client().get_stats()
        except Exception as e:
            print(e)
            result = None

        return result

    def _do_ping(self):
        self._iteration += 1
        if self._iteration != 3:
            return True
        else:
            self._iteration = 0
            return False

    def run(self):
        while self._flag.keep_working:
            if self._do_ping():
                ping = self.get_ping()
                if not ping:
                    self._flag.server_is_stopped()
                    # TODO сделать рассылку для всех что сервер не работает
                else:
                    self._flag.server_is_running()
            else:
                stats = self.get_stats()
                if not stats:
                    self._flag.server_is_stopped()
                    # TODO сделать рассылку для всех что сервер не работает
                else:
                    self._flag.server_is_running()
                    # TODO сделать рассылку статистики для всех
            sleep(1)
