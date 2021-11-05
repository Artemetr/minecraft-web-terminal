import os
import threading
from time import sleep

from src.modules.tail import tail
from src.modules.workers_flags import WorkersFlags


def _mock_send(message):
    pass


class LogsWorker(threading.Thread):
    _show_rcon_logs_at_the_front = bool(os.getenv('SHOW_RCON_LOGS_AT_THE_FRONT'))

    def __init__(self, flags: WorkersFlags):
        threading.Thread.__init__(self)
        self._flags = flags
        self._log_file_path = os.getenv('LOGS_FILE')
        self._send = _mock_send

    def set_send(self, send):
        self._send = send

    def run(self):
        while self._flags.keep_working and self._log_file_path:
            try:
                for line in tail(self._log_file_path):
                    if not self._flags.keep_working or not self._flags.is_server_running and not line:
                        sleep(1)
                        break
                    if line and (self._show_rcon_logs_at_the_front or line.find('Thread RCON') == -1):
                        self._send(line)
            except Exception as e:
                print('LogsWorker::run', e)
                # raise e  # What happens if you don't catch it?
