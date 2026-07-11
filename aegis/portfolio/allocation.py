from __future__ import annotations

from typing import Any, Dict, List


def allocate_capital(portfolio_snapshot: Dict[str, Any], strategy_metrics: Dict[str, Any], trade_intents: List[Dict[str, Any]]):
    cash = float(portfolio_snapshot.get("cash", 0.0) or 0.0)
    budget = cash * float(strategy_metrics.get("capital_fraction", 0.1) or 0.1)
    count = max(1, len(trade_intents))
    per_trade = budget / count if count else 0.0
    result = []
    for trade in trade_intents:
        price = float(trade.get("entry", 0.0) or 0.0)
        qty = int(per_trade // price) if price > 0 else int(strategy_metrics.get("default_qty", 1) or 1)
        enriched = dict(trade)
        enriched["qty"] = max(1, qty)
        enriched["allocated_capital"] = per_trade
        result.append(enriched)
    return result