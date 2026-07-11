from __future__ import annotations

import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from aegis.allocation import CapitalAllocationEngine
from aegis.alpha import AlphaHub, CalibrationService, ModelRegistry, PredictionService
from aegis.execution import ExecutionEngine
from aegis.marketplace import StrategyOnboardingPipeline, StrategyPerformanceStore, StrategyRegistry, StrategyRunner, StrategySelector
from aegis.portfolio import PortfolioManager, PortfolioStore, aggregate_exposures, allocate_capital, attribute_performance, reconcile_positions
from aegis.risk import RiskEngine
from aegis.scoring import AdaptiveWeightingEngine, ExplainableDecisionEngine, MetaModelEngine, TradeScoringEngine
from aegis.scoring.modules import LiquidityScorer, MacroScorer, MLScorer, OrderFlowScorer, RegimeScorer, Scorer, SentimentScorer, ShortSqueezeScorer, TechnicalScorer


class StubScorer(Scorer):
    def __init__(self, name: str, score: float):
        self.name = name
        self._score = score

    def score(self, trade_intent, feature_snapshot, context):
        return {
            "component": self.name,
            "score": self._score,
            "raw": {"symbol": trade_intent["symbol"]},
            "explain": ["stub"],
            "version": "test",
        }


class DummyBroker:
    def __init__(self, response=None):
        self.orders = []
        self.response = dict(response or {"status": "filled", "filled_qty": 1})

    def submit_order(self, order):
        self.orders.append(dict(order))
        return dict(self.response)

    def cancel_order(self, order_id):
        return {"status": "cancelled", "order_id": order_id}


class RetryThenFillBroker(DummyBroker):
    def __init__(self):
        super().__init__({"status": "retry"})
        self.calls = 0

    def submit_order(self, order):
        self.calls += 1
        self.orders.append(dict(order))
        if self.calls == 1:
            return {"status": "retry"}
        return {"status": "filled", "filled_qty": int(order.get("qty", 0))}


class DummyPortfolio:
    def __init__(self):
        self.applied = []

    def apply_trade(self, trade_intent):
        self.applied.append(dict(trade_intent))

    def snapshot(self):
        return {"positions": {}, "cash": 1000.0, "gross_exposure": 0.0}


class DummyEnv:
    def __init__(self, open_state=True):
        self.open_state = open_state

    def is_open(self):
        return self.open_state


class AegisScoringTests(unittest.TestCase):
    def test_score_trade(self):
        engine = TradeScoringEngine([StubScorer("signal", 100.0)], AdaptiveWeightingEngine({}), ExplainableDecisionEngine(), MetaModelEngine({}))
        engine.weighting_engine.weights_by_regime["default"] = {"signal": 1.0}
        result = engine.score_trade({"symbol": "AAPL", "entry": 100.0}, {"score": 1.0}, {"name": "default"})
        self.assertEqual(result["confidence_class"], "elite")
        self.assertEqual(result["component_scores"], {"signal": 100.0})
        self.assertGreaterEqual(result["probability_score"], 100.0)

    def test_deterministic_component_scorers(self):
        trade = {"symbol": "AAPL"}
        features = {
            "technical": {"rsi": 50, "trend": 1.0, "momentum": 1.0},
            "order_flow": {"imbalance": 1.0, "participation": 1.0},
            "sentiment": {"news": 1.0, "social": 1.0},
            "liquidity": {"adv_ratio": 0.05, "spread_bps": 5.0},
            "ml": {"prob_up": 1.0, "uncertainty": 0.0},
            "squeeze": {"short_interest": 0.35, "days_to_cover": 12.0},
            "macro": {"growth": 1.0, "inflation": 0.0, "rates": 0.0},
        }
        regime = {"name": "bull", "confidence": 1.0, "risk": 0.0}
        scorers = [
            TechnicalScorer(),
            OrderFlowScorer(),
            SentimentScorer(),
            RegimeScorer(),
            LiquidityScorer(),
            MLScorer(),
            ShortSqueezeScorer(),
            MacroScorer(),
        ]
        for scorer in scorers:
            score = scorer.score(trade, features, regime)["score"]
            self.assertGreaterEqual(score, 50.0)
            self.assertLessEqual(score, 100.0)


class AegisAlphaTests(unittest.TestCase):
    def test_produce_trade_intent(self):
        registry = ModelRegistry()
        registry.register("growth_v2", {"owner": "aegis"})
        hub = AlphaHub(PredictionService(), CalibrationService(), registry)
        trade = hub.produce_trade_intent({"symbol": "MSFT", "model": "growth_v2", "features": {"score": 0.8, "expected_return": 0.12, "holding_time": "2d", "version": "v2"}, "entry": 200.0})
        self.assertEqual(trade["symbol"], "MSFT")
        self.assertEqual(trade["side"], "BUY")
        self.assertEqual(trade["probability"], 80.0)
        self.assertEqual(trade["alpha_metadata"]["registry"]["owner"], "aegis")


class AegisRiskTests(unittest.TestCase):
    def test_evaluate_trades(self):
        portfolio = DummyPortfolio()
        engine = RiskEngine({"max_position_qty": 10, "max_gross_exposure": 500.0}, portfolio, DummyEnv(), None)
        approved, rejected = engine.evaluate_trades([
            {"symbol": "AAPL", "side": "BUY", "qty": 1, "entry": 10.0},
            {"symbol": "AAPL", "side": "BUY", "qty": 20, "entry": 10.0},
        ])
        self.assertEqual(len(approved), 1)
        self.assertEqual(len(rejected), 1)
        self.assertTrue(rejected[0]["risk_rejected"])


class AegisPortfolioTests(unittest.TestCase):
    def test_apply_trade_and_snapshot(self):
        manager = PortfolioManager({"initial_cash": 1000.0}, DummyBroker(), None)
        manager.apply_trade({"symbol": "AAPL", "side": "BUY", "qty": 2, "entry": 10.0})
        manager.apply_trade({"symbol": "AAPL", "side": "SELL", "qty": 1, "entry": 12.0})
        snapshot = manager.snapshot()
        self.assertEqual(snapshot["positions"]["AAPL"]["qty"], 1)
        self.assertEqual(snapshot["cash"], 992.0)
        self.assertEqual(manager.mark_to_market("AAPL", 15.0), 5.0)

    def test_portfolio_helpers(self):
        exposure = aggregate_exposures({"AAPL": {"qty": 2, "avg_price": 10.0}})
        self.assertEqual(exposure["gross"], 20.0)
        self.assertEqual(allocate_capital({"cash": 1000.0}, {"capital_fraction": 0.2}, [{"symbol": "AAPL", "entry": 50.0}])[0]["qty"], 4)
        self.assertEqual(attribute_performance({"AAPL": 1}, {"benchmark": "SPY", "alpha": 0.5})["benchmark"], "SPY")
        self.assertEqual(reconcile_positions({"AAPL": {"qty": 1}}, {"AAPL": {"qty": 2}})[0]["delta"], 1)
        store = PortfolioStore()
        self.assertEqual(store.save({"cash": 123.0}), {"cash": 123.0})
        self.assertEqual(store.load(), {"cash": 123.0})


class AegisExecutionTests(unittest.TestCase):
    def test_execute_trade_intent(self):
        broker = DummyBroker()
        portfolio = DummyPortfolio()
        engine = ExecutionEngine(broker, portfolio, None, {"max_retries": 2})
        result = engine.execute_trade_intent({"symbol": "AAPL", "side": "BUY", "qty": 3, "entry": 10.0})
        self.assertEqual(result["status"], "filled")
        self.assertEqual(portfolio.applied[0]["symbol"], "AAPL")
        self.assertEqual(broker.orders[0]["qty"], 3)
        self.assertEqual(engine.cancel("abc")["status"], "cancelled")
        self.assertEqual(engine.metrics.snapshot()["fills"], 1)

    def test_retry_then_fill(self):
        broker = RetryThenFillBroker()
        portfolio = DummyPortfolio()
        engine = ExecutionEngine(broker, portfolio, None, {"max_retries": 2})
        result = engine.execute_trade_intent({"symbol": "NVDA", "side": "BUY", "qty": 2, "entry": 10.0})
        self.assertEqual(result["status"], "filled")
        self.assertEqual(engine.metrics.snapshot()["submissions"], 2)


class AegisMarketplaceTests(unittest.TestCase):
    def test_registry_and_selection(self):
        registry = StrategyRegistry()
        registry.register("alpha", {"active": True}, lambda: "ok")
        registry.register("beta", {"active": False}, lambda: "skip")
        self.assertEqual(registry.list_active(), ["alpha"])
        self.assertIn("alpha", registry.snapshot())
        selector = StrategySelector()
        selected = selector.select(strategies=[{"metadata": {"active": True}}, {"metadata": {"active": False}}])
        self.assertEqual(len(selected), 1)
        pipeline = StrategyOnboardingPipeline()
        self.assertTrue(pipeline.validate(strategy={"name": "alpha", "entry_point": lambda: None}))
        self.assertFalse(pipeline.validate(strategy={"name": "beta"}))
        runner = StrategyRunner()
        self.assertEqual(runner.run(strategies=[{"entry_point": lambda: "ran"}]), ["ran"])
        store = StrategyPerformanceStore()
        store.record("alpha", {"score": 1.0})
        self.assertEqual(store.leaderboard(), [("alpha", {"score": 1.0})])


class AegisAllocationTests(unittest.TestCase):
    def test_allocate(self):
        engine = CapitalAllocationEngine({"default_qty": 5, "max_qty": 10})
        allocated = engine.allocate({"cash": 1000.0}, {"capital_fraction": 0.2}, [{"symbol": "AAPL", "entry": 50.0}])
        self.assertEqual(allocated[0]["qty"], 4)
        self.assertEqual(allocated[0]["symbol"], "AAPL")


if __name__ == "__main__":
    unittest.main(verbosity=2)