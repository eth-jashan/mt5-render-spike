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
echo "[spike] env present: login=$([ -n "$MT5_LOGIN" ] && echo yes || echo no) server=$([ -n "$MT5_SERVER" ] && echo yes || echo no) investor=$([ -n "$MT5_INVESTOR_PASSWORD" ] && echo yes || echo no)"
D="/root/.wine/drive_c/Program Files/MetaTrader 5"
printf '[Common]\r\nLogin=%s\r\nPassword=%s\r\nServer=%s\r\nKeepPrivate=1\r\nNewsEnable=0\r\n' "$MT5_LOGIN" "$MT5_INVESTOR_PASSWORD" "$MT5_SERVER" > "$D/start.ini"
( n=0; while sleep 30; do n=$((n+1)); scrot -o /var/empty/screen-$n.png 2>/dev/null; ps -eo rss,comm | awk '/main|terminal/ {printf "[mem] %s RSS %.0f MB\n", $2, $1/1024; fflush()}'; done ) &
s=$(date +%s); ts "starting terminal64 /portable with config login"
( cd "$D" && $W terminal64.exe /portable "/config:C:\\Program Files\\MetaTrader 5\\start.ini" >/tmp/terminal.log 2>&1 & )
sleep 120
ts "terminal running $(( $(date +%s) - s ))s; tail of its log:"; ls "$D/logs" 2>/dev/null; tail -n 15 "$D"/logs/*.log 2>/dev/null | tr -d '\000' | iconv -f utf-16le -t utf-8 2>/dev/null | tail -15
cp /opt/spike.py /root/.wine/drive_c/spike.py && cd /root/.wine/drive_c && timeout 1800 $W py/python.exe -u spike.py
ts "spike finished with $?"
ps -eo rss,comm --sort=-rss | head -8
sleep infinity
