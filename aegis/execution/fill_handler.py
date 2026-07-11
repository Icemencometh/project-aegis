from __future__ import annotations


class FillHandler:
    def summarize(self, result):
        result = dict(result or {})
        return {"status": result.get("status"), "filled_qty": result.get("filled_qty", result.get("qty", 0))}