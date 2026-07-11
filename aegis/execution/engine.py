from __future__ import annotations

from typing import Any, Dict

from .fill_handler import FillHandler
from .metrics import ExecutionMetrics
from .order_builder import OrderBuilder
from .retry_policy import RetryPolicy


class ExecutionEngine:
    def __init__(self, broker, portfolio, logger, cfg: Dict[str, Any]):
        self.broker = broker
        self.portfolio = portfolio
        self.logger = logger
        self.cfg = dict(cfg or {})
        self.order_builder = OrderBuilder()
        self.fill_handler = FillHandler()
        self.retry_policy = RetryPolicy(int(self.cfg.get("max_retries", 3) or 3))
        self.metrics = ExecutionMetrics()

    def configure(self, cfg: Dict[str, Any]) -> None:
        self.cfg.update(dict(cfg or {}))

    def execute(self, trade_intent: Dict[str, Any]) -> Dict[str, Any]:
        return self.execute_trade_intent(trade_intent)

    def execute_trade_intent(self, trade_intent: Dict[str, Any]) -> Dict[str, Any]:
        order = self._build_order(trade_intent)
        result = self._submit(order)
        if result.get("status") == "filled" and self.portfolio is not None:
            self.portfolio.apply_trade(trade_intent)
        result["order"] = order
        result["fill_summary"] = self.fill_handler.summarize(result)
        return result

    def cancel(self, order_id: str):
        return self.broker.cancel_order(order_id)

    def _build_order(self, trade_intent: Dict[str, Any]) -> Dict[str, Any]:
        return self.order_builder.build(trade_intent)

    def _submit(self, order: Dict[str, Any]) -> Dict[str, Any]:
        attempts = max(1, int(getattr(self.retry_policy, "max_retries", 1)))
        result: Dict[str, Any] = {"status": "rejected"}
        for attempt in range(1, attempts + 1):
            self.metrics.record_submission()
            result = dict(self.broker.submit_order(order))
            if result.get("status") == "filled":
                self.metrics.record_fill()
            if not self.retry_policy.should_retry(attempt, result):
                break
        return result