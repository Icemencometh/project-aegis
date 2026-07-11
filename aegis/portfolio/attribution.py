from __future__ import annotations

from typing import Any, Dict


def attribute_performance(trades: Dict[str, Any], snapshot: Dict[str, Any] | None = None):
    snapshot = dict(snapshot or {})
    return {
        "trades": dict(trades or {}),
        "benchmark": snapshot.get("benchmark", "unknown"),
        "alpha": snapshot.get("alpha", 0.0),
    }