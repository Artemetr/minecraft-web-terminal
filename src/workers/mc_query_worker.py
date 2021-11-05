import os
import threading

from mctools.mclient import BaseClient, QUERYClient

from src.modules.workers_flags import WorkersFlags


class McQueryWorker(threading.Thread):
    _server_timeout = int(os.getenv('SERVER_TIMEOUT') or 2)

    def __init__(self, flag: WorkersFlags):
        threading.Thread.__init__(self)
        self._flag = flag

    @classmethod
    def get_full_statistic(cls) -> dict:
        try:
            result = QUERYClient(host=os.getenv('QUERY_HOST'), port=int(os.getenv('QUERY_PORT')),
                                 format_method=BaseClient.REMOVE, timeout=cls._server_timeout).get_full_stats()
            result['status'] = True
        except Exception as e:
            result = {'status': False}
            print('McQueryWorker::get_full_statistic', e)
            # raise e  # What happens if you don't catch it?

        return result

    def run(self):
        while self._flag.keep_working:
            full_statistic = self.get_full_statistic()
            if full_statistic['status']:
                self._flag.server_is_running()
            else:
                self._flag.server_is_stopped()

            # TODO Сделать чтоб результат выполнения команды рассылался всем и вся
            # ws_worker.send_data_for_all_like_task({'action': 'statistic_message', 'result': result})
