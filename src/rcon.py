from mcrcon import MCRcon


class Rcon:
    def __init__(self, host, port, password):
        self.__host = host
        self.__port = int(port)
        self.__password = password
        self.__mc_rcon = None
        self.__mc_rcon_init__()

    def __mc_rcon_init__(self):
        try:
            self.__mc_rcon.disconnect()
        except:
            pass
        try:
            self.__mc_rcon = MCRcon(host=self.__host, port=self.__port, password=self.__password, timeout=1)
            self.__mc_rcon.connect()
        except:
            pass
    
    def exec(self, command: str, repeat=5):
        try:
            result = self.__mc_rcon.command(f'/{command}')
        except:
            if repeat > 0:
                self.__mc_rcon_init__()
                result = self.exec(command, repeat - 1)
            else:
                result = 'Server unavaliable'

        return result

    def disconnect(self):
        try:
            self.__mc_rcon.disconnect()
        except:
            pass
