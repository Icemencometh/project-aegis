from __future__ import annotations

from aegis.parity.execution_adapter import ExecutionParityAdapter


def test_execution_parity_adapter_runs():
    result = ExecutionParityAdapter().run()
    assert result.name == "execution"
    assert result.ok, f"execution parity threshold exceeded: diff={result.diff}, details={result.details}"
