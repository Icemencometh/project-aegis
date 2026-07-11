from __future__ import annotations

from typing import Any, Dict

from .base import Scorer


class TechnicalScorer(Scorer):
    name = "technical"

    def score(self, trade_intent: Dict[str, Any], feature_snapshot: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        technical = dict((feature_snapshot or {}).get("technical", {}))
        rsi = float(technical.get("rsi", 50.0) or 50.0)
        trend = float(technical.get("trend", 0.0) or 0.0)
        momentum = float(technical.get("momentum", 0.0) or 0.0)
        score = self.clamp_score(0.5 * (100.0 - abs(rsi - 50.0) * 2.0) + 30.0 * trend + 20.0 * momentum)
        return {
            "component": self.name,
            "score": score,
            "raw": technical,
            "explain": [f"rsi={rsi:.1f}", f"trend={trend:.3f}", f"momentum={momentum:.3f}"],
            "version": "v1",
        }