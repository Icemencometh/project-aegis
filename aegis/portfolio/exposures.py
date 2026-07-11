from __future__ import annotations


def aggregate_exposures(positions):
    per_symbol = {}
    gross = 0.0
    net = 0.0
    for symbol, payload in dict(positions or {}).items():
        qty = int(payload.get("qty", 0) if isinstance(payload, dict) else getattr(payload, "qty", 0))
        avg_price = float(payload.get("avg_price", 0.0) if isinstance(payload, dict) else getattr(payload, "avg_price", 0.0))
        value = qty * avg_price
        per_symbol[str(symbol)] = {"qty": qty, "avg_price": avg_price, "value": value}
        gross += abs(value)
        net += value
    return {"gross": gross, "net": net, "per_symbol": per_symbol}