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
        mt5.symbol_select(SYMBOL, True)
        now = int(time.time())
        rates, _ = timed_call(lambda: mt5.copy_rates_range(SYMBOL, mt5.TIMEFRAME_H1, now - 400 * 86400, now + 86400), 60)
        hours = week_open_hours([int(r["time"]) for r in rates]) if rates is not None else {}
        tick = mt5.symbol_info_tick(SYMBOL)
        measured = round((tick.time - now) / 3600) if tick else None
        emit("offset", slot=slot, account=account.label, server=account.server, **infer_rule(hours),
             measured_offset_hours=measured, expected_now=expected_offset_hours(now, "EET+US-DST"))
