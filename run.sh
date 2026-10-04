#!/bin/bash
# Keeps Render's health check happy, runs the spike once, prints memory, then idles.
python3 -m http.server "${PORT:-10000}" --directory /tmp >/dev/null 2>&1 &
rm -f /tmp/.X99-lock; Xvfb :99 -screen 0 1024x768x16 >/dev/null 2>&1 &
sleep 2
( while sleep 15; do ps -eo rss,comm | awk '/terminal64/ {printf "[mem] terminal64 RSS %.0f MB\n", $1/1024}'; done ) &
cd /root/.wine/drive_c && timeout 1800 $W py/python.exe -u spike.py
echo "[spike] finished with $?"
ps -eo rss,comm --sort=-rss | head -8
sleep infinity
