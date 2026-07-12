from __future__ import annotations

from aegis.parity.regime_adapter import RegimeParityAdapter


def test_regime_parity_adapter_runs():
    result = RegimeParityAdapter().run()
    assert result.name == "regime"
    assert result.ok, f"regime parity threshold exceeded: diff={result.diff}, details={result.details}"
