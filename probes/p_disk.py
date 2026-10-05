"""Spec 10 row 2: after logins through mt5.login, is any password stored in the terminal's files?
Then: which files are they, and does login still work after deleting them?"""
import os
from common import emit, timed_call
from disksearch import find_secret

DATA = os.environ.get("SPIKE_TERMINAL_DIR", r"C:\Program Files\MetaTrader 5")


def run(mt5, accounts, slot):
    for account in accounts:
        timed_call(lambda: mt5.login(account.login, password=account.investor, server=account.server, timeout=30000), 45)
    hits = sorted({path for a in accounts for path in find_secret(DATA, a.investor)})
    emit("disk-after-login", slot=slot, files_with_password=hits)
    for path in hits:
        os.remove(os.path.join(DATA, path))
    emit("disk-after-wipe", slot=slot, files_with_password=sorted({p for a in accounts for p in find_secret(DATA, a.investor)}))
    first = accounts[0]
    ok, seconds = timed_call(lambda: mt5.login(first.login, password=first.investor, server=first.server, timeout=30000), 45)
    emit("login-after-wipe", slot=slot, account=first.label, ok=bool(ok), seconds=round(seconds, 2), error=str(mt5.last_error()))
