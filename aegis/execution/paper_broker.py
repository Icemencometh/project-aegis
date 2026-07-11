from __future__ import annotations


class PaperBroker:
    def connect(self):
        return None

    def submit_order(self, order):
        return {"status": "filled", "order": dict(order), "filled_qty": order.get("qty", 0)}

    def cancel_order(self, order_id):
        return {"status": "cancelled", "order_id": order_id}
