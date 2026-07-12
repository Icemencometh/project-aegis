from __future__ import annotations

from aegis.parity.portfolio_adapter import PortfolioParityAdapter


def test_portfolio_parity_adapter_runs():
    result = PortfolioParityAdapter().run()
    assert result.name == "portfolio"
    assert result.ok, f"portfolio parity threshold exceeded: diff={result.diff}, details={result.details}"
