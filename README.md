# Minecraft Web Terminal

*Скоро допишу доку.*

## Required

* Python 3.

## Activate environment

```shell
./activate
```

To activate production version, do:

```shell
./activate -p
```

## Run server

```shell
python3 ws_server.py
```

To change environment, edit `.env` file.

## Minecraft start script example

```shell
#!/bin/bash

cd /Users/artemetr/Projects/Artemetr/minecraft-web-terminal/.server && jdk-17.0.1.jdk/Contents/Home/bin/java -jar server.jar nogui &> /dev/null &

```
