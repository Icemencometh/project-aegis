from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..common.types import RiskDecision


class RiskEngine:
    """Hard boundary before execution. No trade may pass without these checks
    (Aegis_Module_Contracts.md: Risk Engine).

    Config accepts two shapes and both are honored at once:
    - legacy flat, absolute-unit keys (`max_position_qty`, `max_gross_exposure`)
      used by early tests and simple setups;
    - percentage-based limits nested under `limits:`, matching
      aegis/config/risk.yaml (`max_symbol_pct`, `max_gross_exposure_pct`,
      `max_drawdown_pct`, `max_heat`, ...), evaluated against portfolio equity
      so limits scale with account size instead of being hardcoded dollars.

    Contract also requires the engine to be able to halt trading and flatten
    positions -- see halt_trading/resume_trading/flatten_positions below.
    """

    def __init__(
        self,
        cfg: Dict[str, Any],
        portfolio,
        env_monitor,
        logger,
        execution_engine: Optional[Any] = None,
    ):
        cfg = dict(cfg or {})
        self.cfg = cfg
        self.limits: Dict[str, Any] = dict(cfg.get("limits", {}))
        self.portfolio = portfolio
        self.env = env_monitor
        self.logger = logger
        self.execution_engine = execution_engine
        self._halted = False
        self._halt_reason = ""

    # ------------------------------------------------------------------
    # Halt / flatten
    # ------------------------------------------------------------------
    def halt_trading(self, reason: str = "manual_halt") -> None:
        self._halted = True
        self._halt_reason = str(reason)
        if self.logger is not None:
            self.logger.warning("risk_engine halted trading: %s", reason)

    def resume_trading(self) -> None:
        self._halted = False
        self._halt_reason = ""

    def is_halted(self) -> bool:
        return self._halted

    def flatten_positions(self) -> List[Dict[str, Any]]:
        """Build (and, if an execution engine is wired, submit) closing orders
        for every open position. Always safe to call even with no execution
        engine attached -- it then just reports what flattening would do."""
        snapshot = self._portfolio_snapshot()
        positions = snapshot.get("positions", {}) or {}
        closing_orders: List[Dict[str, Any]] = []
        for symbol, position in positions.items():
            qty = int(position.get("qty", 0)) if isinstance(position, dict) else int(getattr(position, "qty", 0))
            if qty == 0:
                continue
            closing_orders.append({"symbol": symbol, "side": "SELL" if qty > 0 else "BUY", "qty": abs(qty)})
        if self.execution_engine is not None:
            for order in closing_orders:
                self.execution_engine.execute_trade_intent(order)
        elif closing_orders and self.logger is not None:
            self.logger.warning("risk_engine: flatten_positions computed orders but no execution_engine is wired")
        return closing_orders

    # ------------------------------------------------------------------
    # Evaluation
    # ------------------------------------------------------------------
    def evaluate_trades(self, trade_intents: List[Dict[str, Any]]):
        approved, rejected = [], []
        for trade in trade_intents:
            reasons: List[str] = []
            if self._check_all(trade, reasons):
                approved.append(trade)
            else:
                rejected.append(self._reject(trade, reasons))
        return approved, rejected

    def assess_trade(self, trade: Dict[str, Any]) -> RiskDecision:
        reasons: List[str] = []
        allowed = self._check_all(trade, reasons)
        return self._decision(allowed, reasons)

    def _check_all(self, trade: Dict[str, Any], reasons: List[str]) -> bool:
        if self._halted:
            reasons.append(f"trading_halted:{self._halt_reason}")
            return False
        if not self._check_environment(reasons):
            return False
        if not self._check_trade(trade, reasons):
            return False
        if not self._check_position(trade, reasons):
            return False
        if not self._check_portfolio(trade, reasons):
            return False
        if not self._check_account_risk(reasons):
            return False
        return True

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
        snapshot = self._portfolio_snapshot()
        positions = snapshot.get("positions", {}) or {}
        existing = positions.get(trade.get("symbol"), {}) if isinstance(positions, dict) else {}
        current_qty = int(existing.get("qty", 0)) if isinstance(existing, dict) else 0
        proposed_qty = current_qty + int(trade.get("qty", 0))

        max_position_qty = int(self.cfg.get("max_position_qty", 0) or 0)
        if max_position_qty and abs(proposed_qty) > max_position_qty:
            reasons.append("position_limit_exceeded")
            return False

        max_symbol_pct = float(self.limits.get("max_symbol_pct", 0.0) or 0.0)
        if max_symbol_pct:
            equity = self._equity(snapshot)
            price = float(trade.get("entry", 0.0) or 0.0)
            if equity > 0.0 and abs(proposed_qty) * price > equity * max_symbol_pct:
                reasons.append("symbol_concentration_exceeded")
                return False
        return True

    def _check_portfolio(self, trade: Dict[str, Any], reasons: List[str]) -> bool:
        snapshot = self._portfolio_snapshot()
        gross = float(snapshot.get("gross_exposure", 0.0) or 0.0)
        proposed_notional = abs(float(trade.get("qty", 0))) * float(trade.get("entry", 0.0) or 0.0)

        max_gross_exposure = float(self.cfg.get("max_gross_exposure", 0.0) or 0.0)
        if max_gross_exposure and (gross + proposed_notional) > max_gross_exposure:
            reasons.append("gross_exposure_exceeded")
            return False

        max_gross_pct = float(self.limits.get("max_gross_exposure_pct", 0.0) or 0.0)
        if max_gross_pct:
            equity = self._equity(snapshot)
            if equity > 0.0 and (gross + proposed_notional) > equity * max_gross_pct:
                reasons.append("gross_exposure_pct_exceeded")
                return False
        return True

    def _check_account_risk(self, reasons: List[str]) -> bool:
        """Drawdown/heat breaches halt trading outright (contract: Risk Engine
        can halt trading and flatten positions), not just reject one trade."""
        snapshot = self._portfolio_snapshot()

        max_drawdown_pct = float(self.limits.get("max_drawdown_pct", 0.0) or 0.0)
        drawdown_pct = snapshot.get("drawdown_pct")
        if max_drawdown_pct and drawdown_pct is not None and float(drawdown_pct) > max_drawdown_pct:
            reasons.append("max_drawdown_exceeded")
            self.halt_trading("max_drawdown_exceeded")
            return False

        max_heat = float(self.limits.get("max_heat", 0.0) or 0.0)
        heat = snapshot.get("heat")
        if max_heat and heat is not None and float(heat) > max_heat:
            reasons.append("max_heat_exceeded")
            self.halt_trading("max_heat_exceeded")
            return False
        return True

    def _equity(self, snapshot: Dict[str, Any]) -> float:
        cash = float(snapshot.get("cash", 0.0) or 0.0)
        gross = float(snapshot.get("gross_exposure", 0.0) or 0.0)
        return cash + gross

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
