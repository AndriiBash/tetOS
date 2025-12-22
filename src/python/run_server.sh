#!/bin/sh
cd "$(dirname "$0")"

exec java -Xms2G -Xmx4G -jar server.jar --nogui
