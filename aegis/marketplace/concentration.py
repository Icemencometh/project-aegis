"""Strategy Marketplace concentration guard.

Aegis_AI_Onboarding_Guide.md: "Do not let a single strategy dominate the
portfolio." This enforces that at the point trade intents leave the
marketplace/allocation stage, headed for the Risk Engine.
"""

from __future__ import annotations

from typing import Any, Dict, List


def enforce_strategy_concentration(
    trade_intents: List[Dict[str, Any]],
    portfolio_snapshot: Dict[str, Any],
    max_allocation_pct: float,
) -> List[Dict[str, Any]]:
    """Caps each strategy's aggregate notional to `max_allocation_pct` of
    portfolio cash. Trims qty (never increases it); trades that would round
    down to zero are dropped. Trades with no `strategy` tag are passed
    through untouched -- there's nothing to attribute a cap to."""
    cash = float(portfolio_snapshot.get("cash", 0.0) or 0.0)
    ceiling = cash * float(max_allocation_pct or 0.0)
    if ceiling <= 0.0:
        return list(trade_intents)

    used: Dict[str, float] = {}
    capped: List[Dict[str, Any]] = []
    for trade in trade_intents:
        strategy = trade.get("strategy")
        if not strategy:
            capped.append(trade)
            continue
        price = float(trade.get("entry", 0.0) or 0.0)
        qty = int(trade.get("qty", 0) or 0)
        remaining = max(0.0, ceiling - used.get(strategy, 0.0))
        if price > 0.0 and (price * qty) > remaining:
            qty = int(remaining // price)
        used[strategy] = used.get(strategy, 0.0) + (price * qty)
        trade = dict(trade)
        trade["qty"] = qty
        capped.append(trade)
    return [trade for trade in capped if int(trade.get("qty", 0) or 0) > 0]
