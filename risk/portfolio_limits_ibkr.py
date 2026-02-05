from dataclasses import dataclass
from typing import Dict, Any
from config.risk_limits import RISK_LIMITS
from data.storage import append_log


@dataclass
class ExposureSnapshot:
    gross_exposure: float
    gross_exposure_pct: float
    open_positions: int


def compute_exposure(account_equity: float,
                     open_positions_resp: Dict[str, Any]) -> ExposureSnapshot:
    gross = 0.0
    count = 0
    for pos in open_positions_resp.get("positions", []):
        qty = float(pos.get("position", 0.0))
        avg_cost = float(pos.get("avgCost", 0.0))
        notional = abs(qty * avg_cost)
        gross += notional
        if qty != 0:
            count += 1
    gross_pct = 0.0 if account_equity <= 0 else (gross / account_equity) * 100.0
    return ExposureSnapshot(
        gross_exposure=gross,
        gross_exposure_pct=gross_pct,
        open_positions=count,
    )


def check_portfolio_limits(snapshot: ExposureSnapshot) -> bool:
    if snapshot.gross_exposure_pct > RISK_LIMITS.max_gross_exposure_pct:
        append_log(
            "logs/risk_events.log",
            f"Exposure cap breached: {snapshot.gross_exposure_pct:.2f}%",
        )
        return False
    if snapshot.open_positions >= RISK_LIMITS.max_open_positions:
        append_log(
            "logs/risk_events.log",
            f"Max open positions breached: {snapshot.open_positions}",
        )
        return False
    return True
