"""A minimal, deterministic momentum strategy -- the first concrete plug-in
for the Strategy Marketplace registry.

Emits a single long trade candidate when trend and momentum are both
positive and RSI isn't overbought; emits nothing otherwise. No broker,
execution, or risk calls (contract-compliant: strategies emit candidates,
never orders).
"""

from __future__ import annotations

from typing import Any, Dict, List

from .base import Strategy


class MomentumStrategy(Strategy):
    name = "momentum"
    version = "v1"

    def __init__(self, trend_threshold: float = 0.1, rsi_ceiling: float = 70.0):
        self.trend_threshold = float(trend_threshold)
        self.rsi_ceiling = float(rsi_ceiling)

    def generate(
        self,
        symbol: str,
        feature_snapshot: Dict[str, Any],
        regime_snapshot: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        technical = dict((feature_snapshot or {}).get("technical", {}))
        trend = float(technical.get("trend", 0.0) or 0.0)
        momentum = float(technical.get("momentum", 0.0) or 0.0)
        rsi = float(technical.get("rsi", 50.0) or 50.0)
        last_price = float(technical.get("last_price", 0.0) or 0.0)

        if trend < self.trend_threshold or momentum <= 0.0 or rsi >= self.rsi_ceiling or last_price <= 0.0:
            return []

        return [
            {
                "symbol": str(symbol),
                "side": "BUY",
                "entry": last_price,
                "stop": round(last_price * 0.97, 4),
                "target": round(last_price * 1.05, 4),
                "strategy": self.name,
                "strategy_version": self.version,
                "regime": (regime_snapshot or {}).get("name"),
                "features": {
                    "score": max(0.0, min(1.0, 0.5 + momentum)),
                    "expected_return": 0.05,
                    "holding_time": "swing",
                    "version": self.version,
                },
            }
        ]
