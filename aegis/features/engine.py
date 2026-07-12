"""Feature Engine (Aegis_Module_Contracts.md: "Transform raw data into
deterministic features.").

Contract:
- Features must be deterministic and reproducible.
- Each feature family must be documented (see docstrings on _technical /
  _liquidity below).
- No direct calls to broker or execution.

Output keys match what aegis/scoring/modules/*.py scorers already expect
(technical.{rsi,trend,momentum}, liquidity.{adv_ratio,spread_bps}) so the
Scoring Hub can consume this snapshot with no adapter layer. Feature
families this engine does not yet compute (order_flow, squeeze, ml, macro,
sentiment) are simply absent from the snapshot; each scorer already
degrades to a neutral score when its family is missing.
"""

from __future__ import annotations

from typing import Any, Dict, List

from ..data.engine import Bar

FEATURE_VERSION = "v1"


class FeatureEngine:
    """Computes deterministic technical/liquidity features from bar history."""

    def __init__(self, version: str = FEATURE_VERSION):
        self.version = str(version)

    def compute(self, symbol: str, bars: List[Bar]) -> Dict[str, Any]:
        if not bars:
            return self._empty_snapshot(symbol)
        closes = [bar.close for bar in bars]
        return {
            "symbol": str(symbol),
            "feature_version": self.version,
            "as_of": bars[-1].timestamp,
            "technical": self._technical(closes),
            "liquidity": self._liquidity(bars),
        }

    def _technical(self, closes: List[float]) -> Dict[str, float]:
        """rsi: 14-period Wilder-style RSI (0-100, 50=neutral).
        trend: last close's deviation from its trailing-14 average, clamped to [-1, 1].
        momentum: 1-bar percent change, clamped to [-1, 1].
        """
        last_price = closes[-1]
        window = closes[-14:]
        avg = sum(window) / len(window)
        trend = self.clamp((last_price - avg) / avg, -1.0, 1.0) if avg else 0.0
        momentum = 0.0
        if len(closes) >= 2 and closes[-2]:
            momentum = self.clamp((closes[-1] - closes[-2]) / closes[-2], -1.0, 1.0)
        return {
            "rsi": self._rsi(closes),
            "trend": trend,
            "momentum": momentum,
            "last_price": last_price,
        }

    def _rsi(self, closes: List[float], period: int = 14) -> float:
        if len(closes) < 2:
            return 50.0
        window = closes[-(period + 1):]
        gains, losses = [], []
        for prev, curr in zip(window, window[1:]):
            delta = curr - prev
            gains.append(max(delta, 0.0))
            losses.append(max(-delta, 0.0))
        avg_gain = sum(gains) / len(gains) if gains else 0.0
        avg_loss = sum(losses) / len(losses) if losses else 0.0
        if avg_loss == 0.0:
            return 100.0 if avg_gain > 0.0 else 50.0
        rs = avg_gain / avg_loss
        return 100.0 - (100.0 / (1.0 + rs))

    def _liquidity(self, bars: List[Bar]) -> Dict[str, float]:
        """adv_ratio: latest volume vs trailing-20 average volume, clamped to [0, 5].
        spread_bps: placeholder (no bid/ask in the bar model yet) -- fixed at 5bps
        until a quote feed is wired into DataEngine.
        """
        recent = bars[-20:]
        avg_volume = sum(bar.volume for bar in recent) / len(recent) if recent else 0.0
        last_volume = bars[-1].volume
        adv_ratio = self.clamp(last_volume / avg_volume, 0.0, 5.0) if avg_volume else 0.0
        return {"adv_ratio": adv_ratio, "spread_bps": 5.0, "avg_volume": avg_volume}

    def _empty_snapshot(self, symbol: str) -> Dict[str, Any]:
        return {
            "symbol": str(symbol),
            "feature_version": self.version,
            "as_of": None,
            "technical": {"rsi": 50.0, "trend": 0.0, "momentum": 0.0, "last_price": 0.0},
            "liquidity": {"adv_ratio": 0.0, "spread_bps": 5.0, "avg_volume": 0.0},
        }

    @staticmethod
    def clamp(value: float, floor: float, ceiling: float) -> float:
        return max(floor, min(ceiling, float(value)))
