"""Runs the probes named in SPIKE_PROBES (comma-separated) against this slot's terminal."""
import importlib, os, sys, traceback

# The embeddable Python ignores the script folder (python311._pth), so add it for the probe modules.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import MetaTrader5 as mt5
from common import emit, load_accounts, redact, timed_call

PATH = os.environ.get("SPIKE_TERMINAL", r"C:\Program Files\MetaTrader 5\terminal64.exe")
SLOT = os.environ.get("SPIKE_SLOT", "s1")


def main() -> int:
    accounts = load_accounts(os.environ["SPIKE_ACCOUNTS"])
    secrets = [a.investor for a in accounts] + [a.master for a in accounts if a.master]
    ok, seconds = timed_call(lambda: mt5.initialize(path=PATH, portable=True, timeout=300000), 330)
    emit("initialize", slot=SLOT, ok=bool(ok), seconds=round(seconds, 2), error=str(mt5.last_error()), build=str(mt5.version()))
    if not ok:
        return 1
    for name in filter(None, os.environ.get("SPIKE_PROBES", "").split(",")):
        try:
            importlib.import_module(f"p_{name}").run(mt5, accounts, SLOT)
        except Exception:
            emit("probe-crashed", slot=SLOT, probe_name=name, trace=redact(traceback.format_exc(), secrets)[-1500:])
    mt5.shutdown()
    return 0


if __name__ == "__main__":
    sys.exit(main())
