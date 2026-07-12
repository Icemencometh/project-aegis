from __future__ import annotations

from position_sizer import PositionSizer

from aegis.allocation import CapitalAllocationEngine

from .common import ParityResult, bounded_ratio, get_threshold, load_parity_config
from .fixtures import sample_portfolio_snapshot, sample_trade_intent


class AllocationParityAdapter:
    def run(self) -> ParityResult:
        cfg = load_parity_config()
        threshold = get_threshold(cfg, "allocation", 0.35)

        portfolio = sample_portfolio_snapshot()
        trade = sample_trade_intent()

        legacy_sizer = PositionSizer(max_position_pct=0.2)
        legacy_units = legacy_sizer.fixed_fractional(
            equity=float(portfolio["equity"]),
            risk_pct=0.1,
            price=float(trade["entry"]),
        ).units

        aegis_alloc = CapitalAllocationEngine({"default_qty": 10, "max_qty": 200, "capital_fraction": 0.1})
        allocated = aegis_alloc.allocate({"cash": portfolio["cash"]}, {"capital_fraction": 0.1}, [trade])[0]
        aegis_qty = float(allocated.get("qty", 0))

        diff = bounded_ratio(legacy_units, aegis_qty)
        ok = diff <= threshold
        return ParityResult(
            name="allocation",
            ok=ok,
            diff=diff,
            threshold=threshold,
            details={"legacy_units": legacy_units, "aegis_qty": aegis_qty},
        )
