from __future__ import annotations

from typing import Any, Dict


class Scorer:
    name: str = "base"

    def score(self, trade_intent: Dict[str, Any], feature_snapshot: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    @staticmethod
    def clamp_score(value: float) -> float:
        return max(0.0, min(100.0, float(value)))

    @staticmethod
    def scale_ratio(value: float, floor: float, ceiling: float) -> float:
        floor = float(floor)
        ceiling = float(ceiling)
        if ceiling <= floor:
            return 0.0
        return max(0.0, min(1.0, (float(value) - floor) / (ceiling - floor)))