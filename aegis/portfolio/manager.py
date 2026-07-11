from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict

from .positions import Position


class PortfolioManager:
    def __init__(self, cfg: Dict[str, Any], broker, logger):
        self.cfg = dict(cfg or {})
        self.broker = broker
        self.logger = logger
        self.positions: Dict[str, Position] = {}
        self.cash: float = float(self.cfg.get("initial_cash", 0.0))

    def update_from_broker(self) -> None:
        positions = self.broker.get_positions()
        account = self.broker.get_account()
        self._reconcile(positions, account)

    def apply_trade(self, trade_intent: Dict[str, Any]) -> None:
        symbol = trade_intent["symbol"]
        qty = int(trade_intent.get("qty", 0))
        price = float(trade_intent.get("entry", 0.0) or 0.0)
        side = str(trade_intent.get("side", "BUY")).upper()
        signed_qty = -qty if side == "SELL" else qty
        position = self.positions.get(symbol, Position(symbol=symbol))
        new_qty = position.qty + signed_qty
        if new_qty == 0:
            self.positions.pop(symbol, None)
        else:
            if signed_qty > 0 and position.qty > 0:
                total_qty = position.qty + signed_qty
                if total_qty:
                    position.avg_price = ((position.avg_price * position.qty) + (price * signed_qty)) / total_qty
            elif signed_qty > 0:
                position.avg_price = price
            position.qty = new_qty
            self.positions[symbol] = position
        cash_delta = price * qty
        self.cash = self.cash - cash_delta if side == "BUY" else self.cash + cash_delta

    def enter_position(self, symbol: str, qty: int, avg_price: float) -> Position:
        position = Position(symbol=symbol, qty=int(qty), avg_price=float(avg_price))
        self.positions[str(symbol)] = position
        return position

    def exit_position(self, symbol: str) -> Position | None:
        return self.positions.pop(str(symbol), None)

    def mark_to_market(self, symbol: str, last_price: float) -> float:
        position = self.positions.get(str(symbol))
        if position is None:
            return 0.0
        return (float(last_price) - float(position.avg_price)) * int(position.qty)

    def get_snapshot(self) -> Dict[str, Any]:
        return self.snapshot()

    def snapshot(self) -> Dict[str, Any]:
        return {"positions": {symbol: asdict(position) for symbol, position in self.positions.items()}, "cash": float(self.cash)}

    def _reconcile(self, broker_positions, account) -> None:
        self.positions = {}
        for row in broker_positions or []:
            symbol = row.get("symbol") if isinstance(row, dict) else getattr(row, "symbol", None)
            if not symbol:
                continue
            self.positions[str(symbol)] = Position(
                symbol=str(symbol),
                qty=int(row.get("qty", 0) if isinstance(row, dict) else getattr(row, "qty", 0)),
                avg_price=float(row.get("avg_price", 0.0) if isinstance(row, dict) else getattr(row, "avg_price", 0.0)),
            )
        if isinstance(account, dict):
            self.cash = float(account.get("cash", self.cash))