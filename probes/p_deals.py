"""Spec 10 rows 4-5: every field of every deal and open position, and how investor mode shows."""
from common import emit, timed_call

DEAL_FIELDS = ("ticket", "order", "time", "time_msc", "type", "entry", "magic", "position_id", "reason",
               "volume", "price", "commission", "swap", "profit", "fee", "symbol", "comment")
INFO_FIELDS = ("trade_allowed", "trade_expert", "trade_mode", "margin_mode", "currency", "company", "server", "leverage")


def account_view(info):
    return {field: getattr(info, field, None) for field in INFO_FIELDS}


def run(mt5, accounts, slot):
    for account in accounts:
        ok, _ = timed_call(lambda: mt5.login(account.login, password=account.investor, server=account.server, timeout=30000), 45)
        if not ok:
            emit("deals-login-failed", slot=slot, account=account.label, error=str(mt5.last_error()))
            continue
        emit("account-investor", slot=slot, account=account.label, **account_view(mt5.account_info()))
        deals, _ = timed_call(lambda: mt5.history_deals_get(0, 2_000_000_000), 60)
        for deal in deals or ():
            emit("deal", slot=slot, account=account.label, **{f: getattr(deal, f, None) for f in DEAL_FIELDS})
        positions, _ = timed_call(lambda: mt5.positions_get(), 15)
        emit("positions", slot=slot, account=account.label, ids=[p.ticket for p in positions or ()],
             identifiers=[p.identifier for p in positions or ()])
        for symbol in sorted({d.symbol for d in deals or () if d.symbol}):
            info = mt5.symbol_info(symbol)
            emit("symbol", slot=slot, account=account.label, symbol=symbol,
                 contract=getattr(info, "trade_contract_size", None), tick=getattr(info, "trade_tick_size", None),
                 digits=getattr(info, "digits", None), profit_currency=getattr(info, "currency_profit", None))
        if account.master:
            ok, _ = timed_call(lambda: mt5.login(account.login, password=account.master, server=account.server, timeout=30000), 45)
            if ok:
                emit("account-master", slot=slot, account=account.label, **account_view(mt5.account_info()))
