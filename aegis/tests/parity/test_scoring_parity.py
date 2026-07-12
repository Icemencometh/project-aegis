from __future__ import annotations

from aegis.parity.scoring_adapter import ScoringParityAdapter


def test_scoring_parity_adapter_runs():
    result = ScoringParityAdapter().run()
    assert result.name == "scoring"
    assert result.ok, f"scoring parity threshold exceeded: diff={result.diff}, details={result.details}"
