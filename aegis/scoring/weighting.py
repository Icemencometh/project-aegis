from __future__ import annotations

from typing import Any, Dict


class AdaptiveWeightingEngine:
    def __init__(self, cfg: Dict[str, Any]):
        self.cfg = dict(cfg or {})
        self.weights_by_regime: Dict[str, Dict[str, float]] = {}

    def get_weights(self, regime_snapshot: Dict[str, Any]) -> Dict[str, float]:
        regime = str(regime_snapshot.get("name", "default"))
        return dict(self.weights_by_regime.get(regime, self._default_weights()))

    def _default_weights(self) -> Dict[str, float]:
        return {
            "technical": 0.20,
            "order_flow": 0.20,
            "squeeze": 0.15,
            "ml": 0.20,
            "regime": 0.10,
            "macro": 0.05,
            "liquidity": 0.05,
            "sentiment": 0.05,
        }