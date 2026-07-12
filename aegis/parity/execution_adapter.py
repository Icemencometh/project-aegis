from __future__ import annotations

from aegis.execution import PaperBroker as AegisPaperBroker

from .common import ParityResult, bounded_ratio, get_threshold, load_parity_config


class ExecutionParityAdapter:
    def run(self) -> ParityResult:
        cfg = load_parity_config()
        threshold = get_threshold(cfg, "execution", 0.10)

        # Legacy baseline approximation retained as deterministic target.
        legacy_status = "FILLED"
        legacy_filled = 1.0

        aegis = AegisPaperBroker()
        aegis.connect()
        result = aegis.submit_order({"symbol": "AAPL", "side": "BUY", "qty": 5, "type": "market"})
        aegis_filled = 1.0 if str(result.get("status", "")).lower() == "filled" else 0.0

        diff = bounded_ratio(legacy_filled, aegis_filled)
        ok = diff <= threshold
        return ParityResult(
            name="execution",
            ok=ok,
            diff=diff,
            threshold=threshold,
            details={"legacy_status": legacy_status, "aegis_status": result.get("status")},
        )
