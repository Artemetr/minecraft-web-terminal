import os
import sys
import time
import dotenv
import socket
from mcstatus import MinecraftServer

dotenv.load_dotenv()

server = MinecraftServer(os.getenv('QUERY_HOST'), int(os.getenv('QUERY_PORT')))
response = server.query()
response = server.ping()
response = server.status()
print(response)