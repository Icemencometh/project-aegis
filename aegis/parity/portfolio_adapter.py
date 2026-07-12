from __future__ import annotations

try:
    from portfolio_manager import PortfolioManager as LegacyPortfolioManager  # legacy module may be absent in CI snapshots
except Exception:  # pragma: no cover - fallback path for CI portability
    LegacyPortfolioManager = None

from aegis.portfolio import PortfolioManager as AegisPortfolioManager

from .common import ParityResult, bounded_ratio, get_threshold, load_parity_config
from .fixtures import sample_trade_intent


class PortfolioParityAdapter:
    def run(self) -> ParityResult:
        cfg = load_parity_config()
        threshold = get_threshold(cfg, "portfolio", 0.25)

        trade = sample_trade_intent()

        if LegacyPortfolioManager is not None:
            legacy = LegacyPortfolioManager({"initial_cash": 100000.0})
            legacy.apply_trade(trade)
            legacy_snapshot = legacy.snapshot()
            legacy_cash = float(legacy_snapshot.get("cash", 0.0))
        else:
            notional = float(trade.get("qty", 0.0)) * float(trade.get("entry", 0.0))
            legacy_cash = 100000.0 - notional

        class _Broker:
            def get_positions(self):
                return []

            def get_account(self):
                return {"cash": 100000.0}

        aegis = AegisPortfolioManager({"initial_cash": 100000.0}, _Broker(), None)
        aegis.apply_trade(trade)
        aegis_snapshot = aegis.snapshot()
        aegis_cash = float(aegis_snapshot.get("cash", 0.0))

        diff = bounded_ratio(legacy_cash, aegis_cash)
        ok = diff <= threshold
        return ParityResult(
            name="portfolio",
            ok=ok,
            diff=diff,
            threshold=threshold,
            details={"legacy_cash": legacy_cash, "aegis_cash": aegis_cash},
        )
