"""Legacy position sizing module retained for parity testing.

This module provides the PositionSizer interface used by the Aegis parity
harness (aegis/parity/allocation_adapter.py) to compare legacy sizing
behaviour against the CapitalAllocationEngine.  It is intentionally minimal
and must not be used in any live or paper trading execution path.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class _SizingResult:
    units: int


class PositionSizer:
    """Fixed-fractional position sizer (legacy interface).

    Parameters
    ----------
    max_position_pct:
        Maximum fraction of equity that may be allocated to a single
        position (currently unused in sizing maths, retained for API
        compatibility with the original implementation).
    """

    def __init__(self, max_position_pct: float = 0.2) -> None:
        self.max_position_pct = max_position_pct

    def fixed_fractional(
        self,
        equity: float,
        risk_pct: float,
        price: float,
    ) -> _SizingResult:
        """Return integer units sized by the fixed-fractional rule.

        units = floor(equity * risk_pct / price)
        """
        if price <= 0.0:
            return _SizingResult(units=0)
        target_capital = float(equity) * float(risk_pct)
        units = int(target_capital // float(price))
        return _SizingResult(units=units)
