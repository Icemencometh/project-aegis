from __future__ import annotations

from typing import Any, Dict

from .base import Scorer


class OrderFlowScorer(Scorer):
    name = "order_flow"

    def score(self, trade_intent: Dict[str, Any], feature_snapshot: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        order_flow = dict((feature_snapshot or {}).get("order_flow", {}))
        imbalance = float(order_flow.get("imbalance", 0.0) or 0.0)
        participation = float(order_flow.get("participation", 0.0) or 0.0)
        score = self.clamp_score(50.0 + 35.0 * imbalance + 15.0 * participation)
        return {
            "component": self.name,
            "score": score,
            "raw": order_flow,
            "explain": [f"imbalance={imbalance:.3f}", f"participation={participation:.3f}"],
            "version": "v1",
        }