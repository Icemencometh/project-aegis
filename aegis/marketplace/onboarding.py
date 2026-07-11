from __future__ import annotations


class StrategyOnboardingPipeline:
    def validate(self, *args, **kwargs):
        strategy = kwargs.get("strategy") or (args[0] if args else {})
        return bool(strategy and strategy.get("name") and callable(strategy.get("entry_point")))