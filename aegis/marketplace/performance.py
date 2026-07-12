from __future__ import annotations

from typing import Any, Dict, Optional


class StrategyPerformanceStore:
    """Tracks strategy performance, including per-regime breakdowns
    (Aegis_Module_Contracts.md: "Strategy performance must be tracked per
    regime.").
    """

    def __init__(self):
        self._results: Dict[str, Dict[str, Any]] = {}
        self._by_regime: Dict[str, Dict[str, Dict[str, Any]]] = {}

    def record(self, strategy_name, performance, regime: Optional[str] = None):
        name = str(strategy_name)
        self._results[name] = dict(performance or {})
        if regime is not None:
            self._by_regime.setdefault(name, {})[str(regime)] = dict(performance or {})

    def leaderboard(self):
        return sorted(self._results.items())

    def leaderboard_for_regime(self, regime: str):
        regime = str(regime)
        rows = [
            (name, per_regime[regime])
            for name, per_regime in self._by_regime.items()
            if regime in per_regime
        ]
        return sorted(rows)

    def get(self, strategy_name) -> Dict[str, Any]:
        return dict(self._results.get(str(strategy_name), {}))
