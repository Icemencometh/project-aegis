from __future__ import annotations

from typing import Any, Dict, List


class CapitalAllocationEngine:
    def __init__(self, cfg: Dict[str, Any]):
        self.cfg = dict(cfg or {})

    def allocate(self, portfolio_snapshot: Dict[str, Any], strategy_metrics: Dict[str, Any], trade_intents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        allocated = []
        for trade in trade_intents:
            enriched = dict(trade)
            enriched["qty"] = self._compute_qty(enriched, portfolio_snapshot, strategy_metrics)
            allocated.append(enriched)
        return allocated

    def _compute_qty(self, trade: Dict[str, Any], portfolio_snapshot: Dict[str, Any], strategy_metrics: Dict[str, Any]) -> int:
        default_qty = int(self.cfg.get("default_qty", 10) or 10)
        max_qty = int(self.cfg.get("max_qty", default_qty) or default_qty)
        capital_fraction = float(strategy_metrics.get("capital_fraction", self.cfg.get("capital_fraction", 0.1)) or 0.1)
        cash = float(portfolio_snapshot.get("cash", 0.0) or 0.0)
        price = float(trade.get("entry", 0.0) or 0.0)
        if price <= 0.0:
            return max(1, min(default_qty, max_qty))
        target_capital = cash * capital_fraction
        qty = int(target_capital // price)
        return max(1, min(qty or default_qty, max_qty))