"""Spec 10 row 6: infer each broker's time rule from a year of H1 bars, and measure today's offset."""
import time
from common import emit, timed_call
from offset import expected_offset_hours, infer_rule, week_open_hours

SYMBOL = "EURUSD"


def run(mt5, accounts, slot):
    for account in accounts:
        ok, _ = timed_call(lambda: mt5.login(account.login, password=account.investor, server=account.server, timeout=30000), 45)
        if not ok:
            continue
        symbol = next((s.name for s in mt5.symbols_get() or () if s.name.upper().startswith(SYMBOL)), SYMBOL)
        mt5.symbol_select(symbol, True)
        now = int(time.time())
        rates, waited = None, 0
        while waited < 90:  # price history downloads on first request, like trade history
            rates, _ = timed_call(lambda: mt5.copy_rates_range(symbol, mt5.TIMEFRAME_H1, now - 400 * 86400, now + 86400), 60)
            if rates is not None and len(rates) > 5000:
                break
            time.sleep(3)
            waited += 3
        hours = week_open_hours([int(r["time"]) for r in rates]) if rates is not None else {}
        tick = mt5.symbol_info_tick(symbol)
        measured = round((tick.time - now) / 3600) if tick else None
        emit("offset", slot=slot, account=account.label, server=account.server, symbol=symbol, bars=0 if rates is None else len(rates), waited_s=waited, **infer_rule(hours),
             measured_offset_hours=measured, expected_now=expected_offset_hours(now, "EET+US-DST"))
