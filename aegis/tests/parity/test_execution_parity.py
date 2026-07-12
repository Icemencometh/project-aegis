from __future__ import annotations

from aegis.parity.execution_adapter import ExecutionParityAdapter


def test_execution_parity_adapter_runs():
    result = ExecutionParityAdapter().run()
    assert result.name == "execution"
    assert result.threshold >= 0.0
    assert result.diff >= 0.0
