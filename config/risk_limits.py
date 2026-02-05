from dataclasses import dataclass

@dataclass
class RiskLimits:
    max_risk_per_trade_pct: float = 0.5   # 0.5% per trade (risk at stop).[web:7][web:15]
    max_daily_loss_pct: float = 3.0       # 3% daily prop-style hard stop.[web:7]
    max_overall_loss_pct: float = 8.0     # 8% from high-watermark.
    max_gross_exposure_pct: float = 90.0  # absolute notional / equity.
    max_open_positions: int = 10
    target_monthly_return_pct: float = 12.0

RISK_LIMITS = RiskLimits()
