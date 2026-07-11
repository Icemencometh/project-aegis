from __future__ import annotations

from typing import Any, Dict, List, Sequence

from .explainable import ExplainableDecisionEngine
from .meta import MetaModelEngine
from .modules.base import Scorer
from .weighting import AdaptiveWeightingEngine


class TradeScoringEngine:
    def __init__(
        self,
        scorers: Sequence[Scorer] | None = None,
        weighting_engine: AdaptiveWeightingEngine | None = None,
        explainable_engine: ExplainableDecisionEngine | None = None,
        meta_model: MetaModelEngine | None = None,
    ):
        self.scorers = {scorer.name: scorer for scorer in (scorers or [])}
        self.weighting_engine = weighting_engine or AdaptiveWeightingEngine({})
        self.explainable_engine = explainable_engine or ExplainableDecisionEngine()
        self.meta_model = meta_model

    def add_scorer(self, scorer: Scorer) -> None:
        self.scorers[scorer.name] = scorer

    def get_weights(self, regime_snapshot: Dict[str, Any]) -> Dict[str, float]:
        return self.weighting_engine.get_weights(regime_snapshot)

    def score_components(
        self,
        trade: Dict[str, Any],
        feature_snapshot: Dict[str, Any],
        regime_snapshot: Dict[str, Any],
    ) -> Dict[str, Dict[str, Any]]:
        return {
            name: scorer.score(trade, feature_snapshot, regime_snapshot)
            for name, scorer in self.scorers.items()
        }

    def score_trade(
        self,
        trade: Dict[str, Any],
        feature_snapshot: Dict[str, Any],
        regime_snapshot: Dict[str, Any],
    ) -> Dict[str, Any]:
        scored = self.score_trades([trade], feature_snapshot, regime_snapshot)
        return scored[0] if scored else dict(trade)

    def score_trades(
        self,
        trades: List[Dict[str, Any]],
        feature_snapshot: Dict[str, Any],
        regime_snapshot: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        scored: List[Dict[str, Any]] = []
        weights = self.get_weights(regime_snapshot)
        for trade in trades:
            component_outputs = self.score_components(trade, feature_snapshot, regime_snapshot)
            composite = self._compute_composite(component_outputs, weights)
            meta_score = self.meta_model.score(component_outputs, regime_snapshot) if self.meta_model else None
            confidence_class = self._classify(composite)
            rationale = self.explainable_engine.build_rationale(
                trade,
                component_outputs,
                composite,
                meta_score,
                confidence_class,
                regime_snapshot,
            )
            scored.append(
                {
                    **trade,
                    "component_scores": {name: payload["score"] for name, payload in component_outputs.items()},
                    "weights": weights,
                    "probability_score": composite,
                    "meta_score": meta_score,
                    "confidence_class": confidence_class,
                    "rationale": rationale,
                }
            )
        return scored

    def _compute_composite(self, components: Dict[str, Dict[str, Any]], weights: Dict[str, float]) -> float:
        if not components:
            return 0.0
        return sum(float(components[name]["score"]) * float(weights.get(name, 0.0)) for name in components)

    def _classify(self, score: float) -> str:
        if score >= 95:
            return "elite"
        if score >= 90:
            return "strong_buy"
        if score >= 85:
            return "buy"
        if score >= 80:
            return "watch"
        if score >= 75:
            return "monitor"
        return "reject"