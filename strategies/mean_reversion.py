from typing import Optional
import statistics
from .base import BaseStrategy, Signal

class MeanReversionStrategy(BaseStrategy):
    name = "mean_reversion"

    def __init__(self, lookback: int = 20, band_mult: float = 2.0) -> None:
        self.lookback = lookback
        self.band_mult = band_mult

    def generate_signal(self, instrument: str, candles) -> Optional[Signal]:
        if len(candles) < self.lookback:
            return None
        closes = [c["close"] for c in candles[-self.lookback :]]
        mean = statistics.mean(closes)
        stdev = statistics.pstdev(closes)
        upper = mean + self.band_mult * stdev
        lower = mean - self.band_mult * stdev
        last_close = closes[-1]

        if last_close < lower:
            stop = last_close - 1.5 * stdev
            tp = mean
            return Signal(
                instrument=instrument,
                side="long",
                entry_price=last_close,
                stop_price=stop,
                take_profit_price=tp,
                confidence=0.6,
                meta={"mean": mean, "stdev": stdev},
            )
        elif last_close > upper:
            stop = last_close + 1.5 * stdev
            tp = mean
            return Signal(
                instrument=instrument,
                side="short",
                entry_price=last_close,
                stop_price=stop,
                take_profit_price=tp,
                confidence=0.6,
                meta={"mean": mean, "stdev": stdev},
            )
        return None
