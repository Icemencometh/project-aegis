from __future__ import annotations

from typing import Any, Dict


class MetaModelEngine:
    def __init__(self, cfg: Dict[str, Any]):
        self.cfg = dict(cfg or {})

    def score(self, components: Dict[str, Dict[str, Any]], regime_snapshot: Dict[str, Any]) -> float:
        if not components:
            return 0.0
        return sum(float(component.get("score", 0.0)) for component in components.values()) / len(components)