from __future__ import annotations

from typing import Any, Dict, List

from ..common.types import RiskDecision


class RiskEngine:
    def __init__(self, cfg: Dict[str, Any], portfolio, env_monitor, logger):
        self.cfg = dict(cfg or {})
        self.portfolio = portfolio
        self.env = env_monitor
        self.logger = logger

    def evaluate_trades(self, trade_intents: List[Dict[str, Any]]):
        approved, rejected = [], []
        for trade in trade_intents:
            reasons: List[str] = []
            if not self._check_environment(reasons):
                rejected.append(self._reject(trade, reasons))
                continue
            if not self._check_trade(trade, reasons):
                rejected.append(self._reject(trade, reasons))
                continue
            if not self._check_position(trade, reasons):
                rejected.append(self._reject(trade, reasons))
                continue
            if not self._check_portfolio(trade, reasons):
                rejected.append(self._reject(trade, reasons))
                continue
            approved.append(trade)
        return approved, rejected

    def assess_trade(self, trade: Dict[str, Any]) -> RiskDecision:
        reasons: List[str] = []
        if not self._check_environment(reasons):
            return self._decision(False, reasons)
        if not self._check_trade(trade, reasons):
            return self._decision(False, reasons)
        if not self._check_position(trade, reasons):
            return self._decision(False, reasons)
        if not self._check_portfolio(trade, reasons):
            return self._decision(False, reasons)
        return self._decision(True, reasons)

    def _check_environment(self, reasons: List[str]) -> bool:
        if self.env is None:
            return True
        if hasattr(self.env, "is_open") and not self.env.is_open():
            reasons.append("environment_closed")
            return False
        if getattr(self.env, "halted", False):
            reasons.append("environment_halted")
            return False
        return True

    def _check_trade(self, trade: Dict[str, Any], reasons: List[str]) -> bool:
        if not trade.get("symbol"):
            reasons.append("missing_symbol")
            return False
        qty = int(trade.get("qty", 0))
        if qty <= 0:
            reasons.append("non_positive_qty")
            return False
        if str(trade.get("side", "")).upper() not in {"BUY", "SELL"}:
            reasons.append("invalid_side")
            return False
        return True

    def _check_position(self, trade: Dict[str, Any], reasons: List[str]) -> bool:
        max_position_qty = int(self.cfg.get("max_position_qty", 0) or 0)
        if not max_position_qty:
            return True
        current_qty = 0
        snapshot = self._portfolio_snapshot()
        positions = snapshot.get("positions", {})
        existing = positions.get(trade.get("symbol"), {}) if isinstance(positions, dict) else {}
        if isinstance(existing, dict):
            current_qty = int(existing.get("qty", 0))
        proposed_qty = current_qty + int(trade.get("qty", 0))
        if abs(proposed_qty) > max_position_qty:
            reasons.append("position_limit_exceeded")
            return False
        return True

    def _check_portfolio(self, trade: Dict[str, Any], reasons: List[str]) -> bool:
        max_gross_exposure = float(self.cfg.get("max_gross_exposure", 0.0) or 0.0)
        if not max_gross_exposure:
            return True
        snapshot = self._portfolio_snapshot()
        gross = float(snapshot.get("gross_exposure", 0.0) or 0.0)
        proposed = gross + abs(float(trade.get("qty", 0))) * float(trade.get("entry", 0.0) or 0.0)
        if proposed > max_gross_exposure:
            reasons.append("gross_exposure_exceeded")
            return False
        return True

    def _reject(self, trade: Dict[str, Any], reasons: List[str]) -> Dict[str, Any]:
        trade = dict(trade)
        trade["risk_rejected"] = True
        trade["risk_reasons"] = reasons
        return trade

    def _decision(self, allowed: bool, reasons: List[str]) -> RiskDecision:
        return RiskDecision(allowed=allowed, reason=";".join(reasons), details={"reasons": list(reasons)})

    def _portfolio_snapshot(self) -> Dict[str, Any]:
        if self.portfolio is None:
            return {}
        if hasattr(self.portfolio, "snapshot"):
            return dict(self.portfolio.snapshot())
        if hasattr(self.portfolio, "get_snapshot"):
            return dict(self.portfolio.get_snapshot())
        if isinstance(self.portfolio, dict):
            return dict(self.portfolio)
        return {}