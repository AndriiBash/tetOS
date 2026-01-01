#!/bin/sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SERVER_DIR="$SCRIPT_DIR/../server"

cd "$SERVER_DIR" || { echo "Error: server directory not found!"; exit 1; }

exec java -Xms2G -Xmx6G -jar server.jar --nogui
