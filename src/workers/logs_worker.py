import os
import threading
from time import sleep

from src.modules.workers_flag import WorkersFlag
from src.tail import tail


class LogsWorker(threading.Thread):
    def __init__(self, flag: WorkersFlag):
        threading.Thread.__init__(self)
        self._flag = flag
        self._log_file_path = os.getenv('LOGS_FILE')

    def run(self):
        while self._flag.keep_working and self._log_file_path:
            try:
                for line in tail(self._log_file_path):
                    if not self._flag.keep_working or not self._flag.is_server_running and not line:
                        sleep(1)
                        break
                    if line:
                        # TODO отсылать всем полученную строку логов
                        pass
            except Exception as e:
                print(e)
