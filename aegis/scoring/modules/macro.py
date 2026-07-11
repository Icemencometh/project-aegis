from __future__ import annotations

from typing import Any, Dict

from .base import Scorer


class MacroScorer(Scorer):
    name = "macro"

    def score(self, trade_intent: Dict[str, Any], feature_snapshot: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        macro = dict((feature_snapshot or {}).get("macro", {}))
        growth = float(macro.get("growth", 0.0) or 0.0)
        inflation = float(macro.get("inflation", 0.0) or 0.0)
        rates = float(macro.get("rates", 0.0) or 0.0)
        score = self.clamp_score(50.0 + 25.0 * growth - 15.0 * inflation - 10.0 * rates)
        return {
            "component": self.name,
            "score": score,
            "raw": macro,
            "explain": [f"growth={growth:.3f}", f"inflation={inflation:.3f}", f"rates={rates:.3f}"],
            "version": "v1",
        }