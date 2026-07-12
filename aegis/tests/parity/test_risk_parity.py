from __future__ import annotations

from aegis.parity.risk_adapter import RiskParityAdapter


def test_risk_parity_adapter_runs():
    result = RiskParityAdapter().run()
    assert result.name == "risk"
    assert result.ok, f"risk parity threshold exceeded: diff={result.diff}, details={result.details}"
