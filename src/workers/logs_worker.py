import threading

from src.modules.workers_flag import WorkersFlag


class LogsWorker(threading.Thread):
    def __init__(self, flag: WorkersFlag):
        threading.Thread.__init__(self)
        self._flag = flag

    def run(self):
        while self._flag.keep_working:
            try:
                for line in tail():
                    if STOP or not line and not status_worker.server_enabled:
                        break
                    if line:
                        self.__logs_queue.put(line)
            except FileNotFoundError as e:
                print(e)
