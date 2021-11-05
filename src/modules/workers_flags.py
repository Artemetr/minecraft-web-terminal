class WorkersFlags:
    def __init__(self):
        self._keep_working = True
        self._is_server_running = False

    @property
    def keep_working(self) -> bool:
        return self._keep_working

    def stop(self):
        self._keep_working = False

    @property
    def is_server_running(self) -> bool:
        return self._is_server_running

    def server_is_running(self):
        self._is_server_running = True

    def server_is_stopped(self):
        self._is_server_running = False
