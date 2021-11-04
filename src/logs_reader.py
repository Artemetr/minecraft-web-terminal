import os


def follow(thefile):
    thefile.seek(0, os.SEEK_END)
    while True:
        line = thefile.readline()
        yield line


def tail():
    with open(os.getenv('LOGS_FILE'), 'r') as f:
        for line in follow(f):
            yield line
