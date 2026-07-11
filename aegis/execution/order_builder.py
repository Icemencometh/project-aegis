from __future__ import annotations


class OrderBuilder:
    def build(self, trade_intent):
        return {
            "symbol": trade_intent["symbol"],
            "side": trade_intent["side"],
            "qty": trade_intent.get("qty", 0),
            "type": trade_intent.get("type", "market"),
        }