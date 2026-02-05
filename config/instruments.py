from dataclasses import dataclass
from typing import List

@dataclass
class InstrumentConfig:
    name: str
    max_leverage: float
    enabled: bool = True

INSTRUMENTS: List[InstrumentConfig] = [
    InstrumentConfig("EUR_USD", max_leverage=30.0),
    InstrumentConfig("GBP_USD", max_leverage=30.0),
    InstrumentConfig("USD_JPY", max_leverage=30.0),
    InstrumentConfig("XAU_USD", max_leverage=20.0),
    InstrumentConfig("US30_USD", max_leverage=20.0),
]
