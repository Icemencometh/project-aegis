from __future__ import annotations

from typing import Any, Dict

from .base import Scorer


class MLScorer(Scorer):
    name = "ml"

    def score(self, trade_intent: Dict[str, Any], feature_snapshot: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        ml = dict((feature_snapshot or {}).get("ml", {}))
        prob_up = float(ml.get("prob_up", 0.5) or 0.5)
        uncertainty = float(ml.get("uncertainty", 0.5) or 0.5)
        score = self.clamp_score(100.0 * (0.75 * prob_up + 0.25 * (1.0 - uncertainty)))
        return {
            "component": self.name,
            "score": score,
            "raw": ml,
            "explain": [f"prob_up={prob_up:.3f}", f"uncertainty={uncertainty:.3f}"],
            "version": "v1",
        }