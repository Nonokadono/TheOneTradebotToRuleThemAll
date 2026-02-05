from typing import Dict, Any
from config.risk_limits import RISK_LIMITS
from risk.portfolio_limits_ibkr import ExposureSnapshot
from data.storage import append_log

def will_exceed_exposure(
    snapshot: ExposureSnapshot,
    planned_notional: float,
    equity: float,
) -> bool:
    if equity <= 0:
        return True
    projected_gross = snapshot.gross_exposure + planned_notional
    projected_pct = (projected_gross / equity) * 100.0
    if projected_pct > RISK_LIMITS.max_gross_exposure_pct:
        append_log(
            "logs/risk_events.log",
            f"Projected exposure {projected_pct:.2f}% > cap {RISK_LIMITS.max_gross_exposure_pct:.2f}%",
        )
        return True
    return False
