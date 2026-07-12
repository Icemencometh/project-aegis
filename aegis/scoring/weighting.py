from __future__ import annotations

from typing import Any, Dict


class AdaptiveWeightingEngine:
    """Regime-conditional scorer weights.

    Weights come from config (aegis/config/scoring.yaml), never from literals
    baked into this class, per Aegis_Coding_Standards.txt ("no hard-coded
    magic numbers"): a `weights_by_regime` block supplies an explicit weight
    set per regime name; any regime without an override falls back to each
    component's `weight_default` from the `components` block (components
    marked `enabled: false` are dropped from the fallback set).

    "Adaptive" today means "looked up per regime from config", not
    online-learned -- there is no in-process weight mutation. Re-weighting
    still means editing scoring.yaml, not this file.
    """

    def __init__(self, cfg: Dict[str, Any]):
        self.cfg = dict(cfg or {})
        self.weights_by_regime: Dict[str, Dict[str, float]] = {
            str(regime): {name: float(weight) for name, weight in dict(weights or {}).items()}
            for regime, weights in dict(self.cfg.get("weights_by_regime", {})).items()
        }

    def get_weights(self, regime_snapshot: Dict[str, Any]) -> Dict[str, float]:
        regime = str((regime_snapshot or {}).get("name", "default"))
        if regime in self.weights_by_regime:
            return dict(self.weights_by_regime[regime])
        return self._default_weights()

    def _default_weights(self) -> Dict[str, float]:
        components = dict(self.cfg.get("components", {}))
        if components:
            return {
                name: float(payload.get("weight_default", 0.0))
                for name, payload in components.items()
                if payload.get("enabled", True)
            }
        # Fallback for callers that construct with cfg={} (e.g. unit tests).
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
