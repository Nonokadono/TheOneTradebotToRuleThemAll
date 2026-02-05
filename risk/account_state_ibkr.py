from dataclasses import dataclass
from ibkr_adapter.client import IBKRClient


@dataclass
class AccountState:
    equity: float
    balance: float
    unrealized_pl: float
    realized_pl: float
    margin_used: float
    margin_available: float


def fetch_account_state(client: IBKRClient) -> AccountState:
    s = client.get_account_summary()
    return AccountState(
        equity=s.equity,
        balance=s.balance,
        unrealized_pl=s.unrealized_pl,
        realized_pl=s.realized_pl,
        margin_used=s.margin_used,
        margin_available=s.margin_available,
    )
