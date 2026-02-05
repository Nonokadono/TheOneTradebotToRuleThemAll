import time
from datetime import datetime

from config.instruments import INSTRUMENTS
from config.risk_limits import RISK_LIMITS
from strategies.mean_reversion import MeanReversionStrategy
from strategies.momentum import MomentumStrategy
from strategies.sentiment_module import SentimentModule
from ibkr_adapter.client import IBKRClient
from risk.account_state_ibkr import fetch_account_state
from risk.drawdown_monitor import load_state, can_trade
from risk.portfolio_limits_ibkr import compute_exposure, check_portfolio_limits
from risk.sizing import compute_position_size
from execution.exposure import will_exceed_exposure
from execution.ibkr_orders import execute_signal_ibkr
from data.storage import append_log


class TradingBot:
    def __init__(self) -> None:
        self.client = IBKRClient()
        self.strategies = [
            MeanReversionStrategy(),
            MomentumStrategy(),
        ]
        self.sentiment = SentimentModule()

    def run_forever(self, sleep_seconds: int = 60) -> None:
        while True:
            try:
                self.run_once()
            except Exception as e:
                append_log("logs/errors.log", f"run_once error {e}")
            time.sleep(sleep_seconds)

    def run_once(self) -> None:
        account_state = fetch_account_state(self.client)
        today = datetime.utcnow().date().isoformat()
        dd_state = load_state(today, account_state.equity)
        if not can_trade(account_state.equity, dd_state):
            append_log("logs/risk_events.log", "Trade blocked by drawdown rules")
            return

        positions = self.client.get_open_positions()
        exposure_snapshot = compute_exposure(account_state.equity, positions)
        if not check_portfolio_limits(exposure_snapshot):
            append_log("logs/risk_events.log", "Trade blocked by portfolio limits")
            return

        for inst_cfg in INSTRUMENTS:
            if not inst_cfg.enabled:
                continue
            instrument = inst_cfg.name
            # TODO: replace with IBKR historical data fetch
            candles = []  # placeholder; keep structure like existing strategies expect
            for strat in self.strategies:
                signal = strat.generate_signal(instrument, candles)
                if signal is None:
                    continue

                raw_sent = self.sentiment.get_score(instrument, "signal")
                scale = self.sentiment.scale_for_risk(raw_sent)
                plan = compute_position_size(account_state.equity, signal, scale)
                if plan.units == 0:
                    continue

                if will_exceed_exposure(exposure_snapshot, plan.notional, account_state.equity):
                    append_log("logs/risk_events.log", "Planned trade exceeds exposure cap")
                    continue

                execute_signal_ibkr(self.client, signal, plan)
                return  # one trade per cycle for now

