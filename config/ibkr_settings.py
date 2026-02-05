import os
from dataclasses import dataclass

IBKR_HOST = os.getenv("IBKR_HOST", "127.0.0.1")
IBKR_PORT = int(os.getenv("IBKR_PORT", "4002"))  # your Gateway port
IBKR_CLIENT_ID = int(os.getenv("IBKR_CLIENT_ID", "1"))
IBKR_ACCOUNT_ID = os.getenv("IBKR_ACCOUNT_ID", "")

BASE_CURRENCY = os.getenv("BASE_CURRENCY", "USD")
LOG_LEVEL = os.getenv("TRADEBOT_LOG_LEVEL", "INFO")

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")


@dataclass
class Timeframes:
    signal_tf: str = "15min"
    confirm_tf: str = "1h"
    risk_tf: str = "1d"


TIMEFRAMES = Timeframes()

