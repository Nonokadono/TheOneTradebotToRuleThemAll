from data.storage import append_log
from risk.drawdown_monitor import can_trade, DrawdownState

class KillSwitch:
    def __init__(self) -> None:
        self.triggered = False

    def evaluate(self, equity: float, state: DrawdownState) -> bool:
        """
        Returns True if trading is allowed, False if kill-switch is active.
        """
        if self.triggered:
            return False
        allowed = can_trade(equity, state)
        if not allowed:
            self.triggered = True
            append_log("logs/risk_events.log", "Kill switch activated; trading halted.")
        return allowed
