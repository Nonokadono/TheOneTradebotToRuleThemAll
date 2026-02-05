from ibapi.contract import Contract
from ibapi.order import Order

from ibkr_adapter.client import IBKRClient
from strategies.base import Signal
from risk.sizing import PositionPlan
from data.storage import append_log


def build_fx_contract(instrument: str) -> Contract:
    base, quote = instrument.split("_")
    c = Contract()
    c.symbol = base
    c.secType = "CASH"
    c.currency = quote
    c.exchange = "IDEALPRO"
    return c


def build_bracket_orders(signal: Signal, plan: PositionPlan):
    if plan.units == 0:
        raise ValueError("Zero units in plan")
    qty = abs(plan.units)
    parent = Order()
    parent.action = "BUY" if plan.side == "buy" else "SELL"
    parent.orderType = "MKT"
    parent.totalQuantity = qty
    parent.tif = "DAY"

    tp = Order()
    tp.action = "SELL" if parent.action == "BUY" else "BUY"
    tp.orderType = "LMT"
    tp.totalQuantity = qty
    tp.lmtPrice = float(signal.take_profit_price)

    sl = Order()
    sl.action = "SELL" if parent.action == "BUY" else "BUY"
    sl.orderType = "STP"
    sl.totalQuantity = qty
    sl.auxPrice = float(signal.stop_price)

    return parent, tp, sl


def execute_signal_ibkr(
    client: IBKRClient,
    signal: Signal,
    plan: PositionPlan,
):
    contract = build_fx_contract(signal.instrument)
    parent, tp, sl = build_bracket_orders(signal, plan)
    append_log(
        "logs/orders.log",
        f"IBKR bracket {signal.instrument} side={plan.side} units={plan.units} "
        f"entry≈{signal.entry_price} sl={signal.stop_price} tp={signal.take_profit_price} "
        f"risk={plan.est_risk_amount}",
    )
    return client.place_bracket(contract, parent, tp, sl)

