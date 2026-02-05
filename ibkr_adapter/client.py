from dataclasses import dataclass
from typing import Dict, Any, List, Optional
import threading
import time

from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order

from config.ibkr_settings import IBKR_HOST, IBKR_PORT, IBKR_CLIENT_ID, IBKR_ACCOUNT_ID
from data.storage import append_log


@dataclass
class IBKRAccountSummary:
    equity: float
    balance: float
    unrealized_pl: float
    realized_pl: float
    margin_used: float
    margin_available: float


class _IBKRWrapper(EWrapper, EClient):
    def __init__(self) -> None:
        EWrapper.__init__(self)
        EClient.__init__(self, self)
        self._next_order_id: Optional[int] = None
        self._order_id_event = threading.Event()
        self._account_summary: Dict[str, float] = {}
        self._account_summary_event = threading.Event()
        self._open_positions: List[Dict[str, Any]] = []
        self._positions_event = threading.Event()
        self._last_error: Optional[str] = None

    def nextValidId(self, orderId: int) -> None:
        self._next_order_id = orderId
        self._order_id_event.set()

    def error(self, reqId: int, errorCode: int, errorString: str) -> None:
        msg = f"IBKR error reqId={reqId} code={errorCode} msg={errorString}"
        append_log("logs/errors.log", msg)
        self._last_error = msg

    # account summary
    def accountSummary(self, reqId: int, account: str, tag: str,
                       value: str, currency: str) -> None:
        if IBKR_ACCOUNT_ID and account != IBKR_ACCOUNT_ID:
            return
        try:
            v = float(value)
        except ValueError:
            return
        self._account_summary[tag] = v

    def accountSummaryEnd(self, reqId: int) -> None:
        self._account_summary_event.set()

    # positions
    def position(self, account: str, contract: Contract,
                 position: float, avgCost: float) -> None:
        if IBKR_ACCOUNT_ID and account != IBKR_ACCOUNT_ID:
            return
        self._open_positions.append(
            {
                "account": account,
                "symbol": contract.symbol,
                "secType": contract.secType,
                "currency": contract.currency,
                "position": position,
                "avgCost": avgCost,
            }
        )

    def positionEnd(self) -> None:
        self._positions_event.set()

    # helper
    def get_next_order_id(self, timeout: float = 5.0) -> int:
        if not self._order_id_event.wait(timeout):
            raise RuntimeError("Timeout waiting for nextValidId")
        if self._next_order_id is None:
            raise RuntimeError("next_order_id None")
        oid = self._next_order_id
        self._next_order_id += 1
        return oid


class IBKRClient:
    def __init__(self) -> None:
        self._app = _IBKRWrapper()
        self._thread: Optional[threading.Thread] = None
        self._connected = False

    def connect(self) -> None:
        if self._connected:
            return
        self._app.connect(IBKR_HOST, IBKR_PORT, IBKR_CLIENT_ID)
        self._thread = threading.Thread(target=self._app.run, daemon=True)
        self._thread.start()
        time.sleep(1.0)
        self._connected = True

    def disconnect(self) -> None:
        if not self._connected:
            return
        self._app.disconnect()
        self._connected = False

    def get_account_summary(self, timeout: float = 5.0) -> IBKRAccountSummary:
        self.connect()
        self._app._account_summary.clear()
        self._app._account_summary_event.clear()
        self._app.reqAccountSummary(
            1,
            "All",
            "TotalCashValue,NetLiquidation,UnrealizedPnL,RealizedPnL,MaintMarginReq,AvailableFunds",
        )
        if not self._app._account_summary_event.wait(timeout):
            raise RuntimeError("Timeout waiting for account summary")
        tags = self._app._account_summary
        equity = float(tags.get("NetLiquidation", 0.0))
        balance = float(tags.get("TotalCashValue", equity))
        unrealized = float(tags.get("UnrealizedPnL", 0.0))
        realized = float(tags.get("RealizedPnL", 0.0))
        margin_used = float(tags.get("MaintMarginReq", 0.0))
        margin_available = float(tags.get("AvailableFunds", 0.0))
        return IBKRAccountSummary(
            equity=equity,
            balance=balance,
            unrealized_pl=unrealized,
            realized_pl=realized,
            margin_used=margin_used,
            margin_available=margin_available,
        )

    def get_open_positions(self, timeout: float = 5.0) -> Dict[str, Any]:
        self.connect()
        self._app._open_positions.clear()
        self._app._positions_event.clear()
        self._app.reqPositions()
        if not self._app._positions_event.wait(timeout):
            raise RuntimeError("Timeout waiting for positions")
        return {"positions": list(self._app._open_positions)}

    def place_order(self, contract: Contract, order: Order) -> Dict[str, Any]:
        self.connect()
        order_id = self._app.get_next_order_id()
        append_log(
            "logs/orders.log",
            f"Placing order id={order_id} {contract.symbol} {order.action} {order.totalQuantity}",
        )
        self._app.placeOrder(order_id, contract, order)
        return {"order_id": order_id}

    def place_bracket(self, contract: Contract, parent: Order,
                      tp: Order, sl: Order) -> Dict[str, Any]:
        self.connect()
        base_id = self._app.get_next_order_id()
        parent.orderId = base_id
        tp.orderId = base_id + 1
        sl.orderId = base_id + 2
        tp.parentId = parent.orderId
        sl.parentId = parent.orderId
        parent.transmit = False
        tp.transmit = False
        sl.transmit = True
        self._app.placeOrder(parent.orderId, contract, parent)
        self._app.placeOrder(tp.orderId, contract, tp)
        self._app.placeOrder(sl.orderId, contract, sl)
        return {"parent_id": parent.orderId, "tp_id": tp.orderId, "sl_id": sl.orderId}
