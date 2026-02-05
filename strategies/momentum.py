from typing import Optional
from .base import BaseStrategy, Signal

class MomentumStrategy(BaseStrategy):
    name = "momentum"

    def __init__(self, fast: int = 10, slow: int = 30) -> None:
        self.fast = fast
        self.slow = slow

    def generate_signal(self, instrument: str, candles) -> Optional[Signal]:
        if len(candles) < self.slow:
            return None
        closes = [c["close"] for c in candles]
        fast_ma = sum(closes[-self.fast:]) / self.fast
        slow_ma = sum(closes[-self.slow:]) / self.slow
        last_price = closes[-1]

        if fast_ma > slow_ma:
            stop = last_price * 0.995
            tp = last_price * 1.01
            return Signal(
                instrument=instrument,
                side="long",
                entry_price=last_price,
                stop_price=stop,
                take_profit_price=tp,
                confidence=0.7,
                meta={"fast_ma": fast_ma, "slow_ma": slow_ma},
            )
        elif fast_ma < slow_ma:
            stop = last_price * 1.005
            tp = last_price * 0.99
            return Signal(
                instrument=instrument,
                side="short",
                entry_price=last_price,
                stop_price=stop,
                take_profit_price=tp,
                confidence=0.7,
                meta={"fast_ma": fast_ma, "slow_ma": slow_ma},
            )
        return None
