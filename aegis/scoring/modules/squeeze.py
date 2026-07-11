from __future__ import annotations

from typing import Any, Dict

from .base import Scorer


class ShortSqueezeScorer(Scorer):
    name = "squeeze"

    def score(self, trade_intent: Dict[str, Any], feature_snapshot: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        squeeze = dict((feature_snapshot or {}).get("squeeze", {}))
        short_interest = float(squeeze.get("short_interest", 0.0) or 0.0)
        days_to_cover = float(squeeze.get("days_to_cover", 0.0) or 0.0)
        score = self.clamp_score(100.0 * (0.7 * self.scale_ratio(short_interest, 0.05, 0.35) + 0.3 * self.scale_ratio(days_to_cover, 1.0, 12.0)))
        return {
            "component": self.name,
            "score": score,
            "raw": squeeze,
            "explain": [f"short_interest={short_interest:.3f}", f"days_to_cover={days_to_cover:.2f}"],
            "version": "v1",
        }