from __future__ import annotations

from typing import Any, Dict, List


class ExplainableDecisionEngine:
    def build_rationale(
        self,
        trade: Dict[str, Any],
        components: Dict[str, Dict[str, Any]],
        composite: float,
        meta_score: float | None,
        confidence_class: str,
        regime_snapshot: Dict[str, Any],
    ) -> List[str]:
        bullets: List[str] = [f"Composite score {composite:.1f}, class={confidence_class}"]
        if meta_score is not None:
            bullets.append(f"Meta-model score {meta_score:.1f}")
        for name, component in components.items():
            bullets.append(f"{name}={component['score']:.1f}")
        return bullets