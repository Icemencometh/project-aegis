"""Strategy base class (Aegis_Module_Contracts.md: Strategy Marketplace).

Contract:
- Strategies must emit trade candidates, not orders.
- Strategies must be pluggable and versioned.
"""

from __future__ import annotations

from typing import Any, Dict, List


class Strategy:
    """Base class for Aegis strategies. Concrete strategies set `name` and
    `version` and implement `generate`. Never call broker, execution, or risk
    from strategy code (Aegis_Claude_Usage_Note.txt)."""

    name: str = "base"
    version: str = "v1"

    def generate(
        self,
        symbol: str,
        feature_snapshot: Dict[str, Any],
        regime_snapshot: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def entry_point(
        self,
        symbol: str,
        feature_snapshot: Dict[str, Any],
        regime_snapshot: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Adapter matching the positional-call convention used by
        aegis.marketplace.StrategyRunner."""
        return self.generate(symbol, feature_snapshot, regime_snapshot)

    def metadata(self, active: bool = True) -> Dict[str, Any]:
        return {"name": self.name, "version": self.version, "active": active}
