from __future__ import annotations

from typing import Any, Dict


class MetaModelEngine:
    def __init__(self, cfg: Dict[str, Any]):
        self.cfg = dict(cfg or {})
        self.model = None

    def score(self, components: Dict[str, Dict[str, Any]], regime_snapshot: Dict[str, Any]) -> float:
        if not components:
            return 0.0
        return sum(float(component["score"]) for component in components.values()) / len(components)