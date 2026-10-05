#!/bin/bash
# THROWAWAY spike. Serves /var/empty (results.jsonl, screenshots), prepares one golden Wine prefix with
# Python + MT5, then runs the probes: SPIKE_MODE=single (all probes, slot s1) or four (switching on 4 slots).
mkdir -p /var/empty && python3 -m http.server "${PORT:-10000}" --directory /var/empty >/dev/null 2>&1 &
Xvfb :99 -screen 0 1024x768x16 >/dev/null 2>&1 &
sleep 2
ts() { echo "[spike] $(date +%T) $*"; }
t0=$(date +%s)
ts "wineboot ($($W --version))"; timeout 300 $W wineboot --init >/dev/null 2>&1; ts "wineboot done rc=$?"; sleep 3; $W winecfg -v win10 >/dev/null 2>&1
P=/root/.wine/drive_c/py; mkdir -p $P && cd $P && unzip -q /opt/dl/py.zip && sed -i 's/^#import site/import site/' python311._pth
ts "pip"; $W python.exe /opt/dl/get-pip.py -q --no-warn-script-location >/dev/null 2>&1
timeout 600 $W python.exe -m pip install -q --no-cache-dir numpy==1.26.4 MetaTrader5 >/dev/null 2>&1
ts "wine+python ready after $(( $(date +%s) - t0 ))s"
T="/root/.wine/drive_c/Program Files/MetaTrader 5/terminal64.exe"
s=$(date +%s); $W /opt/dl/mt5setup.exe /auto >/tmp/setup.log 2>&1 &
for i in $(seq 1 180); do [ -f "$T" ] && break; sleep 5; done
[ -f "$T" ] && ts "terminal installed after $(( $(date +%s) - s ))s" || { ts "terminal NOT installed"; tail -20 /tmp/setup.log; sleep infinity; }
ts "letting LiveUpdate download for 150s"; sleep 150; pkill -f terminal64.exe; pkill -f mt5setup.exe; sleep 8
# Accounts: SPIKE_ACCOUNTS (JSON), or the first spike's MT5_* variables as account "mq1".
if [ -z "$SPIKE_ACCOUNTS" ] && [ -n "$MT5_LOGIN" ]; then
  export SPIKE_ACCOUNTS=$(python3 -c 'import json,os; print(json.dumps([{"label":"mq1","login":int(os.environ["MT5_LOGIN"]),"server":os.environ["MT5_SERVER"],"investor":os.environ["MT5_INVESTOR_PASSWORD"]}]))')
fi
ts "accounts configured: $(python3 -c 'import json,os; print([a["label"] for a in json.loads(os.environ.get("SPIKE_ACCOUNTS","[]"))])')"
# No login and no password in the startup config (spec 6.2); Task 3 records whether the wizard then blocks.
printf '[Common]\r\nNewsEnable=0\r\n' > /root/.wine/drive_c/start.ini
for f in /opt/brokers/*/servers.dat; do [ -f "$f" ] && cp "$f" "/root/.wine/drive_c/Program Files/MetaTrader 5/config/" && ts "seeded $(dirname "$f")"; done
( while sleep 30; do line="{\"probe\": \"memory\", \"total_rss_mb\": $(ps -eo rss= | awk '{s+=$1} END {print int(s/1024)}'), \"free_mb\": $(free -m | awk '/Mem:/ {print $7}')}"; echo "[result] $line"; echo "$line" >> /var/empty/results.jsonl; done ) &
start_slot() {  # $1 = slot number; copies the golden prefix and starts its terminal
  local n=$1 P=/slots/s$1; mkdir -p /slots; cp -a /root/.wine "$P"
  ( export WINEPREFIX="$P"; cd "$P/drive_c/Program Files/MetaTrader 5" && $W terminal64.exe /portable '/config:C:\start.ini' >/tmp/terminal-s$n.log 2>&1 & )
}
run_slot() {    # $1 = slot number, $2 = probes, $3 = switches
  local n=$1; export WINEPREFIX=/slots/s$n
  cp -r /opt/probes /slots/s$n/drive_c/probes && cd /slots/s$n/drive_c/probes
  SPIKE_RESULTS='Z:\var\empty\results.jsonl' SPIKE_SLOT=s$n SPIKE_PROBES=$2 SPIKE_SWITCHES=$3 timeout 7200 $W ../py/python.exe -u run_probes.py
}
if [ "${SPIKE_MODE:-single}" = "four" ]; then
  for n in 1 2 3 4; do start_slot $n; done; sleep 90
  for n in 1 2 3 4; do ( run_slot $n switching "${SPIKE_SWITCHES:-60}" ) & done; wait
else
  start_slot 1; sleep 90
  run_slot 1 "${SPIKE_PROBES:-switching,disk,broker,deals,offset,errors}" "${SPIKE_SWITCHES:-200}"
fi
ts "probes finished after $(( $(date +%s) - t0 ))s"
echo "{\"probe\": \"finished\", \"seconds\": $(( $(date +%s) - t0 ))}" >> /var/empty/results.jsonl
sleep infinity
