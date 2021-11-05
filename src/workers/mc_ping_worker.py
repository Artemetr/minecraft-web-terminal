import os
import threading
from time import sleep

from mctools.mclient import BaseClient, PINGClient

from src.modules.workers_flags import WorkersFlags


def _mock_send(stats):
    pass


class McPingWorker(threading.Thread):
    _server_timeout = int(os.getenv('SERVER_TIMEOUT') or 2)

    def __init__(self, flags: WorkersFlags):
        threading.Thread.__init__(self)
        self._flags = flags
        self._iteration = 0
        self._send = _mock_send

    @classmethod
    def _get_ping_client(cls) -> PINGClient:
        return PINGClient(host=os.getenv('PING_HOST'), port=int(os.getenv('PING_PORT')),
                          format_method=BaseClient.REMOVE, timeout=cls._server_timeout)

    @classmethod
    def get_ping(cls) -> float or None:
        try:
            result = cls._get_ping_client().ping()
        except Exception as e:
            print('McPingWorker::get_ping', e)
            # raise e  # What happens if you don't catch it?
            result = None

        return result

    @classmethod
    def get_stats(cls) -> dict or None:
        try:
            result = cls._get_ping_client().get_stats()
        except Exception as e:
            print('McPingWorker::get_ping', e)
            # raise e  # What happens if you don't catch it?
            result = None

        return result

    def _do_ping(self):
        self._iteration += 1
        if self._iteration != 3:
            return True
        else:
            self._iteration = 0
            return False

    def set_send(self, send):
        self._send = send

    def run(self):
        while self._flags.keep_working:
            if self._do_ping():
                ping = self.get_ping()
                if not ping:
                    self._flags.server_is_stopped()
                    self._send(dict(status=False))
                else:
                    self._flags.server_is_running()
            else:
                stats = self.get_stats()
                if not stats:
                    self._flags.server_is_stopped()
                    self._send(dict(status=False))
                else:
                    self._flags.server_is_running()
                    stats['status'] = True
                    self._send(stats)
            sleep(1)
