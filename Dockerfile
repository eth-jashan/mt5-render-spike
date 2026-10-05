# THROWAWAY spike: can an MT5 terminal + the MetaTrader5 Python package run headless under Wine on x86_64 Linux?
# The build only installs packages and downloads files; all Wine work runs at container start (run.sh),
# because background Wine processes keep Render's builder from finishing a step.
FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive WINEPREFIX=/root/.wine WINEARCH=win64 WINEDEBUG=-all DISPLAY=:99 W=wine WINEDLLOVERRIDES="mscoree=;mshtml="
# Wine 10, pinned: the terminal calls Wine 8 "unsupported", and its installer rejected Wine 11 (spike).
ARG WINE_VERSION=10.0.0.0~bookworm-1
RUN dpkg --add-architecture i386 && apt-get update && apt-get install -y --no-install-recommends \
      ca-certificates curl gnupg xvfb procps unzip python3 scrot xdotool \
 && mkdir -pm755 /etc/apt/keyrings \
 && curl -fsSL https://dl.winehq.org/wine-builds/winehq.key | gpg --dearmor -o /etc/apt/keyrings/winehq.gpg \
 && echo "deb [signed-by=/etc/apt/keyrings/winehq.gpg] https://dl.winehq.org/wine-builds/debian/ bookworm main" > /etc/apt/sources.list.d/winehq.list \
 && apt-get update && apt-get install -y --install-recommends \
      winehq-stable=$WINE_VERSION wine-stable=$WINE_VERSION wine-stable-amd64=$WINE_VERSION wine-stable-i386=$WINE_VERSION \
 && rm -rf /var/lib/apt/lists/* && wine --version
RUN mkdir -p /opt/dl && cd /opt/dl \
 && curl -fsSLo py.zip https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip \
 && curl -fsSLo get-pip.py https://bootstrap.pypa.io/get-pip.py \
 && curl -fsSLo mt5setup.exe https://download.mql5.com/cdn/web/metaquotes.software.corp/mt5/mt5setup.exe
COPY probes /opt/probes
COPY brokers /opt/brokers
COPY run.sh /run.sh
CMD ["bash", "/run.sh"]
