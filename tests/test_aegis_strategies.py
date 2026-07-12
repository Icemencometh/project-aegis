from __future__ import annotations

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from aegis.strategies import MomentumStrategy


class MomentumStrategyTests(unittest.TestCase):
    def test_emits_candidate_on_positive_trend_and_momentum(self):
        strategy = MomentumStrategy()
        features = {"technical": {"rsi": 55.0, "trend": 0.2, "momentum": 0.05, "last_price": 100.0}}
        candidates = strategy.generate("AAPL", features, {"name": "bull"})
        self.assertEqual(len(candidates), 1)
        candidate = candidates[0]
        self.assertEqual(candidate["symbol"], "AAPL")
        self.assertEqual(candidate["side"], "BUY")
        self.assertEqual(candidate["strategy"], "momentum")
        self.assertEqual(candidate["strategy_version"], "v1")
        self.assertLess(candidate["stop"], candidate["entry"])
        self.assertGreater(candidate["target"], candidate["entry"])

    def test_no_candidate_when_momentum_negative(self):
        strategy = MomentumStrategy()
        features = {"technical": {"rsi": 55.0, "trend": 0.2, "momentum": -0.01, "last_price": 100.0}}
        self.assertEqual(strategy.generate("AAPL", features, {"name": "bull"}), [])

    def test_no_candidate_when_overbought(self):
        strategy = MomentumStrategy()
        features = {"technical": {"rsi": 90.0, "trend": 0.2, "momentum": 0.05, "last_price": 100.0}}
        self.assertEqual(strategy.generate("AAPL", features, {"name": "bull"}), [])

    def test_no_candidate_when_trend_below_threshold(self):
        strategy = MomentumStrategy(trend_threshold=0.1)
        features = {"technical": {"rsi": 55.0, "trend": 0.01, "momentum": 0.05, "last_price": 100.0}}
        self.assertEqual(strategy.generate("AAPL", features, {"name": "bull"}), [])

    def test_entry_point_matches_marketplace_runner_call_convention(self):
        strategy = MomentumStrategy()
        features = {"technical": {"rsi": 55.0, "trend": 0.2, "momentum": 0.05, "last_price": 100.0}}
        via_entry_point = strategy.entry_point("AAPL", features, {"name": "bull"})
        via_generate = strategy.generate("AAPL", features, {"name": "bull"})
        self.assertEqual(via_entry_point, via_generate)

    def test_metadata_is_versioned(self):
        strategy = MomentumStrategy()
        metadata = strategy.metadata()
        self.assertEqual(metadata["name"], "momentum")
        self.assertEqual(metadata["version"], "v1")
        self.assertTrue(metadata["active"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
