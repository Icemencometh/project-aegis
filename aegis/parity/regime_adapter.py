from __future__ import annotations

from quant_bot.regime.regime_engine import RegimeEngine as LegacyRegimeEngine

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
        legacy_features = {
            "adx": 24.0,
            "bb_width": 0.04,
            "hist_vol_20": 0.2,
            "rsi_14": float(features["technical"]["rsi"]),
            "macd_hist": 0.1,
            "ema_9_cross": 0.7,
            "ema_21_cross": 0.65,
            "ema_50_cross": 0.62,
            "roc_20": 0.2,
            "z_score_20": 0.3,
            "bb_pct": 0.6,
        }

        legacy_engine = LegacyRegimeEngine()
        legacy_state = legacy_engine.classify(legacy_features)
        legacy_num = _regime_to_numeric(legacy_state.regime.value)

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
            details={"legacy_regime": legacy_state.regime.value, "aegis_regime": aegis_state.get("name")},
        )
