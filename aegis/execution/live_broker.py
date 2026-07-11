from __future__ import annotations


class LiveBroker:
    def connect(self):
        return None

    def submit_order(self, order):
        return {"status": "submitted", "order": dict(order)}

    def cancel_order(self, order_id):
        return {"status": "cancelled", "order_id": order_id}
