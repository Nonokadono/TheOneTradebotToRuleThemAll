from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class Signal:
    instrument: str
    side: str  # "long" or "short"
    entry_price: float
    stop_price: float
    take_profit_price: float
    confidence: float  # 0..1
    meta: Dict[str, Any]

class BaseStrategy:
    name: str = "base"

    def generate_signal(self, instrument: str, candles) -> Optional[Signal]:
        raise NotImplementedError
