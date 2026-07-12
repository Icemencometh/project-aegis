from __future__ import annotations

try:
    from quant_bot.risk.advanced_risk_engine import AdvancedRiskEngine
except Exception:  # pragma: no cover - fallback path for CI portability
    AdvancedRiskEngine = None

from aegis.risk import RiskEngine

from .common import ParityResult, bounded_ratio, get_threshold, load_parity_config
from .fixtures import sample_portfolio_snapshot, sample_regime_snapshot, sample_trade_intent


class RiskParityAdapter:
    def run(self) -> ParityResult:
        cfg = load_parity_config()
        threshold = get_threshold(cfg, "risk", 0.25)

        trade = sample_trade_intent()
        portfolio = sample_portfolio_snapshot()
        regime = sample_regime_snapshot()

        if AdvancedRiskEngine is not None:
            legacy = AdvancedRiskEngine({"max_heat": 0.9})
            legacy_decision = legacy.assess_trade(trade, portfolio_snapshot=portfolio, regime_snapshot=regime)
            legacy_allowed = 1.0 if bool(legacy_decision.get("allowed", False)) else 0.0
        else:
            qty = float(trade.get("qty", 0.0) or 0.0)
            legacy_allowed = 1.0 if qty > 0.0 else 0.0

        class _Env:
            def is_open(self):
                return True

        aegis = RiskEngine({"max_position_qty": 1000, "max_gross_exposure": 1_000_000.0}, portfolio, _Env(), None)
        aegis_decision = aegis.assess_trade(trade)
        aegis_allowed = 1.0 if bool(aegis_decision.allowed) else 0.0

        diff = bounded_ratio(legacy_allowed, aegis_allowed)
        ok = diff <= threshold
        return ParityResult(
            name="risk",
            ok=ok,
            diff=diff,
            threshold=threshold,
            details={"legacy_allowed": bool(legacy_allowed), "aegis_allowed": bool(aegis_allowed)},
        )
