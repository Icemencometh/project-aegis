from __future__ import annotations

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from aegis.risk import RiskEngine


class DummyPortfolio:
    def __init__(self, snapshot):
        self._snapshot = snapshot
        self.applied = []

    def snapshot(self):
        return dict(self._snapshot)

    def apply_trade(self, trade_intent):
        self.applied.append(dict(trade_intent))


class DummyEnv:
    def is_open(self):
        return True


class DummyExecutionEngine:
    def __init__(self):
        self.executed = []

    def execute_trade_intent(self, trade_intent):
        self.executed.append(dict(trade_intent))
        return {"status": "filled"}


class RiskEngineHaltFlattenTests(unittest.TestCase):
    def test_halt_and_resume(self):
        engine = RiskEngine({}, DummyPortfolio({"positions": {}, "cash": 1000.0, "gross_exposure": 0.0}), DummyEnv(), None)
        self.assertFalse(engine.is_halted())
        engine.halt_trading("test_reason")
        self.assertTrue(engine.is_halted())
        approved, rejected = engine.evaluate_trades([{"symbol": "AAPL", "side": "BUY", "qty": 1, "entry": 10.0}])
        self.assertEqual(approved, [])
        self.assertIn("trading_halted:test_reason", rejected[0]["risk_reasons"][0])
        engine.resume_trading()
        self.assertFalse(engine.is_halted())
        approved, rejected = engine.evaluate_trades([{"symbol": "AAPL", "side": "BUY", "qty": 1, "entry": 10.0}])
        self.assertEqual(len(approved), 1)

    def test_flatten_positions_without_execution_engine_returns_orders(self):
        portfolio = DummyPortfolio({"positions": {"AAPL": {"qty": 10, "avg_price": 100.0}}, "cash": 1000.0, "gross_exposure": 1000.0})
        engine = RiskEngine({}, portfolio, DummyEnv(), None)
        orders = engine.flatten_positions()
        self.assertEqual(orders, [{"symbol": "AAPL", "side": "SELL", "qty": 10}])

    def test_flatten_positions_submits_via_execution_engine(self):
        portfolio = DummyPortfolio({"positions": {"AAPL": {"qty": -5, "avg_price": 100.0}}, "cash": 1000.0, "gross_exposure": 500.0})
        execution_engine = DummyExecutionEngine()
        engine = RiskEngine({}, portfolio, DummyEnv(), None, execution_engine=execution_engine)
        orders = engine.flatten_positions()
        self.assertEqual(orders, [{"symbol": "AAPL", "side": "BUY", "qty": 5}])
        self.assertEqual(execution_engine.executed, orders)

    def test_max_drawdown_halts_trading_automatically(self):
        portfolio = DummyPortfolio({"positions": {}, "cash": 1000.0, "gross_exposure": 0.0, "drawdown_pct": 0.20})
        engine = RiskEngine({"limits": {"max_drawdown_pct": 0.10}}, portfolio, DummyEnv(), None)
        approved, rejected = engine.evaluate_trades([{"symbol": "AAPL", "side": "BUY", "qty": 1, "entry": 10.0}])
        self.assertEqual(approved, [])
        self.assertIn("max_drawdown_exceeded", rejected[0]["risk_reasons"])
        self.assertTrue(engine.is_halted())

    def test_symbol_concentration_pct_limit(self):
        portfolio = DummyPortfolio({"positions": {}, "cash": 1000.0, "gross_exposure": 0.0})
        engine = RiskEngine({"limits": {"max_symbol_pct": 0.1}}, portfolio, DummyEnv(), None)
        # equity = cash(1000) + gross(0) = 1000; 10 shares * 50 = 500 > 1000*0.1=100
        approved, rejected = engine.evaluate_trades([{"symbol": "AAPL", "side": "BUY", "qty": 10, "entry": 50.0}])
        self.assertEqual(approved, [])
        self.assertIn("symbol_concentration_exceeded", rejected[0]["risk_reasons"])

    def test_legacy_flat_limits_still_work(self):
        portfolio = DummyPortfolio({"positions": {}, "cash": 1000.0, "gross_exposure": 0.0})
        engine = RiskEngine({"max_position_qty": 10, "max_gross_exposure": 500.0}, portfolio, DummyEnv(), None)
        approved, rejected = engine.evaluate_trades([
            {"symbol": "AAPL", "side": "BUY", "qty": 1, "entry": 10.0},
            {"symbol": "AAPL", "side": "BUY", "qty": 20, "entry": 10.0},
        ])
        self.assertEqual(len(approved), 1)
        self.assertEqual(len(rejected), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
