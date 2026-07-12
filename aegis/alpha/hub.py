from __future__ import annotations

from typing import Any, Dict


class AlphaHub:
    def __init__(self, prediction_service, calibration_service, model_registry):
        self.prediction_service = prediction_service
        self.calibration_service = calibration_service
        self.model_registry = model_registry

    def produce_trade_intent(self, scored_trade: Dict[str, Any]) -> Dict[str, Any]:
        symbol = scored_trade["symbol"]
        features = scored_trade.get("features", {})
        model_name = str(scored_trade.get("model", "default"))
        model_meta = self.model_registry.get(model_name) if hasattr(self.model_registry, "get") else {}
        ml_out = self.prediction_service.predict(symbol, features)
        prob_up = self.calibration_service.calibrate(ml_out["prob_up"])
        side = "BUY" if prob_up >= 0.5 else "SELL"
        return {
            "symbol": symbol,
            "side": side,
            "entry": scored_trade.get("entry"),
            "stop": scored_trade.get("stop"),
            "target": scored_trade.get("target"),
            "probability": prob_up * 100.0,
            "expected_return": ml_out.get("expected_return"),
            "holding_time": ml_out.get("holding_time"),
            # Not part of the contract's required field list, but carried
            # through additively so downstream marketplace/allocation stages
            # (e.g. enforce_strategy_concentration) can still attribute a
            # trade intent back to the strategy that emitted the candidate.
            "strategy": scored_trade.get("strategy"),
            "strategy_version": scored_trade.get("strategy_version"),
            "alpha_metadata": {
                "model": model_name,
                "model_version": ml_out.get("version"),
                "registry": model_meta,
            },
        }