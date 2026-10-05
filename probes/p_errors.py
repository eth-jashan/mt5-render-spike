"""Spec 10 row 8: the last_error() codes behind each farm error row in spec section 7.4."""
from common import emit, timed_call

def run(mt5, accounts, slot):
    good = accounts[0]
    cases = {
        "wrong-password": (good.login, "not-the-password-1", good.server),
        "unknown-login": (1, good.investor, good.server),
        "unknown-server": (good.login, good.investor, "NoSuchBroker-Server-42"),
    }
    for case, (login, password, server) in cases.items():
        ok, seconds = timed_call(lambda: mt5.login(login, password=password, server=server, timeout=30000), 45)
        emit("error-code", slot=slot, case=case, ok=bool(ok), seconds=round(seconds, 2), error=str(mt5.last_error()))
