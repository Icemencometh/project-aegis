from __future__ import annotations

from aegis.parity.allocation_adapter import AllocationParityAdapter


def test_allocation_parity_adapter_runs():
    result = AllocationParityAdapter().run()
    assert result.name == "allocation"
    assert result.threshold >= 0.0
    assert result.diff >= 0.0
