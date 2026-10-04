#!/bin/bash
# THROWAWAY. Serves Render's health check, installs MT5 at startup (logs visible), runs the spike, prints memory, idles.
python3 -m http.server "${PORT:-10000}" --directory /var/empty >/dev/null 2>&1 &
mkdir -p /var/empty
rm -f /tmp/.X99-lock; Xvfb :99 -screen 0 1024x768x16 >/dev/null 2>&1 &
sleep 2
T="/root/.wine/drive_c/Program Files/MetaTrader 5/terminal64.exe"
echo "[spike] downloading mt5setup.exe"; curl -fsSLo /tmp/mt5setup.exe https://download.mql5.com/cdn/web/metaquotes.software.corp/mt5/mt5setup.exe
start=$(date +%s); $W /tmp/mt5setup.exe /auto >/tmp/setup.log 2>&1 &
for i in $(seq 1 180); do [ -f "$T" ] && break; sleep 5; done
if [ -f "$T" ]; then echo "[spike] terminal64.exe installed after $(( $(date +%s) - start ))s"; else echo "[spike] terminal64.exe NOT installed after 15 min"; tail -20 /tmp/setup.log; fi
sleep 30; pkill -f terminal64.exe; pkill -f mt5setup.exe; sleep 5
ls "/root/.wine/drive_c/Program Files/MetaTrader 5/" | head -20
( while sleep 20; do ps -eo rss,comm | awk '/terminal64/ {printf "[mem] terminal64 RSS %.0f MB\n", $1/1024; fflush()}'; done ) &
cd /root/.wine/drive_c && timeout 1800 $W py/python.exe -u spike.py
echo "[spike] finished with $?"
ps -eo rss,comm --sort=-rss | head -8
sleep infinity
