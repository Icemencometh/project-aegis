from __future__ import annotations

from aegis.parity.risk_adapter import RiskParityAdapter


def test_risk_parity_adapter_runs():
    result = RiskParityAdapter().run()
    assert result.name == "risk"
    assert result.threshold >= 0.0
    assert result.diff >= 0.0
