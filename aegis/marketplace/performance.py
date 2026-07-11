from __future__ import annotations


class StrategyPerformanceStore:
    def __init__(self):
        self._results = {}

    def record(self, strategy_name, performance):
        self._results[str(strategy_name)] = dict(performance or {})

    def leaderboard(self):
        return sorted(self._results.items())