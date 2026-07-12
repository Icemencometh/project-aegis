"""Regime Engine (Aegis_Module_Contracts.md: "Classify current market regime.").

Contract:
- Must expose a simple API: get_current_regime().
- Must not place trades or modify portfolio.

Regime names (bull/bear/high_volatility/neutral) are chosen to match the
`weights_by_regime` keys in aegis/config/scoring.yaml so the Scoring Hub's
AdaptiveWeightingEngine picks up a real override instead of silently falling
back to defaults.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

DEFAULT_HIGH_VOL_THRESHOLD = 0.6
DEFAULT_TREND_THRESHOLD = 0.15


class RegimeEngine:
    """Classifies market regime from a feature snapshot. Read-only: never
    places trades or touches the portfolio."""

    def __init__(self, cfg: Optional[Dict[str, Any]] = None):
        self.cfg = dict(cfg or {})
        self._current: Dict[str, Any] = {"name": "neutral", "confidence": 0.5, "risk": 0.0}

    def classify(self, feature_snapshot: Dict[str, Any]) -> Dict[str, Any]:
        technical = dict((feature_snapshot or {}).get("technical", {}))
        trend = float(technical.get("trend", 0.0) or 0.0)
        rsi = float(technical.get("rsi", 50.0) or 50.0)
        # Crude volatility proxy until a dedicated volatility feature exists:
        # RSI far from 50 tends to co-occur with fast, choppy moves.
        vol_proxy = abs(rsi - 50.0) / 50.0

        high_vol_threshold = float(self.cfg.get("high_vol_threshold", DEFAULT_HIGH_VOL_THRESHOLD))
        trend_threshold = float(self.cfg.get("trend_threshold", DEFAULT_TREND_THRESHOLD))

        if vol_proxy >= high_vol_threshold:
            name = "high_volatility"
        elif trend >= trend_threshold:
            name = "bull"
        elif trend <= -trend_threshold:
            name = "bear"
        else:
            name = "neutral"

        confidence = max(0.0, min(1.0, 0.5 + abs(trend)))
        self._current = {"name": name, "confidence": confidence, "risk": vol_proxy}
        return dict(self._current)

    def get_current_regime(self) -> Dict[str, Any]:
        return dict(self._current)
