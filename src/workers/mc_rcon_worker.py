import os
import threading
import time
from multiprocessing import Queue
from queue import Empty

from mctools import RCONClient
from mctools.mclient import BaseClient

from src.modules.workers_flags import WorkersFlags


def _mock_send(stats):
    pass


class McRconWorker(threading.Thread):
    def __init__(self, flags: WorkersFlags):
        threading.Thread.__init__(self)
        self._flags = flags
        self._server_timeout = int(os.getenv('SERVER_TIMEOUT') or 2)
        self._server_start_command = os.getenv('SERVER_START_COMMAND')
        self._server_start_command_recovery_time = float(os.getenv('SERVER_START_COMMAND_RECOVERY_TIME') or 120)
        self._commands_queue = Queue(int(os.getenv('COMMANDS_QUEUE_SIZE') or 128))
        self._latest_start_time = 0
        self._send = _mock_send

    @property
    def _recovery_time(self) -> float:
        return time.time() - self._latest_start_time

    @property
    def _recovery_time_has_expired(self) -> bool:
        return self._recovery_time > self._server_start_command_recovery_time

    def _start_command(self) -> str:
        if not self._server_start_command:
            result = 'The server startup command is not defined.'
        elif not self._recovery_time_has_expired:
            result = f'Server startup commands will be available in {int(self._recovery_time)} seconds.'
        elif self._flags.is_server_running:
            result = 'The server is already running.'
        else:
            os.system(self._server_start_command)
            self._latest_start_time = time.time()
            self._flags.server_is_running()
            result = 'Starting the server.'

        return result

    def _get_rcon_client(self) -> RCONClient:
        rcon_client = RCONClient(host=os.getenv('RCON_HOST'), port=int(os.getenv('RCON_PORT')),
                                        format_method=BaseClient.REMOVE, timeout=self._server_timeout)
        rcon_client.login(os.getenv('RCON_PASSWORD'))

        return rcon_client

    def _handle_stop_command(self, command):
        if command == 'stop':
            self._flags.server_is_stopped()

    def _rcon_client_exec(self, command) -> str:
        try:
            rcon_client = self._get_rcon_client()
            result = rcon_client.command(command)
            self._handle_stop_command(command)
        except Exception as e:
            print('McRconWorker::_rcon_client_exec', e)
            # raise e  # What happens if you don't catch it?
            result = f'Failed to execute the command: {command}. Try again or look in the logs.'
        finally:
            try:
                rcon_client.stop()
            except Exception as e:
                print('McRconWorker::_rcon_client_exec::stop', e)
                # raise e  # What happens if you don't catch it?

        return result

    def set_send(self, send):
        self._send = send

    def run(self):
        while self._flags.keep_working:
            command = self._get_command()
            if not command:
                continue

            if command == 'start':
                result = self._start_command()
            else:
                result = self._rcon_client_exec(command)

            self._send(result)

    def _get_command(self) -> str or None:
        try:
            command = self._commands_queue.get(timeout=5)
        except Empty:
            command = None

        return command

    def put(self, command):
        self._commands_queue.put(command)
