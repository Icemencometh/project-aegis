from __future__ import annotations

import warnings

warnings.warn(
    "Legacy module execution_engine.py is deprecated; use aegis.execution.",
    DeprecationWarning,
    stacklevel=2,
)

import time
from datetime import datetime, time as dt_time
from typing import Any, Dict, Optional
from uuid import uuid4

from approval_queue import ApprovalQueue
from modules.approval_queue import ApprovalQueue as _ApprovalQueue
from modules.paper_broker import PaperBroker
from portfolio_manager import PortfolioManager


_QUEUE = _ApprovalQueue()


class ExecutionEngine:
    """
    Approval-flow execution engine backed by a broker and portfolio manager.

    The root webhook uses this class directly via execute(trade_id).
    """

    _halted = False
    _broker = None
    _portfolio = None
    _logger = None
    _cfg: Dict[str, Any] = {
        "allow_after_hours": False,
        "market_open": dt_time(9, 30),
        "market_close": dt_time(16, 0),
        "max_retries": 3,
        "retry_delay_seconds": 0.0,
        "initial_cash": 100000.0,
        "default_order_type": "market",
    }

    @classmethod
    def configure(cls, broker=None, portfolio_manager=None, logger=None, cfg=None):
        if broker is not None:
            cls._broker = broker
        if portfolio_manager is not None:
            cls._portfolio = portfolio_manager
        if logger is not None:
            cls._logger = logger
        if cfg:
            merged = dict(cls._cfg)
            merged.update(cfg)
            cls._cfg = merged

    @classmethod
    def halt_trading(cls):
        cls._halted = True

    @classmethod
    def resume_trading(cls):
        cls._halted = False

    @classmethod
    def get_portfolio_snapshot(cls):
        return cls._get_portfolio().snapshot()

    @classmethod
    def execution_quality_report(cls):
        return cls._get_portfolio().get_execution_quality_report()

    @classmethod
    def weekly_attribution_report(cls):
        return cls._get_portfolio().get_weekly_attribution_report()

    @classmethod
    def execute_trade_intent(cls, trade_intent):
        if cls._halted:
            return {"trade_id": trade_intent.get("trade_id") or trade_intent.get("id"), "status": "HALTED"}

        if not cls._market_hours_ok():
            return cls._reject_trade(trade_intent, "Outside market hours")

        order = cls._build_order(trade_intent)
        if not order.get("symbol") or int(order.get("qty", 0)) <= 0:
            return cls._reject_trade(trade_intent, "Invalid trade intent")

        submission = cls._submit(order)
        portfolio = cls._get_portfolio()
        trade_id = order.get("trade_id")

        if submission.get("status") in {"FILLED", "EXECUTED", "ACCEPTED", "PARTIAL_FILLED"}:
            filled_trade = dict(trade_intent)
            filled_trade["execution_result"] = submission
            filled_trade["trade_id"] = trade_id
            if submission.get("filled_qty") is not None:
                filled_trade["qty"] = int(submission.get("filled_qty"))
            portfolio.apply_trade(filled_trade)
            if trade_id is not None:
                _QUEUE.set_status(
                    trade_id,
                    "executed",
                    decision_by=trade_intent.get("approved_by"),
                    reason=submission.get("reason"),
                    extra={"order_id": submission.get("order_id"), "execution_result": submission},
                )
            return {
                "trade_id": trade_id,
                "status": submission.get("status", "EXECUTED"),
                "order_id": submission.get("order_id"),
                "execution_result": submission,
                "portfolio": portfolio.snapshot(),
            }

        if trade_id is not None:
            _QUEUE.set_status(
                trade_id,
                "closed_error",
                decision_by=trade_intent.get("approved_by"),
                reason=submission.get("reason") or "Order rejected",
                extra={"execution_result": submission},
            )

        return {
            "trade_id": trade_id,
            "status": submission.get("status", "REJECTED"),
            "reason": submission.get("reason", "Order rejected"),
            "execution_result": submission,
        }

    @classmethod
    def execute(cls, trade_id):
        queue = ApprovalQueue
        rec = queue.get(trade_id)
        if rec is None:
            return {"trade_id": trade_id, "status": "NOT_FOUND"}

        current_status = str(rec.get("status", "")).upper()
        if current_status != "APPROVED":
            return {"trade_id": trade_id, "status": "NOT_APPROVED", "current_status": current_status}

        trade = {
            "trade_id": trade_id,
            "symbol": rec.get("symbol"),
            "side": rec.get("side") or "BUY",
            "qty": rec.get("qty") if rec.get("qty") is not None else 0,
            "price": rec.get("price") or 0.0,
            "strategy": (rec.get("metadata") or {}).get("strategy"),
            "correlation_id": (rec.get("metadata") or {}).get("correlation_id") or trade_id,
            "approved_by": rec.get("approved_by"),
            "approval_source": rec.get("approval_source"),
            "metadata": rec.get("metadata", {}),
            "risk_snapshot": rec.get("risk_snapshot", {}),
        }
        return cls.execute_trade_intent(trade)

    @classmethod
    def cancel(cls, trade_id):
        rec = ApprovalQueue.get(trade_id)
        if rec is None:
            return {"trade_id": trade_id, "status": "NOT_FOUND"}
        if str(rec.get("status", "")).lower() == "pending":
            _QUEUE.set_status(trade_id, "rejected", reason="Canceled")
            return {"trade_id": trade_id, "status": "CANCELED"}
        return {"trade_id": trade_id, "status": "NOOP", "current_status": rec.get("status")}

    @classmethod
    def _get_broker(cls):
        if cls._broker is None:
            broker = PaperBroker()
            if hasattr(broker, "connect"):
                broker.connect()
            cls._broker = broker
        return cls._broker

    @classmethod
    def _get_portfolio(cls):
        if cls._portfolio is None:
            cls._portfolio = PortfolioManager(cfg=cls._cfg, broker=cls._get_broker(), logger=cls._logger)
        return cls._portfolio

    @classmethod
    def _market_hours_ok(cls, now: Optional[datetime] = None):
        if cls._cfg.get("allow_after_hours"):
            return True
        now = now or datetime.now()
        if now.weekday() >= 5:
            return False
        current = now.time()
        return cls._cfg["market_open"] <= current <= cls._cfg["market_close"]

    @classmethod
    def _build_order(cls, trade_intent):
        trade = dict(trade_intent or {})
        symbol = str(trade.get("symbol") or trade.get("ticker") or "").upper()
        side = str(trade.get("side") or trade.get("type") or "BUY").upper()
        qty = int(trade.get("qty") if trade.get("qty") is not None else trade.get("size", 0))
        order_type = str(trade.get("order_type") or cls._cfg.get("default_order_type", "market")).lower()
        trade_id = trade.get("trade_id") or trade.get("id") or f"order-{uuid4().hex[:8]}"
        return {
            "trade_id": trade_id,
            "symbol": symbol,
            "side": side,
            "qty": qty,
            "type": order_type,
            "stop": trade.get("stop") or trade.get("stop_price"),
            "target": trade.get("target") or trade.get("target_price"),
            "strategy": trade.get("strategy"),
            "correlation_id": trade.get("correlation_id") or trade_id,
        }

    @classmethod
    def _submit(cls, order):
        broker = cls._get_broker()
        attempts = max(1, int(cls._cfg.get("max_retries", 3)))
        delay = float(cls._cfg.get("retry_delay_seconds", 0.0))
        last_error = None

        for attempt in range(1, attempts + 1):
            try:
                if hasattr(broker, "submit_order"):
                    raw = broker.submit_order(order)
                else:
                    raw = broker.place_order(order["symbol"], order["side"].lower(), int(order["qty"]), order_type=order.get("type", "market"))
                return cls._normalize_submission(order, raw)
            except Exception as exc:
                last_error = str(exc)
                if attempt < attempts and delay > 0:
                    time.sleep(delay * attempt)

        return {"status": "REJECTED", "reason": last_error or "Order submission failed", "order_id": None}

    @staticmethod
    def _normalize_submission(order, raw):
        if isinstance(raw, dict):
            result = dict(raw)
            status = str(result.get("status", "FILLED")).upper()
            result["status"] = status
            result.setdefault("order_id", result.get("id") or f"paper-{order['trade_id']}")
            result.setdefault("filled_qty", result.get("qty", order.get("qty")))
            result.setdefault("filled_price", result.get("price"))
            return result

        return {
            "status": "FILLED",
            "order_id": str(raw),
            "filled_qty": order.get("qty"),
            "filled_price": order.get("price"),
            "partial_fill": False,
        }

    @classmethod
    def _reject_trade(cls, trade_intent, reason):
        trade_id = trade_intent.get("trade_id") or trade_intent.get("id")
        if trade_id is not None:
            _QUEUE.set_status(trade_id, "closed_error", reason=reason)
        return {"trade_id": trade_id, "status": "REJECTED", "reason": reason}


__all__ = ["ExecutionEngine"]
