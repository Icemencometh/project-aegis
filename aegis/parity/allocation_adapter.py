from __future__ import annotations

from aegis.allocation import CapitalAllocationEngine

from .common import ParityResult, bounded_ratio, get_threshold, load_parity_config
from .fixtures import sample_portfolio_snapshot, sample_trade_intent


class AllocationParityAdapter:
    def run(self) -> ParityResult:
        cfg = load_parity_config()
        threshold = get_threshold(cfg, "allocation", 0.35)

        portfolio = sample_portfolio_snapshot()
        trade = sample_trade_intent()

        # Legacy baseline approximation retained as deterministic numeric target.
        equity = float(portfolio["equity"])
        price = max(float(trade["entry"]), 1e-9)
        legacy_units = int((equity * 0.1) // price)

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
