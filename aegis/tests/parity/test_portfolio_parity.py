from __future__ import annotations

from aegis.parity.portfolio_adapter import PortfolioParityAdapter


def test_portfolio_parity_adapter_runs():
    result = PortfolioParityAdapter().run()
    assert result.name == "portfolio"
    assert result.threshold >= 0.0
    assert result.diff >= 0.0
