# THROWAWAY spike: can an MT5 terminal + the MetaTrader5 Python package run headless under Wine on x86_64 Linux?
FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive WINEPREFIX=/root/.wine WINEARCH=win64 WINEDEBUG=-all DISPLAY=:99 W=/usr/lib/wine/wine64
RUN apt-get update && apt-get install -y --no-install-recommends wine64 wine xvfb ca-certificates curl procps unzip python3 && rm -rf /var/lib/apt/lists/*
RUN (Xvfb :99 -screen 0 1024x768x16 &) && sleep 2 && $W wineboot --init && sleep 5 \
 && mkdir -p /root/.wine/drive_c/py && cd /root/.wine/drive_c/py \
 && curl -fsSLo py.zip https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip && unzip -q py.zip && rm py.zip \
 && sed -i 's/^#import site/import site/' python311._pth \
 && curl -fsSLo get-pip.py https://bootstrap.pypa.io/get-pip.py && $W python.exe get-pip.py --no-warn-script-location -q \
 && timeout 600 $W python.exe -m pip install -q --no-cache-dir numpy==1.26.4 MetaTrader5 \
 && timeout 120 $W python.exe -c "import MetaTrader5 as m; print('mt5 pkg', m.__version__)" \
 && (pkill wineserver; pkill -x Xvfb; sleep 2; rm -f /tmp/.X99-lock; true)
COPY spike.py /root/.wine/drive_c/spike.py
COPY run.sh /run.sh
CMD ["bash", "/run.sh"]
