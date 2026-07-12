"""Integration test for the wired-together Aegis contract chain
(Aegis_Module_Contracts.md's data flow, exercised end to end):

    Data -> Features -> Regime -> Strategy Marketplace -> Scoring Hub
          -> Alpha Hub -> Risk Engine -> Execution Engine -> PaperBroker

This is the "full scoring -> alpha -> risk -> allocation -> execution
integration test" called for in docs/aegis_pr_ready.md's follow-up TODOs.
"""

from __future__ import annotations

import os
import random
import sys
import unittest
from typing import Any, Dict, List

ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from aegis.orchestrator import AegisPipeline
from aegis.strategies import MomentumStrategy, Strategy


def _bar(price: float, i: int) -> Dict[str, Any]:
    return {"timestamp": f"t{i}", "open": price, "high": price, "low": price, "close": price, "volume": 1_000_000}


class AlwaysBuyStrategy(Strategy):
    """Deterministic test double: always emits one small BUY candidate,
    independent of features/regime, so pipeline-wiring tests don't depend on
    MomentumStrategy's own trend/momentum/RSI math (covered separately in
    test_aegis_strategies.py)."""

    name = "always_buy"
    version = "test"

    def generate(self, symbol, feature_snapshot, regime_snapshot) -> List[Dict[str, Any]]:
        return [
            {
                "symbol": symbol,
                "side": "BUY",
                "entry": 50.0,
                "stop": 48.0,
                "target": 55.0,
                "strategy": self.name,
                "strategy_version": self.version,
                "features": {"score": 0.9, "expected_return": 0.05, "holding_time": "swing"},
            }
        ]


class AegisPipelineTests(unittest.TestCase):
    def test_happy_path_candidate_flows_to_fill(self):
        pipeline = AegisPipeline()
        pipeline.register_strategy(AlwaysBuyStrategy())

        result = pipeline.run_cycle("AAPL", [_bar(50.0, 0)])

        self.assertEqual(len(result["candidates"]), 1)
        self.assertEqual(len(result["scored"]), 1)
        self.assertGreater(result["scored"][0]["probability_score"], 0.0)
        self.assertEqual(len(result["trade_intents"]), 1)
        self.assertEqual(len(result["approved"]), 1)
        self.assertEqual(result["rejected"], [])
        self.assertEqual(len(result["fills"]), 1)
        self.assertEqual(result["fills"][0]["status"], "filled")

        snapshot = pipeline.portfolio.snapshot()
        self.assertIn("AAPL", snapshot["positions"])
        self.assertLess(snapshot["cash"], 100_000.0)

    def test_oversized_trade_is_rejected_by_risk_engine_not_executed(self):
        # Capital Allocation (not the strategy) owns final sizing, so to
        # exercise a rejection deterministically we tighten the Risk Engine's
        # own limit rather than asking a strategy to request an oversized qty.
        pipeline = AegisPipeline()
        pipeline.register_strategy(AlwaysBuyStrategy())
        pipeline.risk_engine.limits["max_gross_exposure_pct"] = 0.00001

        result = pipeline.run_cycle("AAPL", [_bar(50.0, 0)])

        self.assertEqual(len(result["rejected"]), 1)
        self.assertTrue(result["rejected"][0]["risk_rejected"])
        self.assertEqual(result["fills"], [])
        # Nothing should have reached the broker/portfolio for a rejected trade.
        self.assertEqual(pipeline.portfolio.snapshot()["cash"], 100_000.0)

    def test_no_registered_strategies_yields_empty_but_well_formed_result(self):
        pipeline = AegisPipeline()
        result = pipeline.run_cycle("AAPL", [_bar(50.0, 0)])
        self.assertEqual(result["candidates"], [])
        self.assertEqual(result["scored"], [])
        self.assertEqual(result["approved"], [])
        self.assertEqual(result["fills"], [])
        self.assertIn("name", result["regime"])

    def test_inactive_strategy_is_not_run(self):
        pipeline = AegisPipeline()
        pipeline.register_strategy(AlwaysBuyStrategy(), active=False)
        result = pipeline.run_cycle("AAPL", [_bar(50.0, 0)])
        self.assertEqual(result["candidates"], [])

    def test_momentum_strategy_runs_through_full_pipeline_without_error(self):
        pipeline = AegisPipeline()
        pipeline.register_strategy(MomentumStrategy())

        rng = random.Random(42)
        price = 100.0
        result = None
        for i in range(25):
            price = max(0.01, price + 0.6 + rng.uniform(-1.0, 1.0))
            # Feed one new bar per cycle -- DataEngine retains history itself.
            result = pipeline.run_cycle("AAPL", [_bar(price, i)])

        # Wiring must hold regardless of whether momentum happened to fire:
        # every approved trade must have a corresponding fill, and every
        # rejected trade must carry a reason.
        self.assertEqual(len(result["approved"]), len(result["fills"]))
        for rejected in result["rejected"]:
            self.assertTrue(rejected["risk_reasons"])

    def test_halted_risk_engine_blocks_all_trades(self):
        pipeline = AegisPipeline()
        pipeline.register_strategy(AlwaysBuyStrategy())
        pipeline.risk_engine.halt_trading("test_halt")

        result = pipeline.run_cycle("AAPL", [_bar(50.0, 0)])
        self.assertEqual(result["approved"], [])
        self.assertEqual(result["fills"], [])
        self.assertEqual(len(result["rejected"]), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
