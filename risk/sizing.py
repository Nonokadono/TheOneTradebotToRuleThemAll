from dataclasses import dataclass
from typing import Literal
from config.risk_limits import RISK_LIMITS
from strategies.base import Signal

@dataclass
class PositionPlan:
    units: int
    side: Literal["buy", "sell"]
    notional: float
    est_risk_amount: float

def compute_position_size(
    equity: float,
    signal: Signal,
    sentiment_scale: float,
) -> PositionPlan:
    risk_pct = RISK_LIMITS.max_risk_per_trade_pct / 100.0
    per_trade_risk = equity * risk_pct * sentiment_scale  # up or down depending on sentiment.
    stop_distance = abs(signal.entry_price - signal.stop_price)
    if stop_distance <= 0:
        return PositionPlan(units=0, side="buy", notional=0.0, est_risk_amount=0.0)

    # Value per pip approximated via price, assuming 1 unit ~ 1 quote currency unit.[web:6][web:9]
    units_float = per_trade_risk / stop_distance
    units = int(units_float)
    if units <= 0:
        return PositionPlan(units=0, side="buy", notional=0.0, est_risk_amount=0.0)

    side = "buy" if signal.side == "long" else "sell"
    notional = units * signal.entry_price
    est_risk = units * stop_distance
    return PositionPlan(units=units, side=side, notional=notional, est_risk_amount=est_risk)
