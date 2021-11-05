import os


def tail(log_file_path: str):
    def follow(file):
        file.seek(0, os.SEEK_END)
        while True:
            yield file.readline()

    with open(log_file_path, 'r') as f:
        for line in follow(f):
            yield line
