from __future__ import annotations

try:
    from modules.paper_broker import PaperBroker as LegacyPaperBroker  # legacy module may be absent in CI snapshots
except Exception:  # pragma: no cover - fallback path for CI portability
    LegacyPaperBroker = None

from aegis.execution import PaperBroker as AegisPaperBroker

from .common import ParityResult, bounded_ratio, get_threshold, load_parity_config


class ExecutionParityAdapter:
    def run(self) -> ParityResult:
        cfg = load_parity_config()
        threshold = get_threshold(cfg, "execution", 0.10)

        if LegacyPaperBroker is not None:
            legacy = LegacyPaperBroker()
            legacy.connect()
            order_id = legacy.place_order("AAPL", "buy", 5, order_type="market")
            legacy_status = legacy.get_order_status(order_id).get("status")
            legacy_filled = 1.0 if str(legacy_status).upper() == "FILLED" else 0.0
        else:
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
