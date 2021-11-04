from mcrcon import MCRcon


class McRcon(MCRcon):
    def __init__(self, host, password, port=25575, tlsmode=0, timeout=5):
        self.host = host
        self.password = password
        self.port = port
        self.tlsmode = tlsmode
        self.timeout = timeout


class Rcon:
    def __init__(self, host, port, password):
        self.__host = host
        self.__port = int(port)
        self.__password = password
    
    def exec(self, command: str, repeat=3):
        try:
            with McRcon(host=self.__host, port=self.__port, password=self.__password, timeout=1) as mc:
                result = mc.command(f'{command}')
        except:
            if repeat > 0:
                result = self.exec(command, repeat - 1)
            else:
                result = 'Server unavailable'

        return result
