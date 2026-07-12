from __future__ import annotations

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from aegis.data import DataEngine
from aegis.features import FeatureEngine


class FeatureEngineTests(unittest.TestCase):
    def test_empty_history_returns_neutral_snapshot(self):
        snapshot = FeatureEngine().compute("AAPL", [])
        self.assertEqual(snapshot["technical"]["rsi"], 50.0)
        self.assertEqual(snapshot["technical"]["trend"], 0.0)
        self.assertEqual(snapshot["liquidity"]["adv_ratio"], 0.0)

    def test_uptrend_series_yields_positive_trend_and_momentum(self):
        data = DataEngine()
        bars = [
            {"timestamp": f"t{i}", "open": p, "high": p, "low": p, "close": p, "volume": 1000}
            for i, p in enumerate(range(100, 130))
        ]
        history = data.ingest_bars("AAPL", bars)
        snapshot = FeatureEngine().compute("AAPL", history)
        self.assertGreater(snapshot["technical"]["trend"], 0.0)
        self.assertGreater(snapshot["technical"]["momentum"], 0.0)
        self.assertGreaterEqual(snapshot["technical"]["rsi"], 50.0)
        self.assertEqual(snapshot["symbol"], "AAPL")
        self.assertEqual(snapshot["feature_version"], "v1")

    def test_deterministic_given_same_inputs(self):
        data = DataEngine()
        bars = [
            {"timestamp": f"t{i}", "open": p, "high": p, "low": p, "close": p, "volume": 1000 + i}
            for i, p in enumerate([100, 101, 99, 102, 103, 101, 104])
        ]
        history = data.ingest_bars("AAPL", bars)
        engine = FeatureEngine()
        first = engine.compute("AAPL", history)
        second = engine.compute("AAPL", history)
        self.assertEqual(first, second)

    def test_liquidity_bounds(self):
        data = DataEngine()
        bars = [
            {"timestamp": f"t{i}", "open": 10, "high": 10, "low": 10, "close": 10, "volume": 500}
            for i in range(25)
        ]
        bars[-1]["volume"] = 5000  # volume spike on the latest bar
        history = data.ingest_bars("AAPL", bars)
        snapshot = FeatureEngine().compute("AAPL", history)
        self.assertLessEqual(snapshot["liquidity"]["adv_ratio"], 5.0)
        self.assertGreaterEqual(snapshot["liquidity"]["adv_ratio"], 0.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
