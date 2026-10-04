#!/bin/bash
# THROWAWAY. Serves Render's port, sets up Wine + Python + MT5 (all logged), runs the spike, prints memory, idles.
mkdir -p /var/empty && python3 -m http.server "${PORT:-10000}" --directory /var/empty >/dev/null 2>&1 &
Xvfb :99 -screen 0 1024x768x16 >/dev/null 2>&1 &
sleep 2
ts() { echo "[spike] $(date +%T) $*"; }
t0=$(date +%s)
ts "wineboot"; $W wineboot --init >/dev/null 2>&1; sleep 3
P=/root/.wine/drive_c/py; mkdir -p $P && cd $P && unzip -q /opt/dl/py.zip && sed -i 's/^#import site/import site/' python311._pth
ts "pip"; $W python.exe /opt/dl/get-pip.py -q --no-warn-script-location >/dev/null 2>&1
timeout 600 $W python.exe -m pip install -q --no-cache-dir numpy==1.26.4 MetaTrader5 >/dev/null 2>&1
$W python.exe -c "import MetaTrader5 as m; print('[spike] mt5 pkg', m.__version__)"
ts "wine+python ready after $(( $(date +%s) - t0 ))s"
T="/root/.wine/drive_c/Program Files/MetaTrader 5/terminal64.exe"
s=$(date +%s); $W /opt/dl/mt5setup.exe /auto >/tmp/setup.log 2>&1 &
for i in $(seq 1 180); do [ -f "$T" ] && break; sleep 5; done
if [ -f "$T" ]; then ts "terminal64.exe installed after $(( $(date +%s) - s ))s"; else ts "terminal64.exe NOT installed after 15 min"; tail -20 /tmp/setup.log; fi
sleep 45; pkill -f terminal64.exe; pkill -f mt5setup.exe; sleep 5
ls "/root/.wine/drive_c/Program Files/MetaTrader 5/" | tr '\n' ' '; echo
( while sleep 20; do ps -eo rss,comm | awk '/terminal64/ {printf "[mem] terminal64 RSS %.0f MB\n", $1/1024; fflush()}'; done ) &
cp /opt/spike.py /root/.wine/drive_c/spike.py && cd /root/.wine/drive_c && timeout 1800 $W py/python.exe -u spike.py
ts "spike finished with $?"
ps -eo rss,comm --sort=-rss | head -8
sleep infinity
