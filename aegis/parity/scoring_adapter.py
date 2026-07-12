from __future__ import annotations

from aegis.scoring import AdaptiveWeightingEngine, ExplainableDecisionEngine, MetaModelEngine, TradeScoringEngine
from aegis.scoring.modules import (
    LiquidityScorer,
    MacroScorer,
    MLScorer,
    OrderFlowScorer,
    RegimeScorer,
    SentimentScorer,
    ShortSqueezeScorer,
    TechnicalScorer,
)

from .common import ParityResult, bounded_ratio, get_threshold, load_parity_config
from .fixtures import sample_feature_snapshot, sample_regime_snapshot, sample_scoring_signal


class ScoringParityAdapter:
    def run(self) -> ParityResult:
        cfg = load_parity_config()
        threshold = get_threshold(cfg, "scoring", 0.25)

        signal = sample_scoring_signal()
        feature_snapshot = sample_feature_snapshot()
        regime_snapshot = sample_regime_snapshot()

        # Legacy baseline approximation retained as deterministic target.
        legacy_score = float(signal.get("score", 0.5))

        engine = TradeScoringEngine(
            scorers=[
                TechnicalScorer(),
                OrderFlowScorer(),
                ShortSqueezeScorer(),
                MLScorer(),
                RegimeScorer(),
                MacroScorer(),
                LiquidityScorer(),
                SentimentScorer(),
            ],
            weighting_engine=AdaptiveWeightingEngine({}),
            explainable_engine=ExplainableDecisionEngine(),
            meta_model=MetaModelEngine({}),
        )
        scored = engine.score_trade(signal, feature_snapshot, regime_snapshot)
        aegis_prob = float(scored.get("probability_score", 0.0)) / 100.0

        diff = bounded_ratio(legacy_score, aegis_prob)
        ok = diff <= threshold
        return ParityResult(
            name="scoring",
            ok=ok,
            diff=diff,
            threshold=threshold,
            details={"legacy_confidence": legacy_score, "aegis_probability": aegis_prob},
        )
