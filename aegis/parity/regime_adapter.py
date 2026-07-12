from __future__ import annotations

from aegis.regime import RegimeEngine as AegisRegimeEngine

from .common import ParityResult, bounded_ratio, get_threshold, load_parity_config
from .fixtures import sample_feature_snapshot


def _regime_to_numeric(name: str) -> float:
    name = str(name).lower()
    table = {
        "trending": 1.0,
        "bull": 1.0,
        "mean_reverting": 0.5,
        "neutral": 0.5,
        "quiet": 0.5,
        "volatile": 0.0,
        "high_volatility": 0.0,
        "bear": 0.0,
    }
    return table.get(name, 0.5)


class RegimeParityAdapter:
    def run(self) -> ParityResult:
        cfg = load_parity_config()
        threshold = get_threshold(cfg, "regime", 0.40)

        features = sample_feature_snapshot()

        # Legacy baseline approximation retained as deterministic target.
        trend = float(features.get("technical", {}).get("trend", 0.0) or 0.0)
        legacy_name = "trending" if abs(trend) >= 0.15 else "mean_reverting"
        legacy_num = _regime_to_numeric(legacy_name)

        aegis_engine = AegisRegimeEngine({})
        aegis_state = aegis_engine.classify(features)
        aegis_num = _regime_to_numeric(aegis_state.get("name"))

        diff = bounded_ratio(legacy_num, aegis_num)
        ok = diff <= threshold
        return ParityResult(
            name="regime",
            ok=ok,
            diff=diff,
            threshold=threshold,
            details={"legacy_regime": legacy_name, "aegis_regime": aegis_state.get("name")},
        )
