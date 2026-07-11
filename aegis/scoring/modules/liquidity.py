from __future__ import annotations

from typing import Any, Dict

from .base import Scorer


class LiquidityScorer(Scorer):
    name = "liquidity"

    def score(self, trade_intent: Dict[str, Any], feature_snapshot: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        liquidity = dict((feature_snapshot or {}).get("liquidity", {}))
        adv_ratio = float(liquidity.get("adv_ratio", 0.0) or 0.0)
        spread_bps = float(liquidity.get("spread_bps", 100.0) or 100.0)
        adv_score = self.scale_ratio(adv_ratio, 0.0, 0.05)
        spread_score = 1.0 - self.scale_ratio(spread_bps, 5.0, 80.0)
        score = self.clamp_score(100.0 * (0.6 * adv_score + 0.4 * spread_score))
        return {
            "component": self.name,
            "score": score,
            "raw": liquidity,
            "explain": [f"adv_ratio={adv_ratio:.4f}", f"spread_bps={spread_bps:.2f}"],
            "version": "v1",
        }