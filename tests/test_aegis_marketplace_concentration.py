from __future__ import annotations

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from aegis.marketplace import enforce_strategy_concentration


class ConcentrationGuardTests(unittest.TestCase):
    def test_caps_single_strategy_notional(self):
        portfolio_snapshot = {"cash": 1000.0}
        trades = [
            {"symbol": "AAPL", "entry": 100.0, "qty": 5, "strategy": "momentum"},  # 500 notional
            {"symbol": "MSFT", "entry": 100.0, "qty": 5, "strategy": "momentum"},  # would push to 1000
        ]
        capped = enforce_strategy_concentration(trades, portfolio_snapshot, max_allocation_pct=0.25)
        # ceiling = 1000 * 0.25 = 250; first trade (500 notional) already exceeds it -> trimmed to 2 shares (200)
        self.assertEqual(capped[0]["qty"], 2)

    def test_different_strategies_have_independent_budgets(self):
        portfolio_snapshot = {"cash": 1000.0}
        trades = [
            {"symbol": "AAPL", "entry": 50.0, "qty": 5, "strategy": "momentum"},
            {"symbol": "MSFT", "entry": 50.0, "qty": 5, "strategy": "mean_reversion"},
        ]
        capped = enforce_strategy_concentration(trades, portfolio_snapshot, max_allocation_pct=0.25)
        self.assertEqual(capped[0]["qty"], 5)
        self.assertEqual(capped[1]["qty"], 5)

    def test_untagged_trades_pass_through(self):
        portfolio_snapshot = {"cash": 1000.0}
        trades = [{"symbol": "AAPL", "entry": 100.0, "qty": 50}]
        capped = enforce_strategy_concentration(trades, portfolio_snapshot, max_allocation_pct=0.25)
        self.assertEqual(capped[0]["qty"], 50)

    def test_zero_ceiling_returns_trades_unchanged(self):
        portfolio_snapshot = {"cash": 1000.0}
        trades = [{"symbol": "AAPL", "entry": 100.0, "qty": 50, "strategy": "momentum"}]
        capped = enforce_strategy_concentration(trades, portfolio_snapshot, max_allocation_pct=0.0)
        self.assertEqual(capped[0]["qty"], 50)

    def test_fully_trimmed_trade_is_dropped(self):
        portfolio_snapshot = {"cash": 10.0}
        trades = [{"symbol": "AAPL", "entry": 100.0, "qty": 5, "strategy": "momentum"}]
        capped = enforce_strategy_concentration(trades, portfolio_snapshot, max_allocation_pct=0.25)
        self.assertEqual(capped, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
