"""THROWAWAY spike. Prints timings and counts only; never prints credentials."""
import os, time
from datetime import datetime, timezone
import MetaTrader5 as mt5

PATH = r"C:\Program Files\MetaTrader 5\terminal64.exe"

def step(name, fn):
    t = time.time(); r = fn(); print(f"[spike] {name}: {time.time() - t:.1f}s -> {r!r}"[:400], flush=True); return r

ok = step("initialize (start terminal)", lambda: mt5.initialize(path=PATH, portable=True, timeout=300000))
print("[spike] last_error", mt5.last_error(), flush=True)
if ok:
    ti = mt5.terminal_info(); print("[spike] terminal build", mt5.version(), "connected", ti.connected if ti else None, flush=True)
login, server, pw = os.environ.get("MT5_LOGIN"), os.environ.get("MT5_SERVER"), os.environ.get("MT5_INVESTOR_PASSWORD")
if ok and login and server and pw:
    for attempt in ("cold", "warm"):
        if step(f"login {attempt}", lambda: mt5.login(int(login), password=pw, server=server, timeout=120000)):
            ai = mt5.account_info()
            print(f"[spike] account trade_allowed={ai.trade_allowed} currency={ai.currency} leverage={ai.leverage}", flush=True)
            deals = step("history_deals_get all", lambda: mt5.history_deals_get(datetime(2000, 1, 1), datetime.now(timezone.utc).replace(tzinfo=None)))
            n = len(deals) if deals is not None else None
            print(f"[spike] deals={n} positions={mt5.positions_total()}", flush=True)
            if deals:
                d = deals[-1]
                print(f"[spike] last deal fields: entry={d.entry} position_id_set={d.position_id > 0} time={d.time} time_msc={d.time_msc} symbol={d.symbol}", flush=True)
                s = mt5.symbol_info(d.symbol)
                print(f"[spike] symbol spec contract={s.trade_contract_size if s else None} digits={s.digits if s else None}", flush=True)
            tick = mt5.symbol_info_tick(deals[-1].symbol) if deals else None
            if tick: print(f"[spike] server-minus-utc offset ~ {round((tick.time - time.time()) / 3600, 1)}h", flush=True)
        else:
            print("[spike] login failed", mt5.last_error(), flush=True)
else:
    print("[spike] no credentials set: skipped login", flush=True)
mt5.shutdown()
