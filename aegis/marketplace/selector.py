from __future__ import annotations


class StrategySelector:
    def select(self, *args, **kwargs):
        strategies = kwargs.get("strategies", [])
        return [strategy for strategy in strategies if strategy.get("metadata", {}).get("active", True)]