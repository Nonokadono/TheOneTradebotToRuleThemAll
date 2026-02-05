from dataclasses import dataclass
from typing import Optional
from config.risk_limits import RISK_LIMITS
from data.storage import load_json, save_json, append_log

STATE_FILE = "risk/drawdown_state.json"

@dataclass
class DrawdownState:
    eq_high_watermark: float
    daily_start_equity: float
    current_day: str  # YYYY-MM-DD

def load_state(current_day: str, current_equity: float) -> DrawdownState:
    data = load_json(STATE_FILE)
    if data is None:
        state = DrawdownState(
            eq_high_watermark=current_equity,
            daily_start_equity=current_equity,
            current_day=current_day,
        )
        save_state(state)
        return state
    state = DrawdownState(**data)
    if state.current_day != current_day:
        state.daily_start_equity = current_equity
        state.current_day = current_day
        if current_equity > state.eq_high_watermark:
            state.eq_high_watermark = current_equity
        save_state(state)
    return state

def save_state(state: DrawdownState) -> None:
    save_json(STATE_FILE, state.__dict__)

def can_trade(current_equity: float, state: DrawdownState) -> bool:
    daily_drawdown_pct = 0.0 if state.daily_start_equity <= 0 else (
        (state.daily_start_equity - current_equity) / state.daily_start_equity * 100.0
    )
    overall_drawdown_pct = 0.0 if state.eq_high_watermark <= 0 else (
        (state.eq_high_watermark - current_equity) / state.eq_high_watermark * 100.0
    )

    if daily_drawdown_pct > RISK_LIMITS.max_daily_loss_pct:
        append_log("logs/risk_events.log", f"Daily DD breached: {daily_drawdown_pct:.2f}%")
        return False
    if overall_drawdown_pct > RISK_LIMITS.max_overall_loss_pct:
        append_log("logs/risk_events.log", f"Overall DD breached: {overall_drawdown_pct:.2f}%")
        return False
    return True
