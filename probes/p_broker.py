"""Spec 10 row 3: does a non-MetaQuotes broker's server resolve in a stock terminal?"""
from common import emit, timed_call


def run(mt5, accounts, slot):
    for account in accounts:
        if account.server.lower().startswith("metaquotes"):
            continue
        ok, seconds = timed_call(lambda: mt5.login(account.login, password=account.investor, server=account.server, timeout=60000), 75)
        info = mt5.account_info() if ok else None
        emit("second-broker", slot=slot, account=account.label, ok=bool(ok), seconds=round(seconds, 2),
             error=str(mt5.last_error()), company=getattr(info, "company", None))
