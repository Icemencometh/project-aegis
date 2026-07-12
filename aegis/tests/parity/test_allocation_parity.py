from __future__ import annotations

from aegis.parity.allocation_adapter import AllocationParityAdapter


def test_allocation_parity_adapter_runs():
    result = AllocationParityAdapter().run()
    assert result.name == "allocation"
    assert result.ok, f"allocation parity threshold exceeded: diff={result.diff}, details={result.details}"
