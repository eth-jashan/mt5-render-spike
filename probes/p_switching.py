"""Spec 10 row 1: switch accounts in one terminal SWITCHES times; time each and check the account."""
import os
from common import CallTimeout, emit, timed_call
from stats import summarize_switches

SWITCHES = int(os.environ.get("SPIKE_SWITCHES", "200"))


def run(mt5, accounts, slot):
    rows = []
    for i in range(SWITCHES):
        account = accounts[i % len(accounts)]
        row = {"ok": False, "wrong_account": False, "seconds": None, "error": None}
        try:
            ok, seconds = timed_call(lambda: mt5.login(account.login, password=account.investor, server=account.server, timeout=30000), 45)
            row["seconds"] = round(seconds, 2)
            info = mt5.account_info() if ok else None
            row["ok"] = bool(ok)
            row["wrong_account"] = bool(ok and (info is None or info.login != account.login))
            if not ok:
                row["error"] = str(mt5.last_error())
            else:
                deals, read_seconds = timed_call(lambda: mt5.history_deals_get(0, 2_000_000_000), 60)
                row["read_seconds"] = round(read_seconds, 2)
                row["deals"] = len(deals) if deals is not None else None
        except CallTimeout as timeout:
            row["error"] = f"timeout: {timeout}"
        emit("switch", slot=slot, account=account.label, n=i, **row)
        rows.append(row)
    emit("switch-summary", slot=slot, **summarize_switches(rows))
