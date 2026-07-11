from __future__ import annotations


class StrategyRunner:
    def run(self, *args, **kwargs):
        strategies = kwargs.get("strategies", [])
        results = []
        for strategy in strategies:
            entry_point = strategy.get("entry_point")
            if callable(entry_point):
                results.append(entry_point(*args))
        return results