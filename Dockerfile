# THROWAWAY spike: can an MT5 terminal + the MetaTrader5 Python package run headless under Wine on x86_64 Linux?
# The build only installs packages and downloads files; all Wine work runs at container start (run.sh),
# because background Wine processes keep Render's builder from finishing a step.
FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive WINEPREFIX=/root/.wine WINEARCH=win64 WINEDEBUG=-all DISPLAY=:99 W=/usr/lib/wine/wine64
RUN apt-get update && apt-get install -y --no-install-recommends wine64 wine xvfb ca-certificates curl procps unzip python3 scrot && rm -rf /var/lib/apt/lists/*
RUN mkdir -p /opt/dl && cd /opt/dl \
 && curl -fsSLo py.zip https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip \
 && curl -fsSLo get-pip.py https://bootstrap.pypa.io/get-pip.py \
 && curl -fsSLo mt5setup.exe https://download.mql5.com/cdn/web/metaquotes.software.corp/mt5/mt5setup.exe
COPY spike.py /opt/spike.py
COPY run.sh /run.sh
CMD ["bash", "/run.sh"]
