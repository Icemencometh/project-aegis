from __future__ import annotations

from typing import Any, Dict

from .base import Scorer


class RegimeScorer(Scorer):
    name = "regime"

    def score(self, trade_intent: Dict[str, Any], feature_snapshot: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        regime = dict(context or {})
        confidence = float(regime.get("confidence", 0.5) or 0.5)
        risk = float(regime.get("risk", 0.5) or 0.5)
        score = self.clamp_score(100.0 * (0.7 * confidence + 0.3 * (1.0 - risk)))
        return {
            "component": self.name,
            "score": score,
            "raw": regime,
            "explain": [f"confidence={confidence:.3f}", f"risk={risk:.3f}"],
            "version": "v1",
        }