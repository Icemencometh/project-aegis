from __future__ import annotations

from aegis.parity.scoring_adapter import ScoringParityAdapter


def test_scoring_parity_adapter_runs():
    result = ScoringParityAdapter().run()
    assert result.name == "scoring"
    assert result.threshold >= 0.0
    assert result.diff >= 0.0
