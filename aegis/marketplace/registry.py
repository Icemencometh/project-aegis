from __future__ import annotations

from typing import Any, Callable, Dict


class StrategyRegistry:
    def __init__(self):
        self._strategies: Dict[str, Dict[str, Any]] = {}

    def register(self, name: str, metadata: Dict[str, Any], entry_point: Callable):
        self._strategies[name] = {"metadata": dict(metadata or {}), "entry_point": entry_point}

    def unregister(self, name: str):
        return self._strategies.pop(name, None)

    def get(self, name: str):
        return dict(self._strategies.get(name, {}))

    def list_active(self):
        return [name for name, strategy in self._strategies.items() if strategy.get("metadata", {}).get("active", True)]

    def snapshot(self):
        return {name: dict(payload) for name, payload in self._strategies.items()}