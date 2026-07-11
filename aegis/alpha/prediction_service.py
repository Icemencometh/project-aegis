from __future__ import annotations

from typing import Any, Dict


class PredictionService:
    def predict(self, symbol: str, features: Dict[str, Any]) -> Dict[str, Any]:
        score = float(features.get("score", 0.55))
        probability = max(0.0, min(1.0, score))
        return {
            "symbol": symbol,
            "prob_up": probability,
            "expected_return": float(features.get("expected_return", 0.0)),
            "holding_time": features.get("holding_time", "swing"),
            "version": features.get("version", "skeleton-v1"),
        }