from __future__ import annotations

from typing import Any, Dict

from .base import Scorer


class SentimentScorer(Scorer):
    name = "sentiment"

    def score(self, trade_intent: Dict[str, Any], feature_snapshot: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        sentiment = dict((feature_snapshot or {}).get("sentiment", {}))
        news = float(sentiment.get("news", 0.0) or 0.0)
        social = float(sentiment.get("social", 0.0) or 0.0)
        score = self.clamp_score(50.0 + 30.0 * news + 20.0 * social)
        return {
            "component": self.name,
            "score": score,
            "raw": sentiment,
            "explain": [f"news={news:.3f}", f"social={social:.3f}"],
            "version": "v1",
        }