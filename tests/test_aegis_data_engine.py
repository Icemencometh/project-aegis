from __future__ import annotations

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from aegis.data import Bar, DataEngine


class DataEngineTests(unittest.TestCase):
    def _bar(self, close: float, timestamp: str = "2026-01-01T00:00:00Z"):
        return {"timestamp": timestamp, "open": close, "high": close, "low": close, "close": close, "volume": 1000}

    def test_ingest_and_read(self):
        engine = DataEngine(version="v1")
        bar = engine.ingest_bar("AAPL", self._bar(100.0))
        self.assertIsInstance(bar, Bar)
        self.assertEqual(bar.symbol, "AAPL")
        self.assertEqual(bar.version, "v1")
        self.assertEqual(engine.get_latest("AAPL").close, 100.0)
        self.assertEqual(engine.symbols(), ["AAPL"])

    def test_ingest_bars_and_lookback(self):
        engine = DataEngine()
        engine.ingest_bars("MSFT", [self._bar(p) for p in [10.0, 11.0, 12.0, 13.0]])
        self.assertEqual(len(engine.get_history("MSFT")), 4)
        self.assertEqual([bar.close for bar in engine.get_history("MSFT", lookback=2)], [12.0, 13.0])

    def test_read_only_snapshots_are_copies(self):
        engine = DataEngine()
        engine.ingest_bar("AAPL", self._bar(100.0))
        history = engine.get_history("AAPL")
        history.append("not a bar")
        self.assertEqual(len(engine.get_history("AAPL")), 1)

    def test_missing_symbol_returns_empty(self):
        engine = DataEngine()
        self.assertEqual(engine.get_history("GOOG"), [])
        self.assertIsNone(engine.get_latest("GOOG"))

    def test_validation_error_on_missing_fields(self):
        engine = DataEngine()
        with self.assertRaises(ValueError):
            engine.ingest_bar("AAPL", {"timestamp": "t", "open": 1.0})


if __name__ == "__main__":
    unittest.main(verbosity=2)
