from __future__ import annotations

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from aegis.regime import RegimeEngine


class RegimeEngineTests(unittest.TestCase):
    def test_bull_regime(self):
        engine = RegimeEngine()
        regime = engine.classify({"technical": {"rsi": 55.0, "trend": 0.3, "momentum": 0.1}})
        self.assertEqual(regime["name"], "bull")

    def test_bear_regime(self):
        engine = RegimeEngine()
        regime = engine.classify({"technical": {"rsi": 45.0, "trend": -0.3, "momentum": -0.1}})
        self.assertEqual(regime["name"], "bear")

    def test_neutral_regime(self):
        engine = RegimeEngine()
        regime = engine.classify({"technical": {"rsi": 50.0, "trend": 0.0, "momentum": 0.0}})
        self.assertEqual(regime["name"], "neutral")

    def test_high_volatility_regime_overrides_trend(self):
        engine = RegimeEngine()
        # RSI far from 50 trips the volatility proxy even with a positive trend.
        regime = engine.classify({"technical": {"rsi": 95.0, "trend": 0.3, "momentum": 0.1}})
        self.assertEqual(regime["name"], "high_volatility")

    def test_get_current_regime_reflects_last_classification(self):
        engine = RegimeEngine()
        engine.classify({"technical": {"rsi": 55.0, "trend": 0.3, "momentum": 0.1}})
        self.assertEqual(engine.get_current_regime()["name"], "bull")

    def test_does_not_place_trades_or_touch_portfolio(self):
        # Contract check: RegimeEngine has no broker/execution/portfolio attrs.
        engine = RegimeEngine()
        for forbidden in ("broker", "execution", "portfolio", "place_order", "submit_order"):
            self.assertFalse(hasattr(engine, forbidden))


if __name__ == "__main__":
    unittest.main(verbosity=2)
